import os
import sys
import json
import zipfile
import re

class ModsService:
    """Manages real filesystem mod detection, JAR metadata extraction, and live toggle states."""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.instances_dir = os.path.join(self.root_dir, "instances")
        self._cache = {}

    def _resolve_mods_dir(self, instance_id="26.2"):
        """Resolves the physical mods folder path on disk for any modern, legacy, or custom instance."""
        target_dir = str(instance_id).strip()
        candidates = []

        # 1. Direct instance path
        custom_inst_mods = os.path.join(self.instances_dir, target_dir, "minecraft", "mods")
        if os.path.isdir(custom_inst_mods):
            return custom_inst_mods

        if "1.8.9" in target_dir or "189" in target_dir:
            candidates.extend([
                os.path.join(self.instances_dir, "1.8.9", "minecraft", "mods"),
                os.path.join(self.root_dir, "instances", "1.8.9", "minecraft", "mods"),
                os.path.join(self.root_dir, "SIR Package", "instances", "1.8.9", "minecraft", "mods"),
                os.path.join(self.root_dir, "SIR Launcher", "instances", "1.8.9", "minecraft", "mods"),
            ])
        else:
            candidates.extend([
                os.path.join(self.instances_dir, "26.2", "minecraft", "mods"),
                os.path.join(self.root_dir, "mods"),
                os.path.join(self.root_dir, "instances", "26.2", "minecraft", "mods"),
                os.path.join(self.root_dir, "SIR Package", "mods"),
                os.path.join(self.root_dir, "SIR Launcher", "mods"),
            ])

        for c in candidates:
            if os.path.exists(c):
                return c
        
        fallback = os.path.join(self.root_dir, "mods")
        os.makedirs(fallback, exist_ok=True)
        return fallback

    def _parse_mod_jar(self, jar_path):
        """Extracts real metadata from fabric.mod.json, mcmod.info, or mods.toml."""
        fn = os.path.basename(jar_path)
        is_disabled = fn.endswith(".disabled")
        clean_name = fn.replace(".jar.disabled", "").replace(".jar", "")
        
        # Format human readable default name
        readable_name = re.sub(r'[-_](fabric|forge|neoforge|quilt|mc\d+[\.\d]*|\d+[\.\d]*).*$', '', clean_name, flags=re.IGNORECASE)
        readable_name = readable_name.replace("-", " ").replace("_", " ").strip().title()
        if not readable_name:
            readable_name = clean_name

        mod_info = {
            "id": clean_name.lower(),
            "filename": fn,
            "name": readable_name,
            "version": "1.0.0",
            "desc": "High-performance ecosystem modification module.",
            "category": "Utility",
            "enabled": not is_disabled
        }

        try:
            with zipfile.ZipFile(jar_path, 'r') as z:
                names = z.namelist()
                if 'fabric.mod.json' in names:
                    data = json.loads(z.read('fabric.mod.json').decode('utf-8', errors='ignore'))
                    mod_info['id'] = data.get('id', mod_info['id'])
                    mod_info['name'] = data.get('name', mod_info['name'])
                    mod_info['version'] = str(data.get('version', mod_info['version']))
                    desc = data.get('description', '')
                    if desc:
                        mod_info['desc'] = str(desc).strip()
                elif 'mcmod.info' in names:
                    raw = z.read('mcmod.info').decode('utf-8', errors='ignore').strip()
                    try:
                        data = json.loads(raw)
                        if isinstance(data, list) and len(data) > 0:
                            data = data[0]
                        elif isinstance(data, dict) and 'modList' in data and len(data['modList']) > 0:
                            data = data['modList'][0]
                        if isinstance(data, dict):
                            mod_info['id'] = data.get('modid', mod_info['id'])
                            mod_info['name'] = data.get('name', mod_info['name'])
                            mod_info['version'] = str(data.get('version', mod_info['version']))
                            desc = data.get('description', '')
                            if desc:
                                mod_info['desc'] = str(desc).strip()
                    except Exception:
                        pass
        except Exception:
            pass

        # Smart Categorization Engine
        combined_text = f"{mod_info['name']} {mod_info['desc']} {fn}".lower()
        if any(k in combined_text for k in ['sodium', 'iris', 'lithium', 'ferritecore', 'optimize', 'fps', 'culling', 'performance', 'fast', 'smooth', 'memory', 'cpu', 'speed', 'engine', 'krypton', 'canary', 'lazydfu', 'immediatelyfast', 'modernfix', 'optifine']):
            mod_info['category'] = 'Performance'
        elif any(k in combined_text for k in ['shader', 'pom', 'texture', 'model', 'visual', 'sky', 'light', 'render', 'animation', 'emissive', 'continuity', 'emf', 'etf', 'skin', 'cape', 'heart']):
            mod_info['category'] = 'Visuals'
        elif any(k in combined_text for k in ['pvp', 'cps', 'keystroke', 'armor', 'hud', 'sword', 'hit', 'combat', 'crosshair', 'ias', 'account', 'blockhit']):
            mod_info['category'] = 'PvP'
        elif any(k in combined_text for k in ['sound', 'audio', 'footstep', 'music', 'reverb', 'acoustic', 'voice', 'presence']):
            mod_info['category'] = 'Audio'
        else:
            mod_info['category'] = 'Utility'

        return mod_info

    def get_mods_for_instance(self, instance_dir="26.2", search_query="", category="All"):
        """Scans the live physical filesystem for all .jar and .jar.disabled mods."""
        mods_dir = self._resolve_mods_dir(instance_dir)
        if not os.path.exists(mods_dir):
            return []

        try:
            entries = os.listdir(mods_dir)
        except Exception:
            return []

        mod_files = [f for f in entries if f.endswith(".jar") or f.endswith(".jar.disabled")]
        
        # Build live list
        mods = []
        for fn in sorted(mod_files, key=lambda x: x.lower()):
            full_p = os.path.join(mods_dir, fn)
            mtime = os.path.getmtime(full_p)
            cache_key = f"{full_p}_{mtime}"
            
            if cache_key in self._cache:
                mod_info = self._cache[cache_key]
            else:
                mod_info = self._parse_mod_jar(full_p)
                self._cache[cache_key] = mod_info
            
            mods.append(mod_info)

        # Apply category and search filters
        if category and category != "All":
            mods = [m for m in mods if m["category"].lower() == category.lower()]
        
        if search_query:
            q = search_query.lower()
            mods = [m for m in mods if q in m["name"].lower() or q in m["desc"].lower() or q in m["category"].lower() or q in m["filename"].lower()]

        return mods

    def toggle_mod(self, filename, enabled_state, instance_dir="26.2"):
        """Physically renames the mod file on disk (.jar <-> .jar.disabled)."""
        mods_dir = self._resolve_mods_dir(instance_dir)
        if not os.path.exists(mods_dir):
            return {"success": False, "error": "Mods folder not found"}

        target_enabled = bool(enabled_state)
        current_fn = filename
        
        # Check current file
        full_current = os.path.join(mods_dir, current_fn)
        if not os.path.exists(full_current):
            # Try alternate extension
            if current_fn.endswith(".disabled") and os.path.exists(full_current[:-9]):
                full_current = full_current[:-9]
                current_fn = os.path.basename(full_current)
            elif not current_fn.endswith(".disabled") and os.path.exists(full_current + ".disabled"):
                full_current = full_current + ".disabled"
                current_fn = os.path.basename(full_current)

        if not os.path.exists(full_current):
            return {"success": False, "error": f"File not found: {filename}"}

        if target_enabled:
            # Enable -> remove .disabled
            if current_fn.endswith(".disabled"):
                new_fn = current_fn[:-9]
                new_full = os.path.join(mods_dir, new_fn)
                try:
                    os.rename(full_current, new_full)
                    self._cache.clear()
                    return {"success": True, "enabled": True, "filename": new_fn}
                except Exception as ex:
                    return {"success": False, "error": str(ex)}
            return {"success": True, "enabled": True, "filename": current_fn}
        else:
            # Disable -> append .disabled
            if not current_fn.endswith(".disabled"):
                new_fn = current_fn + ".disabled"
                new_full = os.path.join(mods_dir, new_fn)
                try:
                    os.rename(full_current, new_full)
                    self._cache.clear()
                    return {"success": True, "enabled": False, "filename": new_fn}
                except Exception as ex:
                    return {"success": False, "error": str(ex)}
            return {"success": True, "enabled": False, "filename": current_fn}
