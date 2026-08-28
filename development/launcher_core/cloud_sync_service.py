import urllib.request
import urllib.parse
import json

class CloudSyncService:
    """Synchronizes profiles and settings with Firebase Realtime Database & Cloudinary."""
    
    def __init__(self, rtdb_url="https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app"):
        self.rtdb_url = rtdb_url

    def resolve_6digit_sync_code(self, code):
        """Resolves 6-digit web code to fetch claimed profile."""
        code = str(code).strip()
        if len(code) != 6:
            return {"success": False, "error": "Invalid code format. Please enter a 6-digit code."}
        
        url = f"{self.rtdb_url}/sync_codes/{code}.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = resp.read().decode('utf-8')
                if data and data != "null":
                    parsed = json.loads(data)
                    return {"success": True, "profile": parsed}
                else:
                    return {"success": False, "error": f"Code {code} not found or expired on the website."}
        except Exception as ex:
            return {"success": False, "error": f"Network error: {str(ex)}"}

    def backup_settings_to_cloud(self, user_id, settings_data):
        url = f"{self.rtdb_url}/user_backups/{user_id}.json"
        try:
            req = urllib.request.Request(url, data=json.dumps(settings_data).encode('utf-8'), method="PUT", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                return {"success": True, "message": "Settings backed up to Firebase Cloud."}
        except Exception as ex:
            return {"success": False, "error": str(ex)}
