"""
controls_service.py — Universal Keybinding Profiles & Dual-Mode options.txt Injection.
Supports Modern GLFW Token Strings (Minecraft 1.21+ / 26.2) and Legacy LWJGL 2 Scancodes (1.8.9).
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from shared_core.runtime import atomic_write_text


class KeybindingMode:
    MODERN_GLFW = "glfw"
    LEGACY_LWJGL2 = "lwjgl2"


# Complete bidirectional GLFW token <-> LWJGL 2 scancode lookup table
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
    # Mouse Buttons (Formula: button_index - 100)
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

# Reverse lookup table: LWJGL2 scancode -> GLFW token string
LWJGL2_TO_GLFW: Dict[int, str] = {}
for _glfw, _scancode in GLFW_TO_LWJGL2.items():
    if _scancode not in LWJGL2_TO_GLFW:
        LWJGL2_TO_GLFW[_scancode] = _glfw

# Add canonical mappings for negative mouse codes
LWJGL2_TO_GLFW[-100] = "key.mouse.left"
LWJGL2_TO_GLFW[-99] = "key.mouse.right"
LWJGL2_TO_GLFW[-98] = "key.mouse.middle"
LWJGL2_TO_GLFW[-97] = "key.mouse.4"
LWJGL2_TO_GLFW[-96] = "key.mouse.5"


class ControlsService:
    """Manages universal keybinding profiles and dual-mode options.txt injection."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.profiles = [
            {
                "id": "standard_vanilla",
                "name": "Standard Vanilla Controls",
                "desc": "Default Minecraft layout: Shift for Sneak, Space for Jump, Left-Control for Sprint.",
                "tag": "🎮 Default",
                "keys": {
                    "key_key.sprint": "key.keyboard.left.control",
                    "key_key.sneak": "key.keyboard.left.shift",
                    "key_key.jump": "key.keyboard.space",
                    "key_key.inventory": "key.keyboard.e",
                    "key_key.drop": "key.keyboard.q",
                    "key_key.zoom": "key.keyboard.c",
                    "key_key.attack": "key.mouse.left",
                    "key_key.use": "key.mouse.right",
                    "key_key.inventoryhud.openconfig": "key.keyboard.right.shift",
                }
            },
            {
                "id": "hypixel_pro_pvp",
                "name": "Hypixel Pro PvP Battle Suite",
                "desc": "Tuned for competitive Bedwars & Duels: Fast Sprint on 'F', Zoom on 'C', Perspective on 'V', Rod swap on Mouse4, RSHIFT Client HUD.",
                "tag": "⚔️ Competitive PvP",
                "keys": {
                    "key_key.sprint": "key.keyboard.f",
                    "key_key.sneak": "key.keyboard.left.shift",
                    "key_key.jump": "key.keyboard.space",
                    "key_key.inventory": "key.keyboard.e",
                    "key_key.perspective": "key.keyboard.v",
                    "key_key.zoom": "key.keyboard.c",
                    "key_key.attack": "key.mouse.left",
                    "key_key.use": "key.mouse.right",
                    "key_key.pickItem": "key.mouse.4",
                    "key_key.inventoryhud.openconfig": "key.keyboard.right.shift",
                }
            },
            {
                "id": "ergonomic_blockhit",
                "name": "Ergonomic 1.7 Block-Hit & Mouse5",
                "desc": "Maximizes CPS and reaction speed: Block-Hit on Mouse5, Sprint toggle on 'R', Inventory on 'Tab', RSHIFT Client HUD.",
                "tag": "🏆 High CPS",
                "keys": {
                    "key_key.sprint": "key.keyboard.r",
                    "key_key.sneak": "key.keyboard.left.shift",
                    "key_key.inventory": "key.keyboard.tab",
                    "key_key.zoom": "key.keyboard.c",
                    "key_key.attack": "key.mouse.left",
                    "key_key.use": "key.mouse.5",
                    "key_key.inventoryhud.openconfig": "key.keyboard.right.shift",
                }
            }
        ]

    def get_control_profiles(self) -> List[Dict[str, Any]]:
        return self.profiles

    def detect_instance_mode(self, instance_path: str, instance_id: str = "") -> str:
        """Detects whether target instance requires MODERN_GLFW (1.21+/26.2) or LEGACY_LWJGL2 (1.8.9)."""
        # 1. Check instance id hint
        norm_id = str(instance_id).lower()
        if "1.8" in norm_id or "1.7" in norm_id or "legacy" in norm_id or "forge" in norm_id:
            return KeybindingMode.LEGACY_LWJGL2
        if "26" in norm_id or "1.21" in norm_id or "modern" in norm_id or "fabric" in norm_id:
            return KeybindingMode.MODERN_GLFW

        # 2. Check mmc-pack.json
        mmc_pack = os.path.join(instance_path, "mmc-pack.json")
        if os.path.isfile(mmc_pack):
            try:
                with open(mmc_pack, "r", encoding="utf-8") as f:
                    pack = json.load(f)
                    for comp in pack.get("components", []):
                        ver = comp.get("version", "")
                        if "1.8" in ver or "1.7" in ver:
                            return KeybindingMode.LEGACY_LWJGL2
                        if "26" in ver or "1.21" in ver:
                            return KeybindingMode.MODERN_GLFW
            except Exception:
                pass

        # 3. Check instance.cfg
        inst_cfg = os.path.join(instance_path, "instance.cfg")
        if os.path.isfile(inst_cfg):
            try:
                with open(inst_cfg, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "IntendedVersion=1.8" in content or "IntendedVersion=1.7" in content:
                        return KeybindingMode.LEGACY_LWJGL2
                    if "IntendedVersion=26" in content or "IntendedVersion=1.21" in content:
                        return KeybindingMode.MODERN_GLFW
            except Exception:
                pass

        # 4. Check options.txt header
        options_path = os.path.join(instance_path, "minecraft", "options.txt")
        if not os.path.isfile(options_path):
            options_path = os.path.join(instance_path, "options.txt")
        if os.path.isfile(options_path):
            try:
                with open(options_path, "r", encoding="utf-8") as f:
                    first_line = f.readline()
                    m = re.match(r"^version:(\d+)", first_line.strip())
                    if m:
                        ver_num = int(m.group(1))
                        # 1444 was Minecraft 1.13 flattening
                        return KeybindingMode.MODERN_GLFW if ver_num >= 1444 else KeybindingMode.LEGACY_LWJGL2
                    else:
                        # Legacy 1.8 options.txt often starts with non-version option
                        return KeybindingMode.LEGACY_LWJGL2
            except Exception:
                pass

        return KeybindingMode.MODERN_GLFW

    def translate_key_value(self, key_val: str | int, target_mode: str) -> str:
        """Converts key value between GLFW token string and LWJGL2 numeric scancode."""
        if target_mode == KeybindingMode.LEGACY_LWJGL2:
            if isinstance(key_val, int):
                return str(key_val)
            val_str = str(key_val).strip()
            if val_str.lstrip("-").isdigit():
                return val_str
            # Lookup in GLFW -> LWJGL2 table
            scancode = GLFW_TO_LWJGL2.get(val_str.lower(), 0)
            return str(scancode)
        else:
            # MODERN_GLFW target
            if isinstance(key_val, int) or (isinstance(key_val, str) and key_val.lstrip("-").isdigit()):
                int_code = int(key_val)
                return LWJGL2_TO_GLFW.get(int_code, "key.keyboard.unknown")
            return str(key_val).strip()

    def translate_keys_map(self, keys_map: Dict[str, Any], target_mode: str) -> Dict[str, str]:
        """Translates a dictionary of keybindings for the target mode, handling option key aliases."""
        result: Dict[str, str] = {}
        for opt_key, opt_val in keys_map.items():
            translated_val = self.translate_key_value(opt_val, target_mode)

            if target_mode == KeybindingMode.LEGACY_LWJGL2:
                # Key name aliases for Legacy 1.8.9
                if opt_key == "key_key.perspective":
                    result["key_key.togglePerspective"] = translated_val
                elif opt_key == "key_key.zoom":
                    result["key_of.key.zoom"] = translated_val
                    result["key_key.zoom"] = translated_val
                elif opt_key in ("key_key.inventoryhud.config", "key_key.inventoryhud.openconfig"):
                    result["key_key.inventoryhud.openconfig"] = "54"
                    result["key_key.modmenu.open_menu"] = "54"
                else:
                    result[opt_key] = translated_val
            else:
                # Modern 26.2 / 1.21+ aliases
                if opt_key == "key_key.togglePerspective":
                    result["key_key.perspective"] = translated_val
                elif opt_key == "key_of.key.zoom":
                    result["key_key.zoom"] = translated_val
                elif opt_key in ("key_key.inventoryhud.config", "key_key.inventoryhud.openconfig"):
                    result["key_key.inventoryhud.openconfig"] = "key.keyboard.right.shift"
                else:
                    result[opt_key] = translated_val

        return result

    def apply_control_profile(
        self,
        profile_id: str,
        instance_id: str = "26.2",
        instance_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Applies keybinding profile to instance options.txt with dual-mode conversion and atomic persistence."""
        profile = next((p for p in self.profiles if p["id"] == profile_id), None)
        if not profile:
            return {"success": False, "error": f"Profile '{profile_id}' not found"}

        # Resolve candidate options.txt locations
        search_dirs = []
        if instance_dir:
            search_dirs.append(instance_dir)
            search_dirs.append(os.path.join(instance_dir, "minecraft"))
        elif instance_id:
            inst_primary = os.path.join(self.root_dir, "instances", instance_id)
            search_dirs.extend([
                inst_primary,
                os.path.join(inst_primary, "minecraft"),
            ])

        target_options_files = []
        for d in search_dirs:
            p = os.path.join(d, "options.txt") if not d.endswith("options.txt") else d
            if os.path.isfile(p) and p not in target_options_files:
                target_options_files.append(p)

        applied_count = 0
        detected_modes = []

        for opt_path in target_options_files:
            try:
                inst_folder = os.path.dirname(os.path.dirname(opt_path)) if "minecraft" in opt_path else os.path.dirname(opt_path)
                mode = self.detect_instance_mode(inst_folder, instance_id)
                detected_modes.append(mode)

                keys_map = self.translate_keys_map(profile["keys"], mode)

                lines: List[str] = []
                if os.path.exists(opt_path):
                    with open(opt_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                new_lines = []
                updated_keys = set()

                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        new_lines.append(line)
                        continue

                    parts = stripped.split(":", 1)
                    if len(parts) == 2 and parts[0] in keys_map:
                        new_lines.append(f"{parts[0]}:{keys_map[parts[0]]}\n")
                        updated_keys.add(parts[0])
                    else:
                        new_lines.append(line)

                for k, v in keys_map.items():
                    if k not in updated_keys:
                        new_lines.append(f"{k}:{v}\n")

                atomic_write_text(opt_path, "".join(new_lines))
                applied_count += 1
            except Exception as e:
                print(f"[ControlsService] Error injecting keys to {opt_path}: {e}")

        primary_mode = detected_modes[0] if detected_modes else KeybindingMode.MODERN_GLFW

        return {
            "success": True,
            "profile": profile["name"],
            "mode": primary_mode,
            "applied_instances": applied_count,
            "message": f"Successfully applied '{profile['name']}' in {primary_mode.upper()} mode to Minecraft controls configuration!",
        }

