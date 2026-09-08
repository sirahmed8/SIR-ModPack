import os
import glob
import json
from shared_core.runtime import atomic_write_text

class PacksService:

    """Manages resource packs, 3D texture packs, and safe options.txt resourcePacks injection."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def get_resource_packs(self, instance_id="26.2"):
        packs = []
        packs_dirs = [
            os.path.join(self.root_dir, "resourcepacks"),
            os.path.join(self.root_dir, "instances", instance_id, "minecraft", "resourcepacks"),
            os.path.join(self.root_dir, "instances", "26.2", "minecraft", "resourcepacks"),
            os.path.join(self.root_dir, "instances", "1.8.9", "minecraft", "resourcepacks")
        ]
        
        # Read active packs from options.txt
        active_packs = set()
        opt_path = os.path.join(self.root_dir, "instances", instance_id, "minecraft", "options.txt")
        if not os.path.exists(opt_path):
            opt_path = os.path.join(self.root_dir, "instances", "26.2", "minecraft", "options.txt")
            
        if os.path.exists(opt_path):
            try:
                with open(opt_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("resourcePacks:"):
                            val = line.split(":", 1)[1].strip()
                            try:
                                loaded = json.loads(val)
                                for item in loaded:
                                    # Normalize "file/PackName.zip" -> "PackName.zip"
                                    clean = item.replace("file/", "")
                                    active_packs.add(clean)
                            except Exception:
                                pass
            except Exception:
                pass
                
        # Scan zip and folder packs
        found_packs = []
        for p_dir in packs_dirs:
            if os.path.exists(p_dir):
                for f in os.listdir(p_dir):
                    if f.endswith(".zip") or os.path.isdir(os.path.join(p_dir, f)):
                        found_packs.append((f, os.path.join(p_dir, f)))
                        
        seen = set()
        active_found = False
        
        # 1. Determine the single primary active pack
        primary_active_filename = None
        for filename, _ in found_packs:
            if filename in active_packs:
                primary_active_filename = filename
                break
        if not primary_active_filename and found_packs:
            # Default to SIR Modern if present, else first pack
            for filename, _ in found_packs:
                if "Modern" in filename or "Ultimate" in filename:
                    primary_active_filename = filename
                    break
            if not primary_active_filename:
                primary_active_filename = found_packs[0][0]

        for filename, filepath in found_packs:
            if filename not in seen:
                seen.add(filename)
                is_active = (filename == primary_active_filename)
                size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 1) if os.path.isfile(filepath) else 12.0
                
                tag = "✨ 3D POM Master" if ("Modern" in filename or "Ultimate" in filename) else ("⚔️ 32x PvP Faithful" if "Legacy" in filename else "📦 Resource Pack")
                desc = "3D Parallax Occlusion Mapping, Fresh Animations, and emissive block textures." if ("Modern" in filename or "Ultimate" in filename) else "Crisp 32x low-fire PvP textures with clear glass and armor status."
                
                packs.append({
                    "filename": filename,
                    "name": filename.replace(".zip", "").replace("_", " "),
                    "size_mb": size_mb,
                    "enabled": is_active,
                    "tag": tag,
                    "desc": desc
                })
                
        if not packs:
            packs = [
                {
                    "filename": "SIR Modern.zip",
                    "name": "SIR Modern 3D Master Pack",
                    "size_mb": 151.8,
                    "enabled": True,
                    "tag": "✨ 3D POM Master",
                    "desc": "Ultra-HD 3D Parallax Occlusion Mapping textures, Fresh Animations & Emissive mobs."
                },
                {
                    "filename": "SIR Legacy.zip",
                    "name": "SIR Legacy 32x PvP Faithful",
                    "size_mb": 37.5,
                    "enabled": False,
                    "tag": "⚔️ 32x PvP Faithful",
                    "desc": "Crisp 32x low-fire PvP textures with clear glass and high visibility swords."
                }
            ]
            
        return packs

    def toggle_pack(self, pack_filename, enabled_state, instance_id="26.2"):
        pack_entry = f"file/{pack_filename}"
        current_list = [pack_entry, "vanilla"] if enabled_state else ["vanilla"]

        inst_root = os.path.join(self.root_dir, "instances", instance_id)
        if os.path.isdir(os.path.join(inst_root, "minecraft")):
            primary_opt_path = os.path.join(inst_root, "minecraft", "options.txt")
        else:
            primary_opt_path = os.path.join(inst_root, "options.txt")

        if not os.path.exists(primary_opt_path):
            os.makedirs(os.path.dirname(primary_opt_path), exist_ok=True)
            atomic_write_text(primary_opt_path, f"resourcePacks:{json.dumps(current_list)}\n")

        opt_paths = [
            primary_opt_path,
            os.path.join(self.root_dir, "instances", "26.2-ultra", "minecraft", "options.txt"),
            os.path.join(self.root_dir, "instances", "1.8.9-ultra", "minecraft", "options.txt")
        ]
        
        seen_paths = set()
        for opt_path in opt_paths:
            if opt_path in seen_paths:
                continue
            seen_paths.add(opt_path)
            if os.path.exists(opt_path):
                try:
                    with open(opt_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    new_lines = []
                    found_rp = False

                    for line in lines:
                        if line.startswith("resourcePacks:"):
                            found_rp = True
                            new_lines.append(f"resourcePacks:{json.dumps(current_list)}\n")
                        else:
                            new_lines.append(line)
                            
                    if not found_rp:
                        new_lines.append(f"resourcePacks:{json.dumps(current_list)}\n")
                        
                    atomic_write_text(opt_path, "".join(new_lines))

                except Exception:
                    pass
                    
        return {
            "success": True,
            "filename": pack_filename,
            "enabled": enabled_state,
            "message": f"✓ {'Activated' if enabled_state else 'Deactivated'} {pack_filename} in resource pack order!"
        }

    def open_packs_folder(self, instance_id="26.2"):
        p_dir = os.path.join(self.root_dir, "instances", instance_id, "minecraft", "resourcepacks")
        if not os.path.exists(p_dir):
            p_dir = os.path.join(self.root_dir, "resourcepacks")
        os.makedirs(p_dir, exist_ok=True)
        try:
            os.startfile(p_dir)
            return {"success": True, "path": p_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}

