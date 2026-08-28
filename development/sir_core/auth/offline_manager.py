import os
import json
from ..config import ACCOUNTS_FILE

def load_accounts():
    default_acc = [{"name": "Player", "type": "Offline", "active": True}]
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                accs = data.get("accounts", [])
                res = []
                for a in accs:
                    a_name = a.get("name") or a.get("profile", {}).get("name") or "Player"
                    a_type = a.get("type", "Offline")
                    a_skin = a.get("skinUrl", f"https://mc-heads.net/skin/{a_name}")
                    a_active = a.get("active", False)
                    res.append({
                        "name": a_name,
                        "type": a_type,
                        "skinUrl": a_skin,
                        "active": a_active
                    })
                if res:
                    return res
        except Exception:
            pass
    return default_acc

def save_accounts(accounts, active_account_name="Player"):
    try:
        os.makedirs(os.path.dirname(ACCOUNTS_FILE), exist_ok=True)
        sir_accs = []
        for a in accounts:
            a_name = a.get("name", "Player")
            a_type = a.get("type", "Offline")
            sir_accs.append({
                "profile": {
                    "id": f"offline-{a_name.lower()}",
                    "name": a_name
                },
                "name": a_name,
                "type": a_type,
                "skinUrl": a.get("skinUrl", f"https://mc-heads.net/skin/{a_name}"),
                "active": (a_name == active_account_name),
                "ygg": {
                    "extra": {
                        "clientToken": f"sir-token-{a_name.lower()}",
                        "userName": a_name
                    },
                    "token": "sir-offline-token"
                }
            })
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump({"formatVersion": 3, "accounts": sir_accs}, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving accounts: {e}")
        return False

def add_offline_account(accounts, username):
    clean = username.strip() or "Player"
    existing = next((a for a in accounts if a.get("name", "").lower() == clean.lower()), None)
    if existing:
        existing["name"] = clean
        existing["type"] = "Offline"
    else:
        accounts.append({
            "name": clean,
            "type": "Offline",
            "skinUrl": f"https://mc-heads.net/skin/{clean}",
            "active": True
        })
    return clean
