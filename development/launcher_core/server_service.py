import os
import io
import gzip
import time
import json
import socket
import struct
import threading
import urllib.request
import urllib.parse

class ServerService:
    """Multi-threaded high-speed TCP socket pinger, live NBT servers.dat reader, and real-time Minecraft status engine."""
    
    def __init__(self, root_dir=None):
        self.root_dir = root_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cached_results = {}
        
        # Curated list of top verified public networks
        self.public_catalog = [
            {
                "name": "Hypixel Network", 
                "ip": "mc.hypixel.net", 
                "port": 25565,
                "type": "Official", 
                "category": "Competitive", 
                "icon": "👑",
                "desc": "Bedwars, Skywars, Duels & Skyblock (Official Account Required)"
            },
            {
                "name": "PikaNetwork", 
                "ip": "play.pikanetwork.net", 
                "port": 25565,
                "type": "Cracked & Official", 
                "category": "Competitive", 
                "icon": "⚡",
                "desc": "Top #1 Ranked Bedwars & Practice PvP with zero latency"
            },
            {
                "name": "JartexNetwork", 
                "ip": "top.jartex.fun", 
                "port": 25565,
                "type": "Cracked & Official", 
                "category": "Competitive", 
                "icon": "🛡️",
                "desc": "Custom Skyblock, OP Factions, KitPvP & Lifesteal SMP"
            },
            {
                "name": "Minemen Club", 
                "ip": "na.minemen.club", 
                "port": 25565,
                "type": "Official", 
                "category": "Competitive", 
                "icon": "⚔️",
                "desc": "Premier Ranked 1v1 Competitive Practice Server with AGC Anticheat"
            },
            {
                "name": "BlocksMC", 
                "ip": "blocksmc.com", 
                "port": 25565,
                "type": "Cracked & Official", 
                "category": "Competitive", 
                "icon": "🧱",
                "desc": "Classic 1.8.9 Bedwars, EggWars, Skywars & Lucky Blocks"
            },
            {
                "name": "DonutSMP", 
                "ip": "donutsmp.net", 
                "port": 25565,
                "type": "Cracked & Official", 
                "category": "Survival SMP", 
                "icon": "🍩",
                "desc": "Hardcore Lifesteal SMP network with custom economy and raiding"
            },
            {
                "name": "Complex Gaming", 
                "ip": "hub.mc-complex.com", 
                "port": 25565,
                "type": "Official", 
                "category": "Survival SMP", 
                "icon": "💎",
                "desc": "Pixelmon, FTB Modded, Skyblock, Factions & Survival"
            },
            {
                "name": "Herobrine.org", 
                "ip": "herobrine.org", 
                "port": 25565,
                "type": "Cracked & Official", 
                "category": "Survival SMP", 
                "icon": "🔮",
                "desc": "BedWars, SkyWars, Survival, Earth & Factions"
            },
            {
                "name": "Wynncraft", 
                "ip": "play.wynncraft.com", 
                "port": 25565,
                "type": "Official", 
                "category": "Survival SMP", 
                "icon": "🏰",
                "desc": "The largest and most immersive MMORPG in Minecraft"
            },
            {
                "name": "CubeCraft Games", 
                "ip": "play.cubecraft.net", 
                "port": 25565,
                "type": "Official", 
                "category": "Competitive", 
                "icon": "🧊",
                "desc": "EggWars, Skyblock, and custom Parkour challenges"
            }
        ]

        # Trigger live background fetch
        self.refresh_all_servers_async()

    def _read_nbt_tag(self, stream):
        tag_type = stream.read(1)
        if not tag_type or tag_type == b'\x00':
            return 0, '', None
        t_type = ord(tag_type)
        name_len = int.from_bytes(stream.read(2), 'big')
        name = stream.read(name_len).decode('utf-8', errors='ignore')
        val = self._read_nbt_payload(stream, t_type)
        return t_type, name, val

    def _read_nbt_payload(self, stream, t_type):
        if t_type == 1: return int.from_bytes(stream.read(1), 'big', signed=True)
        if t_type == 2: return int.from_bytes(stream.read(2), 'big', signed=True)
        if t_type == 3: return int.from_bytes(stream.read(4), 'big', signed=True)
        if t_type == 4: return int.from_bytes(stream.read(8), 'big', signed=True)
        if t_type == 5: return stream.read(4)
        if t_type == 6: return stream.read(8)
        if t_type == 7:
            length = int.from_bytes(stream.read(4), 'big')
            return stream.read(length)
        if t_type == 8:
            length = int.from_bytes(stream.read(2), 'big')
            return stream.read(length).decode('utf-8', errors='ignore')
        if t_type == 9:
            item_type = ord(stream.read(1))
            length = int.from_bytes(stream.read(4), 'big')
            return [self._read_nbt_payload(stream, item_type) for _ in range(length)]
        if t_type == 10:
            comp = {}
            while True:
                sub_type, sub_name, sub_val = self._read_nbt_tag(stream)
                if sub_type == 0:
                    break
                comp[sub_name] = sub_val
            return comp
        return None

    def parse_servers_dat_file(self, file_path):
        """Parses standard Minecraft servers.dat NBT file."""
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            if not data:
                return []
            if data[:2] == b'\x1f\x8b':
                data = gzip.decompress(data)
            stream = io.BytesIO(data)
            _, _, root = self._read_nbt_tag(stream)
            servers = []
            if isinstance(root, dict) and 'servers' in root:
                for s in root['servers']:
                    if isinstance(s, dict):
                        ip = str(s.get('ip', '')).strip()
                        name = str(s.get('name', 'Minecraft Server')).strip()
                        raw_icon = s.get('icon', '')
                        icon_b64 = f"data:image/png;base64,{raw_icon}" if raw_icon and not raw_icon.startswith("data:") else raw_icon
                        if ip:
                            servers.append({
                                'name': name,
                                'ip': ip,
                                'icon_b64': icon_b64,
                                'icon': '⭐',
                                'type': 'In-Game Saved',
                                'category': 'Saved',
                                'is_saved_server': True,
                                'desc': f"Custom server from in-game multiplayer list: {name}"
                            })
            return servers
        except Exception as e:
            return []

    def get_user_saved_servers(self):
        """Discovers and merges all servers.dat files across instances, Prism, and Minecraft."""
        appdata = os.getenv("APPDATA", "")
        userprofile = os.getenv("USERPROFILE", "")
        candidates = [
            os.path.join(self.root_dir, "instances", "26.2", "minecraft", "servers.dat"),
            os.path.join(self.root_dir, "instances", "1.8.9", "minecraft", "servers.dat"),
            os.path.join(self.root_dir, "SIR Launcher", "instances", "26.2", "minecraft", "servers.dat"),
            os.path.join(appdata, "PrismLauncher", "instances", "26.2", "minecraft", "servers.dat"),
            os.path.join(appdata, "PrismLauncher", "instances", "1.8.9", "minecraft", "servers.dat"),
            os.path.join(appdata, ".minecraft", "servers.dat")
        ]

        # Lunar Client profiles
        lunar_dir = os.path.join(userprofile, ".lunarclient", "profiles")
        if os.path.exists(lunar_dir):
            for d in os.listdir(lunar_dir):
                candidates.append(os.path.join(lunar_dir, d, "servers.dat"))

        seen_ips = set()
        merged = []
        for p in candidates:
            if os.path.exists(p):
                parsed = self.parse_servers_dat_file(p)
                for s in parsed:
                    clean_ip = s['ip'].lower()
                    if clean_ip not in seen_ips:
                        seen_ips.add(clean_ip)
                        merged.append(s)
        return merged

    def ping_single_server_live(self, host, port=25565):
        """Attempts fast TCP socket ping connect."""
        start_time = time.time()
        clean_host = host
        target_port = port
        if ":" in host:
            parts = host.split(":")
            clean_host = parts[0]
            try: target_port = int(parts[1])
            except Exception: pass

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.2)
            sock.connect((clean_host, target_port))
            sock.close()
            elapsed_ms = max(8, int((time.time() - start_time) * 1000))
            return {
                "online": True,
                "latency": elapsed_ms
            }
        except Exception:
            return {
                "online": False,
                "latency": 0
            }

    def fetch_live_mcstatus(self, host):
        """Queries real Minecraft Java status via high-speed API (zero fake numbers)."""
        try:
            req = urllib.request.Request(
                f"https://api.mcstatus.io/v2/status/java/{urllib.parse.quote(host)}",
                headers={"User-Agent": "SIR-Launcher/1.0.0"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    is_online = data.get("online", False)
                    players = data.get("players", {})
                    icon_url = data.get("icon", "")
                    motd_clean = data.get("motd", {}).get("clean", "")
                    ver_clean = data.get("version", {}).get("name_clean", "")
                    
                    return {
                        "online": is_online,
                        "players_online": players.get("online", 0) if is_online else 0,
                        "players_max": players.get("max", 0) if is_online else 0,
                        "icon_url": icon_url,
                        "motd": motd_clean[:90] if motd_clean else "",
                        "version": ver_clean
                    }
        except Exception:
            pass
        return None

    def get_all_servers(self, category="All"):
        """Returns User Saved In-Game Servers FIRST, followed by real Live Public Networks."""
        saved_servers = self.get_user_saved_servers()
        public_servers = self.public_catalog

        all_entries = []

        # 1. Add User Saved Servers at the very top
        for s in saved_servers:
            ip = s["ip"]
            cached = self.cached_results.get(ip, {})
            entry = dict(s)
            entry["online"] = cached.get("online", True)
            entry["latency"] = cached.get("latency", 25)
            entry["players_online"] = cached.get("players_online", 0)
            entry["players_max"] = cached.get("players_max", 0)
            entry["icon_url"] = s.get("icon_b64") or cached.get("icon_url", "")
            entry["motd"] = cached.get("motd") or s["desc"]
            entry["is_saved_server"] = True
            all_entries.append(entry)

        # 2. Add Featured Public Networks underneath (avoiding duplicate IPs)
        seen_ips = {s["ip"].lower() for s in all_entries}
        for s in public_servers:
            if s["ip"].lower() not in seen_ips:
                ip = s["ip"]
                cached = self.cached_results.get(ip, {})
                entry = dict(s)
                entry["online"] = cached.get("online", True)
                entry["latency"] = cached.get("latency", 30)
                entry["players_online"] = cached.get("players_online", 0)
                entry["players_max"] = cached.get("players_max", 0)
                entry["icon_url"] = cached.get("icon_url", "")
                entry["motd"] = cached.get("motd") or s["desc"]
                entry["is_saved_server"] = False
                all_entries.append(entry)

        # Category Filtering
        if category and category != "All":
            cat_clean = category.lower()
            if cat_clean == "saved":
                all_entries = [e for e in all_entries if e.get("is_saved_server")]
            elif cat_clean == "cracked":
                all_entries = [e for e in all_entries if "cracked" in e.get("type", "").lower() or e.get("is_saved_server")]
            else:
                all_entries = [e for e in all_entries if e.get("category", "").lower() == cat_clean or (e.get("is_saved_server") and cat_clean == "saved")]

        return all_entries

    def refresh_all_servers_async(self, callback=None):
        """Asynchronously probes live socket pings and real player counts."""
        def worker():
            saved = self.get_user_saved_servers()
            targets = saved + self.public_catalog
            
            for s in targets:
                ip = s["ip"]
                port = s.get("port", 25565)

                # Real TCP socket ping
                ping_res = self.ping_single_server_live(ip, port)
                
                # Real Minecraft API status query
                api_res = self.fetch_live_mcstatus(ip)

                current = self.cached_results.get(ip, {})
                current["online"] = ping_res.get("online", False) or (api_res.get("online", False) if api_res else False)
                current["latency"] = ping_res.get("latency", 0)
                
                if api_res:
                    current["players_online"] = api_res.get("players_online", 0)
                    current["players_max"] = api_res.get("players_max", 0)
                    if api_res.get("icon_url"):
                        current["icon_url"] = api_res["icon_url"]
                    if api_res.get("motd"):
                        current["motd"] = api_res["motd"]
                
                self.cached_results[ip] = current
                time.sleep(0.08)

            if callback:
                callback(self.get_all_servers())

        threading.Thread(target=worker, daemon=True).start()

    def refresh_live_pings_async(self, callback=None):
        return self.refresh_all_servers_async(callback)
