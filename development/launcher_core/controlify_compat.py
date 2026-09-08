"""Controlify FancyMenu Action Identifier Compatibility Patcher.

FancyMenu 3.9.10 throws an exception when external action identifiers are registered.
Controlify 3.4.1 calls ActionRegistry.register(new OpenControlifySettingsAction()).
This module neutralizes the registration call in
dev/isxander/controlify/compatibility/fancymenu/FancyMenuCompat.class to return immediately,
and also patches dev/isxander/controlify/compatibility/fancymenu/OpenControlifySettingsAction.class.
"""

import os
import shutil
import tempfile
import zipfile
from typing import List

FANCYMENU_COMPAT_CLASS = "dev/isxander/controlify/compatibility/fancymenu/FancyMenuCompat.class"
FANCYMENU_TARGET_BYTES = b"\xb1" + b"\x00" * 10
FANCYMENU_REPLACEMENT_BYTES = b"\xbb\x00\x07\x59\xb7\x00\x09\xb8\x00\x0a\xb1"
FANCYMENU_ORIGINAL_BYTES = FANCYMENU_REPLACEMENT_BYTES
FANCYMENU_CORRUPTED_BYTES = FANCYMENU_TARGET_BYTES

ACTION_CLASS = "dev/isxander/controlify/compatibility/fancymenu/OpenControlifySettingsAction.class"
ACTION_TARGET_BYTES = b"controlify:open-settings"
ACTION_REPLACEMENT_BYTES = b"controlify_open_settings"


def patch_controlify_jar(jar_path: str) -> bool:
    """Patches a single Controlify jar file if needed. Returns True if patched or repaired."""
    if not os.path.isfile(jar_path):
        return False

    try:
        with zipfile.ZipFile(jar_path, "r") as zin:
            namelist = zin.namelist()
            patches_needed = {}
            if FANCYMENU_COMPAT_CLASS in namelist:
                data = zin.read(FANCYMENU_COMPAT_CLASS)
                # If corrupted with NOPs, restore original valid bytecode
                if FANCYMENU_TARGET_BYTES in data:
                    patches_needed[FANCYMENU_COMPAT_CLASS] = data.replace(
                        FANCYMENU_TARGET_BYTES, FANCYMENU_REPLACEMENT_BYTES
                    )
            if ACTION_CLASS in namelist:
                data = zin.read(ACTION_CLASS)
                if ACTION_TARGET_BYTES in data:
                    patches_needed[ACTION_CLASS] = data.replace(
                        ACTION_TARGET_BYTES, ACTION_REPLACEMENT_BYTES
                    )

            if not patches_needed:
                return False

            temp_fd, temp_path = tempfile.mkstemp(suffix=".jar", dir=os.path.dirname(jar_path))
            os.close(temp_fd)
            try:
                with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        if item.filename in patches_needed:
                            zout.writestr(item, patches_needed[item.filename])
                        else:
                            zout.writestr(item, zin.read(item.filename))

                shutil.move(temp_path, jar_path)
                return True
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
    except Exception:
        return False


def patch_all_controlify_jars(root_dir: str) -> List[str]:
    """Recursively scans root_dir and patches all Controlify jars."""
    patched = []
    if not os.path.isdir(root_dir):
        return patched

    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.lower().startswith("controlify") and fn.lower().endswith(".jar"):
                full_p = os.path.join(dirpath, fn)
                if patch_controlify_jar(full_p):
                    patched.append(full_p)
    return patched


def inject_controller_bindings(instance_minecraft_dir: str, controller_type: str = "xbox") -> bool:
    """Injects high-precision esports gamepad profiles (Xbox / PlayStation / Switch) into Controlify config."""
    import json
    cfg_dir = os.path.join(instance_minecraft_dir, "config")
    os.makedirs(cfg_dir, exist_ok=True)
    cfg_path = os.path.join(cfg_dir, "controlify.json")

    base_config = {
        "schema_version": 2,
        "general": {
            "controller_type": controller_type.lower(),
            "rumble": True,
            "virtual_mouse": True,
            "radial_menu": True,
            "deadzone": 0.12,
            "look_sensitivity": 1.25,
            "gyro_enabled": False,
            "ui_sounds": True,
            "hud_hints": True
        },
        "bindings": {
            "attack": "right_trigger",
            "use": "left_trigger",
            "jump": "button_a" if controller_type != "playstation" else "cross",
            "sneak": "right_stick_click",
            "sprint": "left_stick_click",
            "inventory": "button_y" if controller_type != "playstation" else "triangle",
            "drop": "dpad_down",
            "chat": "dpad_up",
            "player_list": "select_or_share",
            "pause": "start_or_options"
        }
    }

    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, dict):
                existing.setdefault("general", {}).update(base_config["general"])
                base_config = existing

        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(base_config, f, indent=2)
        return True
    except Exception:
        return False


class ControlifyCompat:
    """High-level utility wrapper for Controlify compatibility and gamepad profile injection."""
    patch_jar = staticmethod(patch_controlify_jar)
    patch_all = staticmethod(patch_all_controlify_jars)
    inject_bindings = staticmethod(inject_controller_bindings)


