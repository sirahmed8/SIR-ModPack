"""
server_tray_service.py — Native Windows System Tray Engine & Autostart Manager for SIR Server Manager.

Features:
- Pystray notification area icon using SIR_Icon.ico.
- Context menu: Open Server Manager, Start/Stop Server, Server Settings, Web Guide, Exit Orchestrator.
- Default action (double click) restores and brings window to foreground using Win32 API.
- Safe detached thread execution with clean shutdown and process reaping.
- Ghost window suppression preventing dummy tray taskbar items without affecting EdgeChromium.
"""

from __future__ import annotations

import os
import sys
import threading
from typing import Any, Callable, Optional


def is_server_autostart_enabled() -> bool:
    """Checks whether SIR Server Manager is registered in Windows HKCU Startup Run key."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "SIR Server Manager"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, app_name)
            return True
    except Exception:
        return False


def set_server_autostart(enabled: bool, exe_path: Optional[str] = None) -> bool:
    """Enables or disables SIR Server Manager auto-start on Windows boot with --minimized flag."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "SIR Server Manager"

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                if not exe_path:
                    if getattr(sys, "frozen", False):
                        exe_path = sys.executable
                    else:
                        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                        cand = os.path.join(root, "SIR Server Manager.exe")
                        if os.path.isfile(cand):
                            exe_path = cand
                        else:
                            cand2 = os.path.join(root, "dist_apps", "SIR Server Manager.exe")
                            exe_path = cand2 if os.path.isfile(cand2) else sys.executable

                cmd_value = f'"{exe_path}" --minimized'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd_value)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
        return True
    except Exception as ex:
        print(f"[ServerTrayService] Failed to set autostart: {ex}", file=sys.stderr)
        return False


class ServerTrayService:
    """Manages the Windows System Tray icon, background event loop, and context menu for Server Manager."""

    _instance: Optional["ServerTrayService"] = None

    def __init__(
        self,
        icon_path: str,
        window: Any = None,
        bridge_api: Any = None,
        on_exit_callback: Optional[Callable[[], None]] = None,
    ):
        self.icon_path = os.path.abspath(icon_path)
        self.window = window
        self.bridge_api = bridge_api
        self.on_exit_callback = on_exit_callback
        self.icon: Any = None
        self._lock = threading.Lock()
        self._is_running = False
        ServerTrayService._instance = self

    @classmethod
    def get_instance(cls) -> Optional["ServerTrayService"]:
        return cls._instance

    @property
    def is_running(self) -> bool:
        return bool(self._is_running and self.icon)

    def set_window(self, window: Any) -> None:
        self.window = window

    def set_bridge_api(self, bridge_api: Any) -> None:
        self.bridge_api = bridge_api

    @staticmethod
    def _suppress_dummy_tray_windows() -> None:
        """Suppresses ghost/dummy pystray message windows from the Windows taskbar without touching WebView2."""
        if sys.platform != "win32":
            return
        try:
            import ctypes
            user32 = ctypes.windll.user32
            pid = os.getpid()

            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            GW_OWNER = 4

            @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            def _enum_cb(hwnd, _):
                owner = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                if owner.value == pid:
                    buf_cls = ctypes.create_unicode_buffer(512)
                    user32.GetClassNameW(hwnd, buf_cls, 512)
                    class_name = buf_cls.value.lower()

                    # Strict exclusion: NEVER touch EdgeChromium, WebView2, or WinUI HWNDs
                    forbidden_substrings = ("chrome", "webview", "edge", "intermediate d3d", "hwndhost")
                    if any(sub in class_name for sub in forbidden_substrings):
                        return True

                    # Strict exclusion: Do not touch child or owned windows of server manager
                    if user32.GetParent(hwnd) != 0 or user32.GetWindow(hwnd, GW_OWNER) != 0:
                        return True

                    buf = ctypes.create_unicode_buffer(512)
                    user32.GetWindowTextW(hwnd, buf, 512)
                    win_text = buf.value

                    # Main window title
                    if "SIR Server Orchestrator Pro" in win_text:
                        return True

                    # Suppress ONLY dummy windows created specifically by pystray
                    is_pystray_dummy = "pystray" in class_name.lower() or "pystray" in win_text.lower()
                    if is_pystray_dummy:
                        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                        new_style = (ex_style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
                        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                        user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)  # SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
                        user32.ShowWindow(hwnd, 0)  # SW_HIDE
                return True

            user32.EnumWindows(_enum_cb, None)
        except Exception:
            pass

    def restore_and_focus_window(self, maximize: bool = False) -> None:
        """Unhides, restores, and brings the server manager window to the absolute foreground."""
        if not self.window:
            return

        try:
            self.window.show()
            self.window.restore()
            if maximize:
                self.window.maximize()
        except Exception:
            pass

        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                pid = os.getpid()
                found = {"hwnd": 0}

                @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                def _enum_cb(hwnd, _):
                    owner = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                    if owner.value == pid and user32.GetWindow(hwnd, 4) == 0:
                        found["hwnd"] = hwnd
                        return False
                    return True

                user32.EnumWindows(_enum_cb, None)
                hwnd = found["hwnd"]
                if hwnd:
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    if maximize:
                        user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
                    user32.SetForegroundWindow(hwnd)
            except Exception:
                pass

    def start(self) -> bool:
        """Starts the Pystray icon in a detached background thread."""
        with self._lock:
            if self._is_running and self.icon:
                return True

            try:
                import pystray
                from PIL import Image

                if not os.path.isfile(self.icon_path):
                    image = Image.new("RGBA", (64, 64), color=(6, 182, 212, 255))
                else:
                    image = Image.open(self.icon_path)

                def _on_open(icon, item):
                    self.restore_and_focus_window()

                def _is_server_running() -> bool:
                    if self.bridge_api:
                        return bool(getattr(self.bridge_api, "is_running", False))
                    return False

                def _server_toggle_text(item) -> str:
                    return self.get_server_toggle_text()

                def _on_toggle_server(icon, item):
                    if not self.bridge_api:
                        return
                    if _is_server_running():
                        def _do_stop():
                            try:
                                self.bridge_api.stop_server()
                            finally:
                                self.update_menu()
                        threading.Thread(target=_do_stop, daemon=True).start()
                    else:
                        def _do_start():
                            try:
                                self.bridge_api.start_server()
                            finally:
                                self.update_menu()
                        threading.Thread(target=_do_start, daemon=True).start()
                    threading.Timer(1.0, self.update_menu).start()

                def _on_settings(icon, item):
                    self.restore_and_focus_window()
                    if self.window:
                        try:
                            self.window.evaluate_js("openServerSettingsModal();")
                        except Exception:
                            pass

                def _on_web_guide(icon, item):
                    if self.bridge_api and hasattr(self.bridge_api, "open_server_guide_site"):
                        try:
                            self.bridge_api.open_server_guide_site()
                        except Exception:
                            pass

                def _on_exit(icon, item):
                    self.stop()
                    if self.on_exit_callback:
                        try:
                            self.on_exit_callback()
                        except Exception:
                            pass
                    if self.bridge_api:
                        try:
                            if getattr(self.bridge_api, "is_running", False):
                                self.bridge_api.stop_server()
                        except Exception:
                            pass
                        try:
                            if getattr(self.bridge_api, "is_tunnel_running", False):
                                self.bridge_api.stop_playit_tunnel()
                        except Exception:
                            pass
                    if self.window:
                        try:
                            self.window.destroy()
                        except Exception:
                            pass
                    try:
                        os._exit(0)
                    except Exception:
                        sys.exit(0)

                if sys.platform == "win32":
                    try:
                        import ctypes
                        uxtheme = ctypes.windll.uxtheme
                        try:
                            SetPreferredAppMode = uxtheme[135]
                            SetPreferredAppMode.argtypes = [ctypes.c_int]
                            SetPreferredAppMode.restype = ctypes.c_int
                            SetPreferredAppMode(2)  # ForceDark
                        except Exception:
                            try:
                                AllowDarkModeForApp = uxtheme[133]
                                AllowDarkModeForApp.argtypes = [ctypes.c_bool]
                                AllowDarkModeForApp.restype = ctypes.c_bool
                                AllowDarkModeForApp(True)
                            except Exception:
                                pass
                        try:
                            FlushMenuThemes = uxtheme[136]
                            FlushMenuThemes.restype = None
                            FlushMenuThemes()
                        except Exception:
                            pass
                    except Exception:
                        pass

                menu = pystray.Menu(
                    pystray.MenuItem("✦ Open Server Manager", _on_open, default=True),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(_server_toggle_text, _on_toggle_server),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("⚙ Server Settings", _on_settings),
                    pystray.MenuItem("🌐 Open Web Guide", _on_web_guide),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("✕ Exit Orchestrator", _on_exit),
                )

                self.icon = pystray.Icon(
                    "SIR Server Manager",
                    image,
                    "SIR Server Orchestrator Pro v1.0.0",
                    menu=menu,
                )
                self.icon.run_detached()
                self._is_running = True
                threading.Timer(0.5, self._suppress_dummy_tray_windows).start()
                return True
            except Exception as e:
                print(f"[ServerTrayService] Unable to initialize system tray: {e}", file=sys.stderr)
                return False

    def notify(self, title: str, message: str) -> None:
        """Sends a desktop notification bubble via system tray icon."""
        if self.icon and hasattr(self.icon, "notify"):
            try:
                self.icon.notify(message, title)
            except Exception:
                pass

    def get_server_toggle_text(self) -> str:
        """Returns the current contextual toggle text based on server running status."""
        is_running = False
        if self.bridge_api:
            is_running = bool(getattr(self.bridge_api, "is_running", False))
        return "⏹ Stop Server" if is_running else "▶ Start Server"

    def update_menu(self) -> None:
        """Forces the pystray context menu to re-evaluate dynamic menu items."""
        with self._lock:
            if self.icon and hasattr(self.icon, "update_menu"):
                try:
                    self.icon.update_menu()
                except Exception:
                    pass

    def stop(self) -> None:
        """Stops the system tray icon cleanly."""
        with self._lock:
            if self.icon:
                try:
                    self.icon.stop()
                except Exception:
                    pass
                self.icon = None
            self._is_running = False
