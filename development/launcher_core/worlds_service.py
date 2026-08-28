import os
import time
import zipfile
import shutil
import base64

class WorldsService:
    """Manages real Minecraft singleplayer world saves, base64 thumbnails, backups, and folder operations."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.backups_dir = os.path.join(self.root_dir, "backups")
        os.makedirs(self.backups_dir, exist_ok=True)

    def _get_all_saves_directories(self, instance_id="26.2"):
        """Collects all possible real saves directories across Minecraft, Prism, and local instances."""
        dirs = [
            os.path.expandvars(r"%APPDATA%\.minecraft\saves"),
            os.path.expandvars(rf"%APPDATA%\PrismLauncher\instances\{instance_id}\minecraft\saves"),
            os.path.expandvars(r"%APPDATA%\PrismLauncher\instances\26.2\minecraft\saves"),
            os.path.expandvars(r"%APPDATA%\PrismLauncher\instances\1.8.9\minecraft\saves"),
            os.path.join(self.root_dir, "instances", str(instance_id), "minecraft", "saves"),
            os.path.join(self.root_dir, "instances", "26.2", "minecraft", "saves"),
            os.path.join(self.root_dir, "instances", "1.8.9", "minecraft", "saves"),
            os.path.join(self.root_dir, "saves"),
            os.path.join(self.root_dir, "SIR Launcher", "saves"),
            os.path.join(self.root_dir, "SIR Package", "saves")
        ]
        return [d for d in dirs if os.path.exists(d)]

    def get_worlds(self, instance_id="26.2"):
        """Detects only real physical worlds on the filesystem with valid level.dat files."""
        worlds = []
        saves_dirs = self._get_all_saves_directories(instance_id)
        seen_paths = set()

        for s_dir in saves_dirs:
            try:
                for item in os.listdir(s_dir):
                    w_path = os.path.join(s_dir, item)
                    if os.path.isdir(w_path) and w_path not in seen_paths:
                        level_dat = os.path.join(w_path, "level.dat")
                        if not os.path.exists(level_dat):
                            continue

                        seen_paths.add(w_path)
                        try:
                            # Calculate real folder size
                            total_bytes = 0
                            for root, _, files in os.walk(w_path):
                                for f in files:
                                    fp = os.path.join(root, f)
                                    if os.path.isfile(fp):
                                        total_bytes += os.path.getsize(fp)
                                        
                            size_mb = round(total_bytes / (1024 * 1024), 2)
                            mtime = os.path.getmtime(w_path)
                            mtime_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
                            
                            # Real icon extraction
                            icon_path = os.path.join(w_path, "icon.png")
                            icon_b64 = None
                            if os.path.exists(icon_path):
                                try:
                                    with open(icon_path, "rb") as img_f:
                                        icon_b64 = "data:image/png;base64," + base64.b64encode(img_f.read()).decode('utf-8')
                                except Exception:
                                    pass

                            worlds.append({
                                "folder_name": item,
                                "name": item.replace("_", " ").title(),
                                "path": w_path,
                                "size_mb": size_mb,
                                "last_played": mtime_str,
                                "game_mode": "Singleplayer World",
                                "has_icon": bool(icon_b64),
                                "icon_url": icon_b64,
                                "is_real": True
                            })
                        except Exception:
                            pass
            except Exception:
                pass
                            
        # Strictly return real detected worlds (no fake templates)
        return sorted(worlds, key=lambda x: x["last_played"], reverse=True)

    def create_world_backup(self, world_folder_or_path, instance_id="26.2"):
        """Creates a timestamped .zip backup of the real world directory."""
        w_path = world_folder_or_path
        if not os.path.exists(w_path):
            # Try to resolve in saves dirs
            for s_dir in self._get_all_saves_directories(instance_id):
                cand = os.path.join(s_dir, world_folder_or_path)
                if os.path.exists(cand):
                    w_path = cand
                    break
            
        if not os.path.exists(w_path):
            return {"success": False, "error": f"World folder not found: {world_folder_or_path}"}

        folder_name = os.path.basename(w_path)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{folder_name}_backup_{timestamp}.zip"
        backup_dest = os.path.join(self.backups_dir, backup_filename)
        
        try:
            with zipfile.ZipFile(backup_dest, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(w_path):
                    for f in files:
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, w_path)
                        zf.write(full_p, rel_p)
                        
            return {
                "success": True,
                "backup_file": backup_filename,
                "backup_path": backup_dest,
                "size_mb": round(os.path.getsize(backup_dest) / (1024 * 1024), 2),
                "message": f"✓ World backup successfully saved to {backup_filename}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_world_folder(self, world_folder_or_path, instance_id="26.2"):
        """Reveals the real world directory in Windows File Explorer."""
        w_path = world_folder_or_path
        if not os.path.exists(w_path):
            for s_dir in self._get_all_saves_directories(instance_id):
                cand = os.path.join(s_dir, world_folder_or_path)
                if os.path.exists(cand):
                    w_path = cand
                    break

        if not os.path.exists(w_path):
            saves = self._get_all_saves_directories(instance_id)
            if saves:
                w_path = saves[0]

        if os.path.exists(w_path):
            try:
                os.startfile(w_path)
                return {"success": True, "path": w_path}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "Folder not found"}
