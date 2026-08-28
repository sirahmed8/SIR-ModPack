"""SIR Server Manager — standalone entry-point.

Uses shared_core.runtime for DPI awareness and reliable PID-based window
centering so the window always appears on the correct monitor at the correct
position regardless of any other running SIR windows.
"""

import os
import sys
import webview

# ── path resolution (frozen PyInstaller vs dev) ──────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
    ROOT_DIR = APP_DIR
    if not os.path.exists(os.path.join(ROOT_DIR, "mods")):
        parent = os.path.dirname(APP_DIR)
        if os.path.exists(os.path.join(parent, "mods")):
            ROOT_DIR = parent
    UI_DIR = os.path.join(BASE_DIR, "server_ui")
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    UI_DIR = os.path.join(BASE_DIR, "server_ui")
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

# ── shared runtime (DPI, centering, atomic I/O) ──────────────────────────────
try:
    from shared_core.runtime import ensure_dpi_awareness, center_process_window, canonical_data_root, resolve_payload_root
except ImportError:
    # Fallback — inline minimal versions so the app still works without shared_core
    import ctypes
    import time

    def ensure_dpi_awareness():
        if sys.platform != "win32":
            return
        try:
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

    def center_process_window(pid, width, height, attempts=40):
        if sys.platform != "win32" or not pid:
            return False
        user32 = ctypes.windll.user32
        found = {"hwnd": 0}

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def callback(hwnd, _):
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
                class _RECT(ctypes.Structure):
                    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                                 ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
                rect = _RECT()
                user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
                work_w = rect.right - rect.left
                work_h = rect.bottom - rect.top
                x = rect.left + max(0, (work_w - width) // 2)
                y = rect.top + max(0, (work_h - height) // 2)
                user32.SetWindowPos(hwnd, 0, x, y, width, height, 0x0040)
                return True
            time.sleep(0.1)
        return False

# ── constants ─────────────────────────────────────────────────────────────────
from server_core.server_bridge import ServerBridgeAPI

WINDOW_WIDTH  = 1180
WINDOW_HEIGHT = 760


def _apply_dwm_dark(hwnd) -> None:
    """Apply Windows 11 immersive dark title bar (best-effort)."""
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
    """Called by pywebview after the native window is created.

    1. Centers the window using the reliable PID-based approach.
    2. Applies Win11 dark chrome.
    """
    import ctypes
    import time
    import threading

    pid = os.getpid()

    def _worker():
        # center_process_window loops up to `attempts` × 100 ms looking for the
        # first visible top-level window owned by our PID — no title matching.
        center_process_window(pid, WINDOW_WIDTH, WINDOW_HEIGHT, attempts=40)

        # After centering, also apply the DWM dark attribute.
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


def main() -> None:
    ensure_dpi_awareness()

    PAYLOAD_ROOT = resolve_payload_root(ROOT_DIR)
    DATA_ROOT = canonical_data_root()
    api = ServerBridgeAPI(PAYLOAD_ROOT, data_root=DATA_ROOT)
    html_file = os.path.join(UI_DIR, "index.html")

    if not os.path.exists(html_file):
        raise FileNotFoundError(f"Server UI missing: {html_file}")

    webview.create_window(
        title="SIR Server Orchestrator Pro v1.0.0",
        url=f"file:///{html_file.replace(os.sep, '/')}",
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        x=80,   # will be corrected by on_window_ready via PID centering
        y=80,
        resizable=True,
        min_size=(980, 640),
        background_color="#06090e",
        easy_drag=False,
    )

    webview.start(
        func=on_window_ready,
        debug=False,
        http_server=False,
        gui="edgechromium",
    )


if __name__ == "__main__":
    main()
