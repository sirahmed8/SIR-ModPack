"""cloud_sync_service.py — Unified Google Cloud Auth & Firebase Persistence Engine.

Enables 1-click Google sign-in for desktop apps via local loopback OAuth bridge,
shares sessions seamlessly between SIR Launcher and SIR Server Manager via
%APPDATA%\\SIR ModPack\\cloud_session.json, and synchronizes user accounts,
settings, and server configurations to Firebase Realtime Database.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, Optional

try:
    from shared_core.runtime import atomic_write_json
except ImportError:
    def atomic_write_json(path, value):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
        os.replace(temp, path)


FIREBASE_RTDB_URL = "https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app"
AUTH_BRIDGE_URL = "https://sir-modpack.web.app/auth/desktop"


class CloudSyncService:
    """Manages cross-application Google Authentication and Firebase Cloud Sync."""

    def __init__(self, data_root: Optional[str] = None, on_auth_change: Optional[Callable[[Dict[str, Any]], None]] = None):
        if not data_root:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
            data_root = os.path.join(appdata, "SIR ModPack")
        self.data_root = os.path.abspath(data_root)
        os.makedirs(self.data_root, exist_ok=True)
        self.session_file = os.path.join(self.data_root, "cloud_session.json")
        self.accounts_file = os.path.join(self.data_root, "accounts.json")
        self.settings_file = os.path.join(self.data_root, "launcher_settings.json")
        self.on_auth_change = on_auth_change

        self._http_server: Optional[HTTPServer] = None
        self._server_thread: Optional[threading.Thread] = None
        self._active_port = 49152
        self.current_session: Dict[str, Any] = self.load_session()

        # Check and perform initial cloud restore if local accounts are empty
        if self.is_authenticated():
            self._auto_restore_if_needed()

    # ── Session Management ───────────────────────────────────────────────────

    def load_session(self) -> Dict[str, Any]:
        """Loads shared Google cloud session from disk."""
        if os.path.isfile(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and data.get("uid"):
                    return data
            except Exception as e:
                print(f"[CloudSync] Error reading session: {e}", file=sys.stderr)
        return {}

    def is_authenticated(self) -> bool:
        """Returns True if a valid Google Cloud session exists."""
        return bool(self.current_session and self.current_session.get("uid"))

    def get_user_profile(self) -> Dict[str, Any]:
        """Returns sanitized user metadata for UI rendering."""
        if not self.is_authenticated():
            return {"authenticated": False}
        return {
            "authenticated": True,
            "uid": self.current_session.get("uid"),
            "email": self.current_session.get("email"),
            "displayName": self.current_session.get("displayName") or self.current_session.get("email", "SIR Member"),
            "photoURL": self.current_session.get("photoURL") or "",
            "lastSync": self.current_session.get("lastSync", 0),
        }

    def save_session(self, session_data: Dict[str, Any]) -> None:
        """Saves cloud session and notifies listeners."""
        session_data["updatedAt"] = int(time.time())
        self.current_session = session_data
        atomic_write_json(self.session_file, session_data)
        if self.on_auth_change:
            try:
                self.on_auth_change(self.get_user_profile())
            except Exception:
                pass
        # Automatically trigger cloud restore or backup
        threading.Thread(target=self.sync_all_to_cloud, daemon=True).start()

    def logout(self) -> None:
        """Clears cloud session from disk and notifies listeners."""
        self.current_session = {}
        if os.path.isfile(self.session_file):
            try:
                os.remove(self.session_file)
            except Exception:
                pass
        if self.on_auth_change:
            try:
                self.on_auth_change({"authenticated": False})
            except Exception:
                pass

    # ── Google OAuth Loopback Listener ───────────────────────────────────────

    def start_google_login(self, preferred_port: int = 49152) -> Dict[str, Any]:
        """Starts local loopback server and opens web browser to Google Auth."""
        if self._http_server:
            self.stop_listener()

        self._active_port = preferred_port
        service_ref = self

        class AuthCallbackHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                return  # Silent logging

            def do_OPTIONS(self):
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()

            def do_POST(self):
                if self.path == "/auth/callback":
                    try:
                        content_length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(content_length)
                        data = json.loads(body.decode("utf-8"))

                        if data.get("uid"):
                            service_ref.save_session(data)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.send_header("Access-Control-Allow-Origin", "*")
                            self.end_headers()
                            self.wfile.write(b'{"status":"ok"}')
                            threading.Thread(target=service_ref.stop_listener, daemon=True).start()
                            return
                    except Exception as err:
                        print(f"[CloudSync] Callback error: {err}", file=sys.stderr)

                self.send_response(400)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b'{"status":"error"}')

        for port_offset in range(5):
            port = self._active_port + port_offset
            try:
                self._http_server = HTTPServer(("127.0.0.1", port), AuthCallbackHandler)
                self._active_port = port
                break
            except OSError:
                continue

        if not self._http_server:
            return {"success": False, "error": "Could not bind local OAuth port."}

        self._server_thread = threading.Thread(target=self._http_server.serve_forever, daemon=True)
        self._server_thread.start()

        auth_url = f"{AUTH_BRIDGE_URL}?port={self._active_port}"
        webbrowser.open(auth_url)

        return {
            "success": True,
            "port": self._active_port,
            "auth_url": auth_url,
            "message": "Opened browser for Google Authentication."
        }

    def stop_listener(self) -> None:
        """Stops the local HTTP listener."""
        if self._http_server:
            try:
                self._http_server.shutdown()
                self._http_server.server_close()
            except Exception:
                pass
            self._http_server = None

    # ── Firebase Realtime Database Sync (Backup & Restore) ───────────────────

    def sync_all_to_cloud(self) -> Dict[str, Any]:
        """Pushes accounts, launcher settings, and server settings to Firebase."""
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated with Google."}

        uid = self.current_session.get("uid")
        id_token = self.current_session.get("idToken")

        # Gather local configuration
        backup_payload: Dict[str, Any] = {
            "updatedAt": int(time.time()),
            "email": self.current_session.get("email"),
            "displayName": self.current_session.get("displayName"),
        }

        # 1. Accounts
        if os.path.isfile(self.accounts_file):
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    backup_payload["accounts"] = json.load(f)
            except Exception:
                pass

        # 2. Launcher Settings
        if os.path.isfile(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    backup_payload["launcher_settings"] = json.load(f)
            except Exception:
                pass

        # 3. Server Orchestrator Settings
        server_settings_file = os.path.join(self.data_root, "server_orchestrator_settings.json")
        if os.path.isfile(server_settings_file):
            try:
                with open(server_settings_file, "r", encoding="utf-8") as f:
                    backup_payload["server_settings"] = json.load(f)
            except Exception:
                pass

        # Push to Firebase RTDB
        endpoint = f"{FIREBASE_RTDB_URL}/users/{uid}/cloud_backup.json"
        if id_token:
            endpoint += f"?auth={id_token}"

        last_err = None
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(backup_payload, ensure_ascii=False).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="PUT"
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    if resp.status in (200, 204):
                        self.current_session["lastSync"] = int(time.time())
                        atomic_write_json(self.session_file, self.current_session)
                        return {"success": True, "timestamp": self.current_session["lastSync"]}
            except Exception as e:
                last_err = e
                if attempt == 0:
                    time.sleep(1.0)

        if last_err:
            print(f"[CloudSync] Push error after retries: {last_err}", file=sys.stderr)
            return {"success": False, "error": str(last_err)}

        return {"success": False, "error": "Failed to upload to cloud."}

    def restore_from_cloud(self) -> Dict[str, Any]:
        """Pulls cloud backup and restores local accounts and settings."""
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated with Google."}

        uid = self.current_session.get("uid")
        id_token = self.current_session.get("idToken")

        endpoint = f"{FIREBASE_RTDB_URL}/users/{uid}/cloud_backup.json"
        if id_token:
            endpoint += f"?auth={id_token}"

        try:
            req = urllib.request.Request(endpoint, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data or not isinstance(data, dict):
                    return {"success": False, "message": "No cloud backup found for this account."}

                # Restore accounts
                if data.get("accounts"):
                    atomic_write_json(self.accounts_file, data["accounts"])

                # Restore launcher settings
                if data.get("launcher_settings"):
                    atomic_write_json(self.settings_file, data["launcher_settings"])

                # Restore server settings
                if data.get("server_settings"):
                    server_settings_file = os.path.join(self.data_root, "server_orchestrator_settings.json")
                    atomic_write_json(server_settings_file, data["server_settings"])

                return {"success": True, "message": "Cloud backup successfully restored!"}
        except Exception as e:
            print(f"[CloudSync] Restore error: {e}", file=sys.stderr)
            return {"success": False, "error": str(e)}

    def _auto_restore_if_needed(self) -> None:
        """Restores cloud backup if local accounts.json is missing or empty."""
        needs_restore = False
        if not os.path.isfile(self.accounts_file):
            needs_restore = True
        else:
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                if not acc or (isinstance(acc, dict) and not acc.get("accounts")):
                    needs_restore = True
            except Exception:
                needs_restore = True

        if needs_restore:
            threading.Thread(target=self.restore_from_cloud, daemon=True).start()

    def resolve_6digit_sync_code(self, code: Any) -> Dict[str, Any]:
        """Validates and resolves a 6-digit sync code from Firebase Realtime Database."""
        if code is None:
            return {"success": False, "error": "Invalid code format: code is None"}
        code_str = str(code).strip()
        if len(code_str) != 6 or not code_str.isdigit():
            return {"success": False, "error": f"Invalid code format: '{code}' is not a 6-digit integer"}

        url = f"{FIREBASE_RTDB_URL}/launcherSyncCodes/{code_str}.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SIR-ModPack-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                raw_bytes = resp.read()
                try:
                    data = json.loads(raw_bytes.decode("utf-8"))
                except Exception:
                    return {"success": False, "error": "Network error: Malformed server response"}
            if not data:
                return {"success": False, "error": "Sync code not found or expired"}
            if data.get("claimed"):
                return {"success": False, "error": "Sync code has already been claimed"}
            return {"success": True, "profile": data, "code": code_str}
        except urllib.error.HTTPError as he:
            return {"success": False, "error": f"Network error: HTTP {he.code}"}
        except urllib.error.URLError as ue:
            return {"success": False, "error": f"Network error: {ue}"}
        except Exception as e:
            return {"success": False, "error": f"Network error: {e}"}

    def claim_sync_code(self, code: Any, username: Optional[str] = None) -> Dict[str, Any]:
        """Claims a 6-digit sync code and marks it as claimed in Firebase."""
        resolved = self.resolve_6digit_sync_code(code)
        if not resolved.get("success"):
            return resolved

        profile = resolved.get("profile", {})
        if username:
            profile["username"] = username

        code_str = str(code).strip()
        url = f"{FIREBASE_RTDB_URL}/launcherSyncCodes/{code_str}.json"
        try:
            update_data = json.dumps({"claimed": True, "claimedAt": int(time.time()), "claimedBy": username or ""}).encode("utf-8")
            req = urllib.request.Request(url, data=update_data, method="PATCH", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10.0):
                pass
        except Exception as e:
            return {"success": False, "error": f"Network error: {e}"}

        return {
            "success": True,
            "claimed": True,
            "code": code_str,
            "profile": profile
        }

    def backup_settings_to_cloud(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Backs up user settings to Firebase Realtime Database."""
        if not user_id:
            return {"success": False, "error": "Missing user_id"}
        url = f"{FIREBASE_RTDB_URL}/users/{user_id}/launcher_settings.json"
        try:
            payload = json.dumps(settings).encode("utf-8")
            req = urllib.request.Request(url, data=payload, method="PUT", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10.0):
                pass
            return {"success": True, "message": "Settings successfully backed up to cloud!"}
        except Exception as e:
            return {"success": False, "error": f"Cloud backup failed: {e}"}
