"""Runtime path and Windows window-management primitives.

The old applications derived state from the executable's directory. That made
each copied EXE appear to have a different account list. This module gives all
dispatcher modes one stable per-user state directory while keeping the
read-only release payload separate.
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


APP_NAME = "SIR ModPack"


def canonical_data_root(app_name: str = APP_NAME) -> str:
    """Return and create the one canonical per-user application data root."""

    appdata = os.environ.get("APPDATA") or os.path.join(
        os.path.expanduser("~"), "AppData", "Roaming"
    )
    root = os.path.join(appdata, app_name)
    os.makedirs(root, exist_ok=True)
    os.makedirs(os.path.join(root, "state"), exist_ok=True)
    os.makedirs(os.path.join(root, "logs"), exist_ok=True)
    os.makedirs(os.path.join(root, "skins"), exist_ok=True)
    return os.path.abspath(root)


def resolve_payload_root(start: str | None = None) -> str:
    """Find the managed SIR payload without using an old EXE's sibling state."""

    if start is None:
        start = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.getcwd()

    candidate = os.path.abspath(start)
    candidates = [
        os.path.join(candidate, "payload"),
        candidate,
        os.path.dirname(candidate),
    ]
    for path in candidates:
        if os.path.isdir(path) and any(
            os.path.exists(os.path.join(path, marker))
            for marker in ("instances", "mods", "resourcepacks", "shaderpacks")
        ):
            return path

    # Development entrypoints live in development/<module>; the project root
    # is two levels above that directory.
    if not getattr(sys, "frozen", False):
        here = Path(__file__).resolve()
        for parent in (here.parent.parent.parent, here.parent.parent.parent.parent):
            if (parent / "instances").exists() and (parent / "mods").exists():
                return str(parent)

    return candidate


def detect_system_java(version_hint=21) -> str:
    """Finds real valid javaw.exe on the system for modern (Java 21) or legacy (Java 8)."""
    appdata = os.getenv("APPDATA", "")
    program_files = os.getenv("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)")

    candidates_21 = [
        os.path.join(appdata, ".minecraft", "runtime", "java-runtime-delta", "windows-x64", "bin", "javaw.exe"),
        os.path.join(appdata, ".minecraft", "runtime", "java-runtime-gamma", "windows-x64", "bin", "javaw.exe"),
        os.path.join(appdata, ".minecraft", "runtime", "java-runtime-beta", "windows-x64", "bin", "javaw.exe"),
        os.path.join(program_files, "Java", "jdk-21", "bin", "javaw.exe"),
        os.path.join(program_files, "Java", "jdk-17", "bin", "javaw.exe"),
        os.path.join(program_files, "Eclipse Adoptium", "jdk-21", "bin", "javaw.exe"),
        os.path.join(program_files, "Microsoft", "jdk-21", "bin", "javaw.exe"),
    ]

    candidates_8 = [
        os.path.join(program_files, "Java", "jre1.8.0_503", "bin", "javaw.exe"),
        os.path.join(program_files_x86, "Java", "jre1.8.0_251", "bin", "javaw.exe"),
        os.path.join(program_files_x86, "Common Files", "Oracle", "Java", "java8path", "javaw.exe"),
        os.path.join(appdata, ".minecraft", "runtime", "jre-legacy", "windows-x64", "bin", "javaw.exe"),
        os.path.join(program_files, "Java", "jdk-17", "bin", "javaw.exe"),
    ]

    search_list = candidates_21 if version_hint >= 17 else candidates_8
    for c in search_list:
        if os.path.isfile(c):
            return os.path.abspath(c).replace("\\", "/")

    fallback_list = candidates_8 if version_hint >= 17 else candidates_21
    for c in fallback_list:
        if os.path.isfile(c):
            return os.path.abspath(c).replace("\\", "/")

    try:
        res = subprocess.check_output(["where.exe", "javaw"], text=True, errors="ignore")
        for line in res.splitlines():
            line = line.strip()
            if os.path.isfile(line):
                return os.path.abspath(line).replace("\\", "/")
    except Exception:
        pass

    return "javaw.exe"


def seed_prism_config(prism_dir: str, instances_dir: str | None = None) -> None:
    """Ensure Prism never shows quick setup wizard or telemetry dialogs."""
    appdata = os.getenv("APPDATA", "")
    target_dirs = [prism_dir]
    if appdata:
        target_dirs.append(os.path.join(appdata, "PrismLauncher"))
    
    # Also seed in parent / bin directories if present
    parent = os.path.dirname(os.path.abspath(prism_dir))
    for sub in ["bin", "SIR Launcher/bin", "SIR Package/SIR Launcher/bin"]:
        p = os.path.join(parent, sub)
        if os.path.isdir(p):
            target_dirs.append(p)

    java_path = detect_system_java(21)

    defaults = {
        "ConfigVersion": "1.3",
        "WizardFinished": "true",
        "FirstRun": "false",
        "QuickSetupDone": "true",
        "SetupWizard": "false",
        "QuickSetup": "false",
        "ShowJavaWizard": "false",
        "JavaAutoDownload": "true",
        "JavaAutoDetect": "true",
        "AutoDownloadJava": "true",
        "AutoDetectJava": "true",
        "ShownJavaPrompt": "true",
        "JavaPromptShown": "true",
        "JavaPrompt": "true",
        "JavaPromptVersion": "11.0.3",
        "AutoDownloadJavaFeaturePromptSeen": "true",
        "JavaAutoDownloadNotificationShown": "true",
        "JavaAutoDownloadPromptSeen": "true",
        "ShowWhatsNew": "false",
        "Analytics": "false",
        "AnalyticsSeen": "true",
        "Language": "en_US",
        "ApplicationTheme": "dark",
        "IconTheme": "pe_colored",
        "UseSystemLocale": "true",
        "AutoCloseConsole": "true",
        "ShowConsole": "false",
        "ShowConsoleOnError": "false",
        "RaiseConsole": "false",
        "QuitOnGameStop": "false",
        "CloseAfterLaunch": "true",
        "HideOnLaunch": "true",
        "CloseMainWindow": "true",
        "ShowLauncherOnGameClose": "false",
        "JavaPath": java_path,
        "MinMemAlloc": "4096",
        "MaxMemAlloc": "8192",
    }
    if instances_dir and os.path.isdir(instances_dir):
        defaults["InstanceDir"] = os.path.abspath(instances_dir).replace("\\", "/")
        
    for p_dir in set(target_dirs):
        try:
            os.makedirs(p_dir, exist_ok=True)
            cfg_path = os.path.join(p_dir, "prismlauncher.cfg")
            existing = {}
            if os.path.isfile(cfg_path):
                try:
                    with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            s = line.strip()
                            if "=" in s and not s.startswith("[") and not s.startswith("#"):
                                k, v = s.split("=", 1)
                                existing[k.strip()] = v.strip()
                except Exception:
                    pass

            for k, v in defaults.items():
                existing[k] = v

            out = ["[General]"]
            for k, v in existing.items():
                out.append(f"{k}={v}")
            out.append("")
            
            with open(cfg_path, "w", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(out))
        except Exception:
            pass



def resolve_prism_root(data_root: str | None = None) -> str:
    """Return the private Prism data root used by the dispatcher."""

    root = data_root or canonical_data_root()
    prism = os.path.join(root, "prism")
    os.makedirs(prism, exist_ok=True)
    seed_prism_config(prism)
    return prism


def ensure_dpi_awareness() -> None:
    """Set DPI awareness before creating a native webview window."""

    if sys.platform != "win32":
        return
    try:
        # Per-monitor v2. Older Windows versions may not expose this symbol.
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class _RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def _work_area_for_window(hwnd: int) -> _RECT:
    user32 = ctypes.windll.user32
    monitor = user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
    class _MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("rcMonitor", _RECT),
            ("rcWork", _RECT),
            ("dwFlags", ctypes.c_ulong),
        ]

    info = _MONITORINFO()
    info.cbSize = ctypes.sizeof(info)
    if monitor and user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
        return info.rcWork

    rect = _RECT()
    user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
    return rect


def center_process_window(pid: int | None, width: int, height: int, attempts: int = 40) -> bool:
    """Center the first visible top-level window owned by *pid*.

    This deliberately does not search by title, so old SIR windows cannot be
    accidentally moved when multiple builds are present during development.
    """

    if sys.platform != "win32" or not pid:
        return False
    user32 = ctypes.windll.user32
    found = {"hwnd": 0}

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def callback(hwnd, _extra):
        if not user32.IsWindowVisible(hwnd):
            return True
        owner_pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner_pid))
        if owner_pid.value == int(pid) and user32.GetWindow(hwnd, 4) == 0:
            found["hwnd"] = hwnd
            return False
        return True

    for _ in range(attempts):
        found["hwnd"] = 0
        user32.EnumWindows(callback, None)
        hwnd = found["hwnd"]
        if hwnd:
            work = _work_area_for_window(hwnd)
            work_w = work.right - work.left
            work_h = work.bottom - work.top
            x = work.left + max(0, (work_w - width) // 2)
            y = work.top + max(0, (work_h - height) // 2)
            user32.SetWindowPos(hwnd, 0, x, y, width, height, 0x0040)
            return True
        time.sleep(0.1)
    return False


def atomic_write_json(path: str, value: Any) -> None:
    """Write JSON through a same-directory temporary file and atomic replace."""

    target = os.path.abspath(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".sir-", suffix=".tmp", dir=os.path.dirname(target))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
