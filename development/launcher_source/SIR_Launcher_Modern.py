"""SIR Launcher — standalone development entry-point.

Uses shared_core.runtime for DPI awareness, canonical data paths, and
reliable PID-based window centering.
"""

from __future__ import annotations

import os
import sys
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
from launcher_core import LauncherBridgeAPI

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


def main():
    api = LauncherBridgeAPI(PAYLOAD_ROOT, data_root=DATA_ROOT, prism_root=PRISM_ROOT)
    index_html = os.path.join(UI_DIR, "index.html")

    if not os.path.exists(index_html):
        raise FileNotFoundError(f"Launcher UI missing: {index_html}")

    webview.create_window(
        title="SIR Launcher — The Ultimate Minecraft Experience",
        url=f"file:///{index_html.replace(os.sep, '/')}",
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        x=80,
        y=80,
        min_size=(960, 620),
        background_color="#06090e",
        easy_drag=False,
    )

    webview.start(on_window_ready, gui="edgechromium", debug=False)


if __name__ == "__main__":
    main()
