import urllib.request
import json

def query_minecraft_server_live_status(host):
    try:
        url = f"https://api.mcstatus.io/v2/status/java/{host}"
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
        with urllib.request.urlopen(req, timeout=4) as r:
            res = json.loads(r.read().decode("utf-8"))
            online = res.get("online", False)
            p_info = res.get("players", {})
            p_onl = p_info.get("online", 0)
            p_max = p_info.get("max", 0)
            ver = res.get("version", {}).get("name_clean", "Unknown")
            motd = res.get("motd", {}).get("clean", "")
            return {
                "online": online,
                "players_str": f"{p_onl:,} / {p_max:,} Online" if online else "Offline",
                "online_num": p_onl,
                "max_num": p_max,
                "version": ver,
                "motd": motd.splitlines()[0] if motd else ""
            }, None
    except Exception:
        pass
    return {
        "online": False,
        "players_str": "Unreachable",
        "online_num": 0,
        "max_num": 0,
        "version": "Unknown",
        "motd": ""
    }, "Unreachable"
