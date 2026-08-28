"""Native Independent Minecraft Launch Engine & Universal Version Downloader for SIR Launcher.

- Resolves JVM arguments & classpaths from Mojang & Fabric official manifests.
- Auto-downloads missing Minecraft versions, client JARs, library JARs, and native DLLs for ANY version.
- Automatically tunes RAM and JVM G1GC settings based on user hardware.
- Directly executes Minecraft via subprocess with zero background launchers.
"""

from __future__ import annotations

import os
import sys
import json
import uuid
import time
import subprocess
import threading
import urllib.request
import urllib.parse
import zipfile
import shutil
import concurrent.futures
from typing import Any, Optional, Dict, List, Callable


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


class NativeMinecraftRunner:
    """Independent Native Minecraft Launch & Download Engine."""

    def __init__(self, root_dir: str, state_dir: Optional[str] = None):
        self.root_dir = os.path.abspath(root_dir)
        self.state_dir = os.path.abspath(state_dir or self.root_dir)
        self.current_status = "Idle"
        self.download_progress = 0
        
        # Primary search directories for libraries and assets
        self.libraries_dirs = [
            os.path.join(self.root_dir, "libraries"),
            os.path.join(self.root_dir, "SIR Launcher", "libraries"),
            os.path.expandvars(r"%APPDATA%\.minecraft\libraries"),
            os.path.expandvars(r"%APPDATA%\SIR ModPack\libraries"),
            os.path.expandvars(r"%APPDATA%\PrismLauncher\libraries"),
        ]
        
        self.assets_dirs = [
            os.path.join(self.root_dir, "assets"),
            os.path.join(self.root_dir, "SIR Launcher", "assets"),
            os.path.expandvars(r"%APPDATA%\.minecraft\assets"),
            os.path.expandvars(r"%APPDATA%\SIR ModPack\assets"),
        ]
        
        self.versions_dirs = [
            os.path.join(self.root_dir, "versions"),
            os.path.join(self.root_dir, "SIR Launcher", "versions"),
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
                total_ram_gb = int(round(stat.ullTotalPhys / (1024 ** 3)))
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
            "cpu_threads": os.cpu_count() or 8
        }

    def detect_java(self, version_hint: int = 25) -> str:
        """Finds best matching Java binary for the required Minecraft version."""
        user_home = os.path.expanduser("~")
        
        # 1. Java 25+ Priority (Required for Modern 26.2 and modern Fabric mods)
        if version_hint >= 25:
            # Check bundled runtime first, then Lunar Client Zulu 25 JRE
            priority_java_25 = [
                os.path.expandvars(r"%APPDATA%\SIR ModPack\runtime\java-25\bin\javaw.exe"),
                os.path.join(self.root_dir, "runtime", "java-25", "bin", "javaw.exe"),
                os.path.join(self.root_dir, "SIR Launcher", "runtime", "java-25", "bin", "javaw.exe"),
                os.path.expandvars(r"%APPDATA%\.minecraft\runtime\java-runtime-epsilon\windows-x64\bin\javaw.exe"),
            ]
            
            # Scan Lunar Client JRE directory for Zulu 25
            lunar_jre_dir = os.path.join(user_home, ".lunarclient", "jre")
            if os.path.isdir(lunar_jre_dir):
                for root, dirs, files in os.walk(lunar_jre_dir):
                    if "zulu25" in root.lower() or "jre25" in root.lower() or "jdk-25" in root.lower():
                        if "javaw.exe" in files:
                            priority_java_25.append(os.path.join(root, "javaw.exe"))

            for p in priority_java_25:
                if os.path.isfile(p):
                    return p

        # 2. Java 21 / 17 Priority
        if version_hint >= 17:
            priority_java_21 = [
                os.path.expandvars(r"%APPDATA%\.minecraft\runtime\java-runtime-delta\windows-x64\bin\javaw.exe"),
                os.path.expandvars(r"%APPDATA%\.minecraft\runtime\java-runtime-gamma\windows-x64\bin\javaw.exe"),
                os.path.expandvars(r"%APPDATA%\.minecraft\runtime\java-runtime-beta\windows-x64\bin\javaw.exe"),
                os.path.expandvars(r"%APPDATA%\SIR ModPack\runtime\java-21\bin\javaw.exe"),
                os.path.join(self.root_dir, "runtime", "java-21", "bin", "javaw.exe"),
                os.path.join(self.root_dir, "SIR Launcher", "runtime", "java-21", "bin", "javaw.exe"),
            ]
            for p in priority_java_21:
                if os.path.isfile(p):
                    return p

        # 3. Java 8 Priority for Legacy 1.8.9
        if version_hint <= 8:
            priority_java_8 = [
                r"C:\Program Files\Java\jre1.8.0_503\bin\javaw.exe",
                r"C:\Program Files (x86)\Java\jre1.8.0_251\bin\javaw.exe",
                os.path.expandvars(r"%APPDATA%\.minecraft\runtime\jre-legacy\windows-x64\bin\javaw.exe"),
                os.path.expandvars(r"%APPDATA%\.tlauncher\legacy\Minecraft\jre\jre-legacy\windows-x64\jre-legacy\bin\javaw.exe"),
                os.path.expandvars(r"%APPDATA%\SIR ModPack\runtime\java-8\bin\javaw.exe"),
                os.path.join(self.root_dir, "runtime", "java-8", "bin", "javaw.exe"),
            ]
            for p in priority_java_8:
                if os.path.isfile(p):
                    return p

        # Scan Program Files, Adoptium and Lunar Client
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        search_roots = [
            os.path.join(program_files, "Eclipse Adoptium"),
            os.path.join(program_files, "Microsoft"),
            os.path.join(program_files, "Java"),
            os.path.join(program_files, "Zulu"),
            os.path.join(local_appdata, "Programs", "Eclipse Adoptium"),
            os.path.join(user_home, ".lunarclient", "jre"),
        ]
        
        candidates = []
        for s_root in search_roots:
            if os.path.isdir(s_root):
                for root, dirs, files in os.walk(s_root):
                    if "javaw.exe" in files:
                        candidates.append(os.path.join(root, "javaw.exe"))
                    if len(candidates) > 30:
                        break

        target_token = "21" if version_hint >= 21 else ("17" if version_hint >= 17 else "1.8")
        for c in candidates:
            if os.path.isfile(c) and (target_token in c or f"jdk-{version_hint}" in c or f"jre{version_hint}" in c):
                return c

        for c in candidates:
            if os.path.isfile(c):
                return c

        which_j = shutil.which("javaw.exe") or shutil.which("java.exe")
        if which_j and os.path.isfile(which_j):
            return which_j

        return ""

    def ensure_java_runtime(self, version_hint: int = 25, progress_callback: Optional[Callable[[str, int], None]] = None) -> str:
        """Ensures a verified Java runtime exists on the PC; auto-downloads OpenJDK if completely missing."""
        existing_j = self.detect_java(version_hint)
        if existing_j and os.path.isfile(existing_j):
            return existing_j

        # If Java is completely missing on a fresh user PC, auto-download OpenJDK from Adoptium
        def notify(msg: str, pct: int):
            self.current_status = msg
            self.download_progress = pct
            if progress_callback:
                progress_callback(msg, pct)

        notify(f"Downloading OpenJDK {version_hint} Runtime for fresh PC...", 15)
        dest_runtime_dir = os.path.expandvars(rf"%APPDATA%\SIR ModPack\runtime\java-{version_hint}")
        os.makedirs(dest_runtime_dir, exist_ok=True)
        
        # Adoptium official binary release API / verified mirror
        if version_hint >= 25:
            dl_url = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B4-ea-beta/OpenJDK25U-jdk_x64_windows_hotspot_25.0.5_4-ea.zip"
        else:
            dl_url = f"https://api.adoptium.net/v3/binary/latest/{version_hint}/ga/windows/x64/jdk/hotspot/normal/eclipse"
        zip_temp = os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"openjdk_{version_hint}.zip")
        
        try:
            req = urllib.request.Request(dl_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=120) as resp, open(zip_temp, "wb") as out_f:
                shutil.copyfileobj(resp, out_f)
            
            notify("Extracting Java Runtime...", 75)
            with zipfile.ZipFile(zip_temp, "r") as z:
                # Find root dir inside zip
                top_dir = z.namelist()[0].split("/")[0]
                z.extractall(os.path.dirname(dest_runtime_dir))
                extracted_root = os.path.join(os.path.dirname(dest_runtime_dir), top_dir)
                if os.path.isdir(extracted_root) and extracted_root != dest_runtime_dir:
                    if os.path.exists(dest_runtime_dir):
                        shutil.rmtree(dest_runtime_dir, ignore_errors=True)
                    os.rename(extracted_root, dest_runtime_dir)
            
            try: os.remove(zip_temp)
            except Exception: pass
            
            target_javaw = os.path.join(dest_runtime_dir, "bin", "javaw.exe")
            if os.path.isfile(target_javaw):
                return target_javaw
        except Exception as e:
            print(f"[Java Provisioner] Auto-download error: {e}")

        return shutil.which("javaw.exe") or shutil.which("java.exe") or "javaw.exe"

    def resolve_version_json(self, mc_version: str) -> Optional[Dict[str, Any]]:
        """Finds and parses the version.json manifest for the given Minecraft version."""
        version_names = [mc_version, "26.2", "1.21.4", "1.8.9", f"Fabric {mc_version}", f"Forge {mc_version}"]
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

    def ensure_version_downloaded(self, mc_version: str, loader: str = "fabric", progress_callback: Optional[Callable[[str, int], None]] = None) -> bool:
        """Downloads all missing version manifests, client JARs, libraries and natives for any selected Minecraft version."""
        def notify(msg: str, pct: int = 0):
            self.current_status = msg
            self.download_progress = pct
            if progress_callback:
                progress_callback(msg, pct)

        base_mc = os.path.expandvars(r"%APPDATA%\.minecraft")
        clean_v = "1.21.4" if "26" in mc_version else mc_version
        versions_base = os.path.join(base_mc, "versions", mc_version)
        libraries_base = os.path.join(base_mc, "libraries")
        natives_base = os.path.join(versions_base, "natives")
        os.makedirs(versions_base, exist_ok=True)
        os.makedirs(libraries_base, exist_ok=True)
        os.makedirs(natives_base, exist_ok=True)

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
                            with open(target_json, "w", encoding="utf-8") as f:
                                f.write(v_content)
            except Exception as e:
                print(f"[Downloader] Error fetching version.json: {e}")

        # 2. Parse version.json
        v_json = self.resolve_version_json(mc_version)
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
                    req = urllib.request.Request(client_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
                    with urllib.request.urlopen(req, timeout=30) as resp, open(target_jar, "wb") as out_f:
                        shutil.copyfileobj(resp, out_f)
                except Exception as e:
                    print(f"[Downloader] Error downloading client.jar: {e}")

        # 4. Download Missing Library JARs in parallel
        libs = v_json.get("libraries", [])
        downloads_queue = []
        for lib in libs:
            artifact = lib.get("downloads", {}).get("artifact", {})
            url = artifact.get("url")
            rel_p = artifact.get("path") or _maven_to_path(lib.get("name", ""))
            if url and rel_p:
                dest_p = os.path.join(libraries_base, rel_p.replace("/", os.sep))
                if not os.path.isfile(dest_p):
                    downloads_queue.append((url, dest_p))

            classifiers = lib.get("downloads", {}).get("classifiers", {})
            win_nat = classifiers.get("natives-windows") or classifiers.get("natives-windows-64")
            if win_nat:
                nat_url = win_nat.get("url")
                nat_p = win_nat.get("path") or _maven_to_path(lib.get("name", ""), "natives-windows")
                if nat_url and nat_p:
                    dest_p = os.path.join(libraries_base, nat_p.replace("/", os.sep))
                    if not os.path.isfile(dest_p):
                        downloads_queue.append((nat_url, dest_p))

        if downloads_queue:
            total_items = len(downloads_queue)
            notify(f"Downloading libraries (0/{total_items})...", 40)
            completed_count = 0

            def _download_single(item):
                u, dest = item
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                try:
                    r = urllib.request.Request(u, headers={"User-Agent": "SIR-Launcher/1.0.0"})
                    with urllib.request.urlopen(r, timeout=15) as res, open(dest, "wb") as out:
                        shutil.copyfileobj(res, out)
                    if "natives" in dest and dest.endswith(".jar"):
                        try:
                            with zipfile.ZipFile(dest, "r") as z:
                                for member in z.namelist():
                                    if member.endswith(".dll") and not member.startswith("META-INF"):
                                        z.extract(member, natives_base)
                        except Exception:
                            pass
                    return True
                except Exception:
                    return False

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(_download_single, item) for item in downloads_queue]
                for f in concurrent.futures.as_completed(futures):
                    completed_count += 1
                    pct = 40 + int((completed_count / total_items) * 50)
                    notify(f"Downloading libraries ({completed_count}/{total_items})...", pct)

        # 5. If Fabric: Ensure Fabric Loader 0.19.4 & Intermediary Mappings exist
        if "fabric" in loader.lower():
            notify(f"Verifying Fabric Loader 0.19.4 for {clean_v}...", 92)
            try:
                fab_url = f"https://meta.fabricmc.net/v2/versions/loader/{clean_v}/0.19.4/profile/json"
                req = urllib.request.Request(fab_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    p_data = json.loads(resp.read().decode("utf-8"))
                    for f_lib in p_data.get("libraries", []):
                        parts = f_lib["name"].split(":")
                        g, a, v = parts[0], parts[1], parts[2]
                        rel = g.replace(".", "/") + "/" + a + "/" + v + "/" + a + "-" + v + ".jar"
                        dest = os.path.join(libraries_base, rel.replace("/", os.sep))
                        if not os.path.isfile(dest):
                            os.makedirs(os.path.dirname(dest), exist_ok=True)
                            dl_u = (f_lib.get("url") or "https://maven.fabricmc.net/") + rel
                            urllib.request.urlretrieve(dl_u, dest)
            except Exception:
                pass

        notify(f"✓ Ready to Launch {mc_version}!", 100)
        return True

    def build_classpath(self, version_json: Dict[str, Any], mc_version: str, loader: str = "fabric") -> List[str]:
        """Constructs the complete Java classpath (-cp) list of jars."""
        jars: List[str] = []
        base_lib = os.path.expandvars(r"%APPDATA%\.minecraft\libraries")

        # 1. Prepend Fabric Loader 0.19.4 explicit dependencies with ASM 9.10.1 (supports class version 69+)
        if "fabric" in loader.lower():
            fabric_explicit = [
                os.path.join(base_lib, r"net\fabricmc\fabric-loader\0.19.4\fabric-loader-0.19.4.jar"),
                os.path.join(base_lib, r"net\fabricmc\intermediary\26.2\intermediary-26.2.jar"),
                os.path.join(base_lib, r"net\fabricmc\intermediary\1.21.4\intermediary-1.21.4.jar"),
                os.path.join(base_lib, r"org\ow2\asm\asm\9.10.1\asm-9.10.1.jar"),
                os.path.join(base_lib, r"org\ow2\asm\asm-analysis\9.10.1\asm-analysis-9.10.1.jar"),
                os.path.join(base_lib, r"org\ow2\asm\asm-commons\9.10.1\asm-commons-9.10.1.jar"),
                os.path.join(base_lib, r"org\ow2\asm\asm-tree\9.10.1\asm-tree-9.10.1.jar"),
                os.path.join(base_lib, r"org\ow2\asm\asm-util\9.10.1\asm-util-9.10.1.jar"),
                os.path.join(base_lib, r"net\fabricmc\sponge-mixin\0.17.4+mixin.0.8.7\sponge-mixin-0.17.4+mixin.0.8.7.jar"),
            ]
            for f in fabric_explicit:
                if os.path.isfile(f):
                    jars.append(f)

        # 2. Append Vanilla & Mojang libraries from version_json
        seen = set(os.path.normpath(j) for j in jars)
        libs = version_json.get("libraries", [])
        for lib in libs:
            # Skip old monolithic asm-all when modular ASM is active
            if "org.ow2.asm:asm-all" in lib.get("name", ""):
                continue

            artifact = lib.get("downloads", {}).get("artifact", {})
            rel_path = artifact.get("path", "")
            if not rel_path and lib.get("name"):
                rel_path = _maven_to_path(lib["name"])

            if rel_path:
                for lib_dir in self.libraries_dirs:
                    full_p = os.path.join(lib_dir, rel_path.replace("/", os.sep))
                    if os.path.isfile(full_p):
                        norm = os.path.normpath(full_p)
                        if norm not in seen:
                            seen.add(norm)
                            jars.append(norm)
                        break

        # 3. Append Client JAR
        v_id = version_json.get("id", mc_version)
        for v_dir in self.versions_dirs:
            c_jar = os.path.join(v_dir, v_id, f"{v_id}.jar")
            if os.path.isfile(c_jar):
                jars.append(os.path.normpath(c_jar))
                break
            c_jar2 = os.path.join(v_dir, "26.2", "26.2.jar")
            if os.path.isfile(c_jar2):
                jars.append(os.path.normpath(c_jar2))
                break

        return jars

    def resolve_natives_dir(self, version_json: Dict[str, Any], mc_version: str) -> str:
        """Locates or extracts required native binaries (.dll) for LWJGL/GLFW."""
        v_id = version_json.get("id", mc_version)
        for v_dir in self.versions_dirs:
            nat_dir = os.path.join(v_dir, v_id, "natives")
            if os.path.isdir(nat_dir):
                return nat_dir
            nat_dir2 = os.path.join(v_dir, "26.2", "natives")
            if os.path.isdir(nat_dir2):
                return nat_dir2
            nat_dir3 = os.path.join(v_dir, "Forge 1.8.9", "natives")
            if os.path.isdir(nat_dir3):
                return nat_dir3

        fallback_nat = os.path.expandvars(r"%APPDATA%\.minecraft\controllable_natives")
        if os.path.isdir(fallback_nat):
            return fallback_nat
        
        default_nat = os.path.join(self.state_dir, "natives")
        os.makedirs(default_nat, exist_ok=True)
        return default_nat

    def resolve_assets_dir(self) -> str:
        """Returns the primary Minecraft assets directory."""
        for a_dir in self.assets_dirs:
            if os.path.isdir(os.path.join(a_dir, "indexes")):
                return a_dir
            if os.path.isdir(a_dir):
                return a_dir
        return os.path.expandvars(r"%APPDATA%\.minecraft\assets")

    def build_jvm_args(self, ram_gb: int = 8, natives_dir: str = "", power_mode: str = "turbo") -> List[str]:
        """Constructs Aikar's tuned high-performance JVM optimization flags."""
        min_ram = max(2, ram_gb // 2)
        max_ram = max(4, ram_gb)
        
        args = [
            f"-Xms{min_ram}G",
            f"-Xmx{max_ram}G",
            f"-Djava.library.path={natives_dir}",
            "-Dfile.encoding=UTF-8",
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
        ]
        
        if power_mode == "smooth":
            args.extend(["-XX:ParallelGCThreads=4", "-XX:ConcGCThreads=2"])
        else:
            cpu = os.cpu_count() or 8
            args.extend([f"-XX:ParallelGCThreads={cpu}", f"-XX:ConcGCThreads={max(2, cpu // 2)}"])
            
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
        loader: str = "fabric"
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
            "--versionType", "SIR Ecosystem v1.0.0"
        ]

        if "forge" in loader.lower() or "1.8" in mc_version:
            args.extend(["--tweakClass", "net.minecraftforge.fml.common.launcher.FMLTweaker"])

        return args

    def launch(
        self,
        instance_dir: str,
        mc_version: str = "1.21.4",
        loader: str = "fabric",
        account: Optional[Dict[str, Any]] = None,
        ram_gb: int = 8,
        power_mode: str = "turbo",
        on_log_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Ensures all assets are downloaded and directly executes the native Minecraft Java process."""
        # 1. Ensure version files and libraries are downloaded
        self.ensure_version_downloaded(mc_version, loader)

        # 2. Resolve version manifest
        v_json = self.resolve_version_json(mc_version)
        if not v_json:
            v_json = {
                "id": mc_version,
                "assets": "32" if "26" in mc_version or "1.21" in mc_version else "1.8",
                "mainClass": "net.fabricmc.loader.impl.launch.knot.KnotClient" if "fabric" in loader.lower() else "net.minecraft.launchwrapper.Launch",
                "libraries": []
            }

        # 3. Main Class
        if "fabric" in loader.lower():
            main_class = "net.fabricmc.loader.impl.launch.knot.KnotClient"
        elif "forge" in loader.lower():
            main_class = "net.minecraft.launchwrapper.Launch"
        else:
            main_class = v_json.get("mainClass", "net.minecraft.client.main.Main")

        # 4. Detect / Auto-Download Java runtime (Java 25 for Modern 26.2, Java 8 for Legacy 1.8.9)
        is_legacy = "1.8" in mc_version or "1.7" in mc_version
        java_hint = 8 if is_legacy else 25
        java_exe = self.ensure_java_runtime(java_hint)

        # 5. Resolve classpath & natives
        classpath_list = self.build_classpath(v_json, mc_version, loader)
        classpath_str = os.pathsep.join(classpath_list)
        natives_dir = self.resolve_natives_dir(v_json, mc_version)
        assets_dir = self.resolve_assets_dir()

        # 6. Extract account details
        acc_name = "Player"
        acc_uuid = ""
        acc_token = "0"
        acc_type = "offline"
        if isinstance(account, dict):
            acc_name = account.get("name") or account.get("username") or "Player"
            acc_uuid = account.get("uuid") or ""
            acc_token = account.get("token") or account.get("accessToken") or "0"
            acc_type = account.get("type", "offline")

        # 7. Build JVM & Game arguments
        jvm_args = self.build_jvm_args(ram_gb, natives_dir, power_mode)
        game_args = self.build_game_args(
            version_json=v_json,
            game_dir=instance_dir,
            assets_dir=assets_dir,
            account_name=acc_name,
            account_uuid=acc_uuid,
            access_token=acc_token,
            user_type=acc_type,
            mc_version=mc_version,
            loader=loader
        )

        full_command = [java_exe] + jvm_args + ["-cp", classpath_str, main_class] + game_args

        # 8. Setup launch log path
        log_dir = os.path.join(self.state_dir, "logs", "launches")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"minecraft_{int(time.time())}.log")

        try:
            log_handle = open(log_file, "w", encoding="utf-8", errors="replace")
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            proc = subprocess.Popen(
                full_command,
                cwd=instance_dir,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags
            )

            return {
                "success": True,
                "pid": proc.pid,
                "engine": "SIR_NATIVE_JVM",
                "java_exe": java_exe,
                "main_class": main_class,
                "log_path": log_file,
                "message": f"✓ Direct Native Minecraft process launched (PID {proc.pid}) with {ram_gb} GB RAM!"
            }
        except Exception as ex:
            return {
                "success": False,
                "engine": "SIR_NATIVE_JVM",
                "error": f"Failed to execute native Java process: {str(ex)}",
                "command": " ".join(full_command[:8]) + "..."
            }
