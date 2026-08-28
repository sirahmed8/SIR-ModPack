import urllib.request
import json
from ..config import FIREBASE_RTDB_BASE, APP_VERSION

def check_for_launcher_updates():
    try:
        url = f"{FIREBASE_RTDB_BASE}/releases/latest.json"
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, dict):
                latest_ver = data.get("version", "1.0.0")
                notes = data.get("notes", "New performance enhancements and shader fixes.")
                if latest_ver != APP_VERSION.split()[0]:
                    return True, latest_ver, notes
    except Exception:
        pass
    return False, APP_VERSION, "You are on the latest official build."
