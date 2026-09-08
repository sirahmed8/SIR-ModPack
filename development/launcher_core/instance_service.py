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
    from shared_core.runtime import atomic_write_json, atomic_write_text, download_file_resilient, seed_prism_config, detect_system_java
except ImportError:
    def atomic_write_json(path, value):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
        os.replace(temp, path)
    def atomic_write_text(path, content, encoding="utf-8"):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding=encoding) as handle:
            handle.write(content)
        os.replace(temp, path)
    def seed_prism_config(prism_dir, instances_dir=None):
        pass
    def detect_system_java(version_hint=21):
        return "javaw.exe"

try:
    from launcher_core.native_runner import NativeMinecraftRunner, calculate_ram_parameters
except ImportError:
    try:
        from native_runner import NativeMinecraftRunner, calculate_ram_parameters
    except ImportError:
        NativeMinecraftRunner = None
        def calculate_ram_parameters(max_ram=8, min_ram=None, mc_version="26.2"):
            max_mb = int(max_ram) * 1024 if isinstance(max_ram, (int, float)) and max_ram <= 64 else 8192
            min_mb = min(max_mb, max(512, max_mb // 2))
            return {
                "min_mb": min_mb,
                "max_mb": max_mb,
                "xms_flag": f"-Xms{min_mb // 1024}G" if min_mb >= 1024 and min_mb % 1024 == 0 else f"-Xms{min_mb}M",
                "xmx_flag": f"-Xmx{max_mb // 1024}G" if max_mb >= 1024 and max_mb % 1024 == 0 else f"-Xmx{max_mb}M",
                "new_size_pct": 30,
                "max_new_size_pct": 40,
                "reserve_pct": 15,
                "region_size": "4M",
                "pause_millis": 50,
            }

try:
    from launcher_core.video_preset_service import VideoPresetService
except ImportError:
    try:
        from video_preset_service import VideoPresetService
    except ImportError:
        VideoPresetService = None

class InstanceService:
    """Manages Minecraft instances, presets, JVM launch arguments, memory governor, and runtime execution."""
    
    def __init__(self, root_dir, instances_dir=None, state_dir=None, prism_root=None):
        self.root_dir = root_dir
        self.instances_dir = os.path.abspath(instances_dir or os.path.join(self.root_dir, "instances"))
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
        self.video_preset_service = VideoPresetService(self.instances_dir) if VideoPresetService else None
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
            "selected_instance": "26.2-ultra",
            "jvm_args_custom": "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200",
            "enable_sound_fx": True,
            "theme": "dark",
            "lang": "en",
            "discord_rpc": True,
            "auto_connect_ip": "",
            "window_close_action": "tray",
            "window_launch_action": "tray_trim",
            "window_minimize_action": "taskbar",
            "autostart_on_boot": False,
            "auto_check_updates": True,
            "auto_download_updates": False,
            "last_seen_release": "0.0.0",
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
            if "ram_gb" in new_settings:
                new_settings["ram_allocated_gb"] = new_settings["ram_gb"]
                new_settings["allocated_ram"] = new_settings["ram_gb"]
            elif "ram_allocated_gb" in new_settings:
                new_settings["ram_gb"] = new_settings["ram_allocated_gb"]
                new_settings["allocated_ram"] = new_settings["ram_allocated_gb"]
            self.settings.update(new_settings)
        try:
            atomic_write_json(self.settings_file, self.settings)
            legacy_file = os.path.join(self.root_dir, "launcher_settings.json")
            atomic_write_json(legacy_file, self.settings)
            return {"success": True, "settings": self.settings}
        except Exception as ex:
            return {"success": False, "error": str(ex)}

    def kill_instance(self, inst_id):
        """Cleanly terminates a running Minecraft instance without leaving zombie processes."""
        pid = self.running_processes.get(inst_id)
        if not pid:
            return {"success": False, "error": f"No running process for {inst_id}"}
        try:
            if hasattr(pid, "terminate"):
                pid.terminate()
            elif isinstance(pid, int):
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(pid)],
                        capture_output=True,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                else:
                    os.kill(pid, 9)
            self.running_processes.pop(inst_id, None)
            return {"success": True, "message": f"Terminated instance {inst_id}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def kill_all_instances(self):
        """Ensures all spawned Minecraft child processes are cleanly reaped."""
        for inst_id in list(self.running_processes.keys()):
            self.kill_instance(inst_id)

    def init_default_instances(self):
        self.instances = [
            # Modern 26.2 Profiles
            {
                "id": "26.2-ultra",
                "name": "SIR 26 Visuals",
                "version": "Fabric 26.2 (Modern)",
                "loader": "Fabric 0.16.10",
                "shader": "SIR Modern Shader.zip",
                "pack": "SIR Modern.zip",
                "category": "Modern",
                "tag": "✨ Enhanced Fidelity",
                "desc": "Fabric 26.2 engine with enhanced shaders, crystal water, dynamic skies and 3D textures.",
                "dir_name": "26.2-ultra",
                "instance_id": "26.2-ultra"
            },
            {
                "id": "26.2-balanced",
                "name": "SIR 26 Balanced",
                "version": "Fabric 26.2 (Modern)",
                "loader": "Fabric 0.16.10",
                "shader": "SIR Modern Shader.zip",
                "pack": "SIR Modern.zip",
                "category": "Modern",
                "tag": "⚡ Standard Balanced",
                "desc": "Fabric 26.2 calibrated with Lithium, FerriteCore and ImmediatelyFast for responsive gameplay.",
                "dir_name": "26.2-balanced",
                "instance_id": "26.2-balanced"
            },
            {
                "id": "26.2-performance",
                "name": "SIR 26 Performance",
                "version": "Fabric 26.2 (Modern)",
                "loader": "Fabric 0.16.10",
                "shader": "OFF (Pure Performance)",
                "pack": "SIR Modern.zip",
                "category": "Modern",
                "tag": "🏆 Competitive Engine",
                "desc": "High-framerate Fabric 26.2 engine with Sodium optimization, low-latency input and dynamic memory cleanup.",
                "dir_name": "26.2-performance",
                "instance_id": "26.2-performance"
            },

            # Pure Vanilla Profile (Normal Vanilla inside SIR Launcher)
            {
                "id": "26.2",
                "name": "SIR 26 Vanilla",
                "version": "Minecraft 26.2 (Vanilla)",
                "loader": "Vanilla",
                "shader": "None (Vanilla)",
                "pack": "Default (Vanilla)",
                "category": "Vanilla",
                "tag": "🌿 Pure Clean Vanilla",
                "desc": "Official pure Minecraft 26.2 without any mods or visual overhaul. Original vanilla gameplay accelerated by SIR Launcher.",
                "dir_name": "26.2",
                "instance_id": "26.2",
                "mods_count": 0,
                "is_vanilla": True
            },

            # Legacy 1.8.9 Profiles
            {
                "id": "1.8.9-ultra",
                "name": "SIR 1.8.9 Visuals",
                "version": "Forge 1.8.9 (Legacy)",
                "loader": "Forge 1.8.9-11.15.1.2318",
                "shader": "SIR Legacy Shader.zip",
                "pack": "SIR Legacy.zip",
                "category": "Legacy",
                "tag": "🎬 Enhanced Classic",
                "desc": "Forge 1.8.9 with shader lighting, dynamic skies, 3D animated skins and high-definition clarity.",
                "dir_name": "1.8.9-ultra",
                "instance_id": "1.8.9-ultra"
            },
            {
                "id": "1.8.9-balanced",
                "name": "SIR 1.8.9 Balanced",
                "version": "Forge 1.8.9 (Legacy)",
                "loader": "Forge 1.8.9-11.15.1.2318",
                "shader": "OFF",
                "pack": "SIR Legacy.zip",
                "category": "Legacy",
                "tag": "⚔️ Standard Competitive",
                "desc": "Forge 1.8.9 calibrated for fluid combat animations, custom HUDs, and responsive click handling.",
                "dir_name": "1.8.9-balanced",
                "instance_id": "1.8.9-balanced"
            },
            {
                "id": "1.8.9-performance",
                "name": "SIR 1.8.9 Performance",
                "version": "Forge 1.8.9 (Legacy)",
                "loader": "Forge 1.8.9-11.15.1.2318",
                "shader": "OFF",
                "pack": "SIR Legacy.zip",
                "category": "Legacy",
                "tag": "⚡ Low Latency Pure",
                "desc": "Forge 1.8.9 stripped for maximum motion clarity, instant input response and zero micro-stutters.",
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
        installed = []
        for instance in self.instances:
            instance_id = instance.get("instance_id", instance.get("dir_name", ""))
            instance["instancePath"] = os.path.join(self.instances_dir, instance_id)
            is_avail = os.path.isdir(instance["instancePath"])
            instance["available"] = is_avail
            instance["is_installed"] = is_avail
            if instance.get("is_vanilla") or instance_id == "26.2":
                instance["mods_count"] = 0
            if is_avail:
                installed.append(instance_id)

        selected = self.settings.get("selected_instance", "26.2-ultra")
        alias_map = {
            "sir-26-ultra": "26.2-ultra",
            "sir-26-balanced": "26.2-balanced",
            "sir-26-competitive": "26.2-performance",
            "sir-26-comp": "26.2-performance",
            "sir-26-vanilla": "26.2-ultra",
            "sir-189-pvp": "1.8.9-balanced",
            "sir-189-ultra": "1.8.9-ultra",
            "sir-189-balanced": "1.8.9-balanced",
            "sir-189-competitive": "1.8.9-performance",
        }
        selected = alias_map.get(selected, selected)
        if installed and selected not in installed:
            if "26.2-ultra" in installed:
                selected = "26.2-ultra"
            else:
                selected = installed[0]
            self.settings["selected_instance"] = selected
            self.save_settings()

        return {
            "selected": selected,
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
                headers={"User-Agent": "SIR-Launcher/1.0.0 (a7medorabe7@gmail.com)"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for v in data.get("versions", []):
                    v_type = v.get("type", "release")
                    v_id = v.get("id", "")
                    versions.append({
                        "id": v_id,
                        "name": v_id,
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
                {"id": "25w08a", "name": "25w08a (Snapshot)", "type": "snapshot", "isMajor": False},
                {"id": "1.21.5-pre1", "name": "1.21.5-pre1 (Pre-Release)", "type": "snapshot", "isMajor": False},
                {"id": "24w46a", "name": "24w46a (Snapshot)", "type": "snapshot", "isMajor": False},
                {"id": "1.21.4", "name": "1.21.4 (Latest Release)", "type": "release", "isMajor": True},
                {"id": "1.21.3", "name": "1.21.3", "type": "release", "isMajor": True},
                {"id": "1.21.1", "name": "1.21.1", "type": "release", "isMajor": True},
                {"id": "1.21.0", "name": "1.21.0", "type": "release", "isMajor": True},
                {"id": "1.20.6", "name": "1.20.6", "type": "release", "isMajor": True},
                {"id": "1.20.4", "name": "1.20.4", "type": "release", "isMajor": True},
                {"id": "1.20.2", "name": "1.20.2", "type": "release", "isMajor": True},
                {"id": "1.20.1", "name": "1.20.1", "type": "release", "isMajor": True},
                {"id": "1.19.4", "name": "1.19.4", "type": "release", "isMajor": True},
                {"id": "1.19.2", "name": "1.19.2", "type": "release", "isMajor": True},
                {"id": "1.18.2", "name": "1.18.2", "type": "release", "isMajor": True},
                {"id": "1.17.1", "name": "1.17.1", "type": "release", "isMajor": True},
                {"id": "1.16.5", "name": "1.16.5", "type": "release", "isMajor": True},
                {"id": "1.15.2", "name": "1.15.2", "type": "release", "isMajor": True},
                {"id": "1.14.4", "name": "1.14.4", "type": "release", "isMajor": True},
                {"id": "1.12.2", "name": "1.12.2", "type": "release", "isMajor": True},
                {"id": "1.8.9", "name": "1.8.9 (Legacy PvP)", "type": "release", "isMajor": True},
                {"id": "1.7.10", "name": "1.7.10", "type": "release", "isMajor": True},
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
        
        # Calculate strict RAM bounds and dynamic G1GC flags
        ram_params = calculate_ram_parameters(max_ram=ram_gb, mc_version=inst.get("version", "26.2"))
        
        jvm_flags = [
            ram_params["xms_flag"],
            ram_params["xmx_flag"],
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:+UseG1GC",
            f"-XX:G1NewSizePercent={ram_params['new_size_pct']}",
            f"-XX:G1MaxNewSizePercent={ram_params['max_new_size_pct']}",
            f"-XX:G1ReservePercent={ram_params['reserve_pct']}",
            f"-XX:MaxGCPauseMillis={ram_params['pause_millis']}",
            f"-XX:G1HeapRegionSize={ram_params['region_size']}",
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

    def create_custom_instance(self, name, version="1.21.4", loader="fabric", ram_gb=8, enable_perf=True, icon="sir_crystal", mc_version=None, **kwargs):
        """Provisions a real, launchable Minecraft instance in Prism format with auto-downloading."""
        version = mc_version or version
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

        ram_params = calculate_ram_parameters(max_ram=ram_gb, mc_version=version)
        min_mb = ram_params["min_mb"]
        max_mb = ram_params["max_mb"]
        
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
        atomic_write_text(os.path.join(inst_path, "instance.cfg"), "\n".join(inst_cfg_lines) + "\n")

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
                "cachedVersion": "0.19.4" if any(k in version for k in ["26", "1.21"]) else "0.15.11",
                "uid": "net.fabricmc.fabric-loader",
                "version": "0.19.4" if any(k in version for k in ["26", "1.21"]) else "0.15.11"
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
        atomic_write_json(os.path.join(inst_path, "mmc-pack.json"), mmc_pack)

        new_id = f"custom-{inst_dir_name}"
        loader_title = "Fabric" if "fabric" in loader_clean else ("Forge" if "forge" in loader_clean else ("NeoForge" if "neo" in loader_clean else ("Quilt" if "quilt" in loader_clean else "Vanilla")))
        
        new_inst = {
            "id": new_id,
            "name": name,
            "version": f"{version} ({loader_title})",
            "loader": loader_title,
            "shader": "SIR Modern Shader.zip" if "fabric" in loader_clean else "OFF",
            "pack": "SIR Modern.zip",
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

    def _find_instance(self, inst_id):
        if not inst_id:
            return None
        # 1. Exact match by id
        inst = next((i for i in self.instances if i["id"] == inst_id), None)
        if inst:
            return inst
        # 2. Match by dir_name / instance_id
        inst = next((i for i in self.instances if (i.get("instance_id") == inst_id or i.get("dir_name") == inst_id)), None)
        if inst:
            return inst
        # 3. Match legacy aliases
        alias_map = {
            "sir-26-ultra": "26.2-ultra",
            "sir-26-balanced": "26.2-balanced",
            "sir-26-competitive": "26.2-performance",
            "sir-26-comp": "26.2-performance",
            "sir-26-vanilla": "26.2-ultra",
            "sir-189-pvp": "1.8.9-balanced",
            "sir-189-ultra": "1.8.9-ultra",
            "sir-189-balanced": "1.8.9-balanced",
            "sir-189-competitive": "1.8.9-performance",
            "1.8.9": "1.8.9-balanced",
            "26.2": "26.2-ultra"
        }
        target_id = alias_map.get(inst_id)
        if target_id:
            return next((i for i in self.instances if i["id"] == target_id), None)
        return None

    def delete_instance(self, inst_id):
        inst = self._find_instance(inst_id)
        if not inst:
            return {"success": False, "error": "Instance not found"}

        matched_id = inst["id"]
        dir_name = inst.get("instance_id") or inst.get("dir_name", "")
        target_path = os.path.join(self.instances_dir, dir_name)
        
        if os.path.isdir(target_path) and ("custom" in dir_name.lower() or "clone" in dir_name.lower()):
            try:
                shutil.rmtree(target_path)
            except Exception:
                pass

        self.instances = [i for i in self.instances if i["id"] != matched_id]
        existing_custom = self._load_custom_instances()
        existing_custom = [i for i in existing_custom if i.get("id") != matched_id]
        atomic_write_json(self._custom_instances_file(), existing_custom)

        if self.settings.get("selected_instance") == inst_id or self.settings.get("selected_instance") == matched_id:
            self.settings["selected_instance"] = "26.2-ultra"
            self.save_settings()

        return {"success": True, "deleted": matched_id, "message": f"✓ Deleted profile: {inst.get('name')}"}

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
                            download_file_resilient(url, local_zip, max_retries=2, timeout=12.0)
                            break
                        except Exception:
                            if os.path.exists(local_zip):
                                try: os.remove(local_zip)
                                except Exception: pass

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
                atomic_write_text(cfg_file, f"[General]\nConfigVersion=1.2\nname={inst.get('name', 'SIR Profile')}\niconKey=default\nInstanceType=OneSix\n")

            # 2. Per-Profile Mods Suite Healing & Obsolete Mod Pruning
            mods_dir = os.path.join(mc_game_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)
            for m_item in os.listdir(mods_dir):
                m_item_lower = m_item.lower()
                if "nyctography" in m_item_lower:
                    try:
                        os.remove(os.path.join(mods_dir, m_item))
                    except Exception:
                        pass
            existing_jars = [f for f in os.listdir(mods_dir) if f.endswith('.jar')]
            
            is_modern = "26" in mc_version or "21" in mc_version or "modern" in inst.get("id", "").lower()
            min_jars = 200 if is_modern else 45
            payload_name = "payload_mods_26.2.zip" if is_modern else "payload_mods_1.8.9.zip"
            
            if len(existing_jars) < min_jars:
                self._download_payload_if_missing(payload_name, mods_dir)

            # 3. Optical Shaders Suite Healing
            root_shaders = os.path.join(self.root_dir, "shaderpacks")
            if os.path.isdir(root_shaders) and len(os.listdir(root_shaders)) > 0:
                for tgt in [os.path.join(inst_dir, "shaderpacks"), os.path.join(mc_game_dir, "shaderpacks")]:
                    os.makedirs(tgt, exist_ok=True)
                    for sf in os.listdir(root_shaders):
                        s_src = os.path.join(root_shaders, sf)
                        s_dst = os.path.join(tgt, sf)
                        if not os.path.exists(s_dst) or os.path.getsize(s_dst) != os.path.getsize(s_src):
                            try: shutil.copy2(s_src, s_dst)
                            except Exception: pass
            else:
                self._download_payload_if_missing("payload_shaders.zip", os.path.join(self.root_dir, "shaderpacks"))
                self._download_payload_if_missing("payload_shaders.zip", os.path.join(mc_game_dir, "shaderpacks"))

            # 4. 3D POM Resource Packs Healing
            root_packs = os.path.join(self.root_dir, "resourcepacks")
            if os.path.isdir(root_packs) and len(os.listdir(root_packs)) > 0:
                for tgt in [os.path.join(inst_dir, "resourcepacks"), os.path.join(mc_game_dir, "resourcepacks")]:
                    os.makedirs(tgt, exist_ok=True)
                    for pf in os.listdir(root_packs):
                        p_src = os.path.join(root_packs, pf)
                        p_dst = os.path.join(tgt, pf)
                        if not os.path.exists(p_dst) or os.path.getsize(p_dst) != os.path.getsize(p_src):
                            try: shutil.copy2(p_src, p_dst)
                            except Exception: pass
            else:
                self._download_payload_if_missing("payload_packs.zip", os.path.join(self.root_dir, "resourcepacks"))
                self._download_payload_if_missing("payload_packs.zip", os.path.join(mc_game_dir, "resourcepacks"))

            # 5. High-Performance Configuration Presets Healing & Silent Memory Settings
            cfg_dir = os.path.join(mc_game_dir, "config")
            os.makedirs(cfg_dir, exist_ok=True)
            options_path = os.path.join(mc_game_dir, "options.txt")

            mem_cfg_path = os.path.join(cfg_dir, "memorysettings.json")
            if os.path.isfile(mem_cfg_path):
                try:
                    with open(mem_cfg_path, "r", encoding="utf-8") as mf:
                        m_data = json.load(mf)
                    if isinstance(m_data, dict):
                        m_data["disableWarnings"] = {"disableWarnings": True}
                        m_data["maximumClient"] = {"maximumClient": 32000}
                        atomic_write_json(mem_cfg_path, m_data)
                except Exception:
                    pass

            if not os.path.isfile(options_path):
                if is_modern:
                    atomic_write_text(options_path, "version:3465\ngamma:1.0\nmaxFramerate:260\nenableVsync:false\nfullscreen:true\nfov:0.0\nrenderDistance:12\nsimulationDistance:8\nguiScale:0\ngraphicsMode:0\nsmoothLighting:true\nentityDistanceScaling:1.0\nentityShadows:true\nresourcePacks:[\"vanilla\",\"file/SIR Modern.zip\"]\nincompatibleResourcePacks:[]\nsoundCategory_master:1.0\nsoundCategory_music:0.0\nbiomeBlendRadius:7\n")
                else:
                    atomic_write_text(options_path, "renderDistance:12\ngamma:1.0\nfullscreen:true\nmaxFps:260\nenableVsync:false\nresourcePacks:[\"SIR Legacy.zip\"]\n")

            if is_modern:
                iris_path = os.path.join(cfg_dir, "iris.properties")
                if not os.path.isfile(iris_path):
                    atomic_write_text(iris_path, "enableShaders=true\nshaderPack=SIR Modern Shader.zip\n")

            return True
        except Exception:
            return False

    def launch_instance(self, inst_id, account=None, on_log_callback=None, extra_args=None, server_ip=None, server_port=None):
        inst = self._find_instance(inst_id)
        if not inst:
            return self._launch_result(
                success=False,
                profile_id=inst_id,
                error_code="PROFILE_NOT_FOUND",
                error="The selected SIR profile does not exist.",
            )

        instance_id = inst.get("instance_id") or inst.get("dir_name", "")
        inst_dir = os.path.join(self.instances_dir, instance_id)
        
        # Determine actual game dir containing mods and configuration
        if os.path.isdir(os.path.join(inst_dir, "mods")) and len([f for f in os.listdir(os.path.join(inst_dir, "mods")) if f.endswith('.jar')]) > 0:
            mc_game_dir = inst_dir
        elif os.path.isdir(os.path.join(inst_dir, "minecraft", "mods")) and len([f for f in os.listdir(os.path.join(inst_dir, "minecraft", "mods")) if f.endswith('.jar')]) > 0:
            mc_game_dir = os.path.join(inst_dir, "minecraft")
        elif os.path.isdir(os.path.join(inst_dir, "minecraft")):
            mc_game_dir = os.path.join(inst_dir, "minecraft")
        else:
            mc_game_dir = inst_dir
        
        # Resolve exact Minecraft version and loader
        raw_ver = str(inst.get("version") or inst.get("mc_version") or "").strip()
        if "26" in raw_ver or "26" in instance_id or "26" in inst_id:
            mc_version = "26.2"
        elif "1.8" in raw_ver or "1.8" in instance_id or "189" in inst_id:
            mc_version = "1.8.9"
        elif raw_ver:
            match = re.search(r'(\d+\.\d+(\.\d+)?)', raw_ver)
            mc_version = match.group(1) if match else raw_ver
        else:
            mc_version = "1.21.4"

        raw_loader = str(inst.get("loader") or "").lower()
        if "vanilla" in raw_loader or "vanilla" in raw_ver.lower() or "vanilla" in inst.get("name", "").lower():
            loader_type = "vanilla"
        elif "forge" in raw_loader or "1.8" in mc_version:
            loader_type = "forge"
        else:
            loader_type = "fabric"
        
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
            account_name = str(account.get("displayName") or account.get("name") or account.get("username") or "Player").strip()
            account_type = str(account.get("accountType") or account.get("type") or "offline")
            account_dict = account
        elif account:
            account_name = str(account).strip()
            account_dict = {"displayName": account_name, "name": account_name, "type": "offline"}
        else:
            account_name = "Player"
            account_dict = {"displayName": "Player", "name": "Player", "type": "offline"}

        ram_gb = int(self.settings.get("ram_gb") or self.settings.get("ram_allocated_gb") or self.settings.get("allocated_ram") or 8)
        power_mode = str(self.settings.get("power_governor") or self.settings.get("power_mode") or "turbo")
        # 0. Lunar Client Target Launch Handler
        if "lunar" in str(inst_id).lower() or "lunar" in str(inst.get("name", "")).lower():
            lunar_exes = [
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Lunar Client", "Lunar Client.exe"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "lunarclient", "Lunar Client.exe"),
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Lunar Client", "Lunar Client.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Lunar Client", "Lunar Client.exe"),
                os.path.join(os.path.expanduser("~"), ".lunarclient", "offline", "multiver", "Lunar Client.exe"),
            ]
            lunar_found = next((lx for lx in lunar_exes if os.path.isfile(lx)), None)
            if lunar_found:
                try:
                    proc = subprocess.Popen([lunar_found], creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
                    return self._launch_result(
                        success=True,
                        profile_id=inst_id,
                        instance_id=instance_id,
                        mode=account_type,
                        pid=proc.pid,
                        message=f"✓ Launched official Lunar Client (PID {proc.pid})!",
                    )
                except Exception as lex:
                    return self._launch_result(
                        success=False,
                        profile_id=inst_id,
                        instance_id=instance_id,
                        mode=account_type,
                        error=f"Failed to start Lunar Client: {lex}"
                    )

        # 1. Primary: Direct Native JVM Launch Engine (100% Independent)
        native_res = None
        if self.native_runner:
            native_res = self.native_runner.launch(
                instance_dir=inst_dir,
                mc_version=mc_version,
                loader=loader_type,
                account=account_dict,
                ram_gb=ram_gb,
                power_mode=power_mode,
                on_log_callback=on_log_callback,
                server_ip=server_ip,
                server_port=server_port,
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
            cmd = [exe, "--dir", os.path.dirname(self.instances_dir), "--launch", instance_id]
            if account_name:
                if account_type == "microsoft":
                    cmd.extend(["--profile", account_name])
                else:
                    cmd.extend(["--offline", account_name])
            if server_ip:
                cmd.extend(["--server", str(server_ip)])
                if server_port:
                    cmd.extend(["--port", str(server_port)])
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
                err_msg = str(ex) if (native_res and native_res.get("success")) else (native_res.get("error") if (native_res and isinstance(native_res, dict)) else f"Could not launch Minecraft instance: {ex}")
                return self._launch_result(
                    success=False,
                    profile_id=inst_id,
                    instance_id=instance_id,
                    mode=account_type,
                    error_code="LAUNCH_FAILED",
                    error=err_msg,
                )

        # 3. Direct Failure Contract (ensures UI never hangs on 'Verifying & Launching...')
        err_detail = native_res.get("error") if (native_res and isinstance(native_res, dict)) else "Native Minecraft JVM launch engine could not find valid Java 21/8 runtime or instance libraries."
        return self._launch_result(
            success=False,
            profile_id=inst_id,
            instance_id=instance_id,
            mode=account_type,
            error_code="LAUNCH_FAILED",
            error=err_detail,
        )

    def open_instance_folder(self, inst_id="26.2-ultra"):
        inst = self._find_instance(inst_id)
        dir_name = (inst.get("instance_id") or inst.get("dir_name", "26.2-ultra")) if inst else ("1.8.9-ultra" if "189" in inst_id or "1.8" in inst_id else "26.2-ultra")
        candidates = [
            os.path.join(self.instances_dir, inst_id, "minecraft"),
            os.path.join(self.instances_dir, inst_id),
            os.path.join(self.instances_dir, dir_name, "minecraft"),
            os.path.join(self.instances_dir, dir_name),
        ]
        target_dir = next((c for c in candidates if os.path.exists(c)), None)
        if not target_dir:
            target_dir = os.path.join(self.instances_dir, dir_name)
            os.makedirs(target_dir, exist_ok=True)
        try:
            if sys.platform == "win32":
                opened = False
                try:
                    import ctypes
                    ret = ctypes.windll.shell32.ShellExecuteW(None, "explore", target_dir, None, None, 1)
                    if int(ret) > 32:
                        opened = True
                except Exception:
                    pass
                if not opened:
                    try:
                        os.startfile(target_dir)
                    except Exception:
                        subprocess.Popen(f'explorer "{target_dir}"', shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", target_dir])
            else:
                subprocess.Popen(["xdg-open", target_dir])
            return {"success": True, "path": target_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_instance_mods_folder(self, inst_id="26.2-ultra"):
        inst = self._find_instance(inst_id)
        dir_name = (inst.get("instance_id") or inst.get("dir_name", "26.2-ultra")) if inst else ("1.8.9-ultra" if "189" in inst_id or "1.8" in inst_id else "26.2-ultra")
        candidates = [
            os.path.join(self.instances_dir, inst_id, "minecraft", "mods"),
            os.path.join(self.instances_dir, inst_id, "mods"),
            os.path.join(self.instances_dir, dir_name, "minecraft", "mods"),
            os.path.join(self.instances_dir, dir_name, "mods"),
            os.path.join(self.root_dir, "SIR Package", "instances", inst_id, "minecraft", "mods"),
            os.path.join(self.root_dir, "SIR Package", "instances", dir_name, "minecraft", "mods"),
            os.path.join(self.root_dir, "instances", inst_id, "minecraft", "mods"),
            os.path.join(self.root_dir, "instances", dir_name, "minecraft", "mods"),
            os.path.join(self.root_dir, "mods")
        ]
        target_dir = next((c for c in candidates if os.path.exists(c)), None)
        if not target_dir:
            target_dir = candidates[0]
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception:
                target_dir = candidates[-1]
                os.makedirs(target_dir, exist_ok=True)
        target_dir = os.path.normpath(target_dir)
        try:
            if sys.platform == "win32":
                opened = False
                try:
                    import ctypes
                    ret = ctypes.windll.shell32.ShellExecuteW(None, "explore", target_dir, None, None, 1)
                    if int(ret) > 32:
                        opened = True
                except Exception:
                    pass
                if not opened:
                    try:
                        os.startfile(target_dir)
                    except Exception:
                        subprocess.Popen(f'explorer "{target_dir}"', shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", target_dir])
            else:
                subprocess.Popen(["xdg-open", target_dir])
            return {"success": True, "path": target_dir}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def apply_video_preset(self, inst_id="sir-26-ultra", preset_name="balanced"):
        """Applies Display, Quality, and Performance presets directly across Minecraft, Sodium/OptiFine, and Iris/Shader configs."""
        inst = None
        if isinstance(self.instances, list):
            for i in self.instances:
                if isinstance(i, dict) and (i.get("id") == inst_id or i.get("instance_id") == inst_id or i.get("dir_name") == inst_id or i.get("name") == inst_id):
                    inst = i
                    break

        dir_name = None
        if inst:
            dir_name = inst.get("instance_id") or inst.get("dir_name") or inst.get("id")

        if not dir_name:
            # Check if direct folder in instances_dir exists
            candidate_dir = os.path.join(self.instances_dir, str(inst_id))
            if os.path.isdir(candidate_dir):
                dir_name = str(inst_id)
            elif "189" in str(inst_id) or "1.8" in str(inst_id):
                dir_name = "1.8.9"
            elif "ultra" in str(inst_id) and os.path.isdir(os.path.join(self.instances_dir, "26.2-ultra")):
                dir_name = "26.2-ultra"
            elif str(inst_id).startswith("custom-") and os.path.isdir(os.path.join(self.instances_dir, str(inst_id))):
                dir_name = str(inst_id)
            else:
                dir_name = "26.2"

        inst_root = os.path.join(self.instances_dir, dir_name)
        if not os.path.exists(inst_root):
            # Check if inst_id folder exists directly
            if os.path.isdir(os.path.join(self.instances_dir, str(inst_id))):
                dir_name = str(inst_id)
                inst_root = os.path.join(self.instances_dir, dir_name)
            else:
                os.makedirs(os.path.join(inst_root, "minecraft"), exist_ok=True)

        target_dirs = [
            os.path.join(self.instances_dir, dir_name),
            os.path.join(self.instances_dir, dir_name, "minecraft")
        ]

        # Filter to existing directories or create the minecraft directory
        existing_targets = [d for d in target_dirs if os.path.exists(d)]
        if not existing_targets:
            mc_dir = os.path.join(self.instances_dir, dir_name, "minecraft")
            os.makedirs(mc_dir, exist_ok=True)
            existing_targets = [mc_dir]

        preset_clean = str(preset_name).lower().strip()
        is_189 = "1.8" in dir_name or "189" in str(inst_id) or (inst and ("1.8" in str(inst.get("version", "")) or inst.get("category") == "legacy"))
        applied_files = []

        for g_dir in existing_targets:
            cfg_dir = os.path.join(g_dir, "config")
            os.makedirs(cfg_dir, exist_ok=True)
            options_file = os.path.join(g_dir, "options.txt")

            # Read existing options to avoid destroying audio/controls/narrator
            existing_options = {}
            if os.path.exists(options_file):
                try:
                    with open(options_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if ":" in line:
                                parts = line.strip().split(":", 1)
                                existing_options[parts[0]] = parts[1]
                except Exception:
                    pass

            if is_189:
                cur_fps = existing_options.get("maxFps", "")
                try:
                    fps_val = int(cur_fps)
                    target_fps = str(fps_val) if fps_val > 0 else "260"
                except (ValueError, TypeError):
                    target_fps = "260"

                new_opts = {
                    "guiScale": existing_options.get("guiScale", "2"),
                    "gamma": existing_options.get("gamma", "1.0"),
                    "fullscreen": existing_options.get("fullscreen", "false"),
                    "maxFps": target_fps,
                    "enableVsync": existing_options.get("enableVsync", "false"),
                    "resourcePacks": existing_options.get("resourcePacks", '["SIR Legacy.zip"]')
                }
                if "potato" in preset_clean or "low" in preset_clean:
                    new_opts.update({"renderDistance": "4", "maxFps": target_fps, "particles": "2", "smoothLighting": "false", "clouds": "false", "anisotropicFiltering": "1", "fancyGraphics": "false", "ao": "0"})
                    of_content = "ofRenderDistanceChunks:4\nofFastRender:true\nofFastMath:true\nofSmoothFps:false\nofSmoothWorld:false\nofAo:0\nofClouds:3\nofTrees:1\nofDroppedItems:1\nofDynamicLights:3\nofDynamicFov:false\n"
                    shader_content = "shaderPack=OFF\n"
                elif "performance" in preset_clean or "competitive" in preset_clean or "pvp" in preset_clean or "comp" in preset_clean:
                    new_opts.update({"renderDistance": "8", "maxFps": target_fps, "particles": "2", "smoothLighting": "false", "clouds": "false", "anisotropicFiltering": "1", "fancyGraphics": "false", "ao": "1"})
                    of_content = "ofRenderDistanceChunks:8\nofFastRender:true\nofFastMath:true\nofSmoothFps:false\nofSmoothWorld:false\nofAo:1\nofClouds:3\nofTrees:1\nofDroppedItems:1\nofDynamicLights:3\n"
                    shader_content = "shaderPack=OFF\n"
                elif "ultra" in preset_clean or "extreme" in preset_clean or "high" in preset_clean:
                    new_opts.update({"renderDistance": "16", "maxFps": target_fps, "particles": "0", "smoothLighting": "true", "clouds": "true", "anisotropicFiltering": "8", "fancyGraphics": "true", "ao": "2"})
                    of_content = "ofRenderDistanceChunks:16\nofFastRender:false\nofFastMath:false\nofSmoothFps:true\nofSmoothWorld:true\nofAo:2\nofClouds:1\nofTrees:2\nofDroppedItems:2\nofDynamicLights:1\n"
                    shader_content = "shaderPack=SIR Legacy Shader.zip\n"
                else:  # balanced
                    new_opts.update({"renderDistance": "12", "maxFps": target_fps, "particles": "0", "smoothLighting": "true", "clouds": "true", "anisotropicFiltering": "4", "fancyGraphics": "true", "ao": "2"})
                    of_content = "ofRenderDistanceChunks:12\nofFastRender:false\nofFastMath:true\nofSmoothFps:true\nofSmoothWorld:true\nofAo:2\nofClouds:1\nofTrees:2\nofDroppedItems:2\nofDynamicLights:1\n"
                    shader_content = "shaderPack=SIR Legacy Shader.zip\n"

                existing_options.update(new_opts)
                options_str = "\n".join(f"{k}:{v}" for k, v in existing_options.items()) + "\n"
                atomic_write_text(options_file, options_str)
                atomic_write_text(os.path.join(g_dir, "optionsof.txt"), of_content)
                atomic_write_text(os.path.join(g_dir, "optionsshaders.txt"), shader_content)

                for fname in ["options.txt", "optionsof.txt", "optionsshaders.txt"]:
                    if fname not in applied_files:
                        applied_files.append(fname)
            else:
                # Modern 26.2 / 1.21.x
                cur_fps = existing_options.get("maxFramerate", "")
                try:
                    fps_val = int(cur_fps)
                    target_fps = str(fps_val) if fps_val > 0 else "260"
                except (ValueError, TypeError):
                    target_fps = "260"

                if "maxFps" in existing_options:
                    del existing_options["maxFps"]

                new_opts = {
                    "version": "3465",
                    "guiScale": "2",
                    "gamma": "0.0" if ("balanced" in preset_clean or "ultra" in preset_clean) else "1.0",
                    "maxFramerate": target_fps,
                    "enableVsync": "false",
                    "autoSaveIndicator": "true",
                    "attackIndicator": "1",
                    "resourcePacks": '["vanilla","file/SIR Modern.zip"]',
                    "onboardAccessibility": "false"  # Explicitly disable narrator screen
                }

                if "potato" in preset_clean or "low" in preset_clean:
                    new_opts.update({
                        "renderDistance": "4", "simulationDistance": "4", "smoothLighting": "false",
                        "graphicsMode": "1", "biomeBlendRadius": "0", "entityDistanceScaling": "0.5",
                        "entityShadows": "false", "particles": "2", "mipmapLevels": "0", "clouds": "false"
                    })
                    sodium_cfg = {
                        "quality": {"leaves_quality": "FAST", "weather_quality": "FAST", "cloud_distance": 16, "menu_background_blur": 0, "improved_transparency": False, "weather_radius": 2},
                        "performance": {"chunk_builder": "IMMEDIATE", "animate_only_visible_textures": True},
                        "notifications": {"hide_donation_prompt": True}
                    }
                    iris_content = "enableShaders=false\nshaderPack=OFF\n"
                elif "performance" in preset_clean or "competitive" in preset_clean or "pvp" in preset_clean or "comp" in preset_clean:
                    new_opts.update({
                        "renderDistance": "8", "simulationDistance": "6", "smoothLighting": "false",
                        "graphicsMode": "1", "biomeBlendRadius": "3", "entityDistanceScaling": "0.8",
                        "entityShadows": "false", "particles": "2", "mipmapLevels": "0", "clouds": "false"
                    })
                    sodium_cfg = {
                        "quality": {"leaves_quality": "FAST", "weather_quality": "FAST", "cloud_distance": 32, "menu_background_blur": 0, "improved_transparency": False, "weather_radius": 5},
                        "performance": {"chunk_builder": "IMMEDIATE", "animate_only_visible_textures": True},
                        "notifications": {"hide_donation_prompt": True}
                    }
                    iris_content = "enableShaders=false\nshaderPack=OFF\n"
                elif "ultra" in preset_clean or "extreme" in preset_clean or "high" in preset_clean:
                    new_opts.update({
                        "renderDistance": "16", "simulationDistance": "10", "smoothLighting": "true",
                        "graphicsMode": "0", "biomeBlendRadius": "15", "entityDistanceScaling": "1.5",
                        "entityShadows": "true", "particles": "0", "mipmapLevels": "4", "clouds": "fancy"
                    })
                    sodium_cfg = {
                        "quality": {"leaves_quality": "CUTOUT", "weather_quality": "HIGH", "cloud_distance": 128, "menu_background_blur": 5, "improved_transparency": True, "weather_radius": 10},
                        "performance": {"chunk_builder": "SEMI_BLOCKING", "animate_only_visible_textures": True},
                        "notifications": {"hide_donation_prompt": True}
                    }
                    iris_content = "enableShaders=true\nshaderPack=SIR Modern Shader.zip\n"
                else:  # balanced
                    new_opts.update({
                        "renderDistance": "12", "simulationDistance": "8", "smoothLighting": "true",
                        "graphicsMode": "0", "biomeBlendRadius": "7", "entityDistanceScaling": "1.0",
                        "entityShadows": "true", "particles": "0", "mipmapLevels": "4", "clouds": "fancy"
                    })
                    sodium_cfg = {
                        "quality": {"leaves_quality": "CUTOUT", "weather_quality": "HIGH", "cloud_distance": 128, "menu_background_blur": 5, "improved_transparency": True, "weather_radius": 10},
                        "performance": {"chunk_builder": "SEMI_BLOCKING", "animate_only_visible_textures": True},
                        "notifications": {"hide_donation_prompt": True}
                    }
                    iris_content = "enableShaders=true\nshaderPack=SIR Modern Shader.zip\n"

                existing_options.update(new_opts)
                options_str = "\n".join(f"{k}:{v}" for k, v in existing_options.items()) + "\n"
                atomic_write_text(options_file, options_str)
                atomic_write_json(os.path.join(cfg_dir, "sodium-options.json"), sodium_cfg)
                atomic_write_text(os.path.join(cfg_dir, "iris.properties"), iris_content)

                for fname in ["options.txt", "sodium-options.json", "iris.properties"]:
                    if fname not in applied_files:
                        applied_files.append(fname)

        preset_title = "Visuals (High Fidelity)" if ("ultra" in preset_clean or "extreme" in preset_clean) else ("Performance (Low Latency)" if ("performance" in preset_clean or "comp" in preset_clean or "potato" in preset_clean or "low" in preset_clean) else "Balanced Standard")
        target_label = inst.get("name") if inst else dir_name
        return {
            "success": True,
            "preset": preset_clean,
            "applied": applied_files,
            "error": "",
            "message": f"✓ Applied {preset_title} preset to {target_label}!"
        }

    def auto_fix_incompatible_mods(self, inst_id, conflicting_mods=None):
        """Automatically disables or fixes incompatible Fabric mods for the given instance (Lunar-style auto-fix)."""
        inst = self._find_instance(inst_id)
        if not inst:
            return {"success": False, "error": f"Instance '{inst_id}' not found."}

        inst_dir = os.path.join(self.instances_dir, inst.get("instance_id") or inst.get("dir_name", inst_id))
        mods_dir = os.path.join(inst_dir, "minecraft", "mods") if os.path.isdir(os.path.join(inst_dir, "minecraft", "mods")) else os.path.join(inst_dir, "mods")
        
        fixed_mods = []
        if not os.path.isdir(mods_dir):
            return {"success": False, "error": f"Mods folder not found: {mods_dir}"}

        # If conflicting_mods not provided, inspect latest.log with CrashAnalyzer
        if not conflicting_mods:
            log_candidates = [
                os.path.join(inst_dir, "logs", "latest.log"),
                os.path.join(inst_dir, "minecraft", "logs", "latest.log"),
            ]
            for lp in log_candidates:
                if os.path.isfile(lp):
                    try:
                        with open(lp, "r", encoding="utf-8", errors="ignore") as f:
                            diag = CrashAnalyzer.diagnose_crash(f.read())
                            conflicting_mods = diag.get("conflicting_mods", [])
                            if conflicting_mods:
                                break
                    except Exception:
                        pass

        if not conflicting_mods:
            return {"success": False, "error": "No conflicting mods identified to auto-fix."}

        for fname in os.listdir(mods_dir):
            if fname.endswith(".jar"):
                clean_name = fname.lower().replace("-", "_")
                for c_mod in conflicting_mods:
                    c_clean = c_mod.lower().replace("-", "_")
                    if c_clean in clean_name:
                        src_path = os.path.join(mods_dir, fname)
                        dst_path = os.path.join(mods_dir, fname + ".disabled")
                        try:
                            if os.path.exists(dst_path):
                                os.remove(dst_path)
                            os.rename(src_path, dst_path)
                            fixed_mods.append(fname)
                        except Exception as e:
                            print(f"[AutoFix] Error disabling {fname}: {e}")

        return {
            "success": len(fixed_mods) > 0,
            "fixed_mods": fixed_mods,
            "message": f"✓ Successfully resolved {len(fixed_mods)} incompatible mod(s): {', '.join(fixed_mods)}" if fixed_mods else "Could not disable mods.",
        }

