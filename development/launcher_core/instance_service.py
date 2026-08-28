import os
import sys
import json
import subprocess
import threading
import time
import urllib.request
import zipfile
import re
import shutil
from typing import Any, Optional, Dict, List

try:
    from shared_core.runtime import atomic_write_json, seed_prism_config, detect_system_java
except ImportError:
    def atomic_write_json(path, value):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
        os.replace(temp, path)
    def seed_prism_config(prism_dir, instances_dir=None):
        pass
    def detect_system_java(version_hint=21):
        return "javaw.exe"

try:
    from launcher_core.native_runner import NativeMinecraftRunner
except ImportError:
    try:
        from native_runner import NativeMinecraftRunner
    except ImportError:
        NativeMinecraftRunner = None

class InstanceService:
    """Manages Minecraft instances, presets, JVM launch arguments, memory governor, and runtime execution."""
    
    def __init__(self, root_dir, instances_dir, state_dir=None, prism_root=None):
        self.root_dir = root_dir
        self.instances_dir = instances_dir
        self.state_dir = os.path.abspath(state_dir or self.root_dir)
        self.prism_root = os.path.abspath(prism_root or os.path.join(self.state_dir, "prism"))
        self.settings_file = os.path.join(self.state_dir, "launcher_settings.json")
        self.launch_log_dir = os.path.join(self.state_dir, "logs", "launches")
        os.makedirs(self.launch_log_dir, exist_ok=True)
        if NativeMinecraftRunner:
            self.native_runner = NativeMinecraftRunner(self.root_dir, self.state_dir)
        else:
            self.native_runner = None
        seed_prism_config(self.prism_root, self.instances_dir)
        self.settings = self.load_settings()
        self.running_processes = {}
        self._launch_handles = {}
        self.init_default_instances()

    def _custom_instances_file(self):
        return os.path.join(self.state_dir, "custom_instances.json")

    def _load_custom_instances(self):
        f = self._custom_instances_file()
        if os.path.isfile(f):
            try:
                with open(f, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        return []

    def _save_custom_instance(self, inst_dict):
        existing = self._load_custom_instances()
        existing = [item for item in existing if item.get("id") != inst_dict.get("id")]
        existing.append(inst_dict)
        atomic_write_json(self._custom_instances_file(), existing)

    def load_settings(self):
        defaults = {
            "ram_allocated_gb": 8,
            "power_governor": "turbo",
            "selected_instance": "sir-26-ultra",
            "jvm_args_custom": "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200",
            "enable_sound_fx": True,
            "theme": "dark",
            "lang": "en",
            "discord_rpc": True,
            "auto_connect_ip": ""
        }
        source_file = self.settings_file
        if not os.path.exists(source_file):
            legacy_file = os.path.join(self.root_dir, "launcher_settings.json")
            if os.path.exists(legacy_file):
                source_file = legacy_file
        if os.path.exists(source_file):
            try:
                with open(source_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
            except Exception:
                pass
        return defaults

    def save_settings(self, new_settings=None):
        if new_settings:
            self.settings.update(new_settings)
        try:
            atomic_write_json(self.settings_file, self.settings)
            return {"success": True, "settings": self.settings}
        except Exception as ex:
            return {"success": False, "error": str(ex)}

    def init_default_instances(self):
        self.instances = [
            # Modern 26.2 Profiles
            {
                "id": "sir-26-ultra",
                "name": "SIR 26 (Ultra Visuals)",
                "version": "1.21.4 (Modern 26.2)",
                "loader": "Fabric 0.16.10",
                "shader": "SIR_Extreme_Shader.zip",
                "pack": "SIR_Ultimate_Pack.zip",
                "category": "Modern",
                "tag": "✨ Cinematic Master",
                "fps_target": "144+ FPS",
                "desc": "Full raytracing volumetric atmosphere, physics glowing circular sun, crystal water, and 3D Parallax Occlusion Mapping.",
                "dir_name": "26.2",
                "instance_id": "26.2-ultra"
            },
            {
                "id": "sir-26-balanced",
                "name": "SIR 26 (Balanced 144+ FPS)",
                "version": "1.21.4 (Modern 26.2)",
                "loader": "Fabric 0.16.10",
                "shader": "SIR_Balanced_Shader.zip",
                "pack": "SIR_Ultimate_Pack.zip",
                "category": "Modern",
                "tag": "⚡ High FPS Visuals",
                "fps_target": "180+ FPS",
                "desc": "Optimized shader pipeline maintaining crystal water & glowing sun with ultra-high framerates for 144Hz/240Hz monitors.",
                "dir_name": "26.2",
                "instance_id": "26.2-balanced"
            },
            {
                "id": "sir-26-competitive",
                "name": "SIR 26 (Competitive Speed)",
                "version": "1.21.4 (Modern 26.2)",
                "loader": "Fabric 0.16.10",
                "shader": "OFF (Pure Performance)",
                "pack": "SIR_Ultimate_Pack.zip",
                "category": "Modern",
                "tag": "🏆 0ms Latency",
                "fps_target": "350+ FPS",
                "desc": "Ultra-low render pipeline tuned for competitive modern PvP, crystal clear vision, and instant hit registration.",
                "dir_name": "26.2-performance",
                "instance_id": "26.2-performance"
            },
            {
                "id": "sir-26-vanilla",
                "name": "SIR 26 (Modular Vanilla+)",
                "version": "1.21.4 (Modern 26.2)",
                "loader": "Fabric 0.16.10",
                "shader": "OFF",
                "pack": "SIR_Ultimate_Pack.zip",
                "category": "Modern",
                "tag": "🍃 Vanilla Plus",
                "fps_target": "300+ FPS",
                "desc": "Pure vanilla-compatible experience with Entity Model Features, Fresh Animations, and OptiFine feature parity.",
                "dir_name": "26.2",
                "instance_id": "26.2"
            },

            # Legacy 1.8.9 Profiles
            {
                "id": "sir-189-pvp",
                "name": "Legacy 1.8.9 PvP Battle Suite",
                "version": "1.8.9 (Legacy Forge)",
                "loader": "Forge 1.8.9-11.15.1.2318",
                "shader": "OFF",
                "pack": "SIR_Legacy_32x.zip",
                "category": "Legacy",
                "tag": "⚔️ Hypixel PvP",
                "fps_target": "500+ FPS",
                "desc": "The definitive competitive 1.8.9 setup with 1.7 sword block-hit animations, CPS counter, Armor HUD, and InGameAccountSwitcher.",
                "dir_name": "1.8.9",
                "instance_id": "1.8.9"
            },
            {
                "id": "sir-189-ultra",
                "name": "Legacy 1.8.9 Ultra Visuals",
                "version": "1.8.9 (Legacy Forge)",
                "loader": "Forge 1.8.9-11.15.1.2318",
                "shader": "Custom Shaders Active",
                "pack": "SIR_Legacy_32x.zip",
                "category": "Legacy",
                "tag": "✨ HD Sky & Visuals",
                "fps_target": "300+ FPS",
                "desc": "HD 32x Faithful textures, custom dynamic starry skyboxes, motion blur effects, and OptiFine HD enhancements.",
                "dir_name": "1.8.9-ultra",
                "instance_id": "1.8.9-ultra"
            },
            {
                "id": "sir-189-balanced",
                "name": "Legacy 1.8.9 Ranked Bedwars",
                "version": "1.8.9 (Legacy Forge)",
                "loader": "Forge 1.8.9-11.15.1.2318",
                "shader": "OFF",
                "pack": "SIR_Legacy_32x.zip",
                "category": "Legacy",
                "tag": "⚡ Ranked Bedwars",
                "fps_target": "450+ FPS",
                "desc": "Tuned for competitive Bedwars & Duels with Keystrokes, low-latency hit detection, and custom crosshairs.",
                "dir_name": "1.8.9-balanced",
                "instance_id": "1.8.9-balanced"
            },
            {
                "id": "sir-189-competitive",
                "name": "Legacy 1.8.9 Zero-Delay 500+ FPS",
                "version": "1.8.9 (Legacy Forge)",
                "loader": "Forge 1.8.9-11.15.1.2318",
                "shader": "OFF",
                "pack": "SIR_Legacy_32x.zip",
                "category": "Legacy",
                "tag": "🚀 Max FPS Engine",
                "fps_target": "600+ FPS",
                "desc": "Maximum throughput engine with raw mouse input, minimal particle overhead, and instantaneous response.",
                "dir_name": "1.8.9-performance",
                "instance_id": "1.8.9-performance"
            }
        ]

        # Load any user-created custom profiles
        custom_profiles = self._load_custom_instances()
        existing_ids = {i["id"] for i in self.instances}
        for cp in custom_profiles:
            if cp.get("id") not in existing_ids:
                self.instances.append(cp)

    def get_instances(self):
        for instance in self.instances:
            instance_id = instance.get("instance_id", instance.get("dir_name", ""))
            instance["instancePath"] = os.path.join(self.instances_dir, instance_id)
            instance["available"] = os.path.isdir(instance["instancePath"])
        return {
            "selected": self.settings.get("selected_instance", "sir-26-ultra"),
            "instances": self.instances,
            "running_count": len(self.running_processes)
        }

    def select_instance(self, inst_id):
        self.settings["selected_instance"] = inst_id
        self.save_settings()
        return {"success": True, "selected": inst_id}

    def get_minecraft_versions(self) -> dict[str, Any]:
        """Fetches live Minecraft version manifest from Mojang with offline cache fallback."""
        cache_file = os.path.join(self.state_dir, "version_manifest_cache.json")
        versions = []
        try:
            req = urllib.request.Request(
                "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
                headers={"User-Agent": "SIR-Launcher/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for v in data.get("versions", []):
                    v_type = v.get("type", "release")
                    v_id = v.get("id", "")
                    versions.append({
                        "id": v_id,
                        "type": v_type,
                        "releaseTime": v.get("releaseTime", ""),
                        "isMajor": v_id in ["1.21.4", "1.21.1", "1.20.4", "1.20.1", "1.19.4", "1.18.2", "1.16.5", "1.12.2", "1.8.9", "1.7.10"]
                    })
                atomic_write_json(cache_file, versions)
        except Exception:
            if os.path.isfile(cache_file):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        versions = json.load(f)
                except Exception:
                    pass

        if not versions:
            curated = [
                {"id": "1.21.4", "type": "release", "isMajor": True},
                {"id": "1.21.3", "type": "release", "isMajor": True},
                {"id": "1.21.1", "type": "release", "isMajor": True},
                {"id": "1.21.0", "type": "release", "isMajor": True},
                {"id": "1.20.6", "type": "release", "isMajor": True},
                {"id": "1.20.4", "type": "release", "isMajor": True},
                {"id": "1.20.2", "type": "release", "isMajor": True},
                {"id": "1.20.1", "type": "release", "isMajor": True},
                {"id": "1.19.4", "type": "release", "isMajor": True},
                {"id": "1.19.2", "type": "release", "isMajor": True},
                {"id": "1.18.2", "type": "release", "isMajor": True},
                {"id": "1.17.1", "type": "release", "isMajor": True},
                {"id": "1.16.5", "type": "release", "isMajor": True},
                {"id": "1.15.2", "type": "release", "isMajor": True},
                {"id": "1.14.4", "type": "release", "isMajor": True},
                {"id": "1.12.2", "type": "release", "isMajor": True},
                {"id": "1.8.9", "type": "release", "isMajor": True},
                {"id": "1.7.10", "type": "release", "isMajor": True},
            ]
            versions = curated

        return {
            "success": True,
            "versions": versions,
            "latest_release": "1.21.4"
        }

    def get_mod_loaders(self, mc_version="1.21.4") -> dict[str, Any]:
        """Returns compatible mod loaders for a given Minecraft version."""
        loaders = [
            {
                "id": "fabric",
                "name": "Fabric Loader",
                "tag": "⚡ High Performance",
                "desc": "Ultra-fast, lightweight modding engine with Sodium, Iris Shaders & Modern PvP.",
                "available": True,
                "default": True,
                "version": "0.16.10" if "1.21" in mc_version else "0.15.11"
            },
            {
                "id": "forge",
                "name": "Minecraft Forge",
                "tag": "🔨 Classic Modding",
                "desc": "Standard classic mod loader with massive mod library support for 1.8.9, 1.12.2, 1.16.5, and 1.20.1.",
                "available": True,
                "default": False,
                "version": "11.15.1.2318" if "1.8.9" in mc_version else "47.2.0"
            },
            {
                "id": "neoforge",
                "name": "NeoForge",
                "tag": "🛡️ Next-Gen Engine",
                "desc": "Modernized successor to Forge for Minecraft 1.20.4+ and 1.21+.",
                "available": not any(old in mc_version for old in ["1.8", "1.7", "1.12", "1.16", "1.18", "1.19"]),
                "default": False,
                "version": "21.1.65"
            },
            {
                "id": "quilt",
                "name": "Quilt Loader",
                "tag": "🪶 Modular Ecosystem",
                "desc": "Next-gen community-driven loader compatible with Fabric mods.",
                "available": not any(old in mc_version for old in ["1.8", "1.7", "1.12", "1.13"]),
                "default": False,
                "version": "0.26.0"
            },
            {
                "id": "vanilla",
                "name": "Pure Vanilla",
                "tag": "🧊 Unmodified",
                "desc": "Official Mojang Minecraft client with zero modded dependencies.",
                "available": True,
                "default": False,
                "version": mc_version
            }
        ]
        return {"success": True, "mc_version": mc_version, "loaders": loaders}

    def build_launch_arguments(self, inst_id, account_name=""):
        inst = next((i for i in self.instances if i["id"] == inst_id), self.instances[0])
        ram_gb = self.settings.get("ram_allocated_gb", 8)
        
        jvm_flags = [
            f"-Xms{max(2, ram_gb // 2)}G",
            f"-Xmx{ram_gb}G",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:+UseG1GC",
            "-XX:G1NewSizePercent=20",
            "-XX:G1ReservePercent=15",
            "-XX:MaxGCPauseMillis=50",
            "-XX:G1HeapRegionSize=32M",
            "-XX:+AlwaysPreTouch",
            "-XX:+UseStringDeduplication",
            "-XX:G1HeapWastePercent=5",
            "-XX:G1MixedGCCountTarget=4",
            "-XX:InitiatingHeapOccupancyPercent=15",
            "-XX:G1MixedGCLiveThresholdPercent=90",
            "-XX:G1RSetUpdatingPauseTimePercent=5",
            "-XX:SurvivorRatio=32",
            "-XX:+PerfDisableSharedMem",
            "-XX:MaxTenuringThreshold=1",
            "-Dfile.encoding=UTF-8"
        ]
        
        # Power Governor Threading
        if self.settings.get("power_governor") == "smooth":
            jvm_flags.append("-XX:ParallelGCThreads=4")
            jvm_flags.append("-XX:ConcGCThreads=2")
        else:
            cpu_count = os.cpu_count() or 8
            jvm_flags.append(f"-XX:ParallelGCThreads={cpu_count}")
            jvm_flags.append(f"-XX:ConcGCThreads={max(2, cpu_count // 2)}")
        
        return {
            "instance": inst,
            "jvm_flags": jvm_flags,
            "ram_allocated_gb": ram_gb,
            "account": account_name
        }

    def create_custom_instance(self, name, version="1.21.4", loader="fabric", ram_gb=8, enable_perf=True, icon="sir_crystal"):
        """Provisions a real, launchable Minecraft instance in Prism format with auto-downloading."""
        safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name.strip()) or f"Custom_{int(time.time())}"
        inst_dir_name = f"sir-custom-{safe_name.lower()[:20]}"
        inst_path = os.path.join(self.instances_dir, inst_dir_name)
        
        counter = 1
        while os.path.exists(inst_path):
            inst_dir_name = f"sir-custom-{safe_name.lower()[:16]}-{counter}"
            inst_path = os.path.join(self.instances_dir, inst_dir_name)
            counter += 1

        os.makedirs(os.path.join(inst_path, "minecraft", "mods"), exist_ok=True)
        os.makedirs(os.path.join(inst_path, "minecraft", "shaderpacks"), exist_ok=True)
        os.makedirs(os.path.join(inst_path, "minecraft", "resourcepacks"), exist_ok=True)
        os.makedirs(os.path.join(inst_path, "minecraft", "config"), exist_ok=True)

        is_java_8 = any(v in version for v in ["1.8", "1.7", "1.12", "1.16", "1.15", "1.14"])
        is_java_17 = any(v in version for v in ["1.17", "1.18", "1.19", "1.20.1", "1.20.2", "1.20.4"])
        java_hint = 8 if is_java_8 else (17 if is_java_17 else 21)
        java_path = detect_system_java(java_hint)

        min_mb = max(2048, (int(ram_gb) // 2) * 1024)
        max_mb = int(ram_gb) * 1024
        
        inst_cfg_lines = [
            "[General]",
            "ConfigVersion=1.3",
            "InstanceType=OneSix",
            f"iconKey={icon or 'sir_crystal'}",
            f"name={name}",
            "group=Custom Modpacks",
            "AutomaticJava=true",
            "OverrideJavaLocation=true",
            f"JavaPath={java_path}",
            "OverrideMemory=true",
            f"MinMemAlloc={min_mb}",
            f"MaxMemAlloc={max_mb}",
            "OverrideJavaArgs=true",
            'JvmArgs="-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication -XX:MaxGCPauseMillis=50"'
        ]
        with open(os.path.join(inst_path, "instance.cfg"), "w", encoding="utf-8") as f:
            f.write("\n".join(inst_cfg_lines) + "\n")

        components = [
            {
                "cachedName": "Minecraft",
                "cachedVersion": version,
                "important": True,
                "uid": "net.minecraft",
                "version": version
            }
        ]

        loader_clean = loader.lower()
        if "fabric" in loader_clean:
            components.insert(0, {
                "cachedName": "Intermediary Mappings",
                "cachedVersion": version,
                "cachedVolatile": True,
                "dependencyOnly": True,
                "uid": "net.fabricmc.intermediary",
                "version": version
            })
            components.append({
                "cachedName": "Fabric Loader",
                "cachedVersion": "0.16.10" if "1.21" in version else "0.15.11",
                "uid": "net.fabricmc.fabric-loader",
                "version": "0.16.10" if "1.21" in version else "0.15.11"
            })
        elif "forge" in loader_clean and "neo" not in loader_clean:
            forge_ver = "11.15.1.2318" if "1.8.9" in version else "47.2.0"
            components.append({
                "cachedName": "Forge",
                "cachedVersion": forge_ver,
                "uid": "net.minecraftforge",
                "version": forge_ver
            })
        elif "neo" in loader_clean:
            components.append({
                "cachedName": "NeoForge",
                "cachedVersion": "21.1.65",
                "uid": "net.neoforged",
                "version": "21.1.65"
            })
        elif "quilt" in loader_clean:
            components.append({
                "cachedName": "Quilt Loader",
                "cachedVersion": "0.26.0",
                "uid": "org.quiltmc.quilt-loader",
                "version": "0.26.0"
            })

        mmc_pack = {
            "components": components,
            "formatVersion": 1
        }
        with open(os.path.join(inst_path, "mmc-pack.json"), "w", encoding="utf-8") as f:
            json.dump(mmc_pack, f, indent=2)

        new_id = f"custom-{inst_dir_name}"
        loader_title = "Fabric" if "fabric" in loader_clean else ("Forge" if "forge" in loader_clean else ("NeoForge" if "neo" in loader_clean else ("Quilt" if "quilt" in loader_clean else "Vanilla")))
        
        new_inst = {
            "id": new_id,
            "name": name,
            "version": f"{version} ({loader_title})",
            "loader": loader_title,
            "shader": "SIR_Balanced_Shader.zip" if "fabric" in loader_clean else "OFF",
            "pack": "SIR_Ultimate_Pack.zip",
            "category": "Custom",
            "tag": f"🎮 {loader_title} {version}",
            "fps_target": "200+ FPS",
            "desc": f"Custom instance for Minecraft {version} running {loader_title}.",
            "dir_name": inst_dir_name,
            "instance_id": inst_dir_name,
            "isCustom": True
        }

        self._save_custom_instance(new_inst)
        self.instances.append(new_inst)
        self.settings["selected_instance"] = new_id
        self.save_settings()
        seed_prism_config(self.prism_root, self.instances_dir)

        return {"success": True, "instance": new_inst, "message": f"✓ Created profile: {name}"}

    def clone_instance(self, inst_id, new_name):
        inst = next((i for i in self.instances if i["id"] == inst_id), None)
        if not inst:
            return {"success": False, "error": "Instance not found"}
        
        src_dir_name = inst.get("instance_id") or inst.get("dir_name", "")
        src_path = os.path.join(self.instances_dir, src_dir_name)
        
        new_name_val = new_name or f"{inst['name']} (Clone)"
        safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', new_name_val.strip())
        new_dir_name = f"clone-{safe_name.lower()[:20]}"
        new_path = os.path.join(self.instances_dir, new_dir_name)
        
        counter = 1
        while os.path.exists(new_path):
            new_dir_name = f"clone-{safe_name.lower()[:16]}-{counter}"
            new_path = os.path.join(self.instances_dir, new_dir_name)
            counter += 1

        if os.path.isdir(src_path):
            try:
                shutil.copytree(src_path, new_path)
            except Exception as e:
                return {"success": False, "error": f"Failed to copy instance files: {e}"}

        new_id = f"custom-{new_dir_name}"
        cloned = dict(inst)
        cloned["id"] = new_id
        cloned["name"] = new_name_val
        cloned["dir_name"] = new_dir_name
        cloned["instance_id"] = new_dir_name
        cloned["tag"] = "🌟 Custom Clone"
        cloned["isCustom"] = True

        self._save_custom_instance(cloned)
        self.instances.append(cloned)
        self.settings["selected_instance"] = new_id
        self.save_settings()
        return {"success": True, "instance": cloned, "message": f"✓ Duplicated instance as {new_name_val}"}

    def delete_instance(self, inst_id):
        inst = next((i for i in self.instances if i["id"] == inst_id), None)
        if not inst:
            return {"success": False, "error": "Instance not found"}

        dir_name = inst.get("instance_id") or inst.get("dir_name", "")
        target_path = os.path.join(self.instances_dir, dir_name)
        
        if os.path.isdir(target_path) and "custom" in dir_name.lower() or "clone" in dir_name.lower():
            try:
                shutil.rmtree(target_path)
            except Exception:
                pass

        self.instances = [i for i in self.instances if i["id"] != inst_id]
        existing_custom = self._load_custom_instances()
        existing_custom = [i for i in existing_custom if i.get("id") != inst_id]
        atomic_write_json(self._custom_instances_file(), existing_custom)

        if self.settings.get("selected_instance") == inst_id:
            self.settings["selected_instance"] = "sir-26-ultra"
            self.save_settings()

        return {"success": True, "deleted": inst_id, "message": f"✓ Deleted profile: {inst.get('name')}"}

    def _launch_result(self, *, success, profile_id, instance_id="", mode="offline", pid=None,
                       message="", error_code="", log_path="", error=""):
        """Return the stable launch contract consumed by every desktop mode."""
        result = {
            "success": bool(success),
            "profileId": profile_id,
            "instanceId": instance_id,
            "mode": mode,
            "pid": pid,
            "message": message,
            "errorCode": error_code,
            "logPath": log_path,
        }
        if error:
            result["error"] = error
        return result

    def _download_payload_if_missing(self, payload_name, dest_folder):
        """Helper to fetch and extract a cloud payload if not found locally."""
        try:
            os.makedirs(dest_folder, exist_ok=True)
            local_candidates = [
                os.path.join(self.root_dir, "payload", payload_name),
                os.path.join(self.root_dir, "dist_payloads", payload_name),
                os.path.join(self.root_dir, payload_name),
                os.path.join(os.path.dirname(self.root_dir), "dist_payloads", payload_name)
            ]
            local_zip = next((p for p in local_candidates if os.path.isfile(p)), None)

            if not local_zip:
                cache_dir = os.path.join(self.state_dir, "cache", "payloads")
                os.makedirs(cache_dir, exist_ok=True)
                local_zip = os.path.join(cache_dir, payload_name)

                if not os.path.isfile(local_zip) or os.path.getsize(local_zip) < 1024:
                    cdn_urls = [
                        f"https://github.com/sirahmed8/SIR-ModPack/releases/download/v1.0.0/{payload_name}",
                        f"https://raw.githubusercontent.com/sirahmed8/SIR-ModPack/main/dist_payloads/{payload_name}"
                    ]
                    for url in cdn_urls:
                        try:
                            req = urllib.request.Request(url, headers={"User-Agent": "SIR-Launcher/1.0"})
                            with urllib.request.urlopen(req, timeout=12) as resp:
                                with open(local_zip, "wb") as out_f:
                                    shutil.copyfileobj(resp, out_f)
                            break
                        except Exception:
                            if os.path.exists(local_zip):
                                try: os.remove(local_zip)
                                except: pass

            if local_zip and os.path.isfile(local_zip):
                with zipfile.ZipFile(local_zip, 'r') as zf:
                    zf.extractall(dest_folder)
                return True
        except Exception:
            pass
        return False

    def heal_instance_if_needed(self, inst, inst_dir, mc_game_dir, mc_version):
        """Comprehensive Self-Healing Engine: guarantees mods, shaders, packs, and tuned configs exist across all profiles."""
        try:
            os.makedirs(inst_dir, exist_ok=True)
            os.makedirs(mc_game_dir, exist_ok=True)
            
            # 1. Instance Definition (.cfg / mmc-pack.json)
            cfg_file = os.path.join(inst_dir, "instance.cfg")
            if not os.path.isfile(cfg_file) and not os.path.isfile(os.path.join(inst_dir, "mmc-pack.json")):
                with open(cfg_file, "w", encoding="utf-8") as f:
                    f.write(f"[General]\nConfigVersion=1.2\nname={inst.get('name', 'SIR Profile')}\niconKey=default\nInstanceType=OneSix\n")

            # 2. Per-Profile Mods Suite Healing
            mods_dir = os.path.join(mc_game_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)
            existing_jars = [f for f in os.listdir(mods_dir) if f.endswith('.jar')]
            
            is_modern = "26" in mc_version or "21" in mc_version or "modern" in inst.get("id", "").lower()
            min_jars = 200 if is_modern else 45
            payload_name = "payload_mods_26.2.zip" if is_modern else "payload_mods_1.8.9.zip"
            
            if len(existing_jars) < min_jars:
                self._download_payload_if_missing(payload_name, mods_dir)

            # 3. Optical Shaders Suite Healing
            shaders_targets = [
                os.path.join(self.root_dir, "shaderpacks"),
                os.path.join(self.state_dir, "shaderpacks"),
                os.path.join(mc_game_dir, "shaderpacks")
            ]
            has_shaders = any(
                os.path.isfile(os.path.join(sd, "SIR_Balanced_Shader.zip")) or os.path.isfile(os.path.join(sd, "SIR_Extreme_Shader.zip"))
                for sd in shaders_targets if os.path.isdir(sd)
            )
            if not has_shaders:
                self._download_payload_if_missing("payload_shaders.zip", os.path.join(self.root_dir, "shaderpacks"))
                self._download_payload_if_missing("payload_shaders.zip", os.path.join(mc_game_dir, "shaderpacks"))

            # 4. 3D POM Resource Packs Healing
            packs_targets = [
                os.path.join(self.root_dir, "resourcepacks"),
                os.path.join(self.state_dir, "resourcepacks"),
                os.path.join(mc_game_dir, "resourcepacks")
            ]
            has_packs = any(
                os.path.isfile(os.path.join(pd, "SIR_Ultimate_Pack.zip")) or os.path.isfile(os.path.join(pd, "SIR_Legacy_32x.zip"))
                for pd in packs_targets if os.path.isdir(pd)
            )
            if not has_packs:
                self._download_payload_if_missing("payload_packs.zip", os.path.join(self.root_dir, "resourcepacks"))
                self._download_payload_if_missing("payload_packs.zip", os.path.join(mc_game_dir, "resourcepacks"))

            # 5. High-Performance Configuration Presets Healing
            cfg_dir = os.path.join(mc_game_dir, "config")
            os.makedirs(cfg_dir, exist_ok=True)
            options_path = os.path.join(mc_game_dir, "options.txt")
            
            if not os.path.isfile(options_path):
                if is_modern:
                    with open(options_path, "w", encoding="utf-8") as f:
                        f.write("version:3465\ngamma:1.0\nmaxFps:260\nfov:0.0\nrenderDistance:12\nsimulationDistance:8\nguiScale:0\ngraphicsMode:0\nsmoothLighting:true\nentityDistanceScaling:1.0\nentityShadows:true\nresourcePacks:[\"vanilla\",\"file/SIR_Ultimate_Pack.zip\"]\nincompatibleResourcePacks:[]\nsoundCategory_master:1.0\nsoundCategory_music:0.0\nbiomeBlendRadius:7\n")
                else:
                    with open(options_path, "w", encoding="utf-8") as f:
                        f.write("renderDistance:12\ngamma:1.0\nfullscreen:false\nmaxFps:260\nresourcePacks:[\"SIR_Legacy_32x.zip\"]\n")

            if is_modern:
                iris_path = os.path.join(cfg_dir, "iris.properties")
                if not os.path.isfile(iris_path):
                    with open(iris_path, "w", encoding="utf-8") as f:
                        f.write("enableShaders=true\nshaderPack=SIR_Balanced_Shader.zip\n")

            return True
        except Exception:
            return False

    def launch_instance(self, inst_id, account=None, on_log_callback=None, extra_args=None):
        inst = next((i for i in self.instances if i["id"] == inst_id), None)
        if not inst:
            return self._launch_result(
                success=False,
                profile_id=inst_id,
                error_code="PROFILE_NOT_FOUND",
                error="The selected SIR profile does not exist.",
            )

        instance_id = inst.get("instance_id") or inst.get("dir_name", "")
        inst_dir = os.path.join(self.instances_dir, instance_id)
        mc_game_dir = os.path.join(inst_dir, "minecraft") if os.path.isdir(os.path.join(inst_dir, "minecraft")) else inst_dir
        mc_version = "26.2" if "26" in instance_id or "26" in inst_id else ("1.8.9" if "1.8" in instance_id or "189" in inst_id else "1.21.4")
        
        # Self-Healing Check: Auto-repair missing instance files or mods from Cloud CDN
        self.heal_instance_if_needed(inst, inst_dir, mc_game_dir, mc_version)

        if not os.path.isdir(inst_dir):
            return self._launch_result(
                success=False,
                profile_id=inst_id,
                instance_id=instance_id,
                error_code="INSTANCE_NOT_FOUND",
                error=f"Profile files are missing: {inst_dir}",
            )
        if not (os.path.isfile(os.path.join(inst_dir, "instance.cfg")) or os.path.isfile(os.path.join(inst_dir, "mmc-pack.json"))):
            return self._launch_result(
                success=False,
                profile_id=inst_id,
                instance_id=instance_id,
                error_code="INSTANCE_INVALID",
                error="The selected profile is incomplete and cannot be launched.",
            )
        
        account_name = ""
        account_type = "offline"
        account_dict = None
        if isinstance(account, dict):
            account_name = str(account.get("displayName") or account.get("name") or account.get("username") or "Player")
            account_type = str(account.get("accountType") or account.get("type") or "offline")
            account_dict = account
        elif account:
            account_name = str(account)
            account_dict = {"name": account_name, "type": "offline"}
        else:
            account_name = "Player"
            account_dict = {"name": "Player", "type": "offline"}

        # Target Minecraft game directory
        mc_game_dir = os.path.join(inst_dir, "minecraft") if os.path.isdir(os.path.join(inst_dir, "minecraft")) else inst_dir
        mc_version = "26.2" if "26" in instance_id or "26" in inst_id else ("1.8.9" if "1.8" in instance_id or "189" in inst_id else "1.21.4")
        loader_type = "forge" if "1.8" in mc_version else "fabric"
        ram_gb = int(self.settings.get("ram_allocated_gb", 8))
        power_mode = str(self.settings.get("power_governor", "turbo"))

        # 1. Primary: Direct Native JVM Launch Engine (100% Independent)
        if self.native_runner:
            native_res = self.native_runner.launch(
                instance_dir=mc_game_dir,
                mc_version=mc_version,
                loader=loader_type,
                account=account_dict,
                ram_gb=ram_gb,
                power_mode=power_mode
            )
            if native_res.get("success"):
                pid = native_res.get("pid")
                log_path = native_res.get("log_path", "")
                self.running_processes[inst_id] = pid
                return self._launch_result(
                    success=True,
                    profile_id=inst_id,
                    instance_id=instance_id,
                    mode=account_type,
                    pid=pid,
                    message=f"✓ Launched {inst['name']} (Native Java Direct Engine)",
                    log_path=log_path,
                )

        # 2. Secondary Fallback: Managed Runner (if Prism present)
        launcher_candidates = [
            os.path.join(self.prism_root, "prismlauncher.exe"),
            os.path.join(self.root_dir, "prism", "prismlauncher.exe"),
            os.path.join(self.root_dir, "SIR Launcher", "bin", "prismlauncher.exe"),
            os.path.join(self.root_dir, "SIR Launcher", "prismlauncher.exe"),
            os.path.join(self.root_dir, "bin", "prismlauncher.exe")
        ]
        exe = next((e for e in launcher_candidates if os.path.isfile(e)), None)
        if exe:
            seed_prism_config(self.prism_root, self.instances_dir)
            cmd = [exe, "--dir", self.prism_root, "--launch", instance_id]
            if account_name:
                if account_type == "microsoft":
                    cmd.extend(["--profile", account_name])
                else:
                    cmd.extend(["--offline", account_name])
            if extra_args:
                cmd.extend([str(item) for item in extra_args])

            log_path = os.path.join(self.launch_log_dir, f"{inst_id}-{int(time.time())}.log")
            try:
                with open(log_path, "a", encoding="utf-8") as log_handle:
                    log_handle.write("$ " + " ".join(cmd) + "\n")
                    log_handle.flush()
                    proc = subprocess.Popen(
                        cmd,
                        cwd=os.path.dirname(exe),
                        stdout=log_handle,
                        stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
                    )
                self.running_processes[inst_id] = proc
                return self._launch_result(
                    success=True,
                    profile_id=inst_id,
                    instance_id=instance_id,
                    mode=account_type,
                    pid=proc.pid,
                    message=f"Launching {inst['name']}…",
                    log_path=log_path,
                )
            except Exception as ex:
                pass

        return self._launch_result(
            success=False,
            profile_id=inst_id,
            instance_id=instance_id,
            mode=account_type,
            error_code="LAUNCH_FAILED",
            error=f"Could not launch Minecraft instance. Check logs in {self.launch_log_dir}",
        )

    def open_instance_folder(self, inst_id="sir-26-ultra"):
        inst = next((i for i in self.instances if i["id"] == inst_id), None)
        dir_name = (inst.get("instance_id") or inst.get("dir_name", "26.2")) if inst else ("1.8.9" if "189" in inst_id else "26.2")
        target_dir = os.path.join(self.instances_dir, dir_name, "minecraft")
        if not os.path.exists(target_dir):
            target_dir = os.path.join(self.instances_dir, dir_name)
        if not os.path.exists(target_dir):
            return {"success": False, "error": "The selected instance folder is missing."}
        try:
            os.startfile(target_dir)
            return {"success": True, "path": target_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_instance_mods_folder(self, inst_id="sir-26-ultra"):
        inst = next((i for i in self.instances if i["id"] == inst_id), None)
        dir_name = (inst.get("instance_id") or inst.get("dir_name", "26.2")) if inst else ("1.8.9" if "189" in inst_id else "26.2")
        target_dir = os.path.join(self.instances_dir, dir_name, "minecraft", "mods")
        if not os.path.exists(target_dir):
            target_dir = os.path.join(self.root_dir, "mods")
        if not os.path.exists(target_dir):
            return {"success": False, "error": "The selected instance mods folder is missing."}
        try:
            os.startfile(target_dir)
            return {"success": True, "path": target_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}
