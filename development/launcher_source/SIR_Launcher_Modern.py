"""SIR Launcher — standalone development entry-point.

Uses shared_core.runtime for DPI awareness, canonical data paths, and
reliable PID-based window centering.
"""

from __future__ import annotations

import json
import os
import sys
import time
import threading
import webview

# Path resolution
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
    ROOT_DIR = APP_DIR
    if not os.path.exists(os.path.join(ROOT_DIR, "mods")):
        parent = os.path.dirname(APP_DIR)
        if os.path.exists(os.path.join(parent, "mods")):
            ROOT_DIR = parent
    UI_DIR = os.path.join(BASE_DIR, "launcher_ui")
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    UI_DIR = os.path.join(BASE_DIR, "launcher_ui")
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

from shared_core.runtime import (
    canonical_data_root,
    center_process_window,
    ensure_dpi_awareness,
    resolve_payload_root,
    resolve_prism_root,
)
from launcher_core import LauncherBridgeAPI, TrayService

WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 760

ensure_dpi_awareness()
PAYLOAD_ROOT = resolve_payload_root(ROOT_DIR)
DATA_ROOT = canonical_data_root()
PRISM_ROOT = resolve_prism_root(DATA_ROOT)


def _apply_dwm_dark(hwnd) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        dwmapi = ctypes.windll.dwmapi
        for attr in (20, 19):
            dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
        caption_color = ctypes.c_int(0x000E0906)
        dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption_color), ctypes.sizeof(caption_color))
    except Exception:
        pass


def on_window_ready() -> None:
    import ctypes
    import threading

    pid = os.getpid()

    def _worker():
        center_process_window(pid, WINDOW_WIDTH, WINDOW_HEIGHT, attempts=40)
        if sys.platform == "win32":
            user32 = ctypes.windll.user32
            found = {"hwnd": 0}

            @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            def cb(hwnd, _):
                if not user32.IsWindowVisible(hwnd):
                    return True
                owner = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                if owner.value == pid and user32.GetWindow(hwnd, 4) == 0:
                    found["hwnd"] = hwnd
                    return False
                return True

            user32.EnumWindows(cb, None)
            if found["hwnd"]:
                _apply_dwm_dark(found["hwnd"])

    threading.Thread(target=_worker, daemon=True).start()


def _enforce_single_instance() -> bool:
    """Ensures only one instance of SIR Launcher is running.
    If another instance is already running, activates it and returns False to exit.
    """
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        MUTEX_NAME = "Global\\SIR_Launcher_Pro_SingleInstance_Mutex"
        handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = kernel32.GetLastError()
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            if len(sys.argv) > 1 and any(sys.argv[1].lower().startswith(p) for p in ("sirlauncher://", "sir-launcher://")):
                try:
                    import urllib.parse
                    raw_arg = sys.argv[1]
                    parsed = urllib.parse.urlparse(raw_arg)
                    params = urllib.parse.parse_qs(parsed.query)
                    dl_payload = {
                        "action": parsed.netloc or parsed.path.strip("/"),
                        "params": {k: v[0] if len(v) == 1 else v for k, v in params.items()},
                        "raw": raw_arg,
                        "timestamp": time.time(),
                    }
                    os.makedirs(DATA_ROOT, exist_ok=True)
                    pending_file = os.path.join(DATA_ROOT, "pending_deeplink.json")
                    with open(pending_file, "w", encoding="utf-8") as f:
                        json.dump(dl_payload, f)
                except Exception:
                    pass

            hwnd = user32.FindWindowW(None, "SIR Launcher — The Ultimate Minecraft Experience")
            if hwnd:
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(hwnd)
            return False
        return True
    except Exception:
        return True


def main():
    if not _enforce_single_instance():
        sys.exit(0)

    api = LauncherBridgeAPI(PAYLOAD_ROOT, data_root=DATA_ROOT, prism_root=PRISM_ROOT)
    index_html = os.path.join(UI_DIR, "index.html")

    if not os.path.exists(index_html):
        raise FileNotFoundError(f"Launcher UI missing: {index_html}")

    # Instant Zero-Latency Account & Deep-Link Pre-Hydration
    try:
        acc_info = api.get_accounts()
        deep_link_data = None
        if len(sys.argv) > 1 and any(sys.argv[1].lower().startswith(p) for p in ("sirlauncher://", "sir-launcher://")):
            try:
                import urllib.parse
                raw_arg = sys.argv[1]
                parsed = urllib.parse.urlparse(raw_arg)
                params = urllib.parse.parse_qs(parsed.query)
                deep_link_data = {
                    "action": parsed.netloc or parsed.path.strip("/"),
                    "params": {k: v[0] if len(v) == 1 else v for k, v in params.items()},
                    "raw": raw_arg,
                }
            except Exception:
                pass

        cloud_info = api.get_cloud_status() if hasattr(api, "get_cloud_status") else {"authenticated": False}
        bootstrap_file = os.path.join(UI_DIR, "bootstrap_cache.js")
        with open(bootstrap_file, "w", encoding="utf-8") as bf:
            bf.write(f"window.__SIR_BOOTSTRAP__ = {json.dumps(acc_info)};\n")
            bf.write(f"window.__SIR_CLOUD_BOOTSTRAP__ = {json.dumps(cloud_info)};\n")
            bf.write("window.__SIR_MODS_COUNT_PRE_HYDRATE__ = 228;\n")
            if deep_link_data:
                bf.write(f"window.__SIR_DEEP_LINK__ = {json.dumps(deep_link_data)};\n")
            else:
                bf.write("window.__SIR_DEEP_LINK__ = null;\n")
    except Exception:
        pass

    start_hidden = any(arg.lower() in ("--autostart", "--minimized") for arg in sys.argv[1:])

    window = webview.create_window(
        title="SIR Launcher — The Ultimate Minecraft Experience",
        url=f"file:///{index_html.replace(os.sep, '/')}",
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(960, 620),
        background_color="#06090e",
        easy_drag=False,
        hidden=start_hidden,
    )
    api.set_window(window)

    icon_candidates = [
        os.path.join(ROOT_DIR, "SIR_Icon.ico"),
        os.path.join(BASE_DIR, "SIR_Icon.ico"),
        os.path.join(os.path.dirname(ROOT_DIR), "SIR_Icon.ico"),
    ]
    icon_path = next((p for p in icon_candidates if os.path.isfile(p)), os.path.join(ROOT_DIR, "SIR_Icon.ico"))

    tray = TrayService(
        icon_path=icon_path,
        window=window,
        bridge_api=api,
        on_exit_callback=api.kill_all_instances,
    )

    def on_closing():
        settings = api.instances.load_settings()
        action = settings.get("window_close_action", "tray")
        if action == "tray":
            if tray and getattr(tray, "is_running", False):
                window.hide()
                return False
            else:
                window.minimize()
                return False
        elif action == "taskbar":
            window.minimize()
            return False
        else:  # "exit"
            try:
                tray.stop()
            except Exception:
                pass
            api.kill_all_instances()
            if hasattr(api, "loopback") and api.loopback:
                try:
                    api.loopback.stop()
                except Exception:
                    pass
            if hasattr(api, "cloud_sync") and api.cloud_sync:
                try:
                    api.cloud_sync.stop_listener()
                except Exception:
                    pass
            def _force_exit():
                time.sleep(0.2)
                try:
                    os._exit(0)
                except Exception:
                    pass
            threading.Thread(target=_force_exit, daemon=True).start()
            return True

    def on_minimized():
        settings = api.instances.load_settings()
        action = settings.get("window_minimize_action", "taskbar")
        if action == "tray":
            window.hide()

    window.events.closing += on_closing
    window.events.minimized += on_minimized

    def _ready():
        if not start_hidden:
            on_window_ready()

        # Background daemon thread polling pending_deeplink.json for multi-instance forwarding
        def _poll_pending_deeplink():
            pending_file = os.path.join(DATA_ROOT, "pending_deeplink.json")
            while True:
                time.sleep(0.4)
                if os.path.isfile(pending_file):
                    try:
                        with open(pending_file, "r", encoding="utf-8") as pf:
                            dl_data = json.load(pf)
                        os.remove(pending_file)
                        if dl_data and window:
                            js = f"if (window.handleIncomingDeepLink) window.handleIncomingDeepLink({json.dumps(dl_data)});"
                            window.evaluate_js(js)
                    except Exception:
                        pass
        threading.Thread(target=_poll_pending_deeplink, daemon=True).start()

        # Defer TrayService startup until EdgeChromium message pump is fully processing
        def _deferred_tray_start():
            time.sleep(1.5)
            try:
                tray.start()
            except Exception:
                pass
        threading.Thread(target=_deferred_tray_start, daemon=True).start()

    webview.start(_ready, gui="edgechromium", debug=False)


if __name__ == "__main__":
    main()
