import os
import sys
import json
import zipfile
import re
import base64
import shutil
import tempfile
from .auto_remapper_service import AutoRemapperService

class ModsService:
    """Manages real filesystem mod detection, JAR metadata extraction, and live toggle states."""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.instances_dir = os.path.join(self.root_dir, "instances")
        self._cache = {}
        self.mods_cache_file = os.path.join(self.root_dir, "cache", "mods_cache.json")
        self.metadata_cache_file = os.path.join(self.root_dir, "cache", "mod_metadata.json")
        self._online_metadata = {}
        self._load_online_metadata()
        self._load_mods_cache()

    def _load_mods_cache(self):
        try:
            if os.path.exists(self.mods_cache_file):
                with open(self.mods_cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
        except Exception:
            self._cache = {}

    def _save_mods_cache(self):
        try:
            os.makedirs(os.path.dirname(self.mods_cache_file), exist_ok=True)
            with open(self.mods_cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass

    def _load_online_metadata(self):
        try:
            if os.path.exists(self.metadata_cache_file):
                with open(self.metadata_cache_file, "r", encoding="utf-8") as f:
                    self._online_metadata = json.load(f)
        except Exception:
            self._online_metadata = {}

    def _save_online_metadata(self):
        try:
            os.makedirs(os.path.dirname(self.metadata_cache_file), exist_ok=True)
            with open(self.metadata_cache_file, "w", encoding="utf-8") as f:
                json.dump(self._online_metadata, f, indent=2)
        except Exception:
            pass

    def _start_background_enrichment(self, mods):
        import threading
        def _worker():
            updated = False
            for m in mods:
                mid = m.get("id", "")
                name = m.get("name", "")
                if not m.get("icon_url") or not m.get("author") or m.get("desc") == "High-performance ecosystem modification module.":
                    if mid not in self._online_metadata:
                        meta = self._fetch_online_metadata(name, mid)
                        if meta.get("icon_url") or meta.get("author") or meta.get("summary"):
                            updated = True
                            if meta.get("icon_url") and not m.get("icon_url"):
                                m["icon_url"] = meta["icon_url"]
                            if meta.get("author") and not m.get("author"):
                                m["author"] = meta["author"]
                            if meta.get("summary"):
                                m["desc"] = meta["summary"]
            if updated:
                self._save_online_metadata()
                self._save_mods_cache()
        threading.Thread(target=_worker, daemon=True).start()

    def _fetch_online_metadata(self, clean_name, mod_id=""):
        key = (mod_id or clean_name).lower().strip()
        if key in self._online_metadata:
            return self._online_metadata[key]

        meta = {"icon_url": "", "author": "", "summary": ""}
        import urllib.request
        import urllib.parse
        search_term = key.replace("-fabric", "").replace("-forge", "").replace("-", " ")
        try:
            url = f"https://api.modrinth.com/v2/search?query={urllib.parse.quote(search_term)}&limit=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'SIR-ModPack/1.0.0 (a7medorabe7@gmail.com)'})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    hits = data.get('hits', [])
                    if hits and len(hits) > 0:
                        first = hits[0]
                        meta["icon_url"] = first.get("icon_url", "")
                        meta["author"] = first.get("author", "")
                        meta["summary"] = first.get("description", "")
        except Exception:
            pass

        self._online_metadata[key] = meta
        self._save_online_metadata()
        return meta

    def _resolve_mods_dir(self, instance_id="26.2-ultra"):
        """Resolves the physical mods folder path on disk for any modern, legacy, or custom instance."""
        target_dir = str(instance_id).strip()
        if not target_dir:
            target_dir = "26.2-ultra"

        candidates = []
        # Direct paths for the targeted profile
        candidates.append(os.path.join(self.instances_dir, target_dir, "mods"))
        candidates.append(os.path.join(self.instances_dir, target_dir, "minecraft", "mods"))

        if "1.8.9" in target_dir or "189" in target_dir:
            candidates.extend([
                os.path.join(self.instances_dir, "1.8.9-ultra", "minecraft", "mods"),
                os.path.join(self.instances_dir, "1.8.9-ultra", "mods"),
                os.path.join(self.instances_dir, "1.8.9", "mods"),
                os.path.join(self.instances_dir, "1.8.9", "minecraft", "mods"),
                os.path.join(self.root_dir, "instances", "1.8.9-ultra", "minecraft", "mods"),
                os.path.join(self.root_dir, "SIR Package", "instances", "1.8.9-ultra", "minecraft", "mods"),
            ])
        else:
            candidates.extend([
                os.path.join(self.instances_dir, "26.2-ultra", "mods"),
                os.path.join(self.instances_dir, "26.2-ultra", "minecraft", "mods"),
                os.path.join(self.instances_dir, "26.2", "mods"),
                os.path.join(self.instances_dir, "26.2", "minecraft", "mods"),
                os.path.join(self.root_dir, "mods"),
                os.path.join(self.root_dir, "instances", "26.2-ultra", "mods"),
                os.path.join(self.root_dir, "SIR Package", "mods"),
            ])

        # Prioritize candidates that contain active .jar or .jar.disabled files
        for c in candidates:
            if os.path.isdir(c):
                try:
                    jar_files = [f for f in os.listdir(c) if f.endswith(".jar") or f.endswith(".jar.disabled")]
                    if len(jar_files) > 0:
                        return c
                except Exception:
                    pass

        # Fallback to first existing candidate
        for c in candidates:
            if os.path.isdir(c):
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
                    depends_map = data.get('depends', {})
                    reqs = []
                    if isinstance(depends_map, dict):
                        for dep_id, ver in depends_map.items():
                            if dep_id not in ('minecraft', 'fabricloader', 'java', 'fabric-loader', 'fabric'):
                                reqs.append({'id': str(dep_id), 'version': str(ver)})
                    mod_info['dependencies'] = reqs
                    # Check for embedded icon
                    if 'icon' in data and data['icon']:
                        icon_p = data['icon']
                        if icon_p in names:
                            try:
                                img_data = z.read(icon_p)
                                mod_info['icon_url'] = f"data:image/png;base64,{base64.b64encode(img_data).decode('ascii')}"
                            except Exception:
                                pass
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

        # Apply online metadata if available
        if mod_info['id'] in self._online_metadata:
            meta = self._online_metadata[mod_info['id']]
            if not mod_info.get('icon_url') and meta.get('icon_url'):
                mod_info['icon_url'] = meta['icon_url']
            if meta.get('author'):
                mod_info['author'] = meta['author']
            if meta.get('summary') and (not mod_info.get('desc') or mod_info['desc'] == "High-performance ecosystem modification module."):
                mod_info['desc'] = meta['summary']

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

    def get_mods_for_instance(self, instance_dir="26.2-ultra", search_query="", category="All"):
        """Scans the live physical filesystem for all .jar and .jar.disabled mods."""
        # Pure Vanilla profiles contain zero mods
        if str(instance_dir).lower() == "vanilla" or (str(instance_dir).lower().endswith("vanilla") and "26.2" not in str(instance_dir)):
            return []

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
        cache_updated = False
        for fn in sorted(mod_files, key=lambda x: x.lower()):
            full_p = os.path.join(mods_dir, fn)
            try:
                mtime = os.path.getmtime(full_p)
            except Exception:
                mtime = 0
            cache_key = f"{full_p}_{mtime}"
            
            if cache_key in self._cache:
                mod_info = self._cache[cache_key]
            else:
                mod_info = self._parse_mod_jar(full_p)
                self._cache[cache_key] = mod_info
                cache_updated = True
            
            mods.append(mod_info)

        if cache_updated:
            self._save_mods_cache()

        # Trigger background enrichment asynchronously (does not block)
        self._start_background_enrichment(mods)

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

    def check_mod_dependencies(self, filename, instance_dir="26.2"):
        """Checks if a mod has unfulfilled or disabled dependencies in the target instance."""
        mods_dir = self._resolve_mods_dir(instance_dir)
        full_p = os.path.join(mods_dir, filename)
        if not os.path.exists(full_p):
            if os.path.exists(full_p + ".disabled"):
                full_p = full_p + ".disabled"
            elif filename.endswith(".disabled") and os.path.exists(full_p[:-9]):
                full_p = full_p[:-9]

        if not os.path.exists(full_p):
            return {"has_missing": False, "missing": []}

        mod_info = self._parse_mod_jar(full_p)
        reqs = mod_info.get("dependencies", [])
        if not reqs:
            return {"has_missing": False, "missing": []}

        installed_mods = self.get_mods_for_instance(instance_dir)
        installed_ids = {m["id"].lower(): m for m in installed_mods if m.get("enabled")}
        disabled_ids = {m["id"].lower(): m for m in installed_mods if not m.get("enabled")}

        missing = []
        for r in reqs:
            dep_id = r["id"].lower()
            if dep_id in installed_ids or dep_id in ("fabric-api", "fabric"):
                continue
            if dep_id in disabled_ids:
                missing.append({"id": dep_id, "action": "enable", "filename": disabled_ids[dep_id]["filename"], "name": disabled_ids[dep_id]["name"]})
            else:
                missing.append({"id": dep_id, "action": "download", "name": r["id"].replace("-", " ").title()})

        return {
            "has_missing": len(missing) > 0,
            "mod_name": mod_info["name"],
            "missing": missing
        }

    def resolve_and_install_dependencies(self, missing_list, instance_dir="26.2"):
        """Enables disabled dependencies or auto-copies missing dependencies from ecosystem repository."""
        import shutil
        mods_dir = self._resolve_mods_dir(instance_dir)
        results = []
        for item in missing_list:
            act = item.get("action")
            if act == "enable" and item.get("filename"):
                fn = item["filename"]
                self.toggle_mod(fn, True, instance_dir)
                results.append({"id": item.get("id"), "status": "enabled"})
            elif act == "download":
                dep_id = item.get("id", "").lower()
                found_src = None
                for root_c in [self.root_dir, os.path.join(self.root_dir, "mods"), os.path.join(self.instances_dir, "26.2", "minecraft", "mods")]:
                    if os.path.isdir(root_c):
                        for jf in os.listdir(root_c):
                            if jf.endswith(".jar") and dep_id in jf.lower():
                                found_src = os.path.join(root_c, jf)
                                break
                    if found_src:
                        break
                if found_src:
                    shutil.copy2(found_src, os.path.join(mods_dir, os.path.basename(found_src)))
                    results.append({"id": dep_id, "status": "installed_local"})
                else:
                    results.append({"id": dep_id, "status": "unavailable"})
        self._cache.clear()
        return {"success": True, "results": results}

    def install_dropped_mod(self, file_path_or_data: str, filename: str, instance_dir: str = "26.2") -> dict:
        """Installs a dropped third-party JAR with automated 5-pass ASM remapping and signature stripping."""
        if not filename or not filename.lower().endswith(".jar"):
            return {"success": False, "error": "Invalid mod file: Must have a .jar extension"}

        mods_dir = self._resolve_mods_dir(instance_dir)
        os.makedirs(mods_dir, exist_ok=True)
        dest_path = os.path.join(mods_dir, filename)

        temp_fd, temp_path = tempfile.mkstemp(suffix=".jar")
        os.close(temp_fd)

        try:
            # 1. Write incoming file data to temp path
            if os.path.isfile(file_path_or_data):
                shutil.copy2(file_path_or_data, temp_path)
            elif file_path_or_data.startswith("data:") or len(file_path_or_data) > 100:
                # Handle base64 payload if dropped from browser
                raw_b64 = file_path_or_data.split(",")[-1] if "," in file_path_or_data else file_path_or_data
                with open(temp_path, "wb") as f:
                    f.write(base64.b64decode(raw_b64))
            else:
                return {"success": False, "error": "Could not read mod file source"}

            # 2. Run 5-pass ASM and namespace remapping engine
            remapper = AutoRemapperService(self.root_dir)
            remap_res = remapper.process_mod_jar(temp_path, dest_path)

            if not remap_res.get("success"):
                return {"success": False, "error": remap_res.get("error", "Remapping failed")}

            # 3. Clear cache and extract mod metadata
            self._cache.clear()
            mod_info = self._parse_mod_jar(dest_path)

            return {
                "success": True,
                "filename": filename,
                "mod": mod_info,
                "remapping": remap_res,
                "message": f"Successfully installed and remapped {filename} to {instance_dir}!"
            }
        except Exception as e:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except OSError: pass
            return {"success": False, "error": f"Error installing dropped mod: {str(e)}"}

