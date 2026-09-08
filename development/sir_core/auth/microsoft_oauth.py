import urllib.request
import urllib.parse
import json
import webbrowser
import threading
import time
from ..config import MSA_CLIENT_ID

def start_microsoft_login_flow(on_success_callback, on_status_callback=None):
    """
    Initiates official Microsoft Device Code Flow (matching Prism Launcher Azure registration).
    Requests code, opens https://www.microsoft.com/link, and polls token endpoint.
    """
    device_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
    data = urllib.parse.urlencode({
        "client_id": MSA_CLIENT_ID,
        "scope": "XboxLive.SignIn XboxLive.offline_access"
    }).encode("utf-8")

    req = urllib.request.Request(device_url, data=data, headers={"User-Agent": "SIRLauncher/1.0", "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            dev_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        if on_status_callback:
            on_status_callback(f"Failed to contact Microsoft: {e}")
        return

    user_code = dev_data.get("user_code", "")
    device_code = dev_data.get("device_code", "")
    verification_uri = dev_data.get("verification_uri", "https://www.microsoft.com/link")
    interval = dev_data.get("interval", 5)

    if on_status_callback:
        on_status_callback(f"Enter code: {user_code} at {verification_uri}")

    try:
        webbrowser.open(verification_uri)
    except Exception:
        pass

    def poll_thread():
        token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        poll_data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": MSA_CLIENT_ID,
            "device_code": device_code
        }).encode("utf-8")

        start_time = time.time()
        while time.time() - start_time < 300: # 5 mins
            time.sleep(interval)
            try:
                p_req = urllib.request.Request(token_url, data=poll_data, headers={"User-Agent": "SIRLauncher/1.0", "Content-Type": "application/x-www-form-urlencoded"})
                with urllib.request.urlopen(p_req, timeout=15) as resp:
                    tok_data = json.loads(resp.read().decode("utf-8"))
                    if "access_token" in tok_data:
                        if on_success_callback:
                            on_success_callback({
                                "name": "Microsoft Player",
                                "type": "Microsoft (MSA)",
                                "skinUrl": "https://mc-heads.net/skin/MHF_Alex"
                            })
                        return
            except urllib.error.HTTPError as he:
                try:
                    err_json = json.loads(he.read().decode("utf-8"))
                    err_code = err_json.get("error", "")
                    if err_code == "authorization_pending":
                        continue
                    elif err_code == "slow_down":
                        time.sleep(5)
                        continue
                    else:
                        if on_status_callback:
                            on_status_callback(f"Microsoft auth error: {err_code}")
                        return
                except Exception:
                    pass
            except Exception:
                pass

    threading.Thread(target=poll_thread, daemon=True).start()
