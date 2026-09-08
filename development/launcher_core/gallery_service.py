import os
import glob
import time
import base64

class GalleryService:
    """Manages real in-game screenshots, base64 thumbnails, wallpaper setting, and file operations."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def _get_search_paths(self, instance_id="26.2"):
        inst_dir_name = "1.8.9" if "189" in str(instance_id) or "1.8.9" in str(instance_id) else "26.2"
        appdata = os.getenv("APPDATA", "")
        paths = [
            os.path.join(self.root_dir, "instances", inst_dir_name, "minecraft", "screenshots"),
            os.path.join(self.root_dir, "instances", str(instance_id), "minecraft", "screenshots"),
            os.path.join(self.root_dir, "SIR Launcher", "instances", inst_dir_name, "minecraft", "screenshots"),
            os.path.join(appdata, "PrismLauncher", "instances", inst_dir_name, "minecraft", "screenshots"),
            os.path.join(appdata, "PrismLauncher", "instances", str(instance_id), "minecraft", "screenshots"),
            os.path.join(self.root_dir, "screenshots")
        ]
        return [p for p in paths if os.path.exists(p)]

    def get_screenshots(self, instance_id="26.2", limit=30):
        """Scans filesystem for real in-game screenshots captured by the user."""
        search_paths = self._get_search_paths(instance_id)
        
        found_files = []
        for p in search_paths:
            for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                found_files.extend(glob.glob(os.path.join(p, ext)))
        
        # Deduplicate files by filename
        seen_names = set()
        unique_files = []
        for fp in found_files:
            fname = os.path.basename(fp)
            if fname not in seen_names:
                seen_names.add(fname)
                unique_files.append(fp)
        
        # Sort by modification time descending (newest first)
        unique_files.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        
        screenshots = []
        for fp in unique_files[:limit]:
            try:
                stat = os.stat(fp)
                size_kb = round(stat.st_size / 1024, 1)
                mtime_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                filename = os.path.basename(fp)
                
                # Generate fast base64 data URL for instant display
                b64_str = ""
                try:
                    with open(fp, "rb") as f:
                        ext_type = "jpeg" if fp.lower().endswith((".jpg", ".jpeg")) else "png"
                        b64_str = f"data:image/{ext_type};base64," + base64.b64encode(f.read()).decode('utf-8')
                except Exception:
                    b64_str = f"file:///{fp.replace(os.sep, '/')}"

                screenshots.append({
                    "path": fp,
                    "filename": filename,
                    "size_kb": size_kb,
                    "date": mtime_str,
                    "preview_url": b64_str,
                    "is_local": True
                })
            except Exception:
                pass
                
        # Strictly return real detected screenshots (no fake mock entries)
        return screenshots

    def delete_screenshot(self, filepath):
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return {"success": True, "message": "Screenshot deleted successfully"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "File not found"}

    def open_screenshots_folder(self, instance_id="26.2"):
        """Opens the active screenshots directory in Windows File Explorer."""
        search_paths = self._get_search_paths(instance_id)
        target_dir = search_paths[0] if search_paths else os.path.expandvars(r"%APPDATA%\.minecraft\screenshots")
        os.makedirs(target_dir, exist_ok=True)
        
        try:
            os.startfile(target_dir)
            return {"success": True, "path": target_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}

