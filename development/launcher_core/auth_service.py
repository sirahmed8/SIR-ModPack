"""Canonical SIR account index and Prism account integration.

SIR stores only display metadata. Prism owns Microsoft OAuth/Xbox/Minecraft
tokens in its own local account file; this service never fabricates an official
account from a gamertag and never copies credentials into cloud data.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import threading
import urllib.request
import urllib.parse
import uuid
from typing import Any

try:
    from shared_core.runtime import atomic_write_json
except ImportError:  # direct unit-test/import fallback
    def atomic_write_json(path, value):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
        os.replace(temp, path)


class AuthService:
    """Manage sanitized account metadata and delegate official auth to Prism."""

    SCHEMA_VERSION = 1

    def __init__(self, data_dir: str, prism_root: str | None = None, payload_root: str | None = None):
        self.data_dir = os.path.abspath(data_dir)
        self.prism_root = os.path.abspath(prism_root or os.path.join(self.data_dir, "prism"))
        self.payload_root = os.path.abspath(payload_root or self.data_dir)
        self.accounts_file = os.path.join(self.data_dir, "accounts.json")
        self.ias_file = os.path.join(self.data_dir, "ias_accounts.json")
        self.hidden_file = os.path.join(self.data_dir, "state", "hidden_prism_accounts.json")
        self.migration_marker = os.path.join(self.data_dir, "state", "accounts-migrated-v1.json")
        self.skins_dir = os.path.join(self.data_dir, "skins")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "state"), exist_ok=True)
        os.makedirs(self.prism_root, exist_ok=True)
        os.makedirs(self.skins_dir, exist_ok=True)
        self._hidden_prism_ids = self._load_hidden_ids()
        self.accounts = self.load_accounts()
        self.active_account_id = self._load_active_id()
        self.active_account_name = self._active_name()
        self.user_status = "Online"
        self.sync_to_ingame_ias()

    # ---------- persistence and migration ----------
    def _load_hidden_ids(self) -> set[str]:
        try:
            with open(self.hidden_file, "r", encoding="utf-8") as handle:
                value = json.load(handle)
            return {str(item) for item in value if item}
        except Exception:
            return set()

    def _save_hidden_ids(self) -> None:
        atomic_write_json(self.hidden_file, sorted(self._hidden_prism_ids))

    def _load_active_id(self) -> str:
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as handle:
                    raw = json.load(handle)
                if isinstance(raw, dict) and raw.get("activeAccountId"):
                    return str(raw["activeAccountId"])
            except Exception:
                pass
        for account in self.accounts:
            if account.get("active"):
                return account["accountId"]
        return self.accounts[0]["accountId"] if self.accounts else ""

    def _stable_id(self, kind: str, value: str) -> str:
        digest = hashlib.sha256(f"sir:{kind}:{value}".encode("utf-8")).hexdigest()[:24]
        return f"sir-{digest}"

    def _skin_url(self, name: str, source: dict[str, Any] | None = None) -> str:
        source = source or {}
        profile = source.get("profile") if isinstance(source.get("profile"), dict) else {}
        skin = profile.get("skin") if isinstance(profile.get("skin"), dict) else {}
        return str(source.get("skinUrl") or source.get("skin") or skin.get("url") or f"https://mc-heads.net/skin/{name}")

    def _normalize_legacy(self, source: dict[str, Any]) -> dict[str, Any] | None:
        profile = source.get("profile") if isinstance(source.get("profile"), dict) else {}
        name = str(source.get("displayName") or source.get("name") or profile.get("name") or "").strip()
        if not name:
            return None

        raw_type = str(source.get("accountType") or source.get("type") or "offline").lower()
        official_label = any(token in raw_type for token in ("microsoft", "official", "msa"))
        # A copied SIR record with only a gamertag is not proof of ownership.
        real_prism_record = any(
            key in source for key in ("msa", "utoken", "xrp-mc", "access_token", "refresh_token")
        )
        account_type = "microsoft" if official_label and real_prism_record else "offline"
        profile_id = str(source.get("prismProfileId") or source.get("profileId") or profile.get("id") or "")
        raw_uuid = str(source.get("uuid") or profile_id or "")
        if not raw_uuid:
            raw_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{name}"))
        account_id = str(source.get("accountId") or self._stable_id(account_type, profile_id or name.lower()))
        skin_data = profile.get("skin") if isinstance(profile.get("skin"), dict) else {}
        model = str(source.get("model") or skin_data.get("variant") or "classic")
        return self._public_account(
            account_id=account_id,
            name=name,
            account_type=account_type,
            profile_id=profile_id,
            uuid_value=raw_uuid,
            skin_url=self._skin_url(name, source),
            model=model,
            needs_relink=official_label and account_type == "offline",
            updated_at=str(source.get("updatedAt") or source.get("created_at") or self._now()),
        )

    def _legacy_sources(self) -> list[str]:
        appdata = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        return [
            os.path.join(self.payload_root, "accounts.json"),
            os.path.join(self.payload_root, "SIR Launcher", "accounts.json"),
            os.path.join(self.payload_root, "SIR Launcher", "bin", "accounts.json"),
            os.path.join(self.payload_root, "bin", "accounts.json"),
            os.path.join(appdata, "SIR Launcher", "accounts.json"),
        ]

    def _read_account_file(self, path: str) -> list[dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
            values = raw if isinstance(raw, list) else raw.get("accounts", []) if isinstance(raw, dict) else []
            return [item for item in values if isinstance(item, dict)]
        except Exception:
            return []

    def load_accounts(self) -> list[dict[str, Any]]:
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as handle:
                    raw = json.load(handle)
                values = raw.get("accounts", []) if isinstance(raw, dict) else raw
                normalized = [self._normalize_legacy(item) for item in values if isinstance(item, dict)]
                accounts = [item for item in normalized if item]
                if accounts or os.path.exists(self.migration_marker):
                    return self._dedupe(accounts)
            except Exception:
                pass

        # One-time migration from old executable-local stores. Empty stores are
        # intentionally not replaced with demo accounts.
        migrated: list[dict[str, Any]] = []
        seen_paths: set[str] = set()
        for path in self._legacy_sources():
            normalized_path = os.path.abspath(path)
            if normalized_path in seen_paths or normalized_path == os.path.abspath(self.accounts_file):
                continue
            seen_paths.add(normalized_path)
            for item in self._read_account_file(path):
                account = self._normalize_legacy(item)
                if account:
                    migrated.append(account)

        migrated = self._dedupe(migrated)
        self.accounts = migrated
        self.active_account_id = migrated[0]["accountId"] if migrated else ""
        self.save_accounts(migrated)
        atomic_write_json(self.migration_marker, {"version": 1, "completedAt": self._now()})
        return migrated

    def _dedupe(self, accounts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        seen: set[str] = set()
        for account in accounts:
            key = str(account.get("prismProfileId") or account.get("displayName", "").lower())
            if not key or key in seen:
                continue
            seen.add(key)
            output.append(account)
        return output

    def _public_account(self, *, account_id: str, name: str, account_type: str, profile_id: str, uuid_value: str, skin_url: str, model: str, needs_relink: bool = False, updated_at: str | None = None) -> dict[str, Any]:
        is_microsoft = account_type == "microsoft"
        public_type = "Microsoft (Official)" if is_microsoft else "Offline Alt"
        return {
            "accountId": account_id,
            "displayName": name,
            "accountType": account_type,
            "uuid": uuid_value,
            "skinUrl": skin_url,
            "model": "slim" if model == "slim" else "classic",
            "prismProfileId": profile_id,
            "updatedAt": updated_at or self._now(),
        }

    def _now(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def save_accounts(self, accounts: list[dict[str, Any]] | None = None) -> None:
        if accounts is not None:
            self.accounts = self._dedupe(accounts)
        atomic_write_json(
            self.accounts_file,
            {
                "schemaVersion": self.SCHEMA_VERSION,
                "activeAccountId": self.active_account_id,
                "accounts": self.accounts,
            },
        )

    # ---------- Prism integration ----------
    def _prism_account_file(self) -> str:
        return os.path.join(self.prism_root, "accounts.json")

    def _find_prism(self) -> str | None:
        candidates = [
            os.path.join(self.payload_root, "prism", "prismlauncher.exe"),
            os.path.join(self.payload_root, "SIR Launcher", "bin", "prismlauncher.exe"),
            os.path.join(self.payload_root, "bin", "prismlauncher.exe"),
            os.path.join(self.payload_root, "prismlauncher.exe"),
        ]
        return next((path for path in candidates if os.path.isfile(path)), None)

    def open_prism_account_manager(self) -> dict[str, Any]:
        exe = self._find_prism()
        if not exe:
            return {"success": False, "errorCode": "PRISM_NOT_FOUND", "error": "The bundled Prism engine was not found. Run Installer & Repair first."}
        try:
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            process = subprocess.Popen([exe, "--dir", self.prism_root, "--show-window"], cwd=os.path.dirname(exe), creationflags=creationflags)
            return {"success": True, "authPending": True, "pid": process.pid, "message": "Prism opened. Use Accounts → Add Microsoft account, then return here and refresh."}
        except Exception as exc:
            return {"success": False, "errorCode": "PRISM_START_FAILED", "error": f"Could not open Prism account manager: {exc}"}

    def _import_prism_accounts(self) -> bool:
        raw_accounts = self._read_account_file(self._prism_account_file())
        changed = False
        for source in raw_accounts:
            if str(source.get("type", "")) != "MSA":
                continue
            profile = source.get("profile") if isinstance(source.get("profile"), dict) else {}
            name = str(profile.get("name") or "").strip()
            profile_id = str(profile.get("id") or "").strip()
            if not name or not profile_id or profile_id in self._hidden_prism_ids:
                continue
            skin = profile.get("skin") if isinstance(profile.get("skin"), dict) else {}
            account = self._public_account(
                account_id=self._stable_id("microsoft", profile_id),
                name=name,
                account_type="microsoft",
                profile_id=profile_id,
                uuid_value=profile_id,
                skin_url=str(skin.get("url") or f"https://mc-heads.net/skin/{name}"),
                model=str(skin.get("variant") or "classic"),
            )
            existing = next((item for item in self.accounts if item.get("prismProfileId") == profile_id or item.get("displayName", "").lower() == name.lower()), None)
            if existing:
                existing.update(account)
            else:
                self.accounts.append(account)
            changed = True
        if changed:
            self.save_accounts(self.accounts)
        return changed

    def refresh_accounts(self) -> dict[str, Any]:
        self._import_prism_accounts()
        self.active_account_name = self._active_name()
        self.sync_to_ingame_ias()
        return self.get_all_accounts(refresh=False)

    # ---------- public bridge API ----------
    def _active_name(self) -> str:
        active = next((a for a in self.accounts if a.get("accountId") == self.active_account_id), None)
        return str(active.get("displayName", "")) if active else ""

    def get_default_account_name(self) -> str:
        return self._active_name()

    def get_active_account(self) -> dict[str, Any] | None:
        return next((item for item in self.accounts if item.get("accountId") == self.active_account_id), None)

    def get_all_accounts(self, refresh: bool = True) -> dict[str, Any]:
        if refresh:
            self._import_prism_accounts()
        self.active_account_name = self._active_name()
        return {"active": self.active_account_name, "activeAccountId": self.active_account_id, "status": self.user_status, "accounts": self.accounts if isinstance(self.accounts, list) else []}

    def select_account(self, name_or_id: str) -> dict[str, Any]:
        value = str(name_or_id or "").strip().lower()
        account = next((item for item in self.accounts if str(item.get("accountId", "")).lower() == value or str(item.get("displayName", "")).lower() == value), None)
        if not account:
            return {"success": False, "errorCode": "ACCOUNT_NOT_FOUND", "error": "Account not found."}
        self.active_account_id = account["accountId"]
        self.active_account_name = account["displayName"]
        self.save_accounts()
        self.sync_to_ingame_ias()
        return {"success": True, "active": self.active_account_name, "accountId": self.active_account_id}

    def set_user_status(self, status: str) -> dict[str, Any]:
        valid = {"Online", "Away", "Busy", "Offline"}
        if status not in valid:
            return {"success": False, "error": "Invalid status"}
        self.user_status = status
        return {"success": True, "status": status}

    def add_microsoft_account(self, username: str = "") -> dict[str, Any]:
        """Open Prism's official account flow; a username is never sufficient."""
        if str(username or "").strip():
            return {"success": False, "errorCode": "OFFICIAL_AUTH_REQUIRED", "error": "Microsoft accounts must be verified through Prism. Do not enter a gamertag or IGN."}
        return self.open_prism_account_manager()

    def add_offline_account(self, name: str, skin_url: str = "", model: str = "classic") -> dict[str, Any]:
        name = str(name or "").strip()
        if not name or len(name) < 2 or len(name) > 16:
            return {"success": False, "error": "Username must be between 2 and 16 characters."}
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return {"success": False, "error": "Username contains invalid characters. Use letters, numbers, and underscores only."}
        existing = next((a for a in self.accounts if a.get("displayName", "").lower() == name.lower()), None)
        if existing:
            self.active_account_id = existing["accountId"]
            self.active_account_name = existing["displayName"]
            self.save_accounts()
            self.sync_to_ingame_ias()
            return {"success": True, "account": existing, "message": f"Switched to offline profile '{name}'."}

        account = self._public_account(
            account_id=self._stable_id("offline", name.lower()),
            name=name,
            account_type="offline",
            profile_id="",
            uuid_value=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{name}")),
            skin_url=skin_url or f"https://mc-heads.net/skin/{name}",
            model=model,
        )
        self.accounts.append(account)
        self.active_account_id = account["accountId"]
        self.active_account_name = account["displayName"]
        self.save_accounts()
        self.sync_to_ingame_ias()
        return {"success": True, "account": account, "message": f"Created offline profile '{name}'."}

    def remove_account(self, name_or_id: str) -> dict[str, Any]:
        value = str(name_or_id or "").strip().lower()
        account = next((item for item in self.accounts if item.get("accountId", "").lower() == value or item.get("displayName", "").lower() == value), None)
        if not account:
            return {"success": False, "errorCode": "ACCOUNT_NOT_FOUND", "error": "Account not found."}
        if account.get("prismProfileId"):
            self._hidden_prism_ids.add(account["prismProfileId"])
            self._save_hidden_ids()
        self.accounts = [item for item in self.accounts if item.get("accountId") != account.get("accountId")]
        if self.active_account_id == account.get("accountId"):
            self.active_account_id = self.accounts[0].get("accountId", "") if self.accounts else ""
        self.active_account_name = self._active_name()
        self.save_accounts()
        self.sync_to_ingame_ias()
        return {"success": True, "accounts": self.accounts, "active": self.active_account_name}

    def sync_to_ingame_ias(self) -> None:
        """Write sanitized compatibility metadata for IAS; never write tokens."""
        try:
            atomic_write_json(self.ias_file, {
                "schemaVersion": 1,
                "active": self.active_account_name,
                "accounts": [
                    {"name": item.get("displayName"), "type": item.get("accountType"), "uuid": item.get("uuid"), "skinUrl": item.get("skinUrl"), "model": item.get("model")}
                    for item in self.accounts
                ],
            })
        except Exception:
            pass

    # ---------- Microsoft OAuth 2.0 Authorization Code + Loopback (real browser login) ----------
    # Same method as Prism Launcher / MultiMC. Opens the REAL Microsoft login page
    # in the user's browser. A temporary localhost HTTP server catches the redirect
    # with the auth code, then we exchange it for Xbox/Minecraft tokens.
    # Client ID 00000000402b5328 = well-known public Minecraft client ID.

    _MS_CLIENT_ID = "c36a9fb6-4f2a-41ff-90bd-ae7cc92031eb"
    _MS_SCOPE = "XboxLive.SignIn offline_access"
    _MS_DEVICE_CODE_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
    _MS_TOKEN_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    _XBOX_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
    _XSTS_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
    _MC_AUTH_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
    _MC_PROFILE_URL = "https://api.minecraftservices.com/minecraft/profile"

    def _http_post(self, url: str, data_dict: dict[str, Any]) -> dict[str, Any]:
        """Performs form-urlencoded POST request."""
        try:
            encoded_data = urllib.parse.urlencode(data_dict).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=encoded_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "SIR-Launcher/1.0.0 (Windows NT 10.0; Win64; x64)"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                return json.loads(raw)
        except urllib.error.HTTPError as he:
            try:
                err_body = json.loads(he.read().decode("utf-8", errors="ignore"))
                return err_body
            except Exception:
                return {"error": f"HTTP Error {he.code}: {he.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def _http_post_json(self, url: str, json_dict: dict[str, Any]) -> dict[str, Any]:
        """Performs JSON body POST request."""
        try:
            encoded_data = json.dumps(json_dict).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=encoded_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "SIR-Launcher/1.0.0 (Windows NT 10.0; Win64; x64)"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                return json.loads(raw)
        except urllib.error.HTTPError as he:
            try:
                err_body = json.loads(he.read().decode("utf-8", errors="ignore"))
                return err_body
            except Exception:
                return {"error": f"HTTP Error {he.code}: {he.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def _http_get(self, url: str, bearer_token: str = "") -> dict[str, Any]:
        """Performs authenticated GET request."""
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": "SIR-Launcher/1.0.0 (Windows NT 10.0; Win64; x64)"
            }
            if bearer_token:
                headers["Authorization"] = f"Bearer {bearer_token}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                return json.loads(raw)
        except urllib.error.HTTPError as he:
            try:
                err_body = json.loads(he.read().decode("utf-8", errors="ignore"))
                return err_body
            except Exception:
                return {"error": f"HTTP Error {he.code}: {he.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def start_microsoft_browser_auth(self) -> dict[str, Any]:
        """Start official Microsoft OAuth via interactive Web Browser and local redirect listener."""
        import http.server
        import socketserver
        import webbrowser as _wb
        import secrets
        import base64

        # Clean up any existing running server
        old_state = getattr(self, "_ms_browser_state", None)
        if old_state and old_state.get("server"):
            try:
                old_state["server"].server_close()
            except Exception:
                pass

        # Generate PKCE verifier and challenge
        verifier = secrets.token_urlsafe(64)
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        state_token = secrets.token_hex(16)

        port = 52135
        server = None
        for p in [52135, 52136, 52137, 0]:
            try:
                class CustomTCPServer(socketserver.TCPServer):
                    allow_reuse_address = True
                
                auth_svc_ref = self
                redirect_uri_val = f"http://localhost:{p}/" if p != 0 else ""
                
                class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
                    def do_GET(self):
                        parsed = urllib.parse.urlparse(self.path)
                        params = urllib.parse.parse_qs(parsed.query)
                        code = params.get("code", [None])[0]
                        err = params.get("error", [None])[0]
                        err_desc = params.get("error_description", [None])[0]

                        self.send_response(200)
                        self.send_header("Content-Type", "text/html; charset=utf-8")
                        self.end_headers()

                        if code:
                            html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SIR Launcher - Sign-in Complete</title>
  <style>
    body { background: #06090e; color: #f1f5f9; font-family: system-ui, -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
    .card { background: #0c121e; border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 24px; padding: 40px; text-align: center; max-width: 440px; box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 30px rgba(0,229,255,0.2); }
    h2 { color: #00e5ff; font-size: 22px; margin: 0 0 12px; }
    p { color: #94a3b8; font-size: 14px; line-height: 1.5; margin: 0 0 20px; }
    .badge { display: inline-block; background: rgba(56, 239, 125, 0.15); color: #38ef7d; border: 1px solid rgba(56, 239, 125, 0.3); font-weight: bold; font-size: 12px; padding: 6px 16px; border-radius: 9999px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>✓ Microsoft Sign-in Complete!</h2>
    <p>Your official Minecraft profile has been authenticated. You can safely close this browser window and return to <strong>SIR Launcher</strong>.</p>
    <span class="badge">Connected to SIR Ecosystem</span>
  </div>
  <script>setTimeout(() => window.close(), 2500);</script>
</body>
</html>"""
                            self.wfile.write(html.encode("utf-8"))
                            threading.Thread(target=auth_svc_ref._handle_browser_code, args=(code, redirect_uri_val, verifier), daemon=True).start()
                        else:
                            html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>SIR Launcher - Sign-in Error</title></head>
<body style="background:#06090e;color:#ff5555;font-family:sans-serif;text-align:center;padding:50px;">
  <h2>Authentication Failed</h2>
  <p>{err_desc or err or 'Login cancelled'}</p>
</body>
</html>"""
                            self.wfile.write(html.encode("utf-8"))
                            auth_svc_ref._ms_browser_state["status"] = "error"
                            auth_svc_ref._ms_browser_state["error"] = err_desc or err or "Login cancelled"

                    def log_message(self, format, *args):
                        pass

                server = CustomTCPServer(("127.0.0.1", p), OAuthCallbackHandler)
                if p == 0:
                    real_port = server.server_address[1]
                    redirect_uri_val = f"http://localhost:{real_port}/"
                    port = real_port
                else:
                    port = p
                redirect_uri = redirect_uri_val
                break
            except Exception:
                continue

        if not server:
            return {"success": False, "error": "Could not start local authorization server."}

        self._ms_browser_state = {
            "server": server,
            "status": "waiting",
            "result": None,
            "error": None,
            "verifier": verifier,
            "redirect_uri": redirect_uri,
            "expires_at": time.time() + 300,
        }

        def run_server():
            try:
                server.handle_request()
            except Exception:
                pass
            finally:
                try:
                    server.server_close()
                except Exception:
                    pass

        threading.Thread(target=run_server, daemon=True).start()

        auth_params = {
            "client_id": self._MS_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": self._MS_SCOPE,
            "prompt": "select_account",
            "state": state_token,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        auth_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?" + urllib.parse.urlencode(auth_params)

        try:
            _wb.open(auth_url)
        except Exception:
            pass

        return {
            "success": True,
            "auth_url": auth_url,
            "redirect_uri": redirect_uri,
            "message": "Opening Microsoft account sign-in in your browser...",
        }

    def _handle_browser_code(self, code: str, redirect_uri: str, code_verifier: str) -> None:
        """Background handler to exchange auth code for tokens and Minecraft profile."""
        try:
            token_resp = self._http_post(self._MS_TOKEN_URL, {
                "grant_type": "authorization_code",
                "client_id": self._MS_CLIENT_ID,
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
                "scope": self._MS_SCOPE,
            })

            if "error" in token_resp or not token_resp.get("access_token"):
                err = token_resp.get("error_description") or token_resp.get("error") or "Failed to exchange Microsoft auth code."
                self._ms_browser_state["status"] = "error"
                self._ms_browser_state["error"] = err
                return

            ms_access_token = token_resp["access_token"]
            res = self._finish_microsoft_tokens(ms_access_token)
            if res.get("success"):
                self._ms_browser_state["status"] = "success"
                self._ms_browser_state["result"] = res
            else:
                self._ms_browser_state["status"] = "error"
                self._ms_browser_state["error"] = res.get("error", "Failed to retrieve Minecraft profile.")
        except Exception as ex:
            self._ms_browser_state["status"] = "error"
            self._ms_browser_state["error"] = str(ex)

    def poll_microsoft_browser_auth(self) -> dict[str, Any]:
        """Poll the status of the interactive browser sign-in."""
        state = getattr(self, "_ms_browser_state", None)
        if not state:
            return {"success": False, "error": "No active authentication session."}

        if time.time() > state.get("expires_at", 0):
            self._ms_browser_state = None
            return {"success": False, "error": "Sign-in timed out. Please try again."}

        status = state.get("status")
        if status == "success":
            res = state.get("result", {})
            self._ms_browser_state = None
            return res
        elif status == "error":
            err = state.get("error", "Sign-in failed.")
            self._ms_browser_state = None
            return {"success": False, "error": err}
        else:
            return {"success": False, "pending": True}

    def _process_microsoft_auth_code(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange authorization code for tokens, Xbox Live JWT, XSTS, and Minecraft Profile."""
        token_resp = self._http_post(self._MS_TOKEN_URL, {
            "grant_type": "authorization_code",
            "client_id": self._MS_CLIENT_ID,
            "code": code,
            "redirect_uri": redirect_uri,
            "scope": self._MS_SCOPE,
        })
        if "error" in token_resp or not token_resp.get("access_token"):
            return {"success": False, "error": token_resp.get("error_description", token_resp.get("error", "Failed to exchange auth code"))}

        ms_access_token = token_resp["access_token"]
        return self._finish_microsoft_tokens(ms_access_token)

    def _finish_microsoft_tokens(self, ms_access_token: str) -> dict[str, Any]:
        """Exchanges Microsoft access token -> Xbox Live -> XSTS -> Minecraft Token -> Profile."""
        xbox_resp = self._http_post_json(self._XBOX_AUTH_URL, {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={ms_access_token}",
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        })
        if "error" in xbox_resp:
            return {"success": False, "error": "Xbox Live auth failed: " + str(xbox_resp.get("error"))}

        xbox_token = xbox_resp.get("Token", "")
        user_hash = ""
        try:
            user_hash = xbox_resp["DisplayClaims"]["xui"][0]["uhs"]
        except Exception:
            pass

        xsts_resp = self._http_post_json(self._XSTS_URL, {
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]},
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        })
        if "XErr" in xsts_resp or ("error" in xsts_resp and not xsts_resp.get("Token")):
            xerr = xsts_resp.get("XErr", "")
            if xerr == 2148916238:
                return {"success": False, "error": "You need an Xbox account. Visit xbox.com to create one."}
            if xerr == 2148916233:
                return {"success": False, "error": "Xbox Live is not available in your region."}
            return {"success": False, "error": f"XSTS error {xerr or xsts_resp.get('error', 'Unknown')}"}

        xsts_token = xsts_resp.get("Token", "")

        mc_resp = self._http_post_json(self._MC_AUTH_URL, {
            "identityToken": f"XBL3.0 x={user_hash};{xsts_token}",
        })
        mc_token = mc_resp.get("access_token", "")
        if not mc_token:
            return {"success": False, "error": "Minecraft auth failed: " + str(mc_resp.get("error", "No token"))}

        profile = self._http_get(self._MC_PROFILE_URL, mc_token)
        name = profile.get("name", "")
        profile_id = profile.get("id", "")
        if not name or not profile_id:
            return {"success": False, "error": "Could not fetch Minecraft profile. Do you own the game?"}

        skin_url = f"https://mc-heads.net/skin/{name}"
        skin_model = "classic"
        try:
            for skin in profile.get("skins", []):
                if skin.get("state") == "ACTIVE":
                    skin_url = skin.get("url", skin_url)
                    skin_model = "slim" if skin.get("variant", "").lower() == "slim" else "classic"
                    break
        except Exception:
            pass

        account = self._public_account(
            account_id=self._stable_id("microsoft", profile_id),
            name=name,
            account_type="microsoft",
            profile_id=profile_id,
            uuid_value=profile_id,
            skin_url=skin_url,
            model=skin_model,
        )
        existing = next((a for a in self.accounts if a.get("prismProfileId") == profile_id
                         or a.get("displayName", "").lower() == name.lower()), None)
        if existing:
            existing.update(account)
        else:
            self.accounts.append(account)

        self.active_account_id = account["accountId"]
        self.active_account_name = name
        self.save_accounts()
        self.sync_to_ingame_ias()
        self._write_prism_msa_account(name, profile_id, mc_token, skin_url, skin_model)

        return {"success": True, "name": name, "uuid": profile_id, "skinUrl": skin_url}

    def _write_prism_msa_account(self, name: str, profile_id: str, mc_token: str, skin_url: str, skin_model: str) -> None:
        target_files = [
            self._prism_account_file(),
            os.path.join(os.getenv("APPDATA", ""), "PrismLauncher", "accounts.json")
        ]
        for tf in set(target_files):
            try:
                os.makedirs(os.path.dirname(tf), exist_ok=True)
                existing = {"accounts": [], "formatVersion": 3}
                if os.path.isfile(tf):
                    try:
                        with open(tf, "r", encoding="utf-8") as f:
                            existing = json.load(f)
                    except Exception:
                        existing = {"accounts": [], "formatVersion": 3}
                
                accts = existing.get("accounts", [])
                accts = [a for a in accts if a.get("profile", {}).get("id") != profile_id and a.get("profile", {}).get("name", "").lower() != name.lower()]
                accts.insert(0, {
                    "type": "MSA",
                    "ygg": {
                        "token": mc_token,
                        "extra": {}
                    },
                    "profile": {
                        "id": profile_id,
                        "name": name,
                        "skin": {
                            "url": skin_url,
                            "variant": skin_model
                        }
                    },
                    "active": True
                })
                existing["accounts"] = accts
                atomic_write_json(tf, existing)
            except Exception:
                pass

    def start_microsoft_device_auth(self) -> dict[str, Any]:
        """Start real Microsoft OAuth via official Device Code Flow."""
        import webbrowser as _wb

        resp = self._http_post(self._MS_DEVICE_CODE_URL, {
            "client_id": self._MS_CLIENT_ID,
            "scope": self._MS_SCOPE,
        })
        if "error" in resp or not resp.get("device_code"):
            err_msg = resp.get("error_description") or resp.get("error") or "Failed to contact Microsoft login service."
            return {"success": False, "error": err_msg}

        user_code = resp.get("user_code", "")
        device_code = resp.get("device_code", "")
        verification_uri = resp.get("verification_uri", "https://microsoft.com/link")
        expires_in = resp.get("expires_in", 900)
        interval = resp.get("interval", 5)

        self._ms_oauth_state: dict[str, Any] = {
            "device_code": device_code,
            "user_code": user_code,
            "verification_uri": verification_uri,
            "expires_at": time.time() + expires_in,
            "interval": interval,
            "done": False,
        }

        # Auto-open the verification page in browser
        try:
            _wb.open(verification_uri)
        except Exception:
            pass

        return {
            "success": True,
            "user_code": user_code,
            "verification_uri": verification_uri,
            "expires_in": expires_in,
            "message": f"Enter code {user_code} at {verification_uri}",
        }

    def poll_microsoft_device_auth(self) -> dict[str, Any]:
        """Poll Microsoft OAuth token endpoint to check if user completed device authorization."""
        state = getattr(self, "_ms_oauth_state", None)
        if not state:
            return {"success": False, "error": "No active authentication session."}

        if time.time() > state.get("expires_at", 0):
            self._ms_oauth_state = None
            return {"success": False, "error": "Sign-in code expired. Please try again."}

        device_code = state.get("device_code")
        if not device_code:
            return {"success": False, "error": "Invalid auth state."}

        token_resp = self._http_post(self._MS_TOKEN_URL, {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": self._MS_CLIENT_ID,
            "device_code": device_code,
        })

        err = token_resp.get("error")
        if err == "authorization_pending":
            return {"success": False, "pending": True, "user_code": state.get("user_code")}
        elif err == "slow_down":
            return {"success": False, "pending": True, "user_code": state.get("user_code")}
        elif err == "expired_token":
            self._ms_oauth_state = None
            return {"success": False, "error": "Sign-in session expired."}
        elif err:
            err_desc = token_resp.get("error_description", err)
            return {"success": False, "error": f"Microsoft authentication error: {err_desc}"}

        ms_access_token = token_resp.get("access_token", "")
        if not ms_access_token:
            return {"success": False, "pending": True}

        # Xbox Live token
        xbox_resp = self._http_post_json(self._XBOX_AUTH_URL, {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={ms_access_token}",
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        })
        if "error" in xbox_resp:
            return {"success": False, "error": "Xbox Live auth failed: " + str(xbox_resp["error"])}

        xbox_token = xbox_resp.get("Token", "")
        user_hash = ""
        try:
            user_hash = xbox_resp["DisplayClaims"]["xui"][0]["uhs"]
        except Exception:
            pass

        # XSTS token
        xsts_resp = self._http_post_json(self._XSTS_URL, {
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]},
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        })
        if "XErr" in xsts_resp or ("error" in xsts_resp and not xsts_resp.get("Token")):
            xerr = xsts_resp.get("XErr", "")
            if xerr == 2148916238:
                return {"success": False, "error": "You need an Xbox account. Visit xbox.com to create one."}
            if xerr == 2148916233:
                return {"success": False, "error": "Xbox Live is not available in your region."}
            return {"success": False, "error": f"XSTS error {xerr or xsts_resp.get('error', 'Unknown')}"}

        xsts_token = xsts_resp.get("Token", "")

        # Minecraft access token
        mc_resp = self._http_post_json(self._MC_AUTH_URL, {
            "identityToken": f"XBL3.0 x={user_hash};{xsts_token}",
        })
        mc_token = mc_resp.get("access_token", "")
        if not mc_token:
            return {"success": False, "error": "Minecraft auth failed: " + str(mc_resp.get("error", "No token"))}

        # Minecraft profile
        profile = self._http_get(self._MC_PROFILE_URL, mc_token)
        name = profile.get("name", "")
        profile_id = profile.get("id", "")
        if not name or not profile_id:
            return {"success": False, "error": "Could not fetch Minecraft profile. Do you own the game?"}

        skin_url = f"https://mc-heads.net/skin/{name}"
        skin_model = "classic"
        try:
            for skin in profile.get("skins", []):
                if skin.get("state") == "ACTIVE":
                    skin_url = skin.get("url", skin_url)
                    skin_model = "slim" if skin.get("variant", "").lower() == "slim" else "classic"
                    break
        except Exception:
            pass

        # Save account (metadata only, never store raw tokens)
        account = self._public_account(
            account_id=self._stable_id("microsoft", profile_id),
            name=name,
            account_type="microsoft",
            profile_id=profile_id,
            uuid_value=profile_id,
            skin_url=skin_url,
            model=skin_model,
        )
        existing = next((a for a in self.accounts if a.get("prismProfileId") == profile_id
                         or a.get("displayName", "").lower() == name.lower()), None)
        if existing:
            existing.update(account)
        else:
            self.accounts.append(account)

        self.active_account_id = account["accountId"]
        self.active_account_name = name
        self.save_accounts()
        self.sync_to_ingame_ias()
        self._ms_oauth_state = None

        return {"success": True, "name": name, "uuid": profile_id, "skinUrl": skin_url}

