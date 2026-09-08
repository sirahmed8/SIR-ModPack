import urllib.request
import urllib.parse
import json
import random
from ..config import FIREBASE_RTDB_BASE

def sync_profile_by_ign_or_email(query_val):
    q = query_val.strip()
    if not q:
        return None, "Empty query provided."
    clean_ign = urllib.parse.quote(q.lower())
    try:
        url = f"{FIREBASE_RTDB_BASE}/profiles/{clean_ign}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, dict):
                return {
                    "ign": data.get("ign", q),
                    "skinUrl": data.get("skinUrl", f"https://mc-heads.net/skin/{q}"),
                    "model": data.get("model", "classic"),
                    "type": "Web Claimed"
                }, None
    except Exception:
        pass

    safe_email = q.replace(".", "_").replace("@", "_at_").lower()
    try:
        url = f"{FIREBASE_RTDB_BASE}/accounts_by_email/{safe_email}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            mapped_ign = json.loads(resp.read().decode("utf-8"))
            if mapped_ign and isinstance(mapped_ign, str):
                return sync_profile_by_ign_or_email(mapped_ign)
    except Exception:
        pass

    return None, f"No claimed profile found on Firebase for '{q}'."

def sync_profile_by_code(code_val):
    c = code_val.strip()
    if not c or len(c) != 6:
        return None, "Sync code must be 6 digits."
    try:
        url = f"{FIREBASE_RTDB_BASE}/sync_codes/{c}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, dict) and data.get("ign"):
                return {
                    "ign": data.get("ign"),
                    "skinUrl": data.get("skinUrl", f"https://mc-heads.net/skin/{data.get('ign')}"),
                    "model": data.get("model", "classic"),
                    "type": "Web Claimed"
                }, None
    except Exception as e:
        return None, f"Network error querying sync code: {e}"

    return None, "Invalid or expired 6-digit sync code."

def generate_sync_code(profile):
    code = f"{random.randint(100000, 999999)}"
    try:
        url = f"{FIREBASE_RTDB_BASE}/sync_codes/{code}.json"
        req = urllib.request.Request(url, data=json.dumps(profile).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PUT")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return code
    except Exception:
        return None
