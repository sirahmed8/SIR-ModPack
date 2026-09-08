"""
hardware_monitor_service.py — Native Windows Performance, Multi-GPU & Telemetry Governor.
Zero-Dependency Implementation with Win32 Memory, CPU, Child PID Tracking & EmptyWorkingSet Trimming.
"""
from __future__ import annotations

import ctypes
import os
import shutil
import sys
import time
import winreg
from typing import Any, Dict, List, Optional

from .telemetry_governor_service import TelemetryGovernorService


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


def _filetime_to_int(ft: FILETIME) -> int:
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime


class HardwareMonitorService:
    """Zero-dependency native Windows performance, GPU, and memory telemetry engine."""

    def __init__(self) -> None:
        self.cached_gpu = self._detect_gpu()
        self.cached_gpus = self._detect_all_gpus()
        self._prev_idle = 0
        self._prev_kernel = 0
        self._prev_user = 0
        self._governor = TelemetryGovernorService.get_instance()
        self._init_cpu_times()

    def _init_cpu_times(self) -> None:
        if sys.platform != "win32":
            return
        try:
            idle = FILETIME()
            kernel = FILETIME()
            user = FILETIME()
            if ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
            ):
                self._prev_idle = _filetime_to_int(idle)
                self._prev_kernel = _filetime_to_int(kernel)
                self._prev_user = _filetime_to_int(user)
        except Exception:
            pass

    def _get_cpu_load(self) -> int:
        if sys.platform != "win32":
            return 0
        try:
            idle = FILETIME()
            kernel = FILETIME()
            user = FILETIME()
            if ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
            ):
                i_now = _filetime_to_int(idle)
                k_now = _filetime_to_int(kernel)
                u_now = _filetime_to_int(user)

                idle_delta = i_now - self._prev_idle
                kernel_delta = k_now - self._prev_kernel
                user_delta = u_now - self._prev_user

                self._prev_idle = i_now
                self._prev_kernel = k_now
                self._prev_user = u_now

                total = kernel_delta + user_delta
                if total > 0:
                    cpu_pct = int(100.0 * (total - idle_delta) / total)
                    return max(0, min(100, cpu_pct))
        except Exception:
            pass
        return 0

    def _detect_gpu(self) -> str:
        gpus = self._detect_all_gpus()
        if gpus:
            # Prefer dedicated GPUs (NVIDIA / AMD) over integrated
            for g in gpus:
                g_low = g.lower()
                if "geforce" in g_low or "rtx" in g_low or "gtx" in g_low or "radeon" in g_low:
                    return g
            return gpus[0]
        return "Integrated Graphics"

    def _detect_all_gpus(self) -> List[str]:
        if sys.platform != "win32":
            return []
        found_gpus = []
        try:
            path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    if subkey_name.isdigit():
                        try:
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                name, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                                if name and "basic" not in name.lower() and name not in found_gpus:
                                    found_gpus.append(name)
                        except Exception:
                            pass
        except Exception:
            pass
        return found_gpus

    def get_hardware_telemetry(self) -> Dict[str, Any]:
        """Returns live hardware metrics directly from Windows Kernel."""
        # 1. Physical RAM via kernel32 GlobalMemoryStatusEx
        total_gb, avail_gb, used_gb, load_pct = 0.0, 0.0, 0.0, 0
        if sys.platform == "win32":
            try:
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                    total_gb = round(stat.ullTotalPhys / (1024 ** 3), 1)
                    avail_gb = round(stat.ullAvailPhys / (1024 ** 3), 1)
                    used_gb = round(total_gb - avail_gb, 1)
                    load_pct = stat.dwMemoryLoad
            except Exception:
                pass

        # 2. CPU Logical Cores & Live CPU Load
        cpu_count = os.cpu_count() or 4
        cpu_load_pct = self._get_cpu_load()

        # 3. Disk space telemetry
        try:
            cwd_drive = os.path.splitdrive(os.getcwd())[0] or "C:"
            total_disk, used_disk, free_disk = shutil.disk_usage(cwd_drive)
            disk_total_gb = round(total_disk / (1024 ** 3), 1)
            disk_free_gb = round(free_disk / (1024 ** 3), 1)
        except Exception:
            disk_total_gb, disk_free_gb = 0.0, 0.0

        # 4. Dedicated RAM Recommendation & Power Tier
        if total_gb >= 32:
            rec_ram = 10
            power_tier = f"Ultra / Creator Tier ({int(total_gb)} GB)"
        elif total_gb >= 16:
            rec_ram = 8
            power_tier = f"High Performance Tier ({int(total_gb)} GB)"
        elif total_gb >= 8:
            rec_ram = 6
            power_tier = f"Balanced Standard Tier ({int(total_gb)} GB)"
        elif total_gb >= 4:
            rec_ram = 3
            power_tier = f"Standard Tier ({int(total_gb)} GB)"
        else:
            rec_ram = 2
            power_tier = f"Low-End / Eco Tier ({int(total_gb)} GB)"

        gpu_name = self.cached_gpu or "Generic Display Adapter"
        recommendation = (
            f"System detected: {cpu_count} CPU Threads, {total_gb} GB RAM, {gpu_name}. "
            f"Recommended allocation for optimal frametimes: {rec_ram} GB Dedicated Heap."
        )

        return {
            "success": True,
            "total_ram_gb": total_gb,
            "used_ram_gb": used_gb,
            "avail_ram_gb": avail_gb,
            "ram_load_pct": load_pct,
            "ram_pct": load_pct,
            "cpu_cores": cpu_count,
            "cpu_count": cpu_count,
            "cpu_load_pct": cpu_load_pct,
            "cpu_pct": cpu_load_pct,
            "gpu_name": gpu_name,
            "all_gpus": self.cached_gpus,
            "disk_total_gb": disk_total_gb,
            "disk_free_gb": disk_free_gb,
            "recommended_ram_gb": rec_ram,
            "rec_ram_gb": rec_ram,
            "power_tier": power_tier,
            "recommendation": recommendation,
            "timestamp": time.strftime("%H:%M:%S"),
        }

    def get_process_telemetry(self, pid: int) -> Dict[str, Any]:
        """Delegates process telemetry to TelemetryGovernorService."""
        return self._governor.get_process_telemetry(pid)

    def trim_process_memory(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """Delegates working set trimming to TelemetryGovernorService."""
        return self._governor.trim_process_memory(pid)

    def trim_memory(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """Alias for trim_process_memory."""
        return self.trim_process_memory(pid)

