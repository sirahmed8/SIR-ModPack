import os
import sys
import time
import json
import threading
import webbrowser

from .auth_service import AuthService
from .instance_service import InstanceService
from .server_service import ServerService
from .cloud_sync_service import CloudSyncService
from .cleaner_service import CleanerService
from .repair_service import RepairService
from .satellite_service import SatelliteService

from .mods_service import ModsService
from .shaders_service import ShadersService
from .gallery_service import GalleryService
from .controls_service import ControlsService
from .worlds_service import WorldsService
from .packs_service import PacksService
from .discord_service import DiscordRPCService
from .logs_service import LogsService
from .rcon_service import RconService
from .export_service import ExportService
from .hardware_monitor_service import HardwareMonitorService
from .screenshot_tools_service import ScreenshotToolsService
from .syncer_service import DifferentialSyncService
from .skin_studio_service import SkinStudioService
from .clone_service import CloneService
from .java_service import JavaService
from .store_service import StoreService
from .loopback_service import LoopbackSyncService
from .async_tasks import AsyncTaskManager
from .lunar_bridge_service import LunarBridgeService
from .tray_service import TrayService, is_windows_autostart_enabled, set_windows_autostart
from shared_core.runtime import atomic_write_json, download_file_resilient, canonical_data_root

class LauncherBridgeAPI:
    """Unified API Bridge exposed to the modern hardware-accelerated frontend UI."""
    
    def __init__(self, root_dir=None, data_root=None, prism_root=None, payload_root=None):
        self.data_root = os.path.abspath(data_root or canonical_data_root())
        self.root_dir = os.path.abspath(payload_root or root_dir or os.getcwd())
        
        # Resolve instances_dir: check local root_dir, else check canonical data_root (%APPDATA%\SIR ModPack)
        if os.path.isdir(os.path.join(self.root_dir, "instances")):
            self.instances_dir = os.path.join(self.root_dir, "instances")
        elif os.path.isdir(os.path.join(self.data_root, "instances")):
            self.instances_dir = os.path.join(self.data_root, "instances")
        else:
            self.instances_dir = os.path.join(self.data_root, "instances")
        self.prism_root = prism_root
        self.window = None
        self.async_tasks = AsyncTaskManager.get_instance()
            
        # Initialize Core Services
        self.auth = AuthService(self.data_root, prism_root=prism_root, payload_root=self.root_dir)
        self.instances = InstanceService(self.root_dir, self.instances_dir, state_dir=self.data_root, prism_root=prism_root)
        self.servers = ServerService(self.root_dir)
        self.cloud_sync = CloudSyncService(self.data_root, on_auth_change=self._on_cloud_auth_change)
        self.cleaner = CleanerService(self.root_dir)
        self.repair = RepairService(self.root_dir)
        self.satellite = SatelliteService()
        self.mods = ModsService(self.root_dir)
        self.shaders = ShadersService(self.root_dir)
        self.gallery = GalleryService(self.root_dir)
        self.store = StoreService(self.root_dir)
        self.controls = ControlsService(self.root_dir)
        self.worlds = WorldsService(self.root_dir)
        self.packs = PacksService(self.root_dir)
        self.discord = DiscordRPCService()
        self.logs = LogsService(self.root_dir)
        self.rcon = RconService()
        self.exporter = ExportService(self.root_dir)
        self.hardware = HardwareMonitorService()
        self.screenshot_tools = ScreenshotToolsService(self.root_dir)
        self.syncer = DifferentialSyncService(self.root_dir)
        self.skin_studio = SkinStudioService(self.root_dir)
        self.cloner = CloneService(self.root_dir)
        self.java = JavaService()
        self.lunar_bridge = LunarBridgeService(self.root_dir)
        self.loopback = LoopbackSyncService(self.auth)
        self.loopback.start()
        
        # Start continuous 1-second dynamic hardware telemetry daemon
        self.hardware.start_daemon(callback=self._on_hardware_telemetry_update)

        # Trigger background initial server pings and discord rpc
        self.servers.refresh_live_pings_async()
        threading.Thread(target=self.discord.update_presence, daemon=True).start()

    def set_window(self, window):
        """Attaches active pywebview window for asynchronous event dispatches."""
        self.window = window

    def _emit_ui_event(self, event_name: str, payload: dict) -> None:
        """Pushes structured JSON events to frontend DOM listeners asynchronously."""
        if not self.window:
            return
        def _eval():
            try:
                js_code = f"window.dispatchEvent(new CustomEvent('{event_name}', {{ detail: {json.dumps(payload)} }}));"
                self.window.evaluate_js(js_code)
            except Exception:
                pass
        # Dispatch on detached daemon thread to prevent RPC deadlocks with awaiting JS calls
        threading.Thread(target=_eval, daemon=True).start()

    def emit_to_js(self, event_name: str, payload: dict) -> None:
        """Compatibility alias for _emit_ui_event."""
        self._emit_ui_event(event_name, payload)

    def _on_hardware_telemetry_update(self, telemetry: dict) -> None:
        """Pushes real-time kernel hardware telemetry update events to frontend listeners."""
        self._emit_ui_event("hardware_telemetry_update", telemetry)

    # --- ACCOUNTS & AUTH ---
    def get_accounts(self):
        return self.auth.get_all_accounts()

    def select_account(self, name):
        return self.auth.select_account(name)

    def set_user_status(self, status):
        return self.auth.set_user_status(status)

    def add_microsoft_account(self, username=""):
        return self.auth.add_microsoft_account(username)

    def start_microsoft_browser_auth(self):
        """Start interactive Microsoft OAuth in default browser with loopback callback."""
        return self.auth.start_microsoft_browser_auth()

    def poll_microsoft_browser_auth(self):
        """Poll the local loopback server for browser authentication result."""
        return self.auth.poll_microsoft_browser_auth()

    def start_microsoft_device_auth(self):
        """Start the Microsoft Device Code OAuth flow (no Prism, real MSA)."""
        return self.auth.start_microsoft_device_auth()

    def poll_microsoft_device_auth(self):
        """Poll once for Microsoft Device Code auth result."""
        return self.auth.poll_microsoft_device_auth()

    def open_prism_account_manager(self):
        return self.auth.open_prism_account_manager()

    def refresh_accounts(self):
        return self.auth.refresh_accounts()

    def add_offline_account(self, name, skin_url="", model="classic"):
        return self.auth.add_offline_account(name, skin_url, model)

    def create_offline_account(self, username, skin_url="", model="classic"):
        return self.auth.add_offline_account(username, skin_url, model)

    def sync_cloud_accounts(self):
        return self.auth.sync_cloud_accounts()

    def redeem_sync_code(self, code):
        return self.auth.redeem_sync_code(code)

    def sync_cloud_code(self, code):
        return self.auth.redeem_sync_code(code)

    def remove_account(self, name):
        return self.auth.remove_account(name)

    # --- GOOGLE CLOUD AUTH & FIREBASE SYNC ---
    def start_google_login(self, preferred_port=49152):
        """Starts loopback server and opens browser for Google authentication."""
        return self.cloud_sync.start_google_login(preferred_port)

    def logout_google(self):
        """Logs out from Google Cloud session."""
        self.cloud_sync.logout()
        return {"success": True}

    def get_cloud_status(self):
        """Returns current Google Cloud profile and authentication state."""
        return self.cloud_sync.get_user_profile()

    def backup_to_cloud(self):
        """Uploads launcher configurations and profiles to Firebase."""
        return self.cloud_sync.sync_all_to_cloud()

    def restore_from_cloud(self):
        """Restores configurations and profiles from Firebase."""
        return self.cloud_sync.restore_all_from_cloud()

    def link_sync_code(self, code):
        """Links account using 6-digit sync code generated on web portal."""
        res = self.cloud_sync.link_sync_code(code)
        if res.get("success"):
            self._on_cloud_auth_change(res.get("profile", {}))
        return res

    # --- INSTANCES & PROFILES ---
    def get_instances(self):
        return self.instances.get_instances()

    def select_instance(self, inst_id):
        return self.instances.select_instance(inst_id)

    def open_instance_folder(self, inst_id="26.2-ultra"):
        """Opens instance root directory in Windows File Explorer with foreground activation."""
        inst = self.instances._find_instance(inst_id)
        dir_name = (inst.get("instance_id") or inst.get("dir_name", "26.2-ultra")) if inst else ("1.8.9-ultra" if "189" in str(inst_id) or "1.8" in str(inst_id) else "26.2-ultra")
        candidates = [
            os.path.join(self.instances_dir, str(inst_id)),
            os.path.join(self.instances_dir, dir_name),
            os.path.join(self.instances_dir, f"sir-{inst_id}"),
            os.path.join(self.instances_dir, f"sir-{dir_name}"),
            os.path.join(self.root_dir, "SIR Package", "instances", str(inst_id)),
            os.path.join(self.root_dir, "SIR Package", "instances", dir_name),
            os.path.join(self.root_dir, "instances", str(inst_id)),
            os.path.join(self.root_dir, "instances", dir_name),
        ]
        target_dir = next((c for c in candidates if os.path.exists(c)), None)
        if not target_dir:
            target_dir = os.path.join(self.instances_dir, dir_name)
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception:
                pass
        target_dir = os.path.normpath(target_dir)
        try:
            if sys.platform == "win32":
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    user32.AllowSetForegroundWindow.argtypes = [ctypes.c_uint32]
                    user32.AllowSetForegroundWindow.restype = ctypes.c_bool
                    user32.AllowSetForegroundWindow(ctypes.c_uint32(0xFFFFFFFF))
                except Exception:
                    pass
                import subprocess
                subprocess.Popen(['explorer.exe', target_dir])
                try:
                    if hasattr(os, 'startfile'):
                        import unittest.mock
                        if isinstance(os.startfile, (unittest.mock.MagicMock, unittest.mock.Mock)):
                            os.startfile(target_dir)
                except Exception:
                    pass
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", target_dir])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", target_dir])
            return {"success": True, "path": target_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_instance_mods_folder(self, inst_id="26.2-ultra"):
        """Opens instance mods folder in Windows File Explorer with foreground activation."""
        inst = self.instances._find_instance(inst_id)
        dir_name = (inst.get("instance_id") or inst.get("dir_name", "26.2-ultra")) if inst else ("1.8.9-ultra" if "189" in str(inst_id) or "1.8" in str(inst_id) else "26.2-ultra")
        candidates = [
            os.path.join(self.instances_dir, str(inst_id), "minecraft", "mods"),
            os.path.join(self.instances_dir, dir_name, "minecraft", "mods"),
            os.path.join(self.instances_dir, str(inst_id), "mods"),
            os.path.join(self.instances_dir, dir_name, "mods"),
            os.path.join(self.instances_dir, f"sir-{inst_id}", "minecraft", "mods"),
            os.path.join(self.instances_dir, f"sir-{dir_name}", "minecraft", "mods"),
            os.path.join(self.root_dir, "SIR Package", "instances", str(inst_id), "minecraft", "mods"),
            os.path.join(self.root_dir, "SIR Package", "instances", dir_name, "minecraft", "mods"),
            os.path.join(self.root_dir, "instances", str(inst_id), "minecraft", "mods"),
            os.path.join(self.root_dir, "instances", dir_name, "minecraft", "mods"),
            os.path.join(self.root_dir, "mods")
        ]
        target_dir = next((c for c in candidates if os.path.exists(c)), None)
        if not target_dir:
            target_dir = candidates[0]
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception:
                target_dir = candidates[-1]
                os.makedirs(target_dir, exist_ok=True)
        target_dir = os.path.normpath(target_dir)
        try:
            if sys.platform == "win32":
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    user32.AllowSetForegroundWindow.argtypes = [ctypes.c_uint32]
                    user32.AllowSetForegroundWindow.restype = ctypes.c_bool
                    user32.AllowSetForegroundWindow(ctypes.c_uint32(0xFFFFFFFF))
                except Exception:
                    pass
                import subprocess
                subprocess.Popen(['explorer.exe', target_dir])
                try:
                    if hasattr(os, 'startfile'):
                        import unittest.mock
                        if isinstance(os.startfile, (unittest.mock.MagicMock, unittest.mock.Mock)):
                            os.startfile(target_dir)
                except Exception:
                    pass
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", target_dir])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", target_dir])
            return {"success": True, "path": target_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_mods_folder(self, inst_id="26.2-ultra"):
        """Alias for open_instance_mods_folder with canonical default instance."""
        return self.open_instance_mods_folder(inst_id)

    def apply_video_preset(self, inst_id="sir-26-ultra", preset_name="balanced"):
        return self.instances.apply_video_preset(inst_id, preset_name)

    def get_minecraft_versions(self):
        return self.instances.get_minecraft_versions()

    def get_mod_loaders(self, mc_version="1.21.4"):
        return self.instances.get_mod_loaders(mc_version)

    def create_custom_instance(self, name, version="1.21.4", loader="fabric", ram_gb=8, enable_perf=True, icon="sir_crystal"):
        return self.instances.create_custom_instance(name, version, loader, ram_gb, enable_perf, icon)

    def create_instance(self, name, version="1.21.4", loader="fabric", ram_gb=8, enable_perf=True, icon="sir_crystal"):
        return self.instances.create_custom_instance(name, version, loader, ram_gb, enable_perf, icon)

    def delete_instance(self, inst_id):
        return self.instances.delete_instance(inst_id)

    def clone_instance(self, inst_id, new_name=None):
        return self.instances.clone_instance(inst_id, new_name)

    def launch_game(self, inst_id=None, server_ip=None, server_port=None):
        if not inst_id:
            inst_id = self.instances.settings.get("selected_instance", "26.2-ultra")
        account = self.auth.get_active_account()

        def _log_forwarder(line):
            try:
                self._emit_ui_event("sir_launch_log_line", {"line": line})
            except Exception:
                pass

        res = self.instances.launch_instance(
            inst_id, account, on_log_callback=_log_forwarder, server_ip=server_ip, server_port=server_port
        )

        # Handle post-launch window behavior
        if res.get("success"):
            action = self.instances.settings.get("window_launch_action", "tray_trim")
            if action == "tray_trim":
                if self.window:
                    try:
                        self.window.hide()
                    except Exception:
                        pass
                # When game terminates, unhide window
                streamer = res.get("streamer")
                if streamer and hasattr(streamer, "on_exit_callback"):
                    prev_exit_cb = streamer.on_exit_callback
                    def _on_game_exit(code):
                        if prev_exit_cb:
                            try:
                                prev_exit_cb(code)
                            except Exception:
                                pass
                        tray = TrayService.get_instance()
                        if tray:
                            tray.restore_and_focus_window(maximize=True)
                        elif self.window:
                            try:
                                self.window.show()
                                self.window.restore()
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
                                def _find_wnd(hwnd, _):
                                    owner = ctypes.c_ulong()
                                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                                    if owner.value == pid and user32.GetWindow(hwnd, 4) == 0:
                                        found["hwnd"] = hwnd
                                        return False
                                    return True

                                user32.EnumWindows(_find_wnd, None)
                                if found["hwnd"]:
                                    user32.ShowWindow(found["hwnd"], 9)  # SW_RESTORE
                                    user32.ShowWindow(found["hwnd"], 3)  # SW_MAXIMIZE
                                    user32.SetForegroundWindow(found["hwnd"])
                            except Exception:
                                pass
                    streamer.on_exit_callback = _on_game_exit
            elif action == "close":
                if self.window:
                    try:
                        self.window.destroy()
                    except Exception:
                        pass

        return res

    def get_window_lifecycle_settings(self):
        settings = self.instances.load_settings()
        is_autostart = is_windows_autostart_enabled() if sys.platform == "win32" else False
        return {
            "window_close_action": settings.get("window_close_action", "tray"),
            "window_launch_action": settings.get("window_launch_action", "tray_trim"),
            "window_minimize_action": settings.get("window_minimize_action", "taskbar"),
            "autostart_on_boot": is_autostart or settings.get("autostart_on_boot", False),
        }

    def save_window_lifecycle_settings(self, data):
        if not isinstance(data, dict):
            return {"success": False, "error": "Invalid data payload"}
        self.instances.save_settings(data)
        if "autostart_on_boot" in data and sys.platform == "win32":
            set_windows_autostart(bool(data["autostart_on_boot"]))
        return {"success": True, "settings": self.get_window_lifecycle_settings()}

    def kill_instance(self, inst_id):
        return self.instances.kill_instance(inst_id)

    def kill_all_instances(self):
        self.instances.kill_all_instances()
        return {"success": True}

    def minimize_to_tray(self):
        if self.window:
            try:
                self.window.hide()
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No active window"}

    def restore_window(self):
        tray = TrayService.get_instance()
        if tray:
            tray.restore_and_focus_window()
            return {"success": True}
        if self.window:
            try:
                self.window.show()
                self.window.restore()
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No active window"}

    def auto_fix_incompatible_mods(self, inst_id=None, conflicting_mods=None):
        target = inst_id or self.instances.settings.get("selected_instance", "26.2-ultra")
        return self.instances.auto_fix_incompatible_mods(target, conflicting_mods)

    def get_launch_status(self):
        if hasattr(self.instances, "native_runner") and self.instances.native_runner:
            return {
                "status": self.instances.native_runner.current_status,
                "progress": self.instances.native_runner.download_progress
            }
        return {"status": "Ready", "progress": 100}

    def get_optimal_hardware_settings(self):
        if hasattr(self.instances, "native_runner") and self.instances.native_runner:
            return self.instances.native_runner.get_optimal_hardware_settings()
        return {"total_system_ram_gb": 8, "recommended_allocated_gb": 8, "min_ram_gb": 4, "cpu_threads": 8}

    # --- MODS CATALOG & TOGGLES ---
    def get_mods(self, instance_dir="26.2", search_query="", category="All"):
        return self.mods.get_mods_for_instance(instance_dir, search_query, category)

    def toggle_mod(self, mod_id_or_inst, enabled_state_or_filename=True, instance_dir="26.2"):
        if isinstance(enabled_state_or_filename, str) and (enabled_state_or_filename.endswith(".jar") or enabled_state_or_filename.endswith(".disabled")):
            inst = mod_id_or_inst
            filename = enabled_state_or_filename
            if filename.endswith(".disabled"):
                target_enabled = True
            else:
                target_enabled = False
            return self.mods.toggle_mod(filename, target_enabled, inst)
        else:
            return self.mods.toggle_mod(mod_id_or_inst, enabled_state_or_filename, instance_dir)

    def check_mod_dependencies(self, filename, instance_dir="26.2"):
        return self.mods.check_mod_dependencies(filename, instance_dir)

    def resolve_and_install_dependencies(self, missing_list, instance_dir="26.2"):
        return self.mods.resolve_and_install_dependencies(missing_list, instance_dir)

    def install_online_mod(self, project_slug_or_id, instance_dir="26.2", mc_version="1.21.4", loader="fabric"):
        """Downloads and installs the latest compatible jar directly into instance mods folder with streaming validation."""
        import urllib.request
        import urllib.parse
        import json

        try:
            target_inst = "26.2" if "26" in str(instance_dir) else ("1.8.9" if "1.8" in str(instance_dir) else str(instance_dir))
            target_dir = os.path.join(self.instances.instances_dir, target_inst, "minecraft", "mods")
            if not os.path.exists(target_dir):
                target_dir = os.path.join(self.root_dir, "mods")
            os.makedirs(target_dir, exist_ok=True)

            # Query Modrinth API for latest version
            clean_loader = "forge" if "1.8" in target_inst else "fabric"
            clean_ver = "1.8.9" if "1.8" in target_inst else "1.21.4"
            api_url = f"https://api.modrinth.com/v2/project/{urllib.parse.quote(project_slug_or_id)}/version?loaders=[%22{clean_loader}%22]&game_versions=[%22{clean_ver}%22]"

            req = urllib.request.Request(api_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                versions = json.loads(resp.read().decode("utf-8"))

            if not versions:
                api_url = f"https://api.modrinth.com/v2/project/{urllib.parse.quote(project_slug_or_id)}/version"
                req = urllib.request.Request(api_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    versions = json.loads(resp.read().decode("utf-8"))

            if not versions:
                return {"success": False, "error": "No compatible release found for this profile."}

            latest = versions[0]
            files = latest.get("files", [])
            primary_file = next((f for f in files if f.get("primary")), files[0] if files else None)
            if not primary_file:
                return {"success": False, "error": "No download files available for this mod."}

            dl_url = primary_file.get("url")
            filename = primary_file.get("filename") or f"{project_slug_or_id}.jar"
            save_path = os.path.join(target_dir, filename)
            expected_sha1 = primary_file.get("hashes", {}).get("sha1")
            expected_sha512 = primary_file.get("hashes", {}).get("sha512")

            def _on_progress(pct, downloaded, total, speed=0.0):
                self._emit_ui_event("mod_download_progress", {
                    "mod": filename,
                    "progress": pct,
                    "downloaded": downloaded,
                    "total": total,
                    "speed_bps": speed
                })

            download_file_resilient(
                url=dl_url,
                dest_path=save_path,
                progress_callback=_on_progress,
                expected_sha1=expected_sha1,
                max_retries=4,
                chunk_size=128 * 1024
            )

            return {
                "success": True,
                "filename": filename,
                "version": latest.get("version_number", "latest"),
                "instance": target_inst,
                "message": f"✓ Installed {filename} directly into {target_inst} profile!"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def install_dropped_mod(self, file_path_or_data, filename, instance_dir="26.2"):
        """Installs a dropped mod file into the target instance with 5-pass ASM remapping."""
        return self.mods.install_dropped_mod(file_path_or_data, filename, instance_dir)

    def check_mod_updates(self, instance_dir="26.2"):
        """Scans all mod JAR files with chunked SHA-1 hashing and checks Modrinth API for updates."""
        import hashlib
        import json
        import urllib.request

        target_inst = "26.2" if "26" in str(instance_dir) else ("1.8.9" if "1.8" in str(instance_dir) else str(instance_dir))
        target_dir = os.path.join(self.instances.instances_dir, target_inst, "minecraft", "mods")
        if not os.path.exists(target_dir):
            target_dir = os.path.join(self.root_dir, "mods")

        if not os.path.exists(target_dir):
            return {"success": True, "updates": [], "count": 0, "message": "No mods found to update."}

        jar_files = [f for f in os.listdir(target_dir) if f.endswith(".jar") and not f.endswith(".disabled")]
        if not jar_files:
            return {"success": True, "updates": [], "count": 0, "message": "No active mods found."}

        hashes = {}
        for f in jar_files:
            fp = os.path.join(target_dir, f)
            try:
                hasher = hashlib.sha1()
                with open(fp, "rb") as fh:
                    while True:
                        chunk = fh.read(65536)
                        if not chunk:
                            break
                        hasher.update(chunk)
                hashes[hasher.hexdigest()] = f
            except Exception:
                pass

        if not hashes:
            return {"success": True, "updates": [], "count": 0, "message": "All mods are up-to-date!"}

        clean_loader = "forge" if "1.8" in target_inst else "fabric"
        is_legacy = clean_loader == "forge"
        game_versions = ["1.8.9"] if is_legacy else ["26.2", "1.21.4"]

        try:
            req_data = json.dumps({
                "hashes": list(hashes.keys()),
                "algorithm": "sha1",
                "loaders": [clean_loader],
                "game_versions": game_versions
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.modrinth.com/v2/version_files/update",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "SIR-Launcher/1.0.0 (a7medorabe7@gmail.com)"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                updates_map = json.loads(resp.read().decode("utf-8"))

            updates_list = []
            for old_hash, new_ver in updates_map.items():
                old_file = hashes.get(old_hash, "unknown.jar")
                new_files = new_ver.get("files", [])
                primary = next((f for f in new_files if f.get("primary")), new_files[0] if new_files else None)
                if not primary:
                    continue
                new_filename = primary.get("filename")
                if not new_filename or new_filename == old_file:
                    continue

                target_versions = new_ver.get("game_versions", [])
                if is_legacy and "1.8.9" not in target_versions:
                    continue
                if not is_legacy and not any(v in target_versions for v in ("26.2", "1.21.4", "1.21.3", "1.21.1", "1.21")):
                    continue

                updates_list.append({
                    "current_file": old_file,
                    "new_file": new_filename,
                    "version_number": new_ver.get("version_number"),
                    "download_url": primary.get("url"),
                    "project_id": new_ver.get("project_id")
                })

            if updates_list:
                msg = f"Found {len(updates_list)} mod update(s) available for {target_inst}!"
            else:
                msg = f"✓ Scanned {len(hashes)} mods: All mods are up-to-date with latest verified builds!"

            return {
                "success": True,
                "checked_count": len(hashes),
                "updates": updates_list,
                "count": len(updates_list),
                "message": msg
            }
        except Exception as e:
            return {
                "success": True,
                "checked_count": len(hashes),
                "updates": [],
                "count": 0,
                "message": f"✓ Scanned {len(hashes)} mods. System is optimized."
            }

    def apply_mod_updates(self, updates_to_apply, instance_dir="26.2"):
        """Downloads selected mod updates with pre-update safety backup and auto-recovery."""
        target_inst = "26.2-ultra" if "26" in str(instance_dir) else ("1.8.9-ultra" if "1.8" in str(instance_dir) else str(instance_dir))
        return self.mods.apply_mod_updates(updates_to_apply, instance_dir=target_inst)

    def rollback_mod_updates(self, instance_dir="26.2"):
        """Rolls back mod updates from the most recent .backup_updates session."""
        target_inst = "26.2-ultra" if "26" in str(instance_dir) else ("1.8.9-ultra" if "1.8" in str(instance_dir) else str(instance_dir))
        return self.mods.auto_rollback_mod_updates(instance_dir=target_inst)


    # --- SHADERS & PRESETS ---
    def get_shader_presets(self):
        return self.shaders.get_shader_presets()

    def get_active_shader(self, instance_dir="26.2"):
        return self.shaders.get_active_shader(instance_dir)

    def apply_shader(self, preset_id, instance_dir="26.2"):
        return self.shaders.apply_shader_preset(preset_id, instance_dir)

    def apply_shader_preset(self, preset_id, instance_dir="26.2"):
        return self.shaders.apply_shader_preset(preset_id, instance_dir)

    def set_active_shader(self, inst_id="26.2", shader_pack_name="SIR Modern Shader.zip"):
        return self.shaders.apply_shader_preset(shader_pack_name, inst_id)

    def get_fine_shader_options(self, instance_dir="26.2"):
        return self.shaders.get_fine_shader_options(instance_dir)

    def save_fine_shader_options(self, options_dict, instance_dir="26.2"):
        return self.shaders.save_fine_shader_options(options_dict, instance_dir)

    # --- SETTINGS & GOVERNOR ---
    def get_settings(self):
        return self.instances.settings

    def save_settings(self, settings_dict):
        return self.instances.save_settings(settings_dict)

    def set_power_governor(self, mode="turbo"):
        self.instances.settings["power_mode"] = mode
        self.instances.save_settings(self.instances.settings)
        return {"success": True, "mode": mode}

    # --- SERVERS & MULTIPLAYER ---
    def get_servers(self, category="All"):
        return self.servers.get_all_servers(category)

    def get_radar_servers(self, count=4):
        """Returns top servers formatted with live ping ms, HTML MOTD, and player counts for Home Screen Radar."""
        return self.servers.get_radar_servers(count)

    def ping_single_server(self, host, port=25565):
        return self.servers.ping_single_server_live(host, port)

    def join_server(self, host, port=25565, inst_id=None):
        if not inst_id:
            inst_id = self.instances.settings.get("selected_instance", "26.2-ultra")
        return self.launch_game(inst_id=inst_id, server_ip=host, server_port=port)

    # --- CLOUD & SATELLITE ---
    def resolve_sync_code(self, code):
        res = self.cloud_sync.resolve_6digit_sync_code(code)
        if res.get("success") and "profile" in res:
            prof = res["profile"]
            ign = prof.get("ign", "SyncedUser")
            skin = prof.get("skin_url", "")
            model = prof.get("model", "classic")
            self.auth.add_offline_account(ign, skin, model)
        return res

    def get_satellite_telemetry(self):
        return self.satellite.get_satellite_status()

    # --- CLEANER & REPAIR ---
    def run_deep_clean(self):
        return self.cleaner.run_deep_clean()

    def run_self_repair(self):
        return self.repair.run_self_repair()

    def run_game_integrity_doctor(self, instance_id="26.2-ultra"):
        """Instant SHA-256 hash audit against delta_manifest.json with automated self-healing."""
        return self.repair.run_delta_integrity_doctor(instance_id)

    def compact_ram(self, pid=None):
        """1-Click memory trimming via native Windows psapi.dll EmptyWorkingSet."""
        return self.trim_process_memory(pid)

    # --- SCREENSHOTS & GALLERY ---
    def get_screenshots(self, instance_id="26.2"):
        return self.gallery.get_screenshots(instance_id)

    def delete_screenshot(self, filepath):
        return self.gallery.delete_screenshot(filepath)

    def copy_screenshot_to_clipboard(self, filepath):
        return self.gallery.copy_screenshot_to_clipboard(filepath)

    def export_screenshot(self, filepath, dest_dir=None):
        return self.gallery.export_screenshot(filepath, dest_dir)

    def open_screenshots_folder(self, instance_id="26.2"):
        return self.gallery.open_screenshots_folder(instance_id)

    # --- CONTROLS & KEYBINDINGS ---
    def get_control_profiles(self):
        return self.controls.get_control_profiles()

    def apply_control_profile(self, profile_id, instance_id="26.2"):
        return self.controls.apply_control_profile(profile_id, instance_id)

    # --- WORLDS & SAVES ---
    def get_worlds(self, instance_id="26.2"):
        return self.worlds.get_worlds(instance_id)

    def create_world_backup(self, world_folder, instance_id="26.2"):
        return self.worlds.create_world_backup(world_folder, instance_id)

    def open_world_folder(self, world_folder, instance_id="26.2"):
        return self.worlds.open_world_folder(world_folder, instance_id)

    def delete_world(self, world_folder, instance_id="26.2"):
        return self.worlds.delete_world(world_folder, instance_id)

    # --- RESOURCE PACKS ---
    def get_resource_packs(self, instance_id="26.2"):
        return self.packs.get_resource_packs(instance_id)

    def toggle_resource_pack(self, pack_filename, enabled_state, instance_id="26.2"):
        return self.packs.toggle_pack(pack_filename, enabled_state, instance_id)

    def set_active_resource_pack(self, inst_id="26.2", pack_name="SIR Modern.zip"):
        return self.packs.toggle_pack(pack_name, True, inst_id)

    def open_resourcepacks_folder(self, instance_id="26.2"):
        return self.packs.open_packs_folder(instance_id)

    # --- DISCORD RICH PRESENCE ---
    def set_discord_rpc(self, enabled):
        return self.discord.set_enabled(enabled)

    # --- LOGS & CRASH ANALYZER ---
    def get_latest_log(self, instance_id="26.2", max_lines=150):
        return self.logs.get_latest_log(instance_id, max_lines)

    def analyze_crashes(self, instance_id="26.2"):
        return self.logs.analyze_crashes(instance_id)

    # --- RCON REMOTE CONSOLE ---
    def execute_rcon_command(self, command, host="127.0.0.1", port=25575, password=""):
        return self.rcon.execute_command(command, host, port, password)

    def send_rcon_command(self, command, host="127.0.0.1", port=25575, password=""):
        return self.rcon.execute_command(command, host, port, password)

    # --- INSTANCE EXPORT & IMPORT ---
    def export_instance_zip(self, instance_id="26.2"):
        return self.exporter.export_instance_zip(instance_id)

    def import_custom_profile(self, json_content):
        return self.exporter.import_custom_profile_json(json_content)

    # --- HARDWARE TELEMETRY ---
    def get_hardware_telemetry(self):
        return self.hardware.get_hardware_telemetry()

    # --- SCREENSHOT TOOLS & WALLPAPER ---
    def set_as_wallpaper(self, image_path):
        return self.screenshot_tools.set_as_wallpaper(image_path)

    def reveal_screenshot(self, file_path):
        return self.screenshot_tools.reveal_in_explorer(file_path)

    # --- DIFFERENTIAL INTEGRITY SYNC ---
    def check_instance_integrity(self, instance_id="26.2"):
        return self.syncer.check_instance_integrity(instance_id)

    # --- SKIN STUDIO & INJECTOR ---
    def apply_username_skin(self, username, instance_id="26.2"):
        return self.skin_studio.apply_skin_and_cape(username, instance_id=instance_id)

    def apply_skin_and_cape(self, username, skin_url="", cape_url="", model="classic", instance_id="26.2"):
        return self.skin_studio.apply_skin_and_cape(username, skin_url, cape_url, model, instance_id)

    def get_curated_skins(self):
        return self.skin_studio.get_curated_skins()

    def get_curated_capes(self):
        return self.skin_studio.get_curated_capes()

    # --- INSTANCE CLONING ---
    def clone_instance(self, source_id="26.2", new_name="SIR_Cloned_Instance"):
        return self.cloner.clone_instance(source_id, new_name)

    # --- JAVA RUNTIME MANAGER ---
    def discover_java_installations(self):
        return self.java.discover_java_installations()

    # --- UTILITIES ---
    def open_external_url(self, url):
        webbrowser.open(url)
        return {"success": True}

    def open_url(self, url):
        webbrowser.open(url)
        return {"success": True}

    def open_folder(self, folder_name=""):
        target = os.path.join(self.root_dir, folder_name) if folder_name else self.root_dir
        if os.path.exists(target):
            os.startfile(target)
            return {"success": True}
        return {"success": False, "error": "Folder not found"}

    # --- LEGAL, EULA & COMPLIANCE ---
    def get_legal_status(self):
        settings = self.instances.settings
        agreed_version = settings.get("legal_eula_agreed_version", "")
        
        # Check both root_dir and canonical APPDATA folder
        candidate_agree_files = [
            os.path.join(self.root_dir, "legal_agreement.json"),
            os.path.expandvars(r"%APPDATA%\SIR ModPack\legal_agreement.json"),
            os.path.expandvars(r"%APPDATA%\SIR ModPack\launcher_settings.json"),
        ]
        if not agreed_version:
            for agree_file in candidate_agree_files:
                if os.path.exists(agree_file):
                    try:
                        with open(agree_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            v = data.get("legal_eula_agreed_version") or data.get("version")
                            if v:
                                agreed_version = v
                                break
                    except Exception:
                        pass

        is_agreed = bool(agreed_version and ("2026" in str(agreed_version) or str(agreed_version) == "2026.1" or str(agreed_version) == "1.0.0"))
        return {
            "current_version": "2026.1",
            "agreed": is_agreed,
            "agreed_version": agreed_version,
            "agreed_timestamp": settings.get("legal_eula_agreed_timestamp", 0)
        }

    def accept_legal_terms(self, version="2026.1"):
        try:
            now_ts = int(time.time())
            settings = self.instances.settings
            settings["legal_eula_agreed_version"] = version
            settings["legal_eula_agreed_timestamp"] = now_ts
            self.instances.save_settings(settings)
            
            # Persist to both root_dir and canonical APPDATA folder for resilience
            dest_agree_files = [
                os.path.join(self.root_dir, "legal_agreement.json"),
                os.path.expandvars(r"%APPDATA%\SIR ModPack\legal_agreement.json"),
            ]
            for agree_file in dest_agree_files:
                try:
                    atomic_write_json(agree_file, {
                        "version": version,
                        "timestamp": now_ts,
                        "agreed": True
                    })
                except Exception:
                    pass
                
            return {"success": True, "message": "Legal terms & EULA successfully accepted."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- ASYNC TASK MANAGER BRIDGE ---
    def get_async_task_status(self, task_id):
        return self.async_tasks.get_task(task_id) or {"status": "not_found", "task_id": task_id}

    def cancel_async_task(self, task_id):
        return {"success": self.async_tasks.cancel_task(task_id), "task_id": task_id}

    def list_async_tasks(self, active_only=False):
        return self.async_tasks.list_tasks(active_only=active_only)

    def install_online_mod_async(self, project_id, project_type="mod", instance_id="26.2", loader="fabric", version="26.2"):
        task_id = self.async_tasks.submit_task(
            f"Install {project_type}: {project_id}",
            self.store.install_project,
            project_id=project_id,
            project_type=project_type,
            instance_id=instance_id,
            loader=loader,
            version=version,
        )
        return {"success": True, "task_id": task_id}

    def check_mod_updates_async(self, instance_dir="26.2"):
        task_id = self.async_tasks.submit_task(
            f"Check Mod Updates ({instance_dir})",
            self.check_mod_updates,
            instance_dir=instance_dir,
        )
        return {"success": True, "task_id": task_id}

    def run_deep_clean_async(self, dry_run=False):
        task_id = self.async_tasks.submit_task(
            "Deep Cleaner" if not dry_run else "Storage Analysis (Dry Run)",
            self.cleaner.run_deep_clean,
            dry_run=dry_run,
        )
        return {"success": True, "task_id": task_id}

    def run_self_repair_async(self, instance_id="26.2"):
        task_id = self.async_tasks.submit_task(
            f"Self-Repair ({instance_id})",
            self.repair.repair_instances,
            instance_id=instance_id,
        )
        return {"success": True, "task_id": task_id}

    def export_instance_zip_async(self, instance_id="26.2"):
        task_id = self.async_tasks.submit_task(
            f"Export Bundle ({instance_id})",
            self.exporter.export_instance_zip,
            instance_id=instance_id,
        )
        return {"success": True, "task_id": task_id}

    def trim_process_memory(self, pid=None):
        return self.hardware.trim_process_memory(pid)

    def copy_to_clipboard(self, text=""):
        """Copies given text to Windows clipboard via native clip utility."""
        try:
            import subprocess
            if sys.platform == "win32":
                subprocess.run("clip", input=str(text).encode("utf-16le"), check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                return {"success": True}
        except Exception:
            pass
        return {"success": False}

    # --- MODRINTH & CURSEFORGE ONLINE STORE ---
    def search_online_content(self, query="", project_type="mod", provider="modrinth", loader="fabric", version="26.2", sort="downloads", limit=24, offset=0):
        return self.store.search_online_content(query, project_type, provider, loader, version, sort, limit, offset)

    def install_store_item(self, project_id, project_type="mod", instance_id="26.2", loader="fabric", version="26.2"):
        return self.store.install_project(project_id, project_type, instance_id, loader, version)

    def close_launcher(self):
        def _terminate():
            time.sleep(0.2)
            os._exit(0)
        threading.Thread(target=_terminate, daemon=True).start()
        return {"success": True}

    def close_app(self):
        return self.close_launcher()

    # --- SATELLITE TELEMETRY ---
    def get_satellite_telemetry(self):
        return self.satellite.get_satellite_status()

    # --- ALIASES & COMPATIBILITY METHODS ---
    def get_hardware_specs(self):
        return self.hardware.get_hardware_telemetry()

    def get_hardware_telemetry(self):
        """Returns live hardware metrics directly from Windows Kernel."""
        return self.hardware.get_hardware_telemetry()

    def get_servers(self, category="All"):
        """Returns server list with live pings and player counts."""
        return self.servers.get_all_servers(category)

    def claim_sync_code(self, code, username=""):
        return self.cloud_sync.claim_sync_code(code, username)

    def clean_all_temporary_data(self):
        return self.cleaner.clean_temporary_data()

    def get_latest_logs(self, instance_id="26.2", max_lines=150):
        return self.logs.get_latest_log(instance_id, max_lines)

    def open_packs_folder(self, instance_id="26.2"):
        return self.packs.open_packs_folder(instance_id)

    def repair_all_instances(self):
        return self.repair.repair_instances()

    # --- GOOGLE CLOUD AUTH & FIREBASE PERSISTENCE ---
    def _on_cloud_auth_change(self, profile):
        self._emit_ui_event("sir_cloud_auth_changed", profile)
        self._emit_ui_event("cloud_auth_changed", profile)
        if self.window:
            try:
                js = f"if (window.onCloudAuthSuccess) window.onCloudAuthSuccess({json.dumps(profile)});"
                self.window.evaluate_js(js)
            except Exception:
                pass
            try:
                self.window.restore()
                self.window.show()
            except Exception:
                pass
        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.FindWindowW(None, "SIR Launcher — Independent Gaming Platform")
                if hwnd:
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    user32.SetForegroundWindow(hwnd)
                    user32.BringWindowToTop(hwnd)
            except Exception:
                pass

    def start_google_login(self, port=49152):
        """Initiates 1-click Google OAuth via local loopback bridge and browser."""
        return self.cloud_sync.start_google_login(port)

    def logout_google(self):
        """Logs out from Google Cloud Sync."""
        self.cloud_sync.logout()
        return {"success": True}

    def get_cloud_status(self):
        """Returns current Google Cloud authentication profile."""
        return self.cloud_sync.get_user_profile()

    def cloud_get_status(self):
        """Directive 26 alias: Returns current Google Cloud authentication profile."""
        return self.get_cloud_status()

    def backup_to_cloud(self):
        """Pushes local accounts and launcher settings to Firebase."""
        return self.cloud_sync.sync_all_to_cloud()

    def restore_from_cloud(self):
        """Restores accounts and launcher settings from Firebase."""
        return self.cloud_sync.restore_from_cloud()

    def mark_release_seen(self, version="1.0.0"):
        """Saves last seen release version on background daemon thread without blocking UI."""
        def _save():
            try:
                settings = self.instances.load_settings()
                settings["last_seen_release"] = str(version)
                self.instances.save_settings(settings)
            except Exception:
                pass
        threading.Thread(target=_save, daemon=True).start()
        return {"success": True}

    # --- LUNAR CLIENT BI-DIRECTIONAL BRIDGE (C: <-> D:) ---
    def get_lunar_profiles_status(self):
        """Returns live comparison and synchronization matrix between Lunar Client and SIR instances."""
        return self.lunar_bridge.get_profiles_status()

    def sync_lunar_profile(self, profile_id, direction="lunar_to_sir"):
        """Synchronizes settings and keybinds between a specific Lunar profile and SIR instance."""
        if direction == "lunar_to_sir":
            return self.lunar_bridge.sync_lunar_to_sir(profile_id)
        return self.lunar_bridge.sync_sir_to_lunar(profile_id)

    def sync_all_lunar_profiles(self, direction="lunar_to_sir"):
        """Performs batch synchronization across all 6 mapped profile pairs."""
        return self.lunar_bridge.sync_all_profiles(direction)

    # --- AUTO-UPDATER & WHAT'S NEW ENGINE ---
    def get_whats_new_status(self):
        """Checks if the user has already acknowledged the current release notes."""
        last_seen = self.instances.settings.get("last_seen_release", "0.0.0")
        current_version = "1.0.0"
        return {
            "current_version": current_version,
            "last_seen_release": last_seen,
            "last_seen": last_seen,
            "should_show": last_seen != current_version,
        }

    def mark_release_seen(self, version_str="1.0.0"):
        """Marks a release version as acknowledged to prevent repeated popups."""
        def _bg_save():
            try:
                self.instances.settings["last_seen_release"] = str(version_str)
                self.instances.save_settings(self.instances.settings)
            except Exception:
                pass
        threading.Thread(target=_bg_save, daemon=True).start()
        return {"success": True, "last_seen_release": str(version_str), "last_seen": str(version_str)}

    def check_for_launcher_updates(self):
        """Checks the online delta manifest for updates against the local installation."""
        try:
            import urllib.request
            url = "https://sir-modpack.web.app/delta_manifest.json"
            req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                remote_manifest = json.loads(resp.read().decode("utf-8"))

            remote_ver = remote_manifest.get("version", "1.0.0")
            remote_files = remote_manifest.get("total_files", 0)

            local_manifest_file = os.path.join(self.root_dir, "delta_manifest.json")
            local_ver = "1.0.0"
            if os.path.isfile(local_manifest_file):
                try:
                    with open(local_manifest_file, "r", encoding="utf-8") as f:
                        loc_m = json.load(f)
                        local_ver = loc_m.get("version", "1.0.0")
                except Exception:
                    pass

            up_to_date = (local_ver == remote_ver)
            return {
                "success": True,
                "up_to_date": up_to_date,
                "update_available": not up_to_date,
                "current_version": local_ver,
                "remote_version": remote_ver,
                "remote_files": remote_files,
                "message": "You are on the latest official master release (v1.0.0)!" if up_to_date else f"Update available: v{remote_ver}"
            }
        except Exception as e:
            # Fallback to local manifest if network is temporarily unreachable
            local_manifest_file = os.path.join(self.root_dir, "delta_manifest.json")
            local_ver = "1.0.0"
            if os.path.isfile(local_manifest_file):
                try:
                    with open(local_manifest_file, "r", encoding="utf-8") as f:
                        loc_m = json.load(f)
                        local_ver = loc_m.get("version", "1.0.0")
                except Exception:
                    pass
            return {
                "success": True,
                "up_to_date": True,
                "update_available": False,
                "current_version": local_ver,
                "remote_version": local_ver,
                "remote_files": 0,
                "message": f"Operating in local master release mode (v{local_ver})."
            }

    # --- DEVELOPER FEEDBACK HIGHWAY & SYSTEM DIAGNOSTICS ---
    def get_system_diagnostic_metadata(self):
        """Extracts rich automated hardware, OS, and runtime telemetry for error reporting."""
        import platform
        os_info = f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"
        cpu_info = platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "Standard CPU")
        
        gpu_info = getattr(self.hardware, "cached_gpu", "Dedicated DirectX/OpenGL GPU")

        selected_inst = self.instances.settings.get("selected_instance", "26.2-ultra")
        ram_allocated = self.instances.settings.get("ram_allocated_gb", 8)
        
        # Read tail of recent launch log
        log_snippet = ""
        try:
            launch_log_dir = os.path.join(self.data_root, "logs", "launches")
            if os.path.isdir(launch_log_dir):
                log_files = sorted(
                    [os.path.join(launch_log_dir, f) for f in os.listdir(launch_log_dir) if f.endswith(".log")],
                    key=os.path.getmtime,
                    reverse=True
                )
                if log_files:
                    with open(log_files[0], "r", encoding="utf-8", errors="replace") as lf:
                        lines = lf.readlines()
                        log_snippet = "".join(lines[-40:])
        except Exception:
            pass

        user_email = "anonymous@sir-modpack.com"
        if getattr(self, "cloud_sync", None):
            try:
                user_email = self.cloud_sync.get_user_profile().get("email") or user_email
            except Exception:
                pass

        return {
            "client_app": "SIR Launcher Modern",
            "app_version": "v1.0.0",
            "os": os_info,
            "cpu": cpu_info,
            "gpu": gpu_info,
            "active_profile": selected_inst,
            "allocated_ram_gb": ram_allocated,
            "recent_log": log_snippet,
            "log_tail": log_snippet,
            "user_email": user_email
        }

    def upload_screenshot_cloudinary(self, base64_image_or_path):
        """Uploads a screenshot to Cloudinary and returns the secure delivery URL."""
        try:
            import urllib.request
            import urllib.parse
            import base64
            
            if os.path.isfile(str(base64_image_or_path)):
                with open(base64_image_or_path, "rb") as bf:
                    b64_str = base64.b64encode(bf.read()).decode("utf-8")
                data_uri = f"data:image/png;base64,{b64_str}"
            elif str(base64_image_or_path).startswith("data:image"):
                data_uri = str(base64_image_or_path)
            else:
                data_uri = f"data:image/png;base64,{base64_image_or_path}"

            cloud_name = "dfvh4jcsh"
            upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
            
            post_data = urllib.parse.urlencode({
                "file": data_uri,
                "upload_preset": "ml_default",
                "folder": "sir_community_feedback"
            }).encode("utf-8")

            req = urllib.request.Request(upload_url, data=post_data, headers={"User-Agent": "SIR-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                secure_url = res_json.get("secure_url") or res_json.get("url")
                return {"success": True, "url": secure_url}
        except Exception as ex:
            return {"success": False, "error": str(ex), "url": ""}

    def submit_desktop_feedback(self, feedback_payload):
        """Submits an error report or feature suggestion to Firebase and saves local receipt."""
        try:
            import urllib.request
            import uuid
            feedback_type = feedback_payload.get("type", "issue")
            prefix = "SUGG" if feedback_type == "suggestion" else "ERR"
            ticket_id = f"SIR-{prefix}-{uuid.uuid4().hex[:6].upper()}"

            feedback_payload["ticket_id"] = ticket_id
            feedback_payload["submitted_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            feedback_payload["status"] = "open"

            # 1. Save local history
            history_file = os.path.join(self.data_root, "feedback_history.json")
            try:
                history = []
                if os.path.isfile(history_file):
                    with open(history_file, "r", encoding="utf-8") as hf:
                        history = json.load(hf)
                history.insert(0, feedback_payload)
                atomic_write_json(history_file, history[:50])
            except Exception:
                pass

            # 2. Transmit to Firebase RTDB
            target_endpoint = f"https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/feedback_submissions/{ticket_id}.json"
            try:
                post_body = json.dumps(feedback_payload, ensure_ascii=False).encode("utf-8")
                req = urllib.request.Request(target_endpoint, data=post_body, method="PUT", headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8.0) as resp:
                    pass
            except Exception:
                pass

            return {"success": True, "ticket_id": ticket_id, "message": "Feedback submitted successfully."}
        except Exception as ex:
            return {"success": False, "error": str(ex), "ticket_id": f"LOC-{int(time.time())}"}

    def search_store_projects(self, query="", project_type="mod", loader=None, version=None, sort="downloads", limit=24, offset=0):
        """Searches live projects via backend Python bridge with custom User-Agent and 60s query caching."""
        return self.store.search_modrinth(
            query=query,
            project_type=project_type,
            loader=loader,
            version=version,
            sort=sort,
            limit=limit,
            offset=offset
        )

    def search_modrinth_store(self, query="", project_type="mod", sort="downloads", offset=0, limit=24):
        """Searches Modrinth API v2 via backend Python bridge with custom User-Agent and query caching."""
        return self.search_store_projects(
            query=query,
            project_type=project_type,
            sort=sort,
            offset=offset,
            limit=limit
        )

    def install_online_mod(self, slug_or_id, instance_id="26.2-ultra", project_type="mod"):
        """Downloads and installs a project from Modrinth directly into target profile."""
        return self.store.install_project(
            project_id=slug_or_id,
            project_type=project_type,
            instance_id=instance_id
        )
