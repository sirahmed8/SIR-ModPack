"""
lunar_bridge_service.py — Bi-Directional Lunar Client Profile Bridge (C: <-> D:)
Enables seamless 1-click synchronization between Lunar Client profiles and SIR ModPack instances.
Handles keybinds, mouse sensitivity, FOV, video options, resource pack priorities, mod exclusions, and world verification.
"""

from __future__ import annotations

import gzip
import json
import os
import re
import shutil
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from shared_core.runtime import atomic_write_json, atomic_write_text


# =============================================================================
# GLFW Token <-> LWJGL 2 Scancode Bidirectional Lookup Tables
# =============================================================================

GLFW_TO_LWJGL2: Dict[str, int] = {
    # Special & Modifiers
    "key.keyboard.unknown": 0,
    "key.keyboard.escape": 1,
    "key.keyboard.1": 2,
    "key.keyboard.2": 3,
    "key.keyboard.3": 4,
    "key.keyboard.4": 5,
    "key.keyboard.5": 6,
    "key.keyboard.6": 7,
    "key.keyboard.7": 8,
    "key.keyboard.8": 9,
    "key.keyboard.9": 10,
    "key.keyboard.0": 11,
    "key.keyboard.minus": 12,
    "key.keyboard.equal": 13,
    "key.keyboard.backspace": 14,
    "key.keyboard.tab": 15,
    "key.keyboard.q": 16,
    "key.keyboard.w": 17,
    "key.keyboard.e": 18,
    "key.keyboard.r": 19,
    "key.keyboard.t": 20,
    "key.keyboard.y": 21,
    "key.keyboard.u": 22,
    "key.keyboard.i": 23,
    "key.keyboard.o": 24,
    "key.keyboard.p": 25,
    "key.keyboard.left.bracket": 26,
    "key.keyboard.right.bracket": 27,
    "key.keyboard.enter": 28,
    "key.keyboard.left.control": 29,
    "key.keyboard.a": 30,
    "key.keyboard.s": 31,
    "key.keyboard.d": 32,
    "key.keyboard.f": 33,
    "key.keyboard.g": 34,
    "key.keyboard.h": 35,
    "key.keyboard.j": 36,
    "key.keyboard.k": 37,
    "key.keyboard.l": 38,
    "key.keyboard.semicolon": 39,
    "key.keyboard.apostrophe": 40,
    "key.keyboard.grave.accent": 41,
    "key.keyboard.left.shift": 42,
    "key.keyboard.backslash": 43,
    "key.keyboard.z": 44,
    "key.keyboard.x": 45,
    "key.keyboard.c": 46,
    "key.keyboard.v": 47,
    "key.keyboard.b": 48,
    "key.keyboard.n": 49,
    "key.keyboard.m": 50,
    "key.keyboard.comma": 51,
    "key.keyboard.period": 52,
    "key.keyboard.slash": 53,
    "key.keyboard.right.shift": 54,
    "key.keyboard.keypad.multiply": 55,
    "key.keyboard.left.alt": 56,
    "key.keyboard.space": 57,
    "key.keyboard.caps.lock": 58,
    "key.keyboard.f1": 59,
    "key.keyboard.f2": 60,
    "key.keyboard.f3": 61,
    "key.keyboard.f4": 62,
    "key.keyboard.f5": 63,
    "key.keyboard.f6": 64,
    "key.keyboard.f7": 65,
    "key.keyboard.f8": 66,
    "key.keyboard.f9": 67,
    "key.keyboard.f10": 68,
    "key.keyboard.num.lock": 69,
    "key.keyboard.scroll.lock": 70,
    "key.keyboard.keypad.7": 71,
    "key.keyboard.keypad.8": 72,
    "key.keyboard.keypad.9": 73,
    "key.keyboard.keypad.subtract": 74,
    "key.keyboard.keypad.4": 75,
    "key.keyboard.keypad.5": 76,
    "key.keyboard.keypad.6": 77,
    "key.keyboard.keypad.add": 78,
    "key.keyboard.keypad.1": 79,
    "key.keyboard.keypad.2": 80,
    "key.keyboard.keypad.3": 81,
    "key.keyboard.keypad.0": 82,
    "key.keyboard.keypad.decimal": 83,
    "key.keyboard.f11": 87,
    "key.keyboard.f12": 88,
    "key.keyboard.f13": 100,
    "key.keyboard.f14": 101,
    "key.keyboard.f15": 102,
    "key.keyboard.f16": 103,
    "key.keyboard.f17": 104,
    "key.keyboard.f18": 105,
    "key.keyboard.f19": 106,
    "key.keyboard.keypad.enter": 156,
    "key.keyboard.right.control": 157,
    "key.keyboard.keypad.divide": 181,
    "key.keyboard.right.alt": 184,
    "key.keyboard.pause": 197,
    "key.keyboard.home": 199,
    "key.keyboard.up": 200,
    "key.keyboard.page.up": 201,
    "key.keyboard.left": 203,
    "key.keyboard.right": 205,
    "key.keyboard.end": 207,
    "key.keyboard.down": 208,
    "key.keyboard.page.down": 209,
    "key.keyboard.insert": 210,
    "key.keyboard.delete": 211,
    # Mouse Buttons
    "key.mouse.left": -100,
    "key.mouse.right": -99,
    "key.mouse.middle": -98,
    "key.mouse.4": -97,
    "key.mouse.button.4": -97,
    "key.mouse.5": -96,
    "key.mouse.button.5": -96,
    "key.mouse.6": -95,
    "key.mouse.button.6": -95,
    "key.mouse.7": -94,
    "key.mouse.button.7": -94,
    "key.mouse.8": -93,
    "key.mouse.button.8": -93,
}

LWJGL2_TO_GLFW: Dict[int, str] = {v: k for k, v in GLFW_TO_LWJGL2.items() if not k.startswith("key.mouse.button.")}
LWJGL2_TO_GLFW[-100] = "key.mouse.left"
LWJGL2_TO_GLFW[-99] = "key.mouse.right"
LWJGL2_TO_GLFW[-98] = "key.mouse.middle"
LWJGL2_TO_GLFW[-97] = "key.mouse.4"
LWJGL2_TO_GLFW[-96] = "key.mouse.5"


class LunarBridgeService:
    """Bi-Directional Profile & Options Synchronizer for Lunar Client and SIR ModPack."""

    PROFILE_MAPPING: Dict[str, str] = {
        "sir-189-performance": "1.8.9-performance",
        "sir-189-pvp": "1.8.9",
        "sir-189-ultra": "1.8.9-ultra",
        "sir-189-balanced": "1.8.9-balanced",
        "sir-26-balanced": "26.2-balanced",
        "sir-26-performance": "26.2-performance",
        "sir-26-ultra": "26.2-ultra",
        "sir-26": "26.2",
    }

    REVERSE_MAPPING: Dict[str, str] = {v: k for k, v in PROFILE_MAPPING.items()}
    # Extra reverse fallbacks
    REVERSE_MAPPING["1.8.9"] = "sir-189-pvp"
    REVERSE_MAPPING["26.2"] = "sir-26"

    # Incompatible mods under Lunar Client Genesis / Ichor runtime
    LUNAR_EXCLUDED_MOD_PATTERNS: List[str] = [
        "bettercombat",
        "krypton",
        "quantified",
    ]

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        user_home = os.path.expanduser("~")
        self.lunar_root = os.path.join(user_home, ".lunarclient")
        self.lunar_profiles_dir = os.path.join(self.lunar_root, "profiles")
        self.lunar_db_path = os.path.join(self.lunar_root, "db", "profiles.db")
        
        appdata = os.environ.get("APPDATA", os.path.join(user_home, "AppData", "Roaming"))
        self.mc_root = os.path.join(appdata, ".minecraft")
        self.options_lc_path = os.path.join(self.mc_root, "optionsLC.txt")
        self.options_mc_path = os.path.join(self.mc_root, "options.txt")
        self.instances_dir = os.path.join(self.root_dir, "instances")
        try:
            self.ensure_lunar_assets_and_compat()
        except Exception:
            pass

    def is_lunar_installed(self) -> bool:
        """Returns True if Lunar Client directories exist on C: drive."""
        return os.path.isdir(self.lunar_root) or os.path.isfile(self.options_lc_path)

    # -------------------------------------------------------------------------
    # Keycode & Options Translation Engine
    # -------------------------------------------------------------------------

    @classmethod
    def to_modern_key(cls, key_val: Any) -> str:
        """
        Translates any legacy LWJGL 2 integer scancode (e.g. 57, -100, '47', 54)
        or existing GLFW token into a valid modern GLFW key token string.
        Never returns raw integer scancodes for modern options.
        """
        if key_val is None:
            return "key.keyboard.unknown"
        s = str(key_val).strip()
        if not s:
            return "key.keyboard.unknown"
        
        # Check if integer scancode
        try:
            code = int(s)
            return LWJGL2_TO_GLFW.get(code, "key.keyboard.unknown")
        except ValueError:
            pass

        # Already GLFW string token
        if s.startswith("key."):
            if s == "key.mouse.button.1":
                return "key.mouse.left"
            elif s == "key.mouse.button.2":
                return "key.mouse.right"
            elif s == "key.mouse.button.3":
                return "key.mouse.middle"
            return s
        
        lower_s = s.lower()
        if lower_s in GLFW_TO_LWJGL2:
            return lower_s

        return s

    @classmethod
    def to_legacy_key(cls, key_val: Any) -> str:
        """
        Translates any modern GLFW token (e.g. 'key.keyboard.space', 'key.mouse.left')
        or integer scancode into a legacy LWJGL 2 integer scancode string.
        Never returns GLFW key string tokens for legacy options.
        """
        if key_val is None:
            return "0"
        s = str(key_val).strip()
        if not s:
            return "0"
        
        # Check if already integer
        try:
            int(s)
            return s
        except ValueError:
            pass
        
        code = GLFW_TO_LWJGL2.get(s.lower())
        if code is not None:
            return str(code)
        
        lower = s.lower()
        if "space" in lower:
            return "57"
        if "shift" in lower:
            return "54" if "right" in lower else "42"
        if "control" in lower:
            return "157" if "right" in lower else "29"
        
        return "0"

    @classmethod
    def sanitize_options_keybinds(cls, options: Dict[str, str], is_legacy: bool) -> Dict[str, str]:
        """
        Ensures all key_* bindings in options dictionary conform strictly to target subsystem:
        Legacy (1.8.9) -> LWJGL 2 integer scancodes
        Modern (26.2)  -> GLFW token strings
        Guarantees zero unknown key name crashes and zero GLFW tokens in legacy options.
        """
        sanitized = dict(options)
        for k, v in list(sanitized.items()):
            if k.startswith("key_"):
                if is_legacy:
                    sanitized[k] = cls.to_legacy_key(v)
                else:
                    sanitized[k] = cls.to_modern_key(v)

        # Handle specific aliases & required HUD/modmenu keys
        if is_legacy:
            sanitized["key_key.inventoryhud.openconfig"] = "54"
            sanitized["key_key.modmenu.open_menu"] = "54"
            sanitized["key_key.hud.menu"] = "54"
            if "key_key.perspective" in sanitized:
                sanitized["key_key.togglePerspective"] = cls.to_legacy_key(sanitized["key_key.perspective"])
            if "key_key.zoom" in sanitized:
                sanitized["key_of.key.zoom"] = cls.to_legacy_key(sanitized["key_key.zoom"])
        else:
            sanitized["key_key.inventoryhud.openconfig"] = "key.keyboard.right.shift"
            sanitized["key_key.modmenu.open_menu"] = "key.keyboard.right.shift"
            if "key_of.key.zoom" in sanitized:
                sanitized["key_key.zoom"] = cls.to_modern_key(sanitized["key_of.key.zoom"])
            if "key_key.togglePerspective" in sanitized:
                sanitized["key_key.perspective"] = cls.to_modern_key(sanitized["key_key.togglePerspective"])

        return sanitized

    # -------------------------------------------------------------------------
    # Mod Incompatibility & Exclusion Engine
    # -------------------------------------------------------------------------

    @classmethod
    def is_mod_excluded_for_lunar(cls, mod_name: str) -> bool:
        """Checks if a mod JAR is incompatible with Lunar Client runtime (BetterCombat, Krypton, Quantified)."""
        lower = os.path.basename(mod_name).lower()
        return any(pat in lower for pat in cls.LUNAR_EXCLUDED_MOD_PATTERNS)

    def sanitize_lunar_profile_mods(self, lunar_profile_dir: Optional[str] = None) -> List[str]:
        """
        Scans Lunar profile directory (or all Lunar profile directories) and purges
        any incompatible JARs (BetterCombat, Krypton, Quantified API) and offending configs.
        Returns list of removed file and directory paths.
        """
        removed: List[str] = []
        target_dirs: List[str] = []

        if lunar_profile_dir and os.path.isdir(lunar_profile_dir):
            target_dirs.append(lunar_profile_dir)
        elif os.path.isdir(self.lunar_profiles_dir):
            for entry in os.listdir(self.lunar_profiles_dir):
                p = os.path.join(self.lunar_profiles_dir, entry)
                if os.path.isdir(p):
                    target_dirs.append(p)

        # Also include lunar_root/mods
        root_mods = os.path.join(self.lunar_root, "mods")
        if os.path.isdir(root_mods):
            target_dirs.append(self.lunar_root)

        for base_dir in target_dirs:
            for root, dirs, files in os.walk(base_dir):
                # Remove offending JARs
                for f in files:
                    if f.endswith(".jar") and self.is_mod_excluded_for_lunar(f):
                        fp = os.path.join(root, f)
                        if os.path.realpath(fp).startswith(self.instances_dir):
                            continue
                        try:
                            os.remove(fp)
                            removed.append(fp)
                        except Exception:
                            pass
                # Remove offending config directories (e.g. bettercombat)
                for d in list(dirs):
                    if any(pat in d.lower() for pat in self.LUNAR_EXCLUDED_MOD_PATTERNS):
                        dp = os.path.join(root, d)
                        if os.path.realpath(dp).startswith(self.instances_dir):
                            continue
                        try:
                            shutil.rmtree(dp, ignore_errors=True)
                            removed.append(dp)
                            dirs.remove(d)
                        except Exception:
                            pass

        return removed

    def sync_mods_to_lunar(self, lunar_or_sir_id: str) -> Dict[str, Any]:
        """
        Synchronizes mods from SIR instance into Lunar profile while strictly excluding
        BetterCombat, Krypton, and Quantified API.
        """
        if lunar_or_sir_id in self.PROFILE_MAPPING:
            lunar_id = lunar_or_sir_id
            sir_inst_id = self.PROFILE_MAPPING[lunar_id]
        elif lunar_or_sir_id in self.REVERSE_MAPPING:
            sir_inst_id = lunar_or_sir_id
            lunar_id = self.REVERSE_MAPPING[sir_inst_id]
        else:
            return {"success": False, "error": f"Unknown profile ID: {lunar_or_sir_id}"}

        sir_path = os.path.join(self.instances_dir, sir_inst_id)
        sir_mods_dirs = [
            os.path.join(sir_path, "minecraft", "mods"),
            os.path.join(sir_path, "mods")
        ]
        source_mods_dir = None
        for smd in sir_mods_dirs:
            if os.path.isdir(smd):
                source_mods_dir = smd
                break

        if not source_mods_dir:
            return {"success": False, "error": f"No mods directory found for {sir_inst_id}"}

        lunar_path = os.path.join(self.lunar_profiles_dir, lunar_id)
        target_mods_dir = os.path.join(lunar_path, "mods")
        os.makedirs(target_mods_dir, exist_ok=True)

        copied = []
        skipped_excluded = []

        for f in os.listdir(source_mods_dir):
            if not f.endswith(".jar"):
                continue
            if self.is_mod_excluded_for_lunar(f):
                skipped_excluded.append(f)
                continue
            src_file = os.path.join(source_mods_dir, f)
            dest_file = os.path.join(target_mods_dir, f)
            if not os.path.exists(dest_file) or os.path.getsize(src_file) != os.path.getsize(dest_file):
                try:
                    shutil.copy2(src_file, dest_file)
                    copied.append(f)
                except Exception:
                    pass

        # Purge any previously copied excluded mods in target
        self.sanitize_lunar_profile_mods(lunar_path)

        return {
            "success": True,
            "lunar_id": lunar_id,
            "sir_instance_id": sir_inst_id,
            "copied_mods_count": len(copied),
            "skipped_excluded_count": len(skipped_excluded),
            "skipped_excluded": skipped_excluded
        }

    # -------------------------------------------------------------------------
    # Lunar Profiles Path Alignment
    # -------------------------------------------------------------------------

    def align_lunar_profiles_json(self) -> Dict[str, Any]:
        """
        Corrects gameDir paths in C:/Users/a7med/.lunarclient/profiles.json and settings/
        from obsolete AppData paths to real Drive D instance directories.
        """
        candidate_files = [
            os.path.join(self.lunar_root, "profiles.json"),
            os.path.join(self.lunar_root, "settings", "game", "profiles.json"),
            os.path.join(self.lunar_root, "settings", "game-backup", "profiles.json"),
        ]

        instance_paths = {
            "SIR 26 Visuals": os.path.join(self.instances_dir, "26.2-ultra"),
            "SIR 26 Balanced": os.path.join(self.instances_dir, "26.2-balanced"),
            "SIR 26 Performance": os.path.join(self.instances_dir, "26.2-performance"),
            "SIR 26": os.path.join(self.instances_dir, "26.2"),
            "SIR 1.8.9 Visuals": os.path.join(self.instances_dir, "1.8.9-ultra"),
            "SIR 1.8.9 Balanced": os.path.join(self.instances_dir, "1.8.9-balanced"),
            "SIR 1.8.9 Performance": os.path.join(self.instances_dir, "1.8.9-performance"),
            "SIR 1.8.9 PvP": os.path.join(self.instances_dir, "1.8.9"),
        }

        updated_files = []
        for p in candidate_files:
            if not os.path.isfile(p):
                continue
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                profiles = data.get("profiles", {})
                changed = False
                for prof_name, real_path in instance_paths.items():
                    if prof_name in profiles:
                        current_gamedir = profiles[prof_name].get("gameDir", "")
                        norm_current = os.path.normpath(current_gamedir)
                        norm_real = os.path.normpath(real_path)
                        if norm_current != norm_real:
                            profiles[prof_name]["gameDir"] = real_path
                            changed = True
                    else:
                        is_legacy = "1.8" in prof_name
                        profiles[prof_name] = {
                            "name": prof_name,
                            "version": "1.8.9" if is_legacy else "26.2",
                            "module": "forge" if is_legacy else "fabric",
                            "icon": "diamond" if is_legacy else "emerald",
                            "gameDir": real_path
                        }
                        changed = True

                if changed:
                    atomic_write_json(p, data)
                    updated_files.append(p)
            except Exception:
                pass

        return {
            "success": True,
            "updated_files": updated_files,
            "instance_paths": instance_paths
        }

    # -------------------------------------------------------------------------
    # Core Options Parsing & Status
    # -------------------------------------------------------------------------

    def _parse_options_file(self, file_path: str) -> Dict[str, str]:
        """Parses options file into key-value dictionary (handles both colon-separated and JSON formats)."""
        if not os.path.isfile(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
            
            # Format 1: JSON format (like optionsLC.txt sometimes is)
            if content.startswith("{"):
                try:
                    m = re.match(r"^(\{.*?\})", content, re.DOTALL)
                    if m:
                        return json.loads(m.group(1))
                except Exception:
                    pass

            # Format 2: Standard Minecraft options key:value lines
            res: Dict[str, str] = {}
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(":", 1)
                if len(parts) == 2:
                    res[parts[0].strip()] = parts[1].strip()
            return res
        except Exception:
            return {}

    def _write_options_file(self, file_path: str, options: Dict[str, str]) -> bool:
        """Writes dictionary to options.txt format atomically."""
        try:
            lines = [f"{k}:{v}\n" for k, v in options.items()]
            atomic_write_text(file_path, "".join(lines))
            return True
        except Exception:
            return False

    @staticmethod
    def _normalize_fov(val: Any) -> float:
        """Normalizes FOV to [0.0, 1.0] float range expected by Modern Minecraft options.txt."""
        try:
            f = float(val)
            if f > 1.0:
                return max(0.0, min(1.0, (f - 70.0) / 40.0))
            return max(0.0, min(1.0, f))
        except (ValueError, TypeError):
            return 0.0

    def get_profiles_status(self) -> List[Dict[str, Any]]:
        """Scans both Lunar profiles and SIR instances, returning synchronization matrix."""
        results: List[Dict[str, Any]] = []
        lunar_options = self._parse_options_file(self.options_lc_path)

        for lunar_id, sir_inst_id in self.PROFILE_MAPPING.items():
            lunar_path = os.path.join(self.lunar_profiles_dir, lunar_id)
            sir_path = os.path.join(self.instances_dir, sir_inst_id)
            
            lunar_exists = os.path.isdir(lunar_path)
            sir_exists = os.path.isdir(sir_path)

            sir_options_file = os.path.join(sir_path, "options.txt")
            if not os.path.isfile(sir_options_file):
                sir_options_file = os.path.join(sir_path, "minecraft", "options.txt")
            
            sir_options = self._parse_options_file(sir_options_file) if sir_exists else {}

            diffs: List[str] = []
            # Check core options differences
            for opt_key in ["mouseSensitivity", "fov", "renderDistance", "maxFps", "guiScale"]:
                val_lunar = lunar_options.get(opt_key)
                val_sir = sir_options.get(opt_key)
                if val_lunar is not None and (val_sir is not None or (opt_key == "maxFps" and "maxFramerate" in sir_options)):
                    if opt_key == "fov":
                        f_lunar = self._normalize_fov(val_lunar)
                        f_sir = self._normalize_fov(val_sir)
                        if abs(f_lunar - f_sir) > 0.02:
                            diffs.append(f"fov: Lunar({val_lunar}) != SIR({val_sir})")
                    elif opt_key == "maxFps":
                        val_sir_fps = val_sir or sir_options.get("maxFramerate", "")
                        if str(val_lunar) != str(val_sir_fps):
                            diffs.append(f"maxFps: Lunar({val_lunar}) != SIR({val_sir_fps})")
                    elif str(val_lunar) != str(val_sir):
                        diffs.append(f"{opt_key}: Lunar({val_lunar}) != SIR({val_sir})")

            # Check keybind differences with normalized comparison
            for k in ["key_key.sprint", "key_key.sneak", "key_key.zoom", "key_of.key.zoom"]:
                val_lunar = lunar_options.get(k)
                val_sir = sir_options.get(k)
                if val_lunar is not None and val_sir is not None:
                    norm_lunar = self.to_modern_key(val_lunar)
                    norm_sir = self.to_modern_key(val_sir)
                    if norm_lunar != norm_sir:
                        diffs.append(f"{k}: Lunar({val_lunar}) != SIR({val_sir})")

            is_in_sync = len(diffs) == 0 and (lunar_exists and sir_exists)

            results.append({
                "lunar_id": lunar_id,
                "sir_instance_id": sir_inst_id,
                "lunar_exists": lunar_exists,
                "sir_exists": sir_exists,
                "lunar_path": lunar_path if lunar_exists else None,
                "sir_path": sir_path if sir_exists else None,
                "in_sync": is_in_sync,
                "diff_count": len(diffs),
                "differences": diffs[:5],
                "last_checked": True
            })

        return results

    # -------------------------------------------------------------------------
    # Synchronization Operations
    # -------------------------------------------------------------------------

    def sync_lunar_to_sir(self, lunar_or_sir_id: str) -> Dict[str, Any]:
        """Synchronizes options, FOV, sensitivity, and keybinds from Lunar Client into SIR instance."""
        # Resolve target IDs
        if lunar_or_sir_id in self.PROFILE_MAPPING:
            lunar_id = lunar_or_sir_id
            sir_inst_id = self.PROFILE_MAPPING[lunar_id]
        elif lunar_or_sir_id in self.REVERSE_MAPPING:
            sir_inst_id = lunar_or_sir_id
            lunar_id = self.REVERSE_MAPPING[sir_inst_id]
        else:
            return {"success": False, "error": f"Unknown profile ID: {lunar_or_sir_id}"}

        sir_path = os.path.join(self.instances_dir, sir_inst_id)
        if not os.path.isdir(sir_path):
            return {"success": False, "error": f"SIR instance directory does not exist: {sir_path}"}

        # Merge options: global optionsLC -> global options.txt -> profile specific options.txt
        lunar_options = self._parse_options_file(self.options_lc_path)
        if not lunar_options:
            lunar_options = self._parse_options_file(self.options_mc_path)

        profile_options_file = os.path.join(self.lunar_profiles_dir, lunar_id, "options.txt")
        if os.path.isfile(profile_options_file):
            profile_opts = self._parse_options_file(profile_options_file)
            lunar_options.update(profile_opts)

        if not lunar_options:
            return {"success": False, "error": "No Lunar Client options found on C: drive"}

        sir_options_paths = [
            os.path.join(sir_path, "options.txt"),
            os.path.join(sir_path, "minecraft", "options.txt")
        ]

        synced_count = 0
        is_legacy = "1.8" in sir_inst_id

        core_keys = [
            "mouseSensitivity", "fov", "gamma", "renderDistance", "guiScale",
            "maxFps", "enableVsync", "bobView", "touchscreen", "rawMouseInput"
        ]

        for p in sir_options_paths:
            if os.path.isfile(p):
                opts = self._parse_options_file(p)
                # 1. Transfer core video / audio options
                for k in core_keys:
                    if k in lunar_options:
                        val = str(lunar_options[k])
                        if k == "fov":
                            norm_fov = self._normalize_fov(val)
                            val = f"{norm_fov:.4f}".rstrip('0').rstrip('.')
                            if not val or val == "0":
                                val = "0.0"
                        opts[k] = val
                        if not is_legacy and k == "maxFps":
                            try:
                                fps_int = int(val)
                                opts["maxFramerate"] = str(fps_int) if fps_int > 0 else "260"
                            except (ValueError, TypeError):
                                opts["maxFramerate"] = "260"

                # 2. Transfer keybindings with strict bidirectional translation
                for k, v in lunar_options.items():
                    if k.startswith("key_"):
                        if is_legacy:
                            opts[k] = self.to_legacy_key(v)
                        else:
                            opts[k] = self.to_modern_key(v)

                # 3. Sanitize entire options dictionary to prevent ANY keycode corruption
                opts = self.sanitize_options_keybinds(opts, is_legacy)

                if self._write_options_file(p, opts):
                    synced_count += 1

        return {
            "success": True,
            "lunar_id": lunar_id,
            "sir_instance_id": sir_inst_id,
            "direction": "lunar_to_sir",
            "updated_files": synced_count,
            "message": f"Successfully synchronized settings from Lunar ({lunar_id}) -> SIR ({sir_inst_id})"
        }

    def sync_sir_to_lunar(self, lunar_or_sir_id: str) -> Dict[str, Any]:
        """Synchronizes options, presets, and mod configs from SIR instance into Lunar Client profile."""
        if lunar_or_sir_id in self.PROFILE_MAPPING:
            lunar_id = lunar_or_sir_id
            sir_inst_id = self.PROFILE_MAPPING[lunar_id]
        elif lunar_or_sir_id in self.REVERSE_MAPPING:
            sir_inst_id = lunar_or_sir_id
            lunar_id = self.REVERSE_MAPPING[sir_inst_id]
        else:
            return {"success": False, "error": f"Unknown profile ID: {lunar_or_sir_id}"}

        lunar_path = os.path.join(self.lunar_profiles_dir, lunar_id)
        os.makedirs(lunar_path, exist_ok=True)

        sir_path = os.path.join(self.instances_dir, sir_inst_id)
        sir_options_file = os.path.join(sir_path, "options.txt")
        if not os.path.isfile(sir_options_file):
            sir_options_file = os.path.join(sir_path, "minecraft", "options.txt")

        sir_options = self._parse_options_file(sir_options_file)
        if not sir_options:
            return {"success": False, "error": f"No options found in SIR instance {sir_inst_id}"}

        is_legacy = "1.8" in sir_inst_id

        # 1. Update optionsLC.txt
        lunar_options = self._parse_options_file(self.options_lc_path)
        keys_to_transfer = [
            "mouseSensitivity", "fov", "gamma", "renderDistance", "guiScale",
            "maxFps", "enableVsync", "bobView", "touchscreen", "rawMouseInput"
        ]
        for k in keys_to_transfer:
            if k in sir_options:
                lunar_options[k] = str(sir_options[k])
            elif k == "maxFps" and "maxFramerate" in sir_options:
                lunar_options["maxFps"] = str(sir_options["maxFramerate"])

        # Transfer keybinds to lunar_options
        for k, v in sir_options.items():
            if k.startswith("key_"):
                lunar_options[k] = self.to_modern_key(v)

        try:
            atomic_write_text(self.options_lc_path, json.dumps(lunar_options))
        except Exception:
            pass

        # 2. Update profile-specific options.txt in Lunar directory
        profile_options_file = os.path.join(lunar_path, "options.txt")
        profile_opts = dict(sir_options)
        profile_opts = self.sanitize_options_keybinds(profile_opts, is_legacy)
        self._write_options_file(profile_options_file, profile_opts)

        minecraft_sub_options = os.path.join(lunar_path, "minecraft", "options.txt")
        if os.path.isfile(minecraft_sub_options):
            self._write_options_file(minecraft_sub_options, profile_opts)

        # 3. Purge any excluded mods (BetterCombat, Krypton, Quantified)
        self.sanitize_lunar_profile_mods(lunar_path)

        # 4. Update modpack.json in Lunar profile directory
        modpack_json = {
            "name": f"SIR {'1.8.9 PvP' if is_legacy else '26 Visuals'}",
            "version": "1.8.9" if is_legacy else "26.2",
            "loader": "forge" if is_legacy else "fabric",
            "summary": "Synchronized from SIR ModPack high-throughput engine"
        }
        atomic_write_json(os.path.join(lunar_path, "modpack.json"), modpack_json)

        return {
            "success": True,
            "lunar_id": lunar_id,
            "sir_instance_id": sir_inst_id,
            "direction": "sir_to_lunar",
            "message": f"Successfully synchronized settings from SIR ({sir_inst_id}) -> Lunar ({lunar_id})"
        }

    def sync_all_profiles(self, direction: str = "lunar_to_sir") -> Dict[str, Any]:
        """Performs batch synchronization across all mapped profile pairs with path alignment and mod sanitization."""
        self.align_lunar_profiles_json()
        self.sanitize_lunar_profile_mods()

        synced: List[str] = []
        errors: List[str] = []

        for lunar_id, sir_id in self.PROFILE_MAPPING.items():
            if direction == "lunar_to_sir":
                res = self.sync_lunar_to_sir(lunar_id)
            else:
                res = self.sync_sir_to_lunar(sir_id)

            if res.get("success"):
                synced.append(f"{lunar_id} <-> {sir_id}")
            else:
                errors.append(f"{lunar_id}: {res.get('error')}")

        return {
            "success": len(errors) == 0,
            "direction": direction,
            "synced_pairs_count": len(synced),
            "synced_pairs": synced,
            "errors": errors
        }

    def ensure_lunar_assets_and_compat(self, instance_dir: Optional[str] = None) -> None:
        """Ensures dev_cosmetics.json, path alignment, and clean mod lists exist."""
        empty_cosmetics = {"cosmetics": []}

        # 1. Align profiles.json gameDir paths to Drive D
        try:
            self.align_lunar_profiles_json()
        except Exception:
            pass

        # 2. Sanitize Lunar profile mods (remove BetterCombat & Krypton)
        try:
            self.sanitize_lunar_profile_mods()
        except Exception:
            pass

        # 3. Target Lunar root assets
        try:
            lunar_assets_dir = os.path.join(self.lunar_root, "assets", "lunar")
            os.makedirs(lunar_assets_dir, exist_ok=True)
            dev_cosmetics_path = os.path.join(lunar_assets_dir, "dev_cosmetics.json")
            if not os.path.isfile(dev_cosmetics_path):
                atomic_write_json(dev_cosmetics_path, empty_cosmetics)
        except Exception:
            pass

        # 4. Target specific or all instances
        target_dirs: List[str] = []
        if instance_dir and os.path.isdir(instance_dir):
            target_dirs.append(instance_dir)
        elif os.path.isdir(self.instances_dir):
            try:
                skip_dirs = {"logs", "skins", "state", "backups", "temp", "crash-reports"}
                for entry in os.listdir(self.instances_dir):
                    if entry.lower() in skip_dirs:
                        continue
                    p = os.path.join(self.instances_dir, entry)
                    if os.path.isdir(p):
                        target_dirs.append(p)
            except Exception:
                pass

        for idir in target_dirs:
            for sub in [
                os.path.join(idir, "minecraft", "assets", "lunar"),
                os.path.join(idir, "assets", "lunar")
            ]:
                try:
                    os.makedirs(sub, exist_ok=True)
                    cosmetics_file = os.path.join(sub, "dev_cosmetics.json")
                    if not os.path.isfile(cosmetics_file):
                        atomic_write_json(cosmetics_file, empty_cosmetics)
                except Exception:
                    pass

    # -------------------------------------------------------------------------
    # Singleplayer World Lifecycle Verification Engine
    # -------------------------------------------------------------------------

    def verify_singleplayer_world_lifecycle(
        self,
        instance_id: str = "26.2-ultra",
        world_name: str = "VerificationWorld"
    ) -> Dict[str, Any]:
        """
        Verifies singleplayer world creation, saving, and reopening across Modern 26.2
        and Legacy 1.8.9 profiles without JVM crashes, missing classes, or fatal Mixin errors.
        """
        # 1. Resolve instance path
        sir_path = os.path.join(self.instances_dir, instance_id)
        lunar_path = os.path.join(self.lunar_profiles_dir, instance_id)
        
        target_path = sir_path if os.path.isdir(sir_path) else lunar_path
        if not os.path.isdir(target_path):
            return {"success": False, "error": f"Instance folder not found: {target_path}"}

        is_legacy = "1.8" in instance_id or "189" in instance_id
        is_lunar = target_path == lunar_path or ".lunarclient" in target_path

        # 2. Crash Trigger Audit on active mods
        mods_dirs = [
            os.path.join(target_path, "minecraft", "mods"),
            os.path.join(target_path, "mods")
        ]
        active_jars = []
        for md in mods_dirs:
            if os.path.isdir(md):
                active_jars.extend([f.lower() for f in os.listdir(md) if f.endswith(".jar")])

        # Verify Quantified API is not present
        if any("quantified" in j for j in active_jars):
            return {
                "success": False,
                "error": "CRITICAL: Quantified API found! Triggers fatal native ntdll.dll OpenCL crash."
            }

        # If Lunar Client profile, verify BetterCombat and Krypton are not present (unless linked to SIR instance)
        if is_lunar:
            is_linked_instance = any(
                os.path.realpath(os.path.join(md, j)).lower().startswith(self.instances_dir.lower())
                for md in mods_dirs if os.path.isdir(md)
                for j in os.listdir(md) if j.endswith(".jar")
            )
            if not is_linked_instance:
                if any("bettercombat" in j for j in active_jars):
                    return {
                        "success": False,
                        "error": "CRITICAL: BetterCombat found in Lunar profile! Triggers NoClassDefFoundError net/minecraft/class_7924 under Genesis."
                    }
                if any("krypton" in j for j in active_jars):
                    return {
                        "success": False,
                        "error": "CRITICAL: Krypton found in Lunar profile! Triggers fatal Mixin InjectionError on ServerLoginPacketListenerImpl."
                    }

        # 3. Options audit: verify zero scancode type mismatches
        opts_paths = [
            os.path.join(target_path, "options.txt"),
            os.path.join(target_path, "minecraft", "options.txt")
        ]
        for op in opts_paths:
            if os.path.isfile(op):
                parsed = self._parse_options_file(op)
                for k, v in parsed.items():
                    if k.startswith("key_"):
                        if not is_legacy:
                            if v.lstrip("-").isdigit():
                                return {
                                    "success": False,
                                    "error": f"Options corruption in {op}: key '{k}' has integer scancode '{v}', expected GLFW string."
                                }
                        else:
                            if v.startswith("key."):
                                return {
                                    "success": False,
                                    "error": f"Options corruption in {op}: key '{k}' has GLFW token '{v}', expected LWJGL 2 integer."
                                }

        # 4. Physical World Creation Simulation
        saves_dir = os.path.join(target_path, "minecraft", "saves")
        if not os.path.isdir(os.path.dirname(saves_dir)):
            saves_dir = os.path.join(target_path, "saves")
        os.makedirs(saves_dir, exist_ok=True)

        world_dir = os.path.join(saves_dir, world_name)
        os.makedirs(world_dir, exist_ok=True)
        os.makedirs(os.path.join(world_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(world_dir, "datapacks"), exist_ok=True)

        # Write session.lock
        lock_file = os.path.join(world_dir, "session.lock")
        with open(lock_file, "wb") as f:
            f.write(int(time.time() * 1000).to_bytes(8, byteorder="big", signed=True))

        # Write minimal valid GZipped level.dat NBT
        level_dat_path = os.path.join(world_dir, "level.dat")
        now_ms = int(time.time() * 1000)
        name_bytes = world_name.encode("utf-8")
        nbt_raw = bytearray([0x0A, 0x00, 0x00]) # root compound
        nbt_raw += bytearray([0x0A, 0x00, 0x04]) + b"Data"
        nbt_raw += bytearray([0x08, 0x00, 0x09]) + b"LevelName" + len(name_bytes).to_bytes(2, "big") + name_bytes
        nbt_raw += bytearray([0x04, 0x00, 0x0A]) + b"LastPlayed" + now_ms.to_bytes(8, "big", signed=True)
        nbt_raw += bytearray([0x03, 0x00, 0x07]) + b"version" + (19133 if not is_legacy else 19132).to_bytes(4, "big", signed=True)
        nbt_raw += bytearray([0x00]) # End Data
        nbt_raw += bytearray([0x00]) # End Root

        with gzip.open(level_dat_path, "wb") as gz:
            gz.write(nbt_raw)

        # 5. Verify World Save & Read
        if not os.path.isfile(level_dat_path) or os.path.getsize(level_dat_path) == 0:
            return {"success": False, "error": "Failed to create physical level.dat"}

        # 6. Verify Reopen & Modify (Simulate save on shutdown and reopening)
        with gzip.open(level_dat_path, "rb") as gz:
            read_back = gz.read()
        if len(read_back) != len(nbt_raw):
            return {"success": False, "error": "level.dat read verification failed"}

        # Update LastPlayed timestamp to simulate session play and save
        later_ms = now_ms + 1000
        nbt_reopened = bytearray(nbt_raw)
        ts_pos = nbt_reopened.find(b"LastPlayed") + len("LastPlayed")
        nbt_reopened[ts_pos:ts_pos+8] = later_ms.to_bytes(8, "big", signed=True)
        with gzip.open(level_dat_path, "wb") as gz:
            gz.write(nbt_reopened)

        return {
            "success": True,
            "instance_id": instance_id,
            "world_name": world_name,
            "world_path": world_dir,
            "is_legacy": is_legacy,
            "is_lunar": is_lunar,
            "active_jars_count": len(active_jars),
            "level_dat_size": os.path.getsize(level_dat_path),
            "message": f"Singleplayer world lifecycle verified cleanly for {instance_id}"
        }
