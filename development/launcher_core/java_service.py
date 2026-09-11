"""
java_service.py — Discovers installed Java Runtimes and validates JVM versions.
Zero-Mock Implementation with PE Header Architecture Inspection, Multi-Source
Registry Probing (HKLM & HKCU), Filesystem Discovery & Semver Parsing.
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from typing import Any, Callable, Dict, List, Optional

try:
    import winreg
except ImportError:
    winreg = None

from shared_core.runtime import download_file_resilient


def get_pe_binary_arch(exe_path: str) -> Dict[str, Any]:
    """Reads Windows PE header to determine binary machine architecture without spawning subprocess."""
    if not os.path.isfile(exe_path):
        return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
    try:
        with open(exe_path, "rb") as f:
            if f.read(2) != b"MZ":
                return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
            f.seek(0x3C)
            pe_offset_bytes = f.read(4)
            if len(pe_offset_bytes) < 4:
                return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
            pe_offset = struct.unpack("<I", pe_offset_bytes)[0]
            f.seek(pe_offset)
            if f.read(4) != b"PE\0\0":
                return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
            machine = struct.unpack("<H", f.read(2))[0]
            if machine == 0x8664:
                return {"is_valid": True, "arch": "x64", "is_64bit": True}
            elif machine == 0xAA64:
                return {"is_valid": True, "arch": "ARM64", "is_64bit": True}
            elif machine == 0x014c:
                return {"is_valid": True, "arch": "x86 (32-bit)", "is_64bit": False}
            return {"is_valid": True, "arch": f"Other ({hex(machine)})", "is_64bit": False}
    except Exception:
        return {"is_valid": False, "arch": "Unknown", "is_64bit": False}


def parse_java_runtime_info(java_exe: str, probe_process: bool = True) -> Dict[str, Any]:
    """Inspects a Java binary via PE headers and 'java -version' to extract structured metadata."""
    norm_exe = os.path.normpath(java_exe)
    pe_info = get_pe_binary_arch(norm_exe)

    out = ""
    is_corrupted = False
    if probe_process and os.path.isfile(norm_exe):
        try:
            res = subprocess.run(
                [norm_exe, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=2.5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0,
            )
            rc = getattr(res, "returncode", 0)
            if rc == 0 or not isinstance(rc, int):
                out = res.stdout or ""
            else:
                is_corrupted = True
        except Exception:
            is_corrupted = True

    if is_corrupted:
        return {
            "name": f"Corrupted ({os.path.basename(norm_exe)})",
            "version": "Corrupted",
            "raw_version": "Corrupted",
            "major_version": 0,
            "vendor": "Unknown",
            "arch": "Invalid",
            "is_64bit": False,
            "is_lts": False,
            "is_temurin_21": False,
            "is_java21": False,
            "is_java8": False,
            "is_modern_ready": False,
            "is_legacy_ready": False,
            "is_valid": False,
            "path": norm_exe,
            "recommended": False
        }

    # Semver extraction
    raw_ver = "Unknown"
    major = 0
    m_ver = re.search(r'(?:version|openjdk version)\s+"?([0-9._]+(?:-[a-zA-Z0-9.+]+)?)"?', out, re.IGNORECASE)
    if m_ver:
        raw_ver = m_ver.group(1)
        if raw_ver.startswith("1."):
            parts = raw_ver.split(".")
            if len(parts) > 1:
                try:
                    major = int(parts[1])
                except ValueError:
                    major = 8
        else:
            m_maj = re.match(r"^(\d+)", raw_ver)
            if m_maj:
                major = int(m_maj.group(1))
    else:
        # Fallback to directory/path name parsing if subprocess failed or wasn't run
        path_lower = norm_exe.lower()
        m_dir = re.search(r'(?:jdk|jre|java)[-_]?(\d+)', path_lower)
        if m_dir:
            try:
                major = int(m_dir.group(1))
                raw_ver = f"{major}.0.0"
            except ValueError:
                pass
        elif "1.8" in path_lower or "jre8" in path_lower or "jdk8" in path_lower:
            major = 8
            raw_ver = "1.8.0"

    # Architecture refinement
    is_64bit = pe_info.get("is_64bit", True)
    arch = pe_info.get("arch", "x64")
    if "64-Bit" in out or "x86_64" in out or "amd64" in out:
        is_64bit = True
        arch = "x64"
    elif "32-Bit" in out:
        is_64bit = False
        arch = "x86 (32-bit)"

    # Vendor Classification
    out_lower = out.lower()
    path_lower = norm_exe.lower()
    if "temurin" in out_lower or "adoptium" in out_lower or "adoptium" in path_lower or "temurin" in path_lower:
        vendor = "Eclipse Adoptium (Temurin)"
    elif "microsoft" in out_lower or "microsoft" in path_lower:
        vendor = "Microsoft OpenJDK"
    elif "zulu" in out_lower or "azul" in out_lower or "zulu" in path_lower:
        vendor = "Azul Zulu"
    elif "corretto" in out_lower or "amazon" in out_lower or "corretto" in path_lower:
        vendor = "Amazon Corretto"
    elif "bellsoft" in out_lower or "liberica" in out_lower or "bellsoft" in path_lower:
        vendor = "BellSoft Liberica"
    elif "hotspot" in out_lower or "oracle" in out_lower or "java(tm)" in out_lower:
        vendor = "Oracle Java"
    elif "openjdk" in out_lower:
        vendor = "OpenJDK"
    else:
        vendor = "Custom JDK"

    is_lts = major in (8, 11, 17, 21)
    is_temurin_21 = (major == 21 and "Adoptium" in vendor and is_64bit)
    is_modern_ready = (major >= 21 and is_64bit)
    is_legacy_ready = (major == 8 and is_64bit)

    return {
        "name": f"{vendor} Java {major or raw_ver} ({arch})",
        "path": norm_exe,
        "raw_version": raw_ver,
        "major_version": major,
        "vendor": vendor,
        "arch": arch,
        "is_64bit": is_64bit,
        "is_lts": is_lts,
        "is_temurin_21": is_temurin_21,
        "is_java21": (major == 21),
        "is_java8": (major == 8),
        "is_modern_ready": is_modern_ready,
        "is_legacy_ready": is_legacy_ready,
        "recommended": is_temurin_21 or is_modern_ready,
    }


class JavaService:
    """Discovers installed Java Runtimes and validates JVM versions for Modern and Legacy Minecraft."""

    def __init__(self, root_dir: Optional[str] = None) -> None:
        self.root_dir = os.path.abspath(root_dir) if root_dir else os.getcwd()

    def _probe_java_version(self, java_exe: str) -> str:
        """Executes 'java -version' to retrieve the genuine runtime version string."""
        info = parse_java_runtime_info(java_exe, probe_process=True)
        return info.get("raw_version", "Unknown")

    def discover_java_installations(self) -> Dict[str, Any]:
        """Discovers real Java runtimes via Windows Registry, Environment Variables, and Filesystem directories."""
        found: List[Dict[str, Any]] = []
        seen_canonical_paths = set()

        def _add_candidate(path: str, source: str) -> None:
            if not path or not os.path.exists(path):
                return
            norm = os.path.normpath(path)
            if "oracle\\java\\java8path" in norm.lower() or "oracle/java/java8path" in norm.lower():
                return

            # Prefer javaw.exe for Windows GUI launches if companion exists
            javaw_candidate = os.path.join(os.path.dirname(norm), "javaw.exe")
            target_exe = javaw_candidate if os.path.isfile(javaw_candidate) else norm

            canonical_key = os.path.abspath(target_exe).lower()
            if canonical_key in seen_canonical_paths:
                return
            seen_canonical_paths.add(canonical_key)

            info = parse_java_runtime_info(target_exe, probe_process=True)
            if not info.get("is_valid", True) or not info.get("is_64bit") or info.get("major_version", 0) == 0:
                return

            parent_name = os.path.basename(os.path.dirname(os.path.dirname(target_exe)))

            major = info.get("major_version", 0)
            raw_ver = info.get("raw_version", "Unknown")
            is_64bit = info.get("is_64bit", True)

            if major >= 21 and is_64bit:
                display_ver = f"{raw_ver} (Modern 26.2 Ready)"
            elif major == 8 and is_64bit:
                display_ver = f"{raw_ver} (Legacy 1.8.9 Ready)"
            elif major in (17, 18, 19, 20):
                display_ver = f"{raw_ver} (Minecraft 1.18-1.20)"
            elif not is_64bit:
                display_ver = f"{raw_ver} [32-bit Legacy]"
            else:
                display_ver = f"{raw_ver}"

            entry = {
                "name": f"{info.get('vendor', source)} ({parent_name or 'Java'})",
                "version": display_ver,
                "raw_version": raw_ver,
                "major_version": major,
                "vendor": info.get("vendor", "Custom"),
                "arch": info.get("arch", "x64"),
                "is_64bit": is_64bit,
                "is_lts": info.get("is_lts", False),
                "is_temurin_21": info.get("is_temurin_21", False),
                "is_java21": (major == 21),
                "is_java8": (major == 8),
                "is_modern_ready": info.get("is_modern_ready", False),
                "is_legacy_ready": info.get("is_legacy_ready", False),
                "path": target_exe,
                "source": source,
                "recommended": info.get("recommended", False),
            }
            found.append(entry)

        # 1. Windows Registry Probing (HKLM & HKCU with WOW64_64KEY)
        if sys.platform == "win32" and winreg:
            reg_roots = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Development Kit"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\JRE"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Eclipse Adoptium\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Eclipse Adoptium\JRE"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AdoptOpenJDK\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AdoptOpenJDK\JRE"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Azul Systems\Zulu"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\BellSoft\Liberica"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Amazon Corretto\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Amazon Corretto\JRE"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\JavaSoft\JDK"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Eclipse Adoptium\JDK"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\JDK"),
            ]
            for hkey, subkey_path in reg_roots:
                for access_flag in [winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0), winreg.KEY_READ]:
                    try:
                        with winreg.OpenKey(hkey, subkey_path, 0, access_flag) as k:
                            num_subkeys = winreg.QueryInfoKey(k)[0]
                            for i in range(num_subkeys):
                                ver_name = winreg.EnumKey(k, i)
                                # Try MSI subkey
                                try:
                                    with winreg.OpenKey(k, f"{ver_name}\\MSI", 0, access_flag) as msi_k:
                                        java_home, _ = winreg.QueryValueEx(msi_k, "Path")
                                        for cand in ["bin\\javaw.exe", "bin\\java.exe"]:
                                            exe = os.path.join(java_home, cand)
                                            if os.path.isfile(exe):
                                                _add_candidate(exe, "Eclipse Adoptium / Registry")
                                except Exception:
                                    pass
                                # Try direct JavaHome
                                try:
                                    with winreg.OpenKey(k, ver_name, 0, access_flag) as vk:
                                        java_home, _ = winreg.QueryValueEx(vk, "JavaHome")
                                        for cand in ["bin\\javaw.exe", "bin\\java.exe"]:
                                            exe = os.path.join(java_home, cand)
                                            if os.path.isfile(exe):
                                                _add_candidate(exe, "Registry JDK")
                                except Exception:
                                    pass
                    except Exception:
                        pass

        # 2. Filesystem standard paths
        user_home = os.path.expanduser("~")
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        appdata = os.environ.get("APPDATA", "")

        search_globs = [
            os.path.join(program_files, "Eclipse Adoptium", "*"),
            os.path.join(program_files, "Java", "*"),
            os.path.join(program_files, "Zulu", "*"),
            os.path.join(program_files, "Microsoft", "*"),
            os.path.join(program_files, "BellSoft", "*"),
            os.path.join(program_files, "Amazon Corretto", "*"),
            os.path.join(program_files, "Minecraft Launcher", "runtime", "*"),
            os.path.join(local_appdata, "Programs", "Eclipse Adoptium", "*"),
            os.path.join(local_appdata, "Programs", "Common", "Eclipse Adoptium", "*"),
            os.path.join(user_home, ".jdks", "*"),
            os.path.join(user_home, ".lunarclient", "jre", "*"),
            os.path.join(user_home, ".lunarclient", "jre", "*", "*"),
            os.path.join(appdata, ".minecraft", "runtime", "*"),
            os.path.join(appdata, ".minecraft", "runtime", "*", "*"),
            os.path.join(appdata, "SIR ModPack", "runtime", "*"),
            os.path.join(appdata, "SIR ModPack", "runtime", "*", "*"),
            os.path.join(self.root_dir, "runtime", "*"),
            os.path.join(self.root_dir, "runtime", "*", "*"),
            os.path.join(self.root_dir, "SIR Launcher", "runtime", "*"),
        ]

        for pattern in search_globs:
            for d in glob.glob(pattern):
                for candidate_rel in ["bin/javaw.exe", "bin/java.exe", "javaw.exe", "java.exe"]:
                    exe = os.path.join(d, candidate_rel.replace("/", os.sep))
                    if os.path.isfile(exe):
                        _add_candidate(exe, "Installed Program")

        # 3. JAVA_HOME, JDK_HOME, and PATH discovery
        for env_var in ["JAVA_HOME", "JDK_HOME", "JAVA21_HOME", "JAVA8_HOME"]:
            j_home = os.environ.get(env_var)
            if j_home:
                for candidate_rel in ["bin/javaw.exe", "bin/java.exe"]:
                    exe = os.path.join(j_home, candidate_rel.replace("/", os.sep))
                    if os.path.isfile(exe):
                        _add_candidate(exe, f"Environment ({env_var})")

        which_javaw = shutil.which("javaw")
        if which_javaw:
            _add_candidate(which_javaw, "System PATH")
        which_java = shutil.which("java")
        if which_java:
            _add_candidate(which_java, "System PATH")

        # Ranking & Prioritization:
        # 1. 64-bit Eclipse Temurin 21 LTS
        # 2. 64-bit Java 21+ LTS
        # 3. 64-bit Java 8
        # 4. Other 64-bit Java
        # 5. 32-bit Java
        def _sort_key(item: Dict[str, Any]) -> tuple:
            is_64 = item.get("is_64bit", False)
            major = item.get("major_version", 0)
            is_temurin = item.get("is_temurin_21", False)
            is_j21 = (major == 21)
            is_j8 = (major == 8)
            
            # Highest score comes first
            score = 0
            if is_64 and major >= 25:
                score = 110
            elif is_64 and is_temurin:
                score = 100
            elif is_64 and is_j21:
                score = 90
            elif is_64 and major >= 21:
                score = 80
            elif is_64 and is_j8:
                score = 70
            elif is_64 and major in (17, 18, 19, 20):
                score = 60
            elif is_64:
                score = 50
            else:
                score = 10 # 32-bit
            return (-score, item.get("name", ""))

        found.sort(key=_sort_key)

        return {
            "success": True,
            "installations": found,
            "count": len(found),
        }

    def get_best_runtime_for_version(self, mc_version: str = "26.2") -> Optional[Dict[str, Any]]:
        """Returns the optimal 64-bit Java installation for the specified Minecraft version."""
        installations = self.discover_java_installations().get("installations", [])
        if not installations:
            return None

        is_legacy = any(k in str(mc_version) for k in ["1.8", "1.7", "1.6", "1.5"])
        is_modern_26 = ("26" in str(mc_version))

        if is_legacy:
            # 1. Prefer 64-bit Java 8
            for inst in installations:
                if inst.get("is_64bit") and inst.get("major_version") == 8 and os.path.isfile(inst.get("path", "")):
                    return inst
            return None
        elif is_modern_26:
            # Modern 26.2 officially targets 64-bit Java 25
            for inst in installations:
                if inst.get("is_64bit") and inst.get("major_version", 0) >= 25 and os.path.isfile(inst.get("path", "")):
                    return inst
            for inst in installations:
                if inst.get("is_64bit") and inst.get("major_version", 0) >= 21 and os.path.isfile(inst.get("path", "")):
                    return inst
            return None
        else:
            # Standard 1.21.x: 64-bit Java 21+
            for inst in installations:
                if inst.get("is_64bit") and inst.get("major_version", 0) >= 21 and os.path.isfile(inst.get("path", "")):
                    return inst
            return None

    def find_eclipse_temurin_21(self) -> Optional[str]:
        """Locates Eclipse Temurin 21 LTS x64 executable path if available."""
        best = self.get_best_runtime_for_version("1.21.4")
        if best and best.get("is_64bit") and best.get("major_version") == 21:
            return best.get("path")
        return None

    def find_jre_8(self) -> Optional[str]:
        """Locates 64-bit JRE 8 executable path if available."""
        best = self.get_best_runtime_for_version("1.8.9")
        if best and best.get("major_version") == 8:
            return best.get("path")
        return None

    def ensure_java_runtime(
        self,
        version_hint: int = 25,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> str:
        """Ensures a verified Java runtime exists on the PC; auto-downloads OpenJDK 25/8 if missing."""
        if isinstance(version_hint, str):
            version_hint = 8 if any(k in version_hint for k in ["1.8", "1.7"]) else 25
        ver_str = "1.8.9" if version_hint <= 8 else ("26.2" if version_hint >= 25 else "1.21.4")
        best = self.get_best_runtime_for_version(ver_str)
        if best and os.path.isfile(best.get("path", "")):
            if version_hint >= 25 and best.get("major_version", 0) >= 25 and best.get("is_64bit"):
                return best["path"]
            elif 8 < version_hint < 25 and best.get("major_version", 0) >= 21 and best.get("is_64bit"):
                return best["path"]
            elif version_hint <= 8 and best.get("major_version") == 8 and best.get("is_64bit"):
                return best["path"]

        # Check bundled runtime paths
        appdata = os.environ.get("APPDATA", "")
        dest_runtime_dir = os.path.join(appdata, "SIR ModPack", "runtime", f"java-{version_hint}")
        candidate_exe = os.path.join(dest_runtime_dir, "bin", "javaw.exe" if sys.platform == "win32" else "java")
        if os.path.isfile(candidate_exe):
            info = parse_java_runtime_info(candidate_exe, probe_process=True)
            if info.get("is_valid") and info.get("is_64bit") and ((version_hint >= 25 and info.get("major_version", 0) >= 25) or (version_hint <= 8 and info.get("major_version") == 8) or (info.get("major_version", 0) >= 21)):
                return candidate_exe

        def notify(msg: str, pct: int):
            if progress_callback:
                progress_callback(msg, pct)

        target_ver = 25 if version_hint >= 25 else (8 if version_hint <= 8 else 21)
        notify(f"Downloading OpenJDK {target_ver} Runtime for Minecraft...", 15)
        os.makedirs(dest_runtime_dir, exist_ok=True)

        if target_ver == 25:
            dl_urls = [
                "https://api.adoptium.net/v3/binary/latest/25/ga/windows/x64/jdk/hotspot/normal/eclipse",
                "https://api.adoptium.net/v3/binary/latest/25/ea/windows/x64/jdk/hotspot/normal/eclipse",
                "https://download.oracle.com/java/25/latest/jdk-25_windows-x64_bin.zip",
            ]
        elif target_ver == 8:
            dl_urls = [
                "https://api.adoptium.net/v3/binary/latest/8/ga/windows/x64/jdk/hotspot/normal/eclipse",
            ]
        else:
            dl_urls = [
                "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse",
            ]

        zip_temp = os.path.join(tempfile.gettempdir(), f"openjdk_{target_ver}_{int(os.getpid())}.zip")

        for dl_url in dl_urls:
            try:
                download_file_resilient(dl_url, zip_temp, max_retries=3, timeout=120.0)
                notify("Extracting Java Runtime...", 75)
                parent_dir = os.path.dirname(dest_runtime_dir)
                with zipfile.ZipFile(zip_temp, "r") as z:
                    top_items = {name.split("/")[0] for name in z.namelist() if "/" in name}
                    top_dir = list(top_items)[0] if len(top_items) == 1 else ""
                    z.extractall(parent_dir)
                    if top_dir:
                        extracted_root = os.path.join(parent_dir, top_dir)
                        if os.path.isdir(extracted_root) and os.path.abspath(extracted_root) != os.path.abspath(dest_runtime_dir):
                            if os.path.exists(dest_runtime_dir):
                                shutil.rmtree(dest_runtime_dir, ignore_errors=True)
                            os.rename(extracted_root, dest_runtime_dir)

                try:
                    os.remove(zip_temp)
                except Exception:
                    pass

                for exe_name in ["javaw.exe", "java.exe", "javaw", "java"]:
                    target_java = os.path.join(dest_runtime_dir, "bin", exe_name)
                    if os.path.isfile(target_java):
                        info = parse_java_runtime_info(target_java, probe_process=True)
                        if info.get("is_valid") and info.get("is_64bit"):
                            notify(f"✓ OpenJDK {target_ver} ready!", 100)
                            return target_java
            except Exception as e:
                print(f"[JavaService] Mirror {dl_url} failed: {e}")

        # Fallback to system Java only if verified 64-bit and compatible
        which_j = shutil.which("javaw.exe") or shutil.which("java.exe")
        if which_j and os.path.isfile(which_j):
            info = parse_java_runtime_info(which_j, probe_process=True)
            if info.get("is_valid") and info.get("is_64bit"):
                return which_j

        return "javaw"

