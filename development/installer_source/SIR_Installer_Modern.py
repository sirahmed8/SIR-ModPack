import os
import sys
import ctypes
import webview

# Robust path resolution for frozen pyinstaller executable vs dev source
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
    ROOT_DIR = APP_DIR
    if not os.path.exists(os.path.join(ROOT_DIR, "mods")):
        parent = os.path.dirname(APP_DIR)
        if os.path.exists(os.path.join(parent, "mods")):
            ROOT_DIR = parent
    UI_DIR = os.path.join(BASE_DIR, "installer_ui")
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    UI_DIR = os.path.join(BASE_DIR, "installer_ui")
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

from installer_core.installer_bridge import InstallerBridgeAPI

WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 760

def get_screen_center(width, height):
    """Calculates Windows desktop workarea screen center taking DPI scaling and taskbar into account."""
    try:
        if sys.platform == "win32":
            user32 = ctypes.windll.user32
            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
            rect = RECT()
            user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
            work_w = rect.right - rect.left
            work_h = rect.bottom - rect.top
            x = rect.left + max(0, (work_w - width) // 2)
            y = rect.top + max(0, (work_h - height) // 2)
            return int(x), int(y)
    except Exception:
        pass
    return 100, 100

def on_window_ready():
    """Applies Windows 11 DWM titlebar dark mode and forces precision window centering across DPI scales."""
    import time
    import threading

    def center_worker():
        try:
            if sys.platform != "win32":
                return
            user32 = ctypes.windll.user32
            mypid = os.getpid()

            for _ in range(30):
                time.sleep(0.1)
                hwnds = []

                def enum_cb(hwnd, extra):
                    if not user32.IsWindowVisible(hwnd):
                        return True
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buf, length + 1)
                        val = buf.value
                        if "SIR ModPack Installer" in val or "SIR Installer" in val:
                            hwnds.append(hwnd)
                            return False
                    lpdw_pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_pid))
                    if lpdw_pid.value == mypid:
                        hwnds.append(hwnd)
                        return False
                    return True

                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.py_object)
                user32.EnumWindows(WNDENUMPROC(enum_cb), None)

                if hwnds:
                    hwnd = hwnds[0]
                    # 1. Dark titlebar
                    for attr in [20, 19]:
                        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
                    caption_color = ctypes.c_int(0x000E0906)
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption_color), ctypes.sizeof(caption_color))

                    # 2. Precision Win32 Workarea Centering
                    class RECT(ctypes.Structure):
                        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
                    rect = RECT()
                    user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
                    work_w = rect.right - rect.left
                    work_h = rect.bottom - rect.top
                    pos_x = rect.left + max(0, (work_w - WINDOW_WIDTH) // 2)
                    pos_y = rect.top + max(0, (work_h - WINDOW_HEIGHT) // 2)
                    user32.SetWindowPos(hwnd, 0, pos_x, pos_y, WINDOW_WIDTH, WINDOW_HEIGHT, 0x0040)
                    break
        except Exception:
            pass

    threading.Thread(target=center_worker, daemon=True).start()

def main():
    api = InstallerBridgeAPI(ROOT_DIR)
    html_file = os.path.join(UI_DIR, "index.html")
    cx, cy = get_screen_center(WINDOW_WIDTH, WINDOW_HEIGHT)

    window = webview.create_window(
        title="SIR ModPack Installer Pro v1.0.0 — Modern Deployment Engine",
        url=html_file,
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        x=cx,
        y=cy,
        resizable=True,
        min_size=(900, 600),
        background_color="#06090e",
        easy_drag=False
    )

    def on_closing():
        if api.is_installing:
            # Checkpoint journal is already atomic on disk
            api.write_journal(
                stage="Interrupted by User Exit",
                stage_num=4,
                progress=api.install_progress,
                status="in_progress",
                config={},
                dest_dir=api.installed_path
            )

    window.events.closing += on_closing

    webview.start(
        func=on_window_ready,
        debug=False,
        http_server=False,
        gui='edgechromium'
    )

if __name__ == "__main__":
    main()
