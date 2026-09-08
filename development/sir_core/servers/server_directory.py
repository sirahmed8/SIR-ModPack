import urllib.request
import json
from ..config import FIREBASE_RTDB_BASE

DEFAULT_SERVERS = [
    {"id": "hypixel", "name": "Hypixel Network", "ip": "mc.hypixel.net", "category": "Minigames", "tag": "BEDWARS • SKYBLOCK", "color": "#fbbf24", "bg": "#451a03", "desc": "The largest Minecraft minigame network in the world with Bedwars, SkyWars, and SkyBlock.", "version": "1.8.9 - 1.21.x"},
    {"id": "mcc", "name": "MCC Island", "ip": "play.mccisland.net", "category": "Minigames", "tag": "NOXCREW OFFICIAL", "color": "#f43f5e", "bg": "#4c0519", "desc": "Experience official Minecraft Championship minigames including TGTTOS, Battle Box, and Parkour Warrior.", "version": "1.20.x - 1.21.x"},
    {"id": "complex", "name": "Complex Gaming", "ip": "hub.mc-complex.com", "category": "SMP / Survival", "tag": "PIXELMON • SURVIVAL", "color": "#38ef7d", "bg": "#064e3b", "desc": "Massive multiplayer network featuring Pixelmon Reforged, FTB Modpacks, Vanilla Survival, and Skyblock.", "version": "1.12.2 - 1.21.x"},
    {"id": "wynncraft", "name": "Wynncraft MMORPG", "ip": "play.wynncraft.com", "category": "MMORPG", "tag": "OFFICIAL MMORPG", "color": "#00e5ff", "bg": "#083344", "desc": "The biggest Minecraft MMORPG with custom quests, classes, dungeons, bosses, and a gigantic seamless world.", "version": "1.12.2 - 1.21.x"},
    {"id": "enchanted", "name": "EnchantedMC", "ip": "play.enchantedmc.com", "category": "Prison / SkyBlock", "tag": "PRISON • SKYBLOCK", "color": "#a855f7", "bg": "#3b0764", "desc": "Custom OP Prison, Custom Enchants, SkyBlock Economy, and intense PvP tournaments.", "version": "1.8.9 - 1.21.x"},
    {"id": "purpleprison", "name": "Purple Prison", "ip": "purpleprison.net", "category": "Prison / SkyBlock", "tag": "CLASSIC PVP", "color": "#c084fc", "bg": "#2e1065", "desc": "The longest running and most active classic Minecraft prison server with competitive PvP gang wars.", "version": "1.8.9 - 1.21.x"},
    {"id": "donutsmp", "name": "DonutSMP", "ip": "donutsmp.net", "category": "SMP / Survival", "tag": "HARDCORE • LIFESTEAL", "color": "#f97316", "bg": "#431407", "desc": "The most popular Hardcore Minecraft SMP server with Lifesteal, base raiding, and player economy.", "version": "1.19.x - 1.21.x"},
    {"id": "minemen", "name": "Minemen Club", "ip": "na.minemen.club", "category": "PvP / Bedwars", "tag": "COMPETITIVE PRACTICE", "color": "#06b6d4", "bg": "#164e63", "desc": "The premier competitive practice 1.8.9 PvP server featuring ranked duels, custom anti-cheat, and tournaments.", "version": "1.7.x - 1.8.9"},
    {"id": "2b2t", "name": "2b2t Anarchy", "ip": "2b2t.org", "category": "Anarchy", "tag": "OLDEST ANARCHY", "color": "#ef4444", "bg": "#450a0a", "desc": "The oldest anarchy server in Minecraft history with zero rules, complete freedom, and endless griefing lore.", "version": "1.20.x - 1.21.x"},
    {"id": "cubecraft", "name": "CubeCraft Games", "ip": "play.cubecraft.net", "category": "Minigames", "tag": "SKYWARS • EGGWARS", "color": "#3b82f6", "bg": "#172554", "desc": "Legendary minigame network with EggWars, SkyWars, Lucky Islands, and Parkour.", "version": "1.8.9 - 1.21.x"},
    {"id": "pika", "name": "PikaNetwork", "ip": "play.pika-network.net", "category": "PvP / Bedwars", "tag": "BEDWARS • CRACKED", "color": "#10b981", "bg": "#064e3b", "desc": "High-population cracked & premium network featuring BedWars, Practice, SkyWars, and OpFactions.", "version": "1.8.x - 1.21.x"},
    {"id": "jartex", "name": "JartexNetwork", "ip": "top.jartex.fun", "category": "Prison / SkyBlock", "tag": "FACTIONS • PRISON", "color": "#8b5cf6", "bg": "#2e1065", "desc": "Leading international network with Skyblock, OP Prison, Factions, KitPvP, and Lifesteal.", "version": "1.8.x - 1.21.x"}
]

def fetch_remote_servers():
    try:
        url = f"{FIREBASE_RTDB_BASE}/servers/featured.json"
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception:
        pass
    return DEFAULT_SERVERS
