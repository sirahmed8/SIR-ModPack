"""
telemetry_governor_service.py — Native Windows Performance & Process Governor.
Monitors child JVM process memory working set, commit charge, CPU utilization,
and provides working set memory trimming via ctypes (kernel32.dll, psapi.dll).
"""
from __future__ import annotations

import ctypes
import os
import sys
import threading
import time
from typing import Any, Callable, Dict, Optional


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", ctypes.c_uint), ("dwHighDateTime", ctypes.c_uint)]


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def _filetime_to_int(ft: FILETIME) -> int:
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime


if sys.platform == "win32":
    try:
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi

        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int

        psapi.EmptyWorkingSet.argtypes = [ctypes.c_void_p]
        psapi.EmptyWorkingSet.restype = ctypes.c_int

        psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    except Exception:
        pass


class TelemetryGovernorService:
    """Zero-dependency Win32 telemetry governor and working set memory manager."""

    _instance: Optional[TelemetryGovernorService] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._proc_times: Dict[int, tuple[float, int, int]] = {}  # pid -> (timestamp, kernel_100ns, user_100ns)
        self._monitored_threads: Dict[int, threading.Event] = {}
        self._state_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> TelemetryGovernorService:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def get_process_telemetry(self, pid: int) -> Dict[str, Any]:
        """Monitors child JVM process memory working set, commit charge, and CPU usage."""
        if not pid or pid <= 0:
            return {"success": False, "error": "Invalid PID"}

        if sys.platform != "win32":
            return {
                "success": True,
                "pid": pid,
                "working_set_mb": 0.0,
                "private_commit_mb": 0.0,
                "peak_working_set_mb": 0.0,
                "cpu_load_pct": 0.0,
                "timestamp": time.strftime("%H:%M:%S"),
            }

        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        hProcess = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid
        )
        if not hProcess:
            return {"success": False, "error": f"Process {pid} is not running or access denied"}

        exit_code = ctypes.c_ulong()
        if ctypes.windll.kernel32.GetExitCodeProcess(hProcess, ctypes.byref(exit_code)):
            if exit_code.value != 259:  # STILL_ACTIVE
                ctypes.windll.kernel32.CloseHandle(hProcess)
                return {"success": False, "error": f"Process {pid} is not running or access denied"}

        try:
            pmc = PROCESS_MEMORY_COUNTERS_EX()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
            if ctypes.windll.psapi.GetProcessMemoryInfo(hProcess, ctypes.byref(pmc), pmc.cb):
                working_set_mb = round(pmc.WorkingSetSize / (1024 * 1024), 1)
                private_commit_mb = round(pmc.PrivateUsage / (1024 * 1024), 1)
                peak_working_set_mb = round(pmc.PeakWorkingSetSize / (1024 * 1024), 1)
            else:
                working_set_mb, private_commit_mb, peak_working_set_mb = 0.0, 0.0, 0.0

            # Process CPU calculation
            create_ft = FILETIME()
            exit_ft = FILETIME()
            kernel_ft = FILETIME()
            user_ft = FILETIME()
            proc_cpu_pct = 0.0

            if ctypes.windll.kernel32.GetProcessTimes(
                hProcess,
                ctypes.byref(create_ft),
                ctypes.byref(exit_ft),
                ctypes.byref(kernel_ft),
                ctypes.byref(user_ft),
            ):
                k_int = _filetime_to_int(kernel_ft)
                u_int = _filetime_to_int(user_ft)
                now_t = time.time()

                with self._state_lock:
                    if pid in self._proc_times:
                        prev_t, prev_k, prev_u = self._proc_times[pid]
                        delta_t = now_t - prev_t
                        if delta_t > 0:
                            total_time = (k_int - prev_k) + (u_int - prev_u)  # 100ns units
                            cpu_sec = total_time * 1e-7
                            num_cores = os.cpu_count() or 1
                            proc_cpu_pct = round((cpu_sec / (delta_t * num_cores)) * 100, 1)
                    self._proc_times[pid] = (now_t, k_int, u_int)

            return {
                "success": True,
                "pid": pid,
                "working_set_mb": working_set_mb,
                "private_commit_mb": private_commit_mb,
                "peak_working_set_mb": peak_working_set_mb,
                "cpu_load_pct": max(0.0, min(100.0, proc_cpu_pct)),
                "timestamp": time.strftime("%H:%M:%S"),
            }
        finally:
            ctypes.windll.kernel32.CloseHandle(hProcess)

    def trim_process_memory(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """Flushes idle working set memory pages to pagefile via EmptyWorkingSet API."""
        if sys.platform != "win32":
            return {"success": False, "error": "EmptyWorkingSet is only available on Windows"}

        try:
            if pid is None or pid == 0:
                hProcess = ctypes.windll.kernel32.GetCurrentProcess()
                target_name = "SIR Launcher Engine"
                close_needed = False
            else:
                PROCESS_SET_QUOTA = 0x0100
                PROCESS_QUERY_INFORMATION = 0x0400
                hProcess = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid
                )
                target_name = f"Process PID {pid}"
                close_needed = True

            if not hProcess:
                return {"success": False, "error": f"Failed to acquire handle for {target_name}"}

            try:
                pmc_before = PROCESS_MEMORY_COUNTERS_EX()
                pmc_before.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
                ctypes.windll.psapi.GetProcessMemoryInfo(
                    hProcess, ctypes.byref(pmc_before), pmc_before.cb
                )
                before_mb = round(pmc_before.WorkingSetSize / (1024 * 1024), 2)

                trimmed = ctypes.windll.psapi.EmptyWorkingSet(hProcess)

                pmc_after = PROCESS_MEMORY_COUNTERS_EX()
                pmc_after.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
                ctypes.windll.psapi.GetProcessMemoryInfo(
                    hProcess, ctypes.byref(pmc_after), pmc_after.cb
                )
                after_mb = round(pmc_after.WorkingSetSize / (1024 * 1024), 2)
                freed_mb = max(0.0, round(before_mb - after_mb, 2))

                return {
                    "success": bool(trimmed),
                    "target": target_name,
                    "before_mb": before_mb,
                    "after_mb": after_mb,
                    "freed_mb": freed_mb,
                    "message": (
                        f"Memory Governor trimmed {freed_mb} MB working set from {target_name} "
                        f"({before_mb} MB -> {after_mb} MB)."
                    ),
                }
            finally:
                if close_needed:
                    ctypes.windll.kernel32.CloseHandle(hProcess)
        except Exception as ex:
            return {"success": False, "error": str(ex)}
