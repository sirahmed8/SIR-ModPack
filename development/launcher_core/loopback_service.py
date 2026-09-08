"""Local, metadata-only pairing bridge for the SIR website.

The bridge is intentionally loopback-only.  It exposes sanitized account
metadata and accepts only offline-profile sync requests authenticated with a
short-lived process token.  Prism/Microsoft credentials never cross this API.
"""

from __future__ import annotations

import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


ALLOWED_ORIGINS = {
    "https://sir-modpack.web.app",
    "https://sir-modpack.firebaseapp.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}


class LoopbackSyncService:
    def __init__(self, auth_service, port: int = 52136):
        self.auth = auth_service
        self.port = port
        self.token = secrets.token_urlsafe(24)
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def _payload(self) -> dict:
        result = self.auth.get_all_accounts(refresh=False)
        return {
            "accounts": [
                {
                    "accountId": item.get("accountId", ""),
                    "name": item.get("displayName", item.get("name", "")),
                    "skinUrl": item.get("skinUrl", item.get("skin", "")),
                    "model": item.get("model", "classic"),
                    "accountType": item.get("accountType", "offline"),
                }
                for item in result.get("accounts", [])
            ],
            "active_account": result.get("active", ""),
            "pairing_token": self.token,
            "metadata_only": True,
        }

    def start(self) -> None:
        service = self

        class Handler(BaseHTTPRequestHandler):
            def _origin(self) -> str:
                origin = self.headers.get("Origin", "")
                return origin if origin in ALLOWED_ORIGINS else ""

            def _send(self, status: int, payload: dict) -> None:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                origin = self._origin()
                if origin:
                    self.send_header("Access-Control-Allow-Origin", origin)
                    self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-SIR-Pairing")
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self):  # noqa: N802
                self._send(204, {})

            def do_GET(self):  # noqa: N802
                parsed = urlparse(self.path)
                query = parse_qs(parsed.query)
                if parsed.path in ("/accounts", "/status"):
                    self._send(200, service._payload())
                    return
                if parsed.path == "/sync":
                    supplied = query.get("token", [""])[0] or self.headers.get("X-SIR-Pairing", "")
                    if not secrets.compare_digest(supplied, service.token):
                        self._send(401, {"success": False, "errorCode": "PAIRING_REQUIRED", "error": "SIR launcher pairing is required."})
                        return
                    name = query.get("ign", [""])[0].strip()
                    if not name:
                        self._send(400, {"success": False, "error": "Offline profile name is required."})
                        return
                    result = service.auth.add_offline_account(
                        name,
                        query.get("skinUrl", [""])[0],
                        "slim" if query.get("model", ["classic"])[0] == "slim" else "classic",
                    )
                    self._send(200 if result.get("success") else 400, result)
                    return
                self._send(404, {"success": False, "error": "Not found"})

            def log_message(self, *_args):
                return

        try:
            self.server = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
            self.server.daemon_threads = True
        except OSError:
            self.server = None
            return
        self.thread = threading.Thread(target=self.server.serve_forever, name="sir-loopback-sync", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

