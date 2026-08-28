import os
import urllib.request
import json
from ..config import INSTANCES_DIR

def download_and_install_mod(project_id, instance_id, source="Modrinth"):
    inst_mods = os.path.join(INSTANCES_DIR, instance_id, "minecraft", "mods")
    os.makedirs(inst_mods, exist_ok=True)
    if source == "Modrinth":
        try:
            ver_url = f"https://api.modrinth.com/v2/project/{project_id}/version"
            req = urllib.request.Request(ver_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                versions = json.loads(r.read().decode("utf-8"))
                if versions:
                    files = versions[0].get("files", [])
                    if files:
                        dl_url = files[0].get("url")
                        fn = files[0].get("filename")
                        target = os.path.join(inst_mods, fn)
                        urllib.request.urlretrieve(dl_url, target)
                        return True, f"Successfully installed {fn}"
        except Exception as e:
            return False, f"Installation error: {e}"
    return False, "Manual installation required for this provider."
