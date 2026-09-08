"""Native Independent Minecraft Launch Engine & Universal Version Downloader for SIR Launcher.

- Resolves JVM arguments & classpaths dynamically from Mojang, Fabric, and MultiMC/Prism manifests.
- Evaluates Mojang OS rules and builds ordered classpaths without conflicts.
- Dynamic Pre-Launch Natives Extraction for LWJGL 2 / LWJGL 3 with file-lock recovery.
- Strictly honors user-selected RAM boundaries (-Xmx/-Xms) with dynamic G1GC nursery and region sizing.
- Non-blocking real-time stdout/stderr log streaming with circular ring buffer and crash detection.
- Directly executes Minecraft via subprocess with zero background launcher dependencies.
"""

from __future__ import annotations

import concurrent.futures
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import uuid
import zipfile
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from shared_core.runtime import atomic_write_text, download_file_resilient
except ImportError:
    try:
        from runtime import atomic_write_text, download_file_resilient
    except ImportError:
        def atomic_write_text(p, c):
            with open(p, "w", encoding="utf-8") as f: f.write(c)
        def download_file_resilient(url, dst, **k):
            import urllib.request
            urllib.request.urlretrieve(url, dst)

try:
    from .crash_analyzer import CrashAnalyzer
    from .java_service import JavaService
    from .logs_service import ProcessLogStreamer
except (ImportError, ValueError):
    try:
        from crash_analyzer import CrashAnalyzer
        from java_service import JavaService
        from logs_service import ProcessLogStreamer
    except ImportError:
        from launcher_core.crash_analyzer import CrashAnalyzer
        from launcher_core.java_service import JavaService
        from launcher_core.logs_service import ProcessLogStreamer


def _maven_to_path(name: str, classifier: str = "") -> str:
    """Converts maven coordinates 'group:name:version[:classifier]' to relative jar path."""
    parts = name.split(":")
    if len(parts) < 3:
        return ""
    group, artifact, version = parts[0], parts[1], parts[2]
    classif = parts[3] if len(parts) > 3 else classifier
    group_path = group.replace(".", "/")
    if classif:
        jar_name = f"{artifact}-{version}-{classif}.jar"
    else:
        jar_name = f"{artifact}-{version}.jar"
    return os.path.join(group_path, artifact, version, jar_name)


def _parse_to_mb(val: int | float | str, default_mb: int = 8192) -> int:
    """Parses memory specifications (int, float, '8G', '8GB', '4096M', '4096MB', '4 GiB') into integer Megabytes."""
    if val is None:
        return default_mb
    if isinstance(val, (int, float)):
        if val <= 0:
            return 256
        # If <= 64, treat as GB; otherwise treat as MB
        if val <= 64:
            return max(256, int(round(val * 1024)))
        return max(256, int(round(val)))

    val_str = str(val).strip()
    if not val_str:
        return default_mb

    # Check for negative numbers or zero in string form
    m_neg = re.match(r"^-\d+(?:\.\d+)?\s*(?:[gG]|[mM]|[kK])?.*$", val_str)
    if m_neg:
        return 256

    # Match GB / GiB / G
    m_g = re.match(r"^(\d+(?:\.\d+)?)\s*(?:g|gb|gib)$", val_str, re.IGNORECASE)
    if m_g:
        num = float(m_g.group(1))
        if num <= 0:
            return 256
        return max(256, int(round(num * 1024)))

    # Match MB / MiB / M or plain numeric string
    m_m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:m|mb|mib)?$", val_str, re.IGNORECASE)
    if m_m:
        val_num = float(m_m.group(1))
        if val_num <= 0:
            return 256
        has_m_unit = bool(re.search(r"[mM]", val_str))
        if val_num <= 64 and not has_m_unit:
            return max(256, int(round(val_num * 1024)))
        return max(256, int(round(val_num)))

    # Match KB / KiB / K
    m_k = re.match(r"^(\d+(?:\.\d+)?)\s*(?:k|kb|kib)$", val_str, re.IGNORECASE)
    if m_k:
        val_num = float(m_k.group(1))
        if val_num <= 0:
            return 256
        return max(256, int(round(val_num / 1024)))

    return default_mb


def calculate_ram_parameters(
    max_ram: int | float | str = 8,
    min_ram: Optional[int | float | str] = None,
    mc_version: str = "26.2",
) -> Dict[str, Any]:
    """Strictly parses and normalizes RAM boundaries (-Xmx/-Xms) without arbitrary upward clamps."""
    # 1. Parse max_ram to MB
    max_mb = _parse_to_mb(max_ram, default_mb=8192)

    # 2. Parse min_ram to MB (strictly bounded: 256MB <= min_mb <= max_mb)
    if min_ram is not None:
        min_mb = _parse_to_mb(min_ram, default_mb=max(256, max_mb // 2))
        min_mb = max(256, min(min_mb, max_mb))
    else:
        # Default policy: min_mb = max(512, max_mb // 2) if max_mb >= 1024 else max_mb
        min_mb = max(512, max_mb // 2) if max_mb >= 1024 else max_mb
        min_mb = min(min_mb, max_mb)

    # 3. Format -Xms and -Xmx arguments
    xms_arg = f"-Xms{min_mb // 1024}G" if min_mb % 1024 == 0 else f"-Xms{min_mb}M"
    xmx_arg = f"-Xmx{max_mb // 1024}G" if max_mb % 1024 == 0 else f"-Xmx{max_mb}M"

    # 4. Dynamic G1GC Nursery and Region Parameters
    max_gb = max_mb / 1024.0
    if max_gb <= 3.0:
        new_size_pct = 20
        max_new_size_pct = 30
        reserve_pct = 10
        region_size = "1M" if max_gb < 2.0 else "2M"
    elif max_gb <= 8.0:
        new_size_pct = 30
        max_new_size_pct = 40
        reserve_pct = 15
        region_size = "4M" if max_gb <= 4.0 else "8M"
    elif max_gb <= 16.0:
        new_size_pct = 40
        max_new_size_pct = 50
        reserve_pct = 20
        region_size = "16M"
    else:
        new_size_pct = 50
        max_new_size_pct = 60
        reserve_pct = 20
        region_size = "32M"

    is_legacy_189 = any(k in str(mc_version) for k in ["1.8", "1.7"])
    pause_millis = 200 if is_legacy_189 else 50

    return {
        "min_mb": min_mb,
        "max_mb": max_mb,
        "xms_flag": xms_arg,
        "xmx_flag": xmx_arg,
        "new_size_pct": new_size_pct,
        "max_new_size_pct": max_new_size_pct,
        "reserve_pct": reserve_pct,
        "region_size": region_size,
        "pause_millis": pause_millis,
    }


class NativeMinecraftRunner:
    """Independent Native Minecraft Launch & Download Engine."""

    def __init__(self, root_dir: str, state_dir: Optional[str] = None):
        self.root_dir = os.path.abspath(root_dir)
        self.state_dir = os.path.abspath(state_dir or self.root_dir)
        self.current_status = "Idle"
        self.download_progress = 0
        self.java_service = JavaService(self.root_dir)
        self.active_streamers: Dict[int, ProcessLogStreamer] = {}

        # Primary search directories for libraries and assets
        self.libraries_dirs = [
            os.path.join(self.root_dir, "libraries"),
            os.path.join(self.root_dir, "SIR Launcher", "libraries"),
            os.path.join(self.state_dir, "libraries"),
            os.path.expandvars(r"%APPDATA%\.minecraft\libraries"),
            os.path.expandvars(r"%APPDATA%\SIR ModPack\libraries"),
            os.path.expandvars(r"%APPDATA%\PrismLauncher\libraries"),
        ]

        self.assets_dirs = [
            os.path.join(self.root_dir, "assets"),
            os.path.join(self.root_dir, "SIR Launcher", "assets"),
            os.path.join(self.state_dir, "assets"),
            os.path.expandvars(r"%APPDATA%\.minecraft\assets"),
            os.path.expandvars(r"%APPDATA%\SIR ModPack\assets"),
        ]

        self.versions_dirs = [
            os.path.join(self.root_dir, "versions"),
            os.path.join(self.root_dir, "SIR Launcher", "versions"),
            os.path.join(self.state_dir, "versions"),
            os.path.expandvars(r"%APPDATA%\.minecraft\versions"),
            os.path.expandvars(r"%APPDATA%\SIR ModPack\versions"),
        ]

    def get_optimal_hardware_settings(self) -> Dict[str, Any]:
        """Automatically calculates optimal RAM and JVM flags based on the user's PC hardware."""
        total_ram_gb = 8
        if sys.platform == "win32":
            try:
                import ctypes

                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                total_ram_gb = int(round(stat.ullTotalPhys / (1024**3)))
            except Exception:
                total_ram_gb = 8

        if total_ram_gb <= 4:
            allocated_gb = 2
            min_gb = 1
        elif total_ram_gb <= 8:
            allocated_gb = 4
            min_gb = 2
        elif total_ram_gb <= 16:
            allocated_gb = 8
            min_gb = 4
        elif total_ram_gb <= 24:
            allocated_gb = 10
            min_gb = 4
        else:
            allocated_gb = 12
            min_gb = 6

        return {
            "total_system_ram_gb": total_ram_gb,
            "recommended_allocated_gb": allocated_gb,
            "min_ram_gb": min_gb,
            "cpu_threads": os.cpu_count() or 8,
        }

    def detect_java(self, version_hint: int = 25) -> str:
        """Finds best matching Java binary for the required Minecraft version via JavaService."""
        ver_str = "1.8.9" if version_hint <= 8 else "26.2"
        best = self.java_service.get_best_runtime_for_version(ver_str)
        if best and best.get("path") and os.path.isfile(best["path"]):
            return best["path"]

        which_j = shutil.which("javaw.exe") or shutil.which("java.exe") or shutil.which("java")
        return which_j or "java"

    def ensure_java_runtime(
        self,
        version_hint: int = 25,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> str:
        """Ensures a verified Java runtime exists on the PC; auto-downloads OpenJDK if completely missing."""
        return self.java_service.ensure_java_runtime(version_hint, progress_callback)

    def inspect_instance_config(self, instance_dir: str) -> Dict[str, Any]:
        """Parses mmc-pack.json and instance.cfg to extract components, memory bounds, and JVM overrides."""
        result: Dict[str, Any] = {
            "components": [],
            "loader": "",
            "loader_version": "",
            "mc_version": "",
            "min_ram_mb": None,
            "max_ram_mb": None,
            "java_path": "",
            "jvm_args": "",
        }
        if not instance_dir or not os.path.isdir(instance_dir):
            return result

        # Search candidates: instance_dir, parent dir (if instance_dir is minecraft/), and child minecraft/
        search_dirs = [instance_dir]
        parent = os.path.dirname(instance_dir)
        if parent and os.path.isdir(parent) and parent not in search_dirs:
            search_dirs.append(parent)
        child_mc = os.path.join(instance_dir, "minecraft")
        if os.path.isdir(child_mc) and child_mc not in search_dirs:
            search_dirs.append(child_mc)

        # 1. Parse mmc-pack.json
        for s_dir in search_dirs:
            pack_json_path = os.path.join(s_dir, "mmc-pack.json")
            if os.path.isfile(pack_json_path):
                try:
                    with open(pack_json_path, "r", encoding="utf-8") as f:
                        pack = json.load(f)
                        comps = pack.get("components", [])
                        result["components"] = comps
                        for comp in comps:
                            uid = comp.get("uid", "")
                            ver = comp.get("version", "")
                            if uid == "net.minecraft":
                                result["mc_version"] = ver
                            elif uid == "net.fabricmc.fabric-loader":
                                result["loader"] = "fabric"
                                result["loader_version"] = ver
                            elif uid == "net.minecraftforge":
                                result["loader"] = "forge"
                                result["loader_version"] = ver
                            elif uid == "org.lwjgl3":
                                result["lwjgl_version"] = ver
                    break
                except Exception:
                    pass

        # 2. Parse instance.cfg
        for s_dir in search_dirs:
            cfg_path = os.path.join(s_dir, "instance.cfg")
            if os.path.isfile(cfg_path):
                try:
                    with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            if k == "MinMemAlloc":
                                try:
                                    result["min_ram_mb"] = int(v)
                                except ValueError:
                                    pass
                            elif k == "MaxMemAlloc":
                                try:
                                    result["max_ram_mb"] = int(v)
                                except ValueError:
                                    pass
                            elif k == "JavaPath":
                                result["java_path"] = v.strip().strip('"').strip("'")
                            elif k == "JvmArgs":
                                result["jvm_args"] = v.strip().strip('"').strip("'")
                            elif k == "IntendedVersion" and not result["mc_version"]:
                                result["mc_version"] = v.strip().strip('"').strip("'")
                    break
                except Exception:
                    pass

        return result

    def evaluate_library_rules(
        self,
        rules: List[Dict[str, Any]],
        target_os: str = "windows",
        target_arch: str = "x64",
    ) -> bool:
        """Evaluates Mojang library rule conditions ('allow'/'disallow' by OS and features)."""
        if not rules:
            return True

        allow = False
        for rule in rules:
            action = rule.get("action", "allow")
            os_rule = rule.get("os", {})
            features_rule = rule.get("features", {})

            # If rule specifies features not satisfied, skip
            if features_rule:
                continue

            if not os_rule:
                allow = (action == "allow")
                continue

            rule_os_name = os_rule.get("name", "")
            rule_os_arch = os_rule.get("arch", "")

            os_match = (not rule_os_name) or (rule_os_name.lower() == target_os.lower())
            arch_match = (not rule_os_arch) or (rule_os_arch.lower() == target_arch.lower())

            if os_match and arch_match:
                allow = (action == "allow")

        return allow

    def resolve_maven_coordinate_path(self, coordinate: str, classifier: str = "") -> Optional[str]:
        """Scans all configured library search roots for a matching jar."""
        rel_p = _maven_to_path(coordinate, classifier)
        if not rel_p:
            return None

        for lib_dir in self.libraries_dirs:
            full_p = os.path.join(lib_dir, rel_p.replace("/", os.sep))
            if os.path.isfile(full_p):
                return os.path.normpath(full_p)

        return None

    def resolve_version_json(
        self,
        mc_version: str,
        loader: str = "",
        instance_dir: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Finds and parses the version.json manifest for the given Minecraft version."""
        # Check instance folder first
        if instance_dir:
            for cand_rel in ["version.json", f"{mc_version}.json", "minecraft/version.json"]:
                v_cand = os.path.join(instance_dir, cand_rel)
                if os.path.isfile(v_cand):
                    try:
                        with open(v_cand, "r", encoding="utf-8") as f:
                            return json.load(f)
                    except Exception:
                        pass

        version_names = []
        if loader == "fabric":
            version_names.extend([f"Fabric {mc_version}", f"fabric-{mc_version}"])
        elif loader == "forge":
            version_names.extend([f"Forge {mc_version}", f"forge-{mc_version}"])
        version_names.extend([
            mc_version,
            "26.2",
            "1.21.4",
            "1.8.9",
            f"Fabric {mc_version}",
            f"Forge {mc_version}",
            "Forge 1.8.9",
        ])

        for v_dir in self.versions_dirs:
            if not os.path.isdir(v_dir):
                continue
            for v_name in version_names:
                json_path = os.path.join(v_dir, v_name, f"{v_name}.json")
                if os.path.isfile(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            return json.load(f)
                    except Exception:
                        pass
                alt_json = os.path.join(v_dir, f"{v_name}.json")
                if os.path.isfile(alt_json):
                    try:
                        with open(alt_json, "r", encoding="utf-8") as f:
                            return json.load(f)
                    except Exception:
                        pass
        return None

    def extract_natives(
        self,
        version_json: Dict[str, Any],
        mc_version: str = "26.2",
        target_dir: Optional[str] = None,
        force_reextract: bool = False,
    ) -> str:
        """Extracts platform-matching native DLLs into target_dir with Windows file-lock collision recovery."""
        is_legacy = any(k in str(mc_version) for k in ["1.8", "1.7"])

        if not target_dir:
            target_dir = os.path.join(self.state_dir, "natives", mc_version)

        os.makedirs(target_dir, exist_ok=True)

        # Check if essential DLLs already exist
        if not force_reextract:
            if is_legacy:
                has_lwjgl = any(
                    os.path.isfile(os.path.join(target_dir, d))
                    for d in ["lwjgl64.dll", "lwjgl.dll"]
                )
                has_openal = any(
                    os.path.isfile(os.path.join(target_dir, d))
                    for d in ["OpenAL64.dll", "OpenAL32.dll"]
                )
                if has_lwjgl and has_openal:
                    return target_dir
            else:
                has_modern_lwjgl = os.path.isfile(os.path.join(target_dir, "lwjgl.dll"))
                has_glfw = os.path.isfile(os.path.join(target_dir, "glfw.dll"))
                if has_modern_lwjgl and has_glfw:
                    return target_dir

        # Collect native JARs to extract
        native_jars: List[str] = []

        # 1. From version_json libraries
        for lib in version_json.get("libraries", []):
            rules = lib.get("rules", [])
            if rules and not self.evaluate_library_rules(rules, "windows", "x64"):
                continue

            classifiers = lib.get("downloads", {}).get("classifiers", {})
            for c_key in ["natives-windows", "natives-windows-64", "natives-windows-x86_64"]:
                c_art = classifiers.get(c_key)
                if c_art:
                    rel_p = c_art.get("path") or _maven_to_path(lib.get("name", ""), c_key)
                    if rel_p:
                        for lib_dir in self.libraries_dirs:
                            full_p = os.path.join(lib_dir, rel_p.replace("/", os.sep))
                            if os.path.isfile(full_p) and full_p not in native_jars:
                                native_jars.append(full_p)

            # Natives classifier in natives field
            natives_map = lib.get("natives", {})
            win_classifier = natives_map.get("windows")
            if win_classifier:
                win_classifier = win_classifier.replace("${arch}", "64")
                rel_p = _maven_to_path(lib.get("name", ""), win_classifier)
                if rel_p:
                    for lib_dir in self.libraries_dirs:
                        full_p = os.path.join(lib_dir, rel_p.replace("/", os.sep))
                        if os.path.isfile(full_p) and full_p not in native_jars:
                            native_jars.append(full_p)

        # 2. Filesystem search across library roots filtered strictly by version archetype
        for lib_dir in self.libraries_dirs:
            if not os.path.isdir(lib_dir):
                continue
            for root, dirs, files in os.walk(lib_dir):
                for f in files:
                    if not f.endswith(".jar"):
                        continue
                    f_low = f.lower()
                    if "natives-windows" not in f_low and "natives_windows" not in f_low:
                        continue

                    # Filter out non-x64 architectures
                    if "-x86.jar" in f_low or "-arm64.jar" in f_low or "-arm32.jar" in f_low:
                        continue

                    if is_legacy:
                        # Only accept LWJGL 2 / legacy libraries
                        if any(k in f_low for k in ["lwjgl-platform", "jinput-platform", "twitch-platform"]):
                            full_p = os.path.join(root, f)
                            if full_p not in native_jars:
                                native_jars.append(full_p)
                    else:
                        # Only accept LWJGL 3 / modern libraries; reject LWJGL 2 to avoid 32-bit lwjgl.dll overwrite
                        if any(k in f_low for k in ["lwjgl-platform", "jinput-platform", "twitch-platform"]):
                            continue
                        full_p = os.path.join(root, f)
                        if full_p not in native_jars:
                            native_jars.append(full_p)

        # Extraction with locked file recovery
        destination_dir = target_dir
        lock_occurred = False

        for n_jar in native_jars:
            try:
                with zipfile.ZipFile(n_jar, "r") as z:
                    for member in z.namelist():
                        if member.lower().endswith(".dll") and not member.startswith("META-INF"):
                            dest_file = os.path.join(destination_dir, os.path.basename(member))
                            try:
                                with z.open(member) as source_f, open(dest_file, "wb") as target_f:
                                    shutil.copyfileobj(source_f, target_f)
                            except (PermissionError, OSError) as perm_ex:
                                # Windows WinError 32 / PermissionError on locked DLL
                                lock_occurred = True
                                break
                    if lock_occurred:
                        break
            except Exception:
                pass

        if lock_occurred:
            # Fallback to unique process-isolated directory
            fallback_dir = os.path.join(
                tempfile.gettempdir(),
                f"sir_natives_{mc_version}_{os.getpid()}_{int(time.time() * 1000)}",
            )
            os.makedirs(fallback_dir, exist_ok=True)
            for n_jar in native_jars:
                try:
                    with zipfile.ZipFile(n_jar, "r") as z:
                        for member in z.namelist():
                            if member.lower().endswith(".dll") and not member.startswith("META-INF"):
                                dest_file = os.path.join(fallback_dir, os.path.basename(member))
                                try:
                                    with z.open(member) as source_f, open(dest_file, "wb") as target_f:
                                        shutil.copyfileobj(source_f, target_f)
                                except Exception:
                                    pass
                except Exception:
                    pass
            destination_dir = fallback_dir

        return destination_dir

    def resolve_natives_dir(
        self,
        version_json: Dict[str, Any],
        mc_version: str,
        instance_dir: str = "",
    ) -> str:
        """Locates or dynamically extracts required native binaries (.dll) for LWJGL/GLFW."""
        # 1. If instance directory has a populated natives directory
        if instance_dir:
            inst_nat = os.path.join(instance_dir, "natives")
            if os.path.isdir(inst_nat) and any(f.endswith(".dll") for f in os.listdir(inst_nat)):
                return inst_nat

        # 2. Check standard version natives directories
        v_id = version_json.get("id", mc_version)
        is_legacy = any(k in str(mc_version) for k in ["1.8", "1.7"])
        cand_list = [v_id, "Forge 1.8.9", "1.8.9"] if is_legacy else [v_id, "26.2", "1.21.4"]
        for v_dir in self.versions_dirs:
            for cand_id in cand_list:
                nat_dir = os.path.join(v_dir, cand_id, "natives")
                if os.path.isdir(nat_dir) and any(f.endswith(".dll") for f in os.listdir(nat_dir)):
                    return nat_dir

        # 3. Check controllable natives for legacy
        if is_legacy:
            appdata = os.environ.get("APPDATA", "")
            fallback_nat = os.path.join(appdata, ".minecraft", "controllable_natives")
            if os.path.isdir(fallback_nat) and any(f.endswith(".dll") for f in os.listdir(fallback_nat)):
                return fallback_nat

        # 4. Perform dynamic pre-launch extraction
        target_dir = os.path.join(self.state_dir, "natives", mc_version)
        return self.extract_natives(version_json, mc_version, target_dir)

    def resolve_assets_dir(self) -> str:
        """Returns the primary Minecraft assets directory."""
        for a_dir in self.assets_dirs:
            if os.path.isdir(os.path.join(a_dir, "indexes")):
                return a_dir
            if os.path.isdir(a_dir):
                return a_dir
        appdata = os.environ.get("APPDATA", "")
        return os.path.join(appdata, ".minecraft", "assets")

    def build_classpath(
        self,
        version_json: Dict[str, Any],
        mc_version: str,
        loader: str = "fabric",
        instance_dir: Optional[str] = None,
    ) -> List[str]:
        """Constructs the complete Java classpath (-cp) list of jars dynamically without ASM conflicts."""
        jars: List[str] = []
        appdata = os.environ.get("APPDATA", "")
        base_lib = os.path.join(appdata, ".minecraft", "libraries")

        # Inspect instance config if provided
        inst_cfg = self.inspect_instance_config(instance_dir) if instance_dir else {}
        fabric_loader_ver = inst_cfg.get("loader_version") or "0.15.11"
        forge_ver = inst_cfg.get("loader_version") or "11.15.1.2318"

        is_fabric = "fabric" in loader.lower() or inst_cfg.get("loader") == "fabric"
        is_forge = "forge" in loader.lower() or "1.8" in mc_version or inst_cfg.get("loader") == "forge"

        # Layer 1 & 2: Mod Loader & Bytecode Manipulation
        if is_fabric:
            # Candidate Fabric Loader jars
            fabric_loader_candidates = [
                os.path.join(base_lib, "net", "fabricmc", "fabric-loader", fabric_loader_ver, f"fabric-loader-{fabric_loader_ver}.jar"),
                os.path.join(base_lib, "net", "fabricmc", "fabric-loader", "0.19.4", "fabric-loader-0.19.4.jar"),
                os.path.join(base_lib, "net", "fabricmc", "fabric-loader", "0.19.3", "fabric-loader-0.19.3.jar"),
                os.path.join(base_lib, "net", "fabricmc", "fabric-loader", "0.16.10", "fabric-loader-0.16.10.jar"),
                os.path.join(base_lib, "net", "fabricmc", "fabric-loader", "0.15.11", "fabric-loader-0.15.11.jar"),
            ]
            for fl in fabric_loader_candidates:
                if os.path.isfile(fl):
                    jars.append(os.path.normpath(fl))
                    break

            # Intermediary Mappings
            intermediary_candidates = [
                os.path.join(base_lib, "net", "fabricmc", "intermediary", "26.2", "intermediary-26.2.jar"),
                os.path.join(base_lib, "net", "fabricmc", "intermediary", "1.21.4", "intermediary-1.21.4.jar"),
                os.path.join(base_lib, "net", "fabricmc", "intermediary", mc_version, f"intermediary-{mc_version}.jar"),
            ]
            for im in intermediary_candidates:
                if os.path.isfile(im):
                    jars.append(os.path.normpath(im))
                    break

            # ASM 9.10.1+ (Supports Java 21/25 class version 69+)
            asm_modules = ["asm", "asm-analysis", "asm-commons", "asm-tree", "asm-util"]
            for mod in asm_modules:
                asm_jar = os.path.join(base_lib, "org", "ow2", "asm", mod, "9.10.1", f"{mod}-9.10.1.jar")
                if os.path.isfile(asm_jar):
                    jars.append(os.path.normpath(asm_jar))

            # Sponge Mixin
            mixin_jar = os.path.join(base_lib, "net", "fabricmc", "sponge-mixin", "0.17.4+mixin.0.8.7", "sponge-mixin-0.17.4+mixin.0.8.7.jar")
            if os.path.isfile(mixin_jar):
                jars.append(os.path.normpath(mixin_jar))

        elif is_forge:
            forge_candidates = [
                os.path.join(base_lib, "net", "minecraftforge", "forge", f"1.8.9-{forge_ver}-1.8.9", f"forge-1.8.9-{forge_ver}-1.8.9.jar"),
                os.path.join(base_lib, "net", "minecraftforge", "forge", "1.8.9-11.15.1.2318-1.8.9", "forge-1.8.9-11.15.1.2318-1.8.9.jar"),
                os.path.join(base_lib, "net", "minecraftforge", "forge", "1.8.9-11.15.1.2318", "forge-1.8.9-11.15.1.2318.jar"),
            ]
            for fc in forge_candidates:
                if os.path.isfile(fc):
                    jars.append(os.path.normpath(fc))
                    break

            launchwrapper_jar = os.path.join(base_lib, "net", "minecraft", "launchwrapper", "1.12", "launchwrapper-1.12.jar")
            if os.path.isfile(launchwrapper_jar):
                jars.append(os.path.normpath(launchwrapper_jar))

            asm_legacy = os.path.join(base_lib, "org", "ow2", "asm", "asm-all", "5.0.3", "asm-all-5.0.3.jar")
            if os.path.isfile(asm_legacy):
                jars.append(os.path.normpath(asm_legacy))

            lzma_candidates = [
                os.path.join(base_lib, "lzma", "lzma", "0.0.1", "lzma-0.0.1.jar"),
                os.path.join(self.state_dir, "libraries", "lzma", "lzma", "0.0.1", "lzma-0.0.1.jar"),
                os.path.join(self.root_dir, "libraries", "lzma", "lzma", "0.0.1", "lzma-0.0.1.jar"),
            ]
            for lz in lzma_candidates:
                if os.path.isfile(lz):
                    jars.append(os.path.normpath(lz))
                    break

            forge_runtime_deps = [
                ("net", "sf", "trove4j", "trove4j", "3.0.3", "trove4j-3.0.3.jar"),
                ("java3d", "vecmath", "1.5.2", "vecmath-1.5.2.jar"),
                ("org", "scala-lang", "scala-library", "2.11.1", "scala-library-2.11.1.jar"),
                ("org", "scala-lang", "scala-reflect", "2.11.1", "scala-reflect-2.11.1.jar"),
                ("org", "scala-lang", "scala-compiler", "2.11.1", "scala-compiler-2.11.1.jar"),
                ("org", "scala-lang", "scala-parser-combinators_2.11", "1.0.1", "scala-parser-combinators_2.11-1.0.1.jar"),
                ("org", "scala-lang", "scala-xml_2.11", "1.0.2", "scala-xml_2.11-1.0.2.jar"),
                ("org", "scala-lang", "plugins", "scala-continuations-library_2.11", "1.0.2", "scala-continuations-library_2.11-1.0.2.jar"),
                ("org", "scala-lang", "plugins", "scala-continuations-plugin_2.11.1", "1.0.2", "scala-continuations-plugin_2.11.1-1.0.2.jar"),
                ("org", "scala-lang", "scala-actors-migration_2.11", "1.1.0", "scala-actors-migration_2.11-1.1.0.jar"),
                ("org", "apache", "commons", "commons-compress", "1.8.1", "commons-compress-1.8.1.jar"),
                ("com", "ibm", "icu", "icu4j-core-mojang", "51.2", "icu4j-core-mojang-51.2.jar"),
            ]
            for dep_parts in forge_runtime_deps:
                for lib_dir in self.libraries_dirs:
                    dep_path = os.path.join(lib_dir, *dep_parts)
                    if os.path.isfile(dep_path):
                        jars.append(os.path.normpath(dep_path))
                        break

        # Layer 3: Mojang / Vanilla libraries (with OS Rule evaluation)
        seen = set(os.path.normpath(j) for j in jars)
        skip_keys = set()
        if is_fabric:
            skip_keys.update([
                "org.ow2.asm:asm",
                "org.ow2.asm:asm-analysis",
                "org.ow2.asm:asm-commons",
                "org.ow2.asm:asm-tree",
                "org.ow2.asm:asm-util",
                "org.ow2.asm:asm-all",
                "net.fabricmc:sponge-mixin",
                "net.fabricmc:fabric-loader",
                "net.fabricmc:intermediary",
            ])

        libs = version_json.get("libraries", [])
        for lib in libs:
            lib_name = lib.get("name", "")

            # Evaluate OS rules: exclude OS X, Linux, or non-Windows artifacts
            rules = lib.get("rules", [])
            if rules and not self.evaluate_library_rules(rules, "windows", "x64"):
                continue

            # Skip older monolithic ASM when modern modular ASM is prepended
            if is_fabric and "org.ow2.asm:asm-all" in lib_name:
                continue

            parts = lib_name.split(":")
            if len(parts) >= 2:
                key = f"{parts[0]}:{parts[1]}"
                if key in skip_keys:
                    continue

            artifact = lib.get("downloads", {}).get("artifact", {})
            rel_path = artifact.get("path", "")
            if not rel_path and lib_name:
                rel_path = _maven_to_path(lib_name)

            if rel_path:
                for lib_dir in self.libraries_dirs:
                    full_p = os.path.join(lib_dir, rel_path.replace("/", os.sep))
                    if os.path.isfile(full_p):
                        norm = os.path.normpath(full_p)
                        if norm not in seen:
                            seen.add(norm)
                            jars.append(norm)
                        break

        # Layer 4: Minecraft Client Executable JAR
        v_id = version_json.get("id", mc_version)
        for v_dir in self.versions_dirs:
            for cand_id in [v_id, mc_version, "26.2", "1.21.4", "1.8.9", "Forge 1.8.9"]:
                c_jar = os.path.join(v_dir, cand_id, f"{cand_id}.jar")
                if os.path.isfile(c_jar):
                    norm = os.path.normpath(c_jar)
                    if norm not in seen:
                        seen.add(norm)
                        jars.append(norm)
                    break
                c_jar_direct = os.path.join(v_dir, f"{cand_id}.jar")
                if os.path.isfile(c_jar_direct):
                    norm = os.path.normpath(c_jar_direct)
                    if norm not in seen:
                        seen.add(norm)
                        jars.append(norm)
                    break

        return jars

    def build_jvm_args(
        self,
        ram_gb: int | float | str = 8,
        natives_dir: str = "",
        power_mode: str = "turbo",
        min_ram_gb: Optional[int | float | str] = None,
        mc_version: str = "26.2",
        extra_flags: Optional[List[str]] = None,
        game_dir: str = "",
    ) -> List[str]:
        """Constructs Aikar's tuned high-performance JVM optimization flags with strict RAM bounds."""
        ram_params = calculate_ram_parameters(max_ram=ram_gb, min_ram=min_ram_gb, mc_version=mc_version)

        norm_nat = os.path.normpath(natives_dir) if natives_dir else ""

        is_legacy = any(k in str(mc_version) for k in ["1.8", "1.7"])
        target_title = "Minecraft 1.8.9 - SIR Launcher" if is_legacy else "Minecraft 26.2 - SIR Launcher"
        branding_flags = [
            f"-Dorg.lwjgl.opengl.Display.title={target_title}",
            "-Dminecraft.launcher.brand=SIR-Launcher",
            "-Dminecraft.launcher.version=1.0.0",
        ]
        if game_dir:
            branding_flags.append(f"-Dminecraft.applet.TargetDirectory={game_dir}")

        if is_legacy:
            args = [
                ram_params["xms_flag"],
                ram_params["xmx_flag"],
                f"-Djava.library.path={norm_nat}",
                f"-Dorg.lwjgl.system.SharedLibraryExtractPath={os.path.join(norm_nat, 'lwjgl')}",
                "-Dfile.encoding=UTF-8",
                "-Djava.net.preferIPv4Stack=true",
                "-XX:+UseG1GC",
                f"-XX:MaxGCPauseMillis={ram_params['pause_millis']}",
                "-XX:+AlwaysPreTouch",
                "-XX:+UseStringDeduplication",
            ] + branding_flags
        else:
            use_zgc = bool(extra_flags and any("UseZGC" in str(f) for f in extra_flags))
            args = [
                ram_params["xms_flag"],
                ram_params["xmx_flag"],
                f"-Djava.library.path={norm_nat}",
                f"-Dorg.lwjgl.system.SharedLibraryExtractPath={os.path.join(norm_nat, 'lwjgl')}",
                f"-Djna.tmpdir={os.path.join(norm_nat, 'jna')}",
                f"-Dio.netty.native.workdir={os.path.join(norm_nat, 'netty')}",
                "-Dfile.encoding=UTF-8",
                "-Djava.net.preferIPv4Stack=true",
                "-XX:+UnlockExperimentalVMOptions",
                "-XX:+AlwaysPreTouch",
                "-XX:+UseStringDeduplication",
            ] + branding_flags
            if use_zgc:
                args.extend([
                    "-XX:+UseZGC",
                    "-XX:+ZGenerational",
                ])
            else:
                args.extend([
                    "-XX:+UseG1GC",
                    f"-XX:G1NewSizePercent={ram_params['new_size_pct']}",
                    f"-XX:G1MaxNewSizePercent={ram_params['max_new_size_pct']}",
                    f"-XX:G1ReservePercent={ram_params['reserve_pct']}",
                    f"-XX:MaxGCPauseMillis={ram_params['pause_millis']}",
                    f"-XX:G1HeapRegionSize={ram_params['region_size']}",
                    "-XX:G1HeapWastePercent=5",
                    "-XX:G1MixedGCCountTarget=4",
                    "-XX:InitiatingHeapOccupancyPercent=15",
                    "-XX:G1MixedGCLiveThresholdPercent=90",
                    "-XX:G1RSetUpdatingPauseTimePercent=5",
                    "-XX:SurvivorRatio=32",
                    "-XX:+PerfDisableSharedMem",
                    "-XX:MaxTenuringThreshold=1",
                ])

        if is_legacy:
            args.extend(["-XX:ParallelGCThreads=4", "-XX:ConcGCThreads=2"])
        elif power_mode == "smooth":
            args.extend(["-XX:ParallelGCThreads=4", "-XX:ConcGCThreads=2"])
        else:
            cpu = os.cpu_count() or 8
            args.extend([f"-XX:ParallelGCThreads={cpu}", f"-XX:ConcGCThreads={max(2, cpu // 2)}"])

        if extra_flags:
            for flag in extra_flags:
                if isinstance(flag, str):
                    s_flag = flag.strip()
                    # Filter out conflicting GC thread overrides for legacy HotSpot JVM
                    if is_legacy and any(k in s_flag for k in ["ParallelGCThreads", "ConcGCThreads", "UnlockExperimentalVMOptions"]):
                        continue
                    if s_flag and s_flag not in args:
                        args.append(s_flag)
                elif isinstance(flag, (list, tuple)):
                    for sub in flag:
                        s_sub = str(sub).strip()
                        if is_legacy and any(k in s_sub for k in ["ParallelGCThreads", "ConcGCThreads", "UnlockExperimentalVMOptions"]):
                            continue
                        if s_sub and s_sub not in args:
                            args.append(s_sub)

        return args

    def build_game_args(
        self,
        version_json: Dict[str, Any],
        game_dir: str,
        assets_dir: str,
        account_name: str = "Player",
        account_uuid: str = "",
        access_token: str = "0",
        user_type: str = "offline",
        mc_version: str = "1.21.4",
        loader: str = "fabric",
        server_ip: str = "",
        server_port: str = "25565",
    ) -> List[str]:
        """Constructs the command-line game arguments for Minecraft."""
        u_name = account_name or "Player"
        u_uuid = account_uuid or str(uuid.uuid3(uuid.NAMESPACE_DNS, u_name)).replace("-", "")
        u_token = access_token or "0"
        u_type = "msa" if user_type in ["msa", "microsoft"] else "offline"
        asset_index = version_json.get("assets") or ("32" if "26" in mc_version or "1.21" in mc_version else "1.8")

        args = [
            "--username", u_name,
            "--version", version_json.get("id", mc_version),
            "--gameDir", game_dir,
            "--assetsDir", assets_dir,
            "--assetIndex", str(asset_index),
            "--uuid", u_uuid,
            "--accessToken", u_token,
            "--userType", u_type,
            "--versionType", "SIR Launcher • Minecraft",
        ]

        if "forge" in loader.lower():
            args.extend(["--tweakClass", "net.minecraftforge.fml.common.launcher.FMLTweaker"])

        if server_ip:
            is_legacy = any(k in str(mc_version) for k in ["1.8", "1.7"])
            if is_legacy:
                args.extend(["--server", server_ip, "--port", str(server_port or "25565")])
            else:
                args.extend(["--quickPlayMultiplayer", f"{server_ip}:{server_port or '25565'}"])

        return args

    def ensure_version_downloaded(
        self,
        mc_version: str,
        loader: str = "fabric",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bool:
        """Downloads missing version manifests, client JARs, and libraries if missing on disk."""
        def notify(msg: str, pct: int = 0):
            self.current_status = msg
            self.download_progress = pct
            if progress_callback:
                progress_callback(msg, pct)

        appdata = os.environ.get("APPDATA", "")
        base_mc = os.path.join(appdata, ".minecraft")
        clean_v = "1.21.4" if "26" in mc_version else mc_version
        versions_base = os.path.join(base_mc, "versions", mc_version)
        libraries_base = os.path.join(base_mc, "libraries")
        os.makedirs(versions_base, exist_ok=True)
        os.makedirs(libraries_base, exist_ok=True)

        target_json = os.path.join(versions_base, f"{mc_version}.json")
        target_jar = os.path.join(versions_base, f"{mc_version}.jar")

        # 1. Fetch Mojang Version Manifest if version.json is missing
        if not os.path.isfile(target_json):
            notify(f"Fetching Mojang manifest for {clean_v}...", 10)
            try:
                manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
                req = urllib.request.Request(manifest_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    m_data = json.loads(resp.read().decode("utf-8"))
                    v_entry = next((v for v in m_data.get("versions", []) if v["id"] == clean_v), None)
                    if v_entry and v_entry.get("url"):
                        v_req = urllib.request.Request(v_entry["url"], headers={"User-Agent": "SIR-Launcher/1.0.0"})
                        with urllib.request.urlopen(v_req, timeout=10) as v_resp:
                            v_content = v_resp.read().decode("utf-8")
                            atomic_write_text(target_json, v_content)
            except Exception as e:
                print(f"[Downloader] Error fetching version.json: {e}")

        # 2. Parse version.json
        v_json = self.resolve_version_json(mc_version, loader)
        if not v_json and os.path.isfile(target_json):
            try:
                with open(target_json, "r", encoding="utf-8") as f:
                    v_json = json.load(f)
            except Exception:
                pass

        if not v_json:
            return False

        # 3. Download Client JAR if missing
        if not os.path.isfile(target_jar):
            client_url = v_json.get("downloads", {}).get("client", {}).get("url")
            if client_url:
                notify(f"Downloading Minecraft {clean_v} Client JAR...", 25)
                try:
                    download_file_resilient(client_url, target_jar, max_retries=3, timeout=30.0)
                except Exception as e:
                    print(f"[Downloader] Error downloading client.jar: {e}")

        notify(f"✓ Ready to Launch {mc_version}!", 100)
        return True

    @staticmethod
    def _watch_and_set_window_title(proc_or_pid: Any, target_title: str) -> None:
        """Monitors for the Minecraft process window and persistently enforces official SIR Launcher window branding."""
        if sys.platform != "win32":
            return
        import ctypes
        user32 = ctypes.windll.user32
        pid = proc_or_pid.pid if hasattr(proc_or_pid, "pid") else proc_or_pid

        def _worker():
            while True:
                if hasattr(proc_or_pid, "poll") and proc_or_pid.poll() is not None:
                    break
                found_hwnds = []

                def _enum_windows_proc(hwnd, _):
                    if user32.IsWindowVisible(hwnd):
                        owner = ctypes.c_ulong()
                        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                        if owner.value == pid:
                            found_hwnds.append(hwnd)
                    return True

                try:
                    proc_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                    user32.EnumWindows(proc_type(_enum_windows_proc), 0)
                    for h in found_hwnds:
                        length = user32.GetWindowTextLengthW(h)
                        if length > 0:
                            buf = ctypes.create_unicode_buffer(length + 1)
                            user32.GetWindowTextW(h, buf, length + 1)
                            curr = buf.value
                            if any(token in curr for token in ["Minecraft", "GLFW", "LWJGL", "1.21", "1.8", "26.2", "SIR Launcher"]):
                                if not curr.endswith("- SIR Launcher") or curr != target_title:
                                    user32.SetWindowTextW(h, target_title)
                except Exception:
                    pass
                time.sleep(2.0)

        threading.Thread(target=_worker, daemon=True).start()

    def launch(
        self,
        instance_dir: str,
        mc_version: str = "1.21.4",
        loader: str = "fabric",
        account: Optional[Dict[str, Any]] = None,
        ram_gb: int | float | str = 8,
        power_mode: str = "turbo",
        on_log_callback: Optional[Callable[[str], None]] = None,
        on_crash_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        server_ip: Optional[str] = None,
        server_port: Optional[int | str] = None,
    ) -> Dict[str, Any]:
        """Directly executes the native Minecraft Java process with real-time log streaming and strict bounds."""
        abs_instance_dir = os.path.abspath(instance_dir)
        instance_dir = abs_instance_dir

        # Pre-Launch Compatibility Healing (Controlify FancyMenu & Lunar assets)
        try:
            from .controlify_compat import patch_all_controlify_jars
            patch_all_controlify_jars(instance_dir)
        except Exception:
            pass

        try:
            from .lunar_bridge_service import LunarBridgeService
            LunarBridgeService(self.root_dir).ensure_lunar_assets_and_compat(instance_dir)
        except Exception:
            pass

        # 1. Inspect instance configuration
        inst_cfg = self.inspect_instance_config(instance_dir)
        eff_mc_ver = inst_cfg.get("mc_version") or mc_version
        eff_loader = inst_cfg.get("loader") or loader

        # Memory overrides
        eff_max_ram = ram_gb or inst_cfg.get("max_ram_mb") or 8
        if isinstance(eff_max_ram, (int, float)) and eff_max_ram <= 64:
            eff_max_ram = int(eff_max_ram * 1024)
        if any(k in str(eff_mc_ver) for k in ["1.8", "1.7"]) and isinstance(eff_max_ram, (int, float)):
            eff_max_ram = min(eff_max_ram, 4096)
        eff_min_ram = inst_cfg.get("min_ram_mb")

        # 2. Resolve version manifest
        v_json = self.resolve_version_json(eff_mc_ver, eff_loader, instance_dir)
        if not v_json:
            v_json = {
                "id": eff_mc_ver,
                "assets": "32" if "26" in eff_mc_ver or "1.21" in eff_mc_ver else "1.8",
                "mainClass": "net.fabricmc.loader.impl.launch.knot.KnotClient" if "fabric" in eff_loader.lower() else "net.minecraft.launchwrapper.Launch",
                "libraries": [],
            }

        # 3. Main Class resolution
        if "fabric" in eff_loader.lower():
            main_class = "net.fabricmc.loader.impl.launch.knot.KnotClient"
        elif "forge" in eff_loader.lower():
            main_class = "net.minecraft.launchwrapper.Launch"
        else:
            main_class = v_json.get("mainClass", "net.minecraft.client.main.Main")

        # 4. Java Runtime resolution
        is_legacy = any(k in str(eff_mc_ver) for k in ["1.8", "1.7"])
        java_hint = 8 if is_legacy else 25
        inst_java = inst_cfg.get("java_path")
        if inst_java and os.path.isfile(inst_java):
            java_exe = inst_java
        else:
            java_exe = self.ensure_java_runtime(java_hint)
            if not java_exe or not os.path.isfile(java_exe):
                java_exe = self.detect_java(java_hint)

        # 5. Classpath, Natives, and Assets resolution
        classpath_list = self.build_classpath(v_json, eff_mc_ver, eff_loader, instance_dir)
        classpath_str = os.pathsep.join(classpath_list)
        natives_dir = self.resolve_natives_dir(v_json, eff_mc_ver, instance_dir)
        assets_dir = self.resolve_assets_dir()

        # 6. Extract account details
        acc_name = "Player"
        acc_uuid = ""
        acc_token = "0"
        acc_type = "offline"
        if isinstance(account, dict):
            acc_name = str(account.get("displayName") or account.get("name") or account.get("username") or "Player").strip()
            acc_uuid = str(account.get("uuid") or account.get("uuid_value") or account.get("profileId") or "").replace("-", "")
            acc_token = str(account.get("accessToken") or account.get("token") or account.get("access_token") or "0")
            raw_t = str(account.get("accountType") or account.get("type", "offline")).lower()
            acc_type = "msa" if any(x in raw_t for x in ["msa", "microsoft", "official"]) else "offline"
        elif account:
            acc_name = str(account).strip()

        if not acc_uuid or len(acc_uuid) != 32:
            acc_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{acc_name}")).replace("-", "")

        # 7. Build JVM & Game arguments
        extra_jvm = []
        if inst_cfg.get("jvm_args"):
            raw_jvm = str(inst_cfg["jvm_args"]).strip()
            while (raw_jvm.startswith('"') and raw_jvm.endswith('"')) or (raw_jvm.startswith("'") and raw_jvm.endswith("'")):
                raw_jvm = raw_jvm[1:-1].strip()
            for flag_token in raw_jvm.split():
                clean_tok = flag_token.strip().strip('"').strip("'")
                if clean_tok and clean_tok not in extra_jvm:
                    extra_jvm.append(clean_tok)

        eff_game_dir = os.path.join(instance_dir, "minecraft") if os.path.isdir(os.path.join(instance_dir, "minecraft")) else instance_dir
        jvm_args = self.build_jvm_args(
            ram_gb=eff_max_ram,
            natives_dir=natives_dir,
            power_mode=power_mode,
            min_ram_gb=eff_min_ram,
            mc_version=eff_mc_ver,
            extra_flags=extra_jvm,
            game_dir=eff_game_dir,
        )
        game_args = self.build_game_args(
            version_json=v_json,
            game_dir=eff_game_dir,
            assets_dir=assets_dir,
            account_name=acc_name,
            account_uuid=acc_uuid,
            access_token=acc_token,
            user_type=acc_type,
            mc_version=eff_mc_ver,
            loader=eff_loader,
            server_ip=str(server_ip) if server_ip else "",
            server_port=str(server_port or "25565"),
        )

        # Use javaw.exe as the native Windows GUI launcher so no black CMD box appears
        # while keeping the interactive desktop window station active for GLFW/OpenGL rendering
        eff_java_exe = java_exe

        full_command = [eff_java_exe] + jvm_args + ["-cp", classpath_str, main_class] + game_args

        # 8. Setup launch log path and streamer
        log_dir = os.path.join(self.state_dir, "logs", "launches")
        inst_id = os.path.basename(os.path.normpath(instance_dir))
        log_file = os.path.join(log_dir, f"{inst_id}_{int(time.time())}.log")

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            proc = subprocess.Popen(
                full_command,
                cwd=instance_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creation_flags,
            )

            streamer = ProcessLogStreamer(
                proc=proc,
                log_file=log_file,
                instance_dir=instance_dir,
                on_line_callback=on_log_callback,
                on_crash_callback=on_crash_callback,
            )
            self.active_streamers[proc.pid] = streamer

            # Enforce official window titlebar branding on Windows DWM
            target_branding_title = "Minecraft 1.8.9 - SIR Launcher" if is_legacy else "Minecraft 26.2 - SIR Launcher"
            self._watch_and_set_window_title(proc, target_branding_title)

            return {
                "success": True,
                "pid": proc.pid,
                "engine": "SIR_NATIVE_JVM",
                "java_exe": java_exe,
                "main_class": main_class,
                "log_path": log_file,
                "streamer": streamer,
                "message": f"✓ Direct Native Minecraft process launched (PID {proc.pid}) with {eff_max_ram} RAM!",
            }
        except Exception as ex:
            return {
                "success": False,
                "engine": "SIR_NATIVE_JVM",
                "error": f"Failed to execute native Java process: {str(ex)}",
                "command": " ".join(full_command[:8]) + "...",
            }
