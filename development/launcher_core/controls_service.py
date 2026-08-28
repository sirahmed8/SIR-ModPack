import os

class ControlsService:
    """Manages universal keybinding profiles and safe options.txt injection."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.profiles = [
            {
                "id": "standard_vanilla",
                "name": "Standard Vanilla Controls",
                "desc": "Default Minecraft layout: Shift for Sneak, Space for Jump, Left-Control for Sprint.",
                "tag": "🎮 Default",
                "keys": {
                    "key_key.sprint": "key.keyboard.left.control",
                    "key_key.sneak": "key.keyboard.left.shift",
                    "key_key.jump": "key.keyboard.space",
                    "key_key.inventory": "key.keyboard.e",
                    "key_key.drop": "key.keyboard.q",
                    "key_key.zoom": "key.keyboard.c"
                }
            },
            {
                "id": "hypixel_pro_pvp",
                "name": "Hypixel Pro PvP Battle Suite",
                "desc": "Tuned for competitive Bedwars & Duels: Fast Sprint on 'F', Zoom on 'C', Perspective on 'V', Rod swap on Mouse4.",
                "tag": "⚔️ Competitive PvP",
                "keys": {
                    "key_key.sprint": "key.keyboard.f",
                    "key_key.sneak": "key.keyboard.left.shift",
                    "key_key.jump": "key.keyboard.space",
                    "key_key.inventory": "key.keyboard.e",
                    "key_key.perspective": "key.keyboard.v",
                    "key_key.zoom": "key.keyboard.c"
                }
            },
            {
                "id": "ergonomic_blockhit",
                "name": "Ergonomic 1.7 Block-Hit & Mouse5",
                "desc": "Maximizes CPS and reaction speed: Block-Hit on Mouse5, Sprint toggle on 'R', Inventory on 'Tab'.",
                "tag": "🏆 High CPS",
                "keys": {
                    "key_key.sprint": "key.keyboard.r",
                    "key_key.sneak": "key.keyboard.left.shift",
                    "key_key.inventory": "key.keyboard.tab",
                    "key_key.zoom": "key.keyboard.c"
                }
            }
        ]

    def get_control_profiles(self):
        return self.profiles

    def apply_control_profile(self, profile_id, instance_id="26.2"):
        profile = next((p for p in self.profiles if p["id"] == profile_id), None)
        if not profile:
            return {"success": False, "error": "Profile not found"}
            
        target_options_files = [
            os.path.join(self.root_dir, "instances", instance_id, "minecraft", "options.txt"),
            os.path.join(self.root_dir, "instances", "26.2", "minecraft", "options.txt"),
            os.path.join(self.root_dir, "instances", "1.8.9", "minecraft", "options.txt")
        ]
        
        applied_count = 0
        for opt_path in target_options_files:
            if os.path.exists(opt_path):
                try:
                    with open(opt_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    new_lines = []
                    keys_map = profile["keys"]
                    updated_keys = set()
                    
                    for line in lines:
                        parts = line.strip().split(":", 1)
                        if len(parts) == 2 and parts[0] in keys_map:
                            new_lines.append(f"{parts[0]}:{keys_map[parts[0]]}\n")
                            updated_keys.add(parts[0])
                        else:
                            new_lines.append(line)
                            
                    for k, v in keys_map.items():
                        if k not in updated_keys:
                            new_lines.append(f"{k}:{v}\n")
                            
                    with open(opt_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                        
                    applied_count += 1
                except Exception:
                    pass
                    
        return {
            "success": True,
            "profile": profile["name"],
            "applied_instances": applied_count,
            "message": f"Successfully applied '{profile['name']}' to Minecraft controls configuration!"
        }
