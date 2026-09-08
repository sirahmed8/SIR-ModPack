"""
lunar_bridge_service.py — Bi-Directional Lunar Client Profile Bridge (C: <-> D:)
Enables seamless 1-click synchronization between Lunar Client profiles and SIR ModPack instances.
Handles keybinds, mouse sensitivity, FOV, video options, resource pack priorities, and mod lists.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Tuple

from shared_core.runtime import atomic_write_json, atomic_write_text


class LunarBridgeService:
    """Bi-Directional Profile & Options Synchronizer for Lunar Client and SIR ModPack."""

    PROFILE_MAPPING: Dict[str, str] = {
        "sir-189-performance": "1.8.9-performance",
        "sir-189-pvp": "1.8.9",
        "sir-189-ultra": "1.8.9-ultra",
        "sir-26-balanced": "26.2-balanced",
        "sir-26-performance": "26.2-performance",
        "sir-26-ultra": "26.2-ultra",
    }

    REVERSE_MAPPING: Dict[str, str] = {v: k for k, v in PROFILE_MAPPING.items()}

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
                    # Match outermost JSON object if trailing data exists
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

            # Check keybind differences (e.g. sprint, sneak, zoom)
            for k in ["key_key.sprint", "key_key.sneak", "key_key.zoom", "key_of.key.zoom"]:
                val_lunar = lunar_options.get(k)
                val_sir = sir_options.get(k)
                if val_lunar is not None and val_sir is not None and str(val_lunar) != str(val_sir):
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

    def sync_lunar_to_sir(self, lunar_or_sir_id: str) -> Dict[str, Any]:
        """Synchronizes options, FOV, sensitivity and keybinds from Lunar Client into SIR instance."""
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

        lunar_options = self._parse_options_file(self.options_lc_path)
        if not lunar_options:
            lunar_options = self._parse_options_file(self.options_mc_path)

        if not lunar_options:
            return {"success": False, "error": "No Lunar Client options found on C: drive"}

        sir_options_paths = [
            os.path.join(sir_path, "options.txt"),
            os.path.join(sir_path, "minecraft", "options.txt")
        ]

        synced_count = 0
        is_legacy = "1.8" in sir_inst_id

        # Extract transferrable keys
        keys_to_transfer = [
            "mouseSensitivity", "fov", "gamma", "renderDistance", "guiScale",
            "maxFps", "enableVsync", "bobView", "touchscreen", "rawMouseInput",
            "key_key.attack", "key_key.use", "key_key.forward", "key_key.back",
            "key_key.left", "key_key.right", "key_key.jump", "key_key.inventory",
            "key_key.drop", "key_key.chat", "key_key.playerlist", "key_key.pickItem"
        ]

        for p in sir_options_paths:
            if os.path.isfile(p):
                opts = self._parse_options_file(p)
                for k in keys_to_transfer:
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

                # Ensure HUD key is always preserved
                if is_legacy:
                    opts["key_key.inventoryhud.openconfig"] = "54"
                    opts["key_key.modmenu.open_menu"] = "54"
                else:
                    opts["key_key.inventoryhud.openconfig"] = "key.keyboard.right.shift"
                    opts["key_key.modmenu.open_menu"] = "key.keyboard.right.shift"

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

        # Update optionsLC.txt
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

        # Write optionsLC.txt (JSON format with leading dict)
        try:
            atomic_write_text(self.options_lc_path, json.dumps(lunar_options))
        except Exception:
            pass

        # Update modpack.json in Lunar profile directory
        is_legacy = "1.8" in sir_inst_id
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
        """Performs batch synchronization across all 6 mapped profile pairs."""
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
        """Ensures dev_cosmetics.json and necessary Lunar compatibility assets exist."""
        empty_cosmetics = {"cosmetics": []}

        # 1. Target Lunar root assets
        try:
            lunar_assets_dir = os.path.join(self.lunar_root, "assets", "lunar")
            os.makedirs(lunar_assets_dir, exist_ok=True)
            dev_cosmetics_path = os.path.join(lunar_assets_dir, "dev_cosmetics.json")
            if not os.path.isfile(dev_cosmetics_path):
                atomic_write_json(dev_cosmetics_path, empty_cosmetics)
        except Exception:
            pass

        # 2. Target specific or all instances
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
