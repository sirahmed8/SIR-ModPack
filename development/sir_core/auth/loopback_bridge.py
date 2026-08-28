import http.server
import socketserver
import urllib.parse
import threading

def start_loopback_sync_bridge(on_profile_received_callback, port=52136):
    class WebSyncHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path.startswith("/sync"):
                query = urllib.parse.parse_qs(parsed.query)
                ign = query.get("ign", ["Player"])[0]
                skin_url = query.get("skinUrl", [""])[0]
                acc_type = query.get("type", ["Web Claimed"])[0]
                model = query.get("model", ["classic"])[0]
                try:
                    on_profile_received_callback(ign, skin_url, acc_type, model)
                except Exception as ex:
                    print(f"Error in sync callback: {ex}")
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok","message":"Profile synchronized into SIR Launcher"}')
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    def _run():
        try:
            server = socketserver.TCPServer(("127.0.0.1", port), WebSyncHandler)
            server.serve_forever()
        except Exception:
            pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t
