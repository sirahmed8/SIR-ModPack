import os
import json

mods_dir = r"D:\Projects\SIR ModPack\mods"
manifest_file = r"D:\Projects\SIR ModPack\mods\mod_manifest.json"

categories = {
    "Optimization": ["sodium", "lithium", "ferritecore", "c2me", "immediatelyfast", "badoptimizations", "fastquit", "modernfix", "krypton", "scalablelux", "entityculling", "vmp"],
    "Visuals & Shaders": ["iris", "skinlayers3d", "continuity", "connectedglass", "lambdynamiclights", "visuality", "fallingleaves", "fancy-door-anim", "spawnanimations", "physics-mod"],
    "Audio & Immersion": ["sound-physics-remastered", "ambientsounds", "presencefootsteps", "sounds", "audiothrottle", "voicechat"],
    "Gameplay & Utility": ["bettercombat", "carryon", "comforts", "elevatorid", "fallingtree", "appleskin", "bridgingmod", "chatanimation", "chat_heads", "easyanvils", "easymagic", "farmingforblockheads", "goblintraders", "inventoryhud", "jei", "journeymap", "justzoom", "mouse_tweaks", "naturescompass", "pickupnotifier", "rightclickharvest", "shouldersurfing", "trashcans", "veinminer", "waystones", "zoomify"],
    "World Generation": ["biomesoplenty", "terralith", "better-nether", "structory", "moogs", "towns_and_towers", "worldweaver"],
    "Core & Libraries": ["sir_core", "fabric-api", "cloth-config", "architectury", "fzzy_config", "yacl", "puzzleslib", "supermartijn642corelib", "balm", "iceberg", "collective", "resourcefullib"]
}

mod_list = []
if os.path.exists(mods_dir):
    for f in sorted(os.listdir(mods_dir)):
        if f.endswith(".jar") and not f.endswith(".disabled"):
            f_lower = f.lower()
            cat = "Gameplay & Utility"
            for c_name, keywords in categories.items():
                if any(k in f_lower for k in keywords):
                    cat = c_name
                    break
            
            size_kb = round(os.path.getsize(os.path.join(mods_dir, f)) / 1024, 1)
            mod_list.append({
                "filename": f,
                "name": f.replace(".jar", "").replace("-fabric", "").replace("_mc26.2", ""),
                "category": cat,
                "size_kb": size_kb,
                "status": "active"
            })

manifest = {
    "modpack": "SIR ModPack Ultimate",
    "version": "2.0.0",
    "total_mods": len(mod_list),
    "engine": "Fabric 0.16.10 (Minecraft 1.21.4)",
    "mods": mod_list
}

with open(manifest_file, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print(f"Generated manifest with {len(mod_list)} mods in {manifest_file}")
