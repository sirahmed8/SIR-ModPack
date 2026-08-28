import os
import json
from ..config import INSTANCES_DIR

MASTER_POSTERS = [
    {"id": "26.2-balanced", "name": "SIR 26 (Tiny Takeover)", "tag_name": "SIR 26", "ver": "26.2", "loader": "Fabric", "desc": "144+ FPS, Crystal Water, Glowing Sun, 3D POM Relief.", "group": "Modern 26", "tag_color": "#ff3b5c", "banner_color": "#450a0a", "artwork": "🔴"},
    {"id": "1.21-trials", "name": "SIR 1.21 (Tricky Trials)", "tag_name": "SIR 1.21", "ver": "1.21.4", "loader": "Fabric", "desc": "Trial Chambers, Mace combat, Breeze encounters, and Wind Charges.", "group": "Modern 1.21", "tag_color": "#fbbf24", "banner_color": "#451a03", "artwork": "⚔️"},
    {"id": "1.8.9-pvp", "name": "SIR 1.8 (Legacy Performance)", "tag_name": "SIR 1.8", "ver": "1.8.9", "loader": "Forge", "desc": "Stripped-down, pure maximum FPS configuration for 1.8.9. All heavy rendering overhead disabled for maximum competitive PvP.", "group": "Legacy 1.8", "tag_color": "#00e5ff", "banner_color": "#083344", "artwork": "🌊"},
    {"id": "1.20-trails", "name": "SIR 1.20 (Trails & Tales)", "tag_name": "SIR 1.20", "ver": "1.20.4", "loader": "Fabric", "desc": "Archaeology, Sniffer, Camel riding, Bamboo wood, and Armor Trims.", "group": "Modern 1.20", "tag_color": "#10b981", "banner_color": "#064e3b", "artwork": "🏺"},
    {"id": "1.19-deepdark", "name": "SIR 1.19 (The Wild Update)", "tag_name": "SIR 1.19", "ver": "1.19.4", "loader": "Fabric", "desc": "Deep Dark, Warden encounters, Allays, Mangrove Swamps, and Froglights.", "group": "Modern 1.19", "tag_color": "#06b6d4", "banner_color": "#083344", "artwork": "🦇"},
    {"id": "1.18-caves", "name": "SIR 1.18 (Caves & Cliffs II)", "tag_name": "SIR 1.18", "ver": "1.18.2", "loader": "Fabric", "desc": "Gigantic 3D cave generation, lush caves, jagged peaks, and new world height.", "group": "Modern 1.18", "tag_color": "#8b5cf6", "banner_color": "#2e1065", "artwork": "🏔️"},
    {"id": "1.17-cliffs", "name": "SIR 1.17 (Caves & Cliffs I)", "tag_name": "SIR 1.17", "ver": "1.17.1", "loader": "Fabric", "desc": "Copper, Amethyst geodes, Axolotls, Glow squid, and tinted glass.", "group": "Modern 1.17", "tag_color": "#ec4899", "banner_color": "#500724", "artwork": "✨"},
    {"id": "1.16-nether", "name": "SIR 1.16 (Nether Update)", "tag_name": "SIR 1.16", "ver": "1.16.5", "loader": "Fabric", "desc": "Complete Nether overhaul: Piglins, Netherite gear, Warped & Crimson forests.", "group": "Modern 1.16", "tag_color": "#f97316", "banner_color": "#431407", "artwork": "🔥"},
    {"id": "1.12-color", "name": "SIR 1.12 (World of Color)", "tag_name": "SIR 1.12", "ver": "1.12.2", "loader": "Forge", "desc": "The golden era of massive technical Forge modpacks and concrete builds.", "group": "Legacy 1.12", "tag_color": "#eab308", "banner_color": "#422006", "artwork": "🎨"},
    {"id": "1.7-classic", "name": "SIR 1.7 (The Update That Changed)", "tag_name": "SIR 1.7", "ver": "1.7.10", "loader": "Forge", "desc": "Legendary classic Minecraft with beloved legacy combat and mods.", "group": "Legacy 1.7", "tag_color": "#64748b", "banner_color": "#0f172a", "artwork": "📜"}
]

def scan_instances():
    insts = []
    os.makedirs(INSTANCES_DIR, exist_ok=True)
    for p in MASTER_POSTERS:
        inst_path = os.path.join(INSTANCES_DIR, p["id"])
        is_inst = os.path.exists(inst_path)
        insts.append({
            "id": p["id"],
            "name": p["name"],
            "tag_name": p["tag_name"],
            "version": p["ver"],
            "loader": p["loader"],
            "desc": p["desc"],
            "group": p["group"],
            "tag_color": p["tag_color"],
            "banner_color": p["banner_color"],
            "artwork": p["artwork"],
            "installed": is_inst,
            "path": inst_path
        })
    return insts

def create_instance(name, version="26.2", loader="Fabric", group="Modern"):
    safe_id = name.lower().replace(" ", "-")
    inst_path = os.path.join(INSTANCES_DIR, safe_id)
    os.makedirs(os.path.join(inst_path, "minecraft", "mods"), exist_ok=True)
    cfg_path = os.path.join(inst_path, "instance.cfg")
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write(f"name={name}\nIntendedVersion={version}\n")
    return safe_id
