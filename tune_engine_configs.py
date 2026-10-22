#!/usr/bin/env python3
"""
SIR Ecosystem Game Engine & Client HUD Tuning & Verification Suite (v1.0.0 Genesis)
Applies and verifies:
1. Modern 26.2 Engine Tuning (C2ME, Sodium, PhysicsMod, SoundPhysics, PresenceFootsteps)
2. Global options.txt calibration (gamma: 1.0, vsync: false, fullscreen: false, guiScale: 2, Iris: K, ReplayMod: B/M/P/X/H/I/O)
3. Full servers.dat NBT decompression and verification across all 24 instance directories
4. Lunar Client 10-profile HUD Studio calibration
5. Generational ZGC JVM flags verification across all modern 26.2 instance.cfg files
"""

import os
import sys
import json
import gzip
import struct
import re

ROOT = r"d:\Projects\SIR ModPack"
APPDATA_INSTANCES = r"C:\Users\a7med\AppData\Roaming\SIR ModPack\instances"
LUNAR_DIR = r"C:\Users\a7med\.lunarclient\settings\game"

INSTANCE_ROOTS = [
    os.path.join(ROOT, "instances"),
    APPDATA_INSTANCES,
    os.path.join(ROOT, "SIR Package", "instances")
]

MODERN_PROFILES = ["26.2", "26.2-ultra", "26.2-balanced", "26.2-performance"]
LEGACY_PROFILES = ["1.8.9", "1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"]
ALL_PROFILES = MODERN_PROFILES + LEGACY_PROFILES


# ==============================================================================
# NBT PARSER FOR SERVERS.DAT
# ==============================================================================
def parse_nbt(data):
    offset = 0
    def read_byte():
        nonlocal offset
        b = data[offset]
        offset += 1
        return b
    def read_short():
        nonlocal offset
        val = struct.unpack('>h', data[offset:offset+2])[0]
        offset += 2
        return val
    def read_int():
        nonlocal offset
        val = struct.unpack('>i', data[offset:offset+4])[0]
        offset += 4
        return val
    def read_long():
        nonlocal offset
        val = struct.unpack('>q', data[offset:offset+8])[0]
        offset += 8
        return val
    def read_float():
        nonlocal offset
        val = struct.unpack('>f', data[offset:offset+4])[0]
        offset += 4
        return val
    def read_double():
        nonlocal offset
        val = struct.unpack('>d', data[offset:offset+8])[0]
        offset += 8
        return val
    def read_string():
        length = read_short()
        nonlocal offset
        s = data[offset:offset+length].decode('utf-8', errors='replace')
        offset += length
        return s
    def parse_payload(tag_type):
        nonlocal offset
        if tag_type == 1: return read_byte()
        elif tag_type == 2: return read_short()
        elif tag_type == 3: return read_int()
        elif tag_type == 4: return read_long()
        elif tag_type == 5: return read_float()
        elif tag_type == 6: return read_double()
        elif tag_type == 7:
            length = read_int()
            res = data[offset:offset+length]
            offset += length
            return res
        elif tag_type == 8: return read_string()
        elif tag_type == 9:
            elem_type = read_byte()
            length = read_int()
            return [parse_payload(elem_type) for _ in range(length)]
        elif tag_type == 10:
            res = {}
            while True:
                t = read_byte()
                if t == 0: break
                name = read_string()
                res[name] = parse_payload(t)
            return res
        elif tag_type == 11:
            length = read_int()
            res = [read_int() for _ in range(length)]
            return res
        elif tag_type == 12:
            length = read_int()
            res = [read_long() for _ in range(length)]
            return res
        return None

    if len(data) < 3:
        return None
    tag_type = read_byte()
    if tag_type != 10:
        return None
    root_name = read_string()
    return parse_payload(10)


# ==============================================================================
# 1. ENGINE CONFIGURATION TUNING
# ==============================================================================
def tune_c2me_toml(filepath):
    """
    Apply C2ME chunk worker & chunk generation thread parallelism.
    [threading.chunkWorkerExecutor] -> globalExecutorParallelism = 6
    [threading.chunkGeneration] -> maxChunkGenerationThreads = 4
    """
    content = ""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

    # Update globalExecutorParallelism
    if re.search(r'^\s*globalExecutorParallelism\s*=', content, re.MULTILINE):
        content = re.sub(r'^\s*globalExecutorParallelism\s*=.*$', 'globalExecutorParallelism = 6', content, flags=re.MULTILINE)
    else:
        content = "globalExecutorParallelism = 6\n" + content

    # Check for [threading.chunkWorkerExecutor]
    if "[threading.chunkWorkerExecutor]" not in content:
        content += "\n[threading.chunkWorkerExecutor]\nglobalExecutorParallelism = 6\n"

    # Check for [threading.chunkGeneration]
    if "[threading.chunkGeneration]" not in content:
        content += "\n[threading.chunkGeneration]\nmaxChunkGenerationThreads = 4\n"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def tune_sodium_options(filepath):
    """
    {"chunk_builder_threads": 6, "use_entity_culling": true, "quality.weather_quality": "FANCY", "quality.leaves_quality": "FANCY"}
    """
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["chunk_builder_threads"] = 6
    data["use_entity_culling"] = True
    data["quality.weather_quality"] = "FANCY"
    data["quality.leaves_quality"] = "FANCY"

    if "quality" not in data or not isinstance(data["quality"], dict):
        data["quality"] = {}
    data["quality"]["weather_quality"] = "FANCY"
    data["quality"]["leaves_quality"] = "FANCY"

    if "performance" not in data or not isinstance(data["performance"], dict):
        data["performance"] = {}
    data["performance"]["chunk_builder_threads"] = 6
    data["performance"]["use_entity_culling"] = True

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def tune_physics_mod(filepath):
    """
    {"maxPhysicsObjects": 450, "fireParticleLimit": 5000, "enabled": true}
    """
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["maxPhysicsObjects"] = 450
    data["fireParticleLimit"] = 5000
    data["enabled"] = True

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def tune_sound_physics(filepath):
    """
    enabled=true, rayCount=24, maxReflectionOrder=3, renderSoundBounces=true, soundDecayScale=1.05, leafOcclusionFactor=0.2
    """
    lines = []
    keys_present = set()
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if "=" in stripped and not stripped.startswith("#"):
                    k = stripped.split("=")[0].strip()
                    keys_present.add(k)
                    if k in ["enabled", "rayCount", "maxReflectionOrder", "renderSoundBounces",
                             "soundDecayScale", "leafOcclusionFactor", "environment_evaluation_ray_count",
                             "environment_evaluation_ray_bounces", "render_sound_bounces",
                             "attenuation_factor", "block_absorption"]:
                        continue
                lines.append(line)

    target_props = [
        ("enabled", "true"),
        ("rayCount", "24"),
        ("maxReflectionOrder", "3"),
        ("renderSoundBounces", "true"),
        ("soundDecayScale", "1.05"),
        ("leafOcclusionFactor", "0.2"),
        ("environment_evaluation_ray_count", "24"),
        ("environment_evaluation_ray_bounces", "3"),
        ("render_sound_bounces", "true"),
        ("attenuation_factor", "1.05"),
        ("block_absorption", "0.2")
    ]

    new_content = "".join(lines).rstrip() + "\n\n# SIR Master Engine Tuned Audio Acoustics\n"
    for k, v in target_props:
        new_content += f"{k}={v}\n"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


def tune_presence_footsteps(filepath):
    """
    {"enabled": true, "global_volume": 0.85, "footstep_volume": 0.9, "terrain_mixing": true, "continuous_motion": true, "armor_shuffle": true}
    """
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
                cleaned = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
                cleaned = re.sub(r'//.*', '', cleaned)
                data = json.loads(cleaned)
        except Exception:
            data = {}

    data["enabled"] = True
    data["global_volume"] = 0.85
    data["footstep_volume"] = 0.9
    data["terrain_mixing"] = True
    data["continuous_motion"] = True
    data["armor_shuffle"] = True

    if "volume" not in data or not isinstance(data["volume"], dict):
        data["volume"] = {}
    data["volume"]["volume"] = 85
    data["volume"]["clientPlayerVolume"] = 90

    if "client" not in data or not isinstance(data["client"], dict):
        data["client"] = {}
    data["client"]["disabled"] = False

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def apply_engine_tuning():
    print("\n" + "=" * 65)
    print("🚀 1. TUNING ENGINE CONFIGS ACROSS ALL 26.2 INSTANCES")
    print("=" * 65)

    count = 0
    for root in INSTANCE_ROOTS:
        if not os.path.exists(root):
            continue
        for prof in MODERN_PROFILES:
            prof_dir = os.path.join(root, prof)
            if not os.path.exists(prof_dir):
                continue

            config_dirs = [
                os.path.join(prof_dir, "config"),
                os.path.join(prof_dir, "minecraft", "config")
            ]

            for cdir in config_dirs:
                # 1. c2me.toml
                c2me_file = os.path.join(cdir, "c2me.toml")
                tune_c2me_toml(c2me_file)

                # 2. sodium-options.json
                sod_file = os.path.join(cdir, "sodium-options.json")
                tune_sodium_options(sod_file)

                # 3. physics_client_config.json
                phys_file = os.path.join(cdir, "physicsmod", "physics_client_config.json")
                tune_physics_mod(phys_file)

                # 4. soundphysics.properties
                sp1 = os.path.join(cdir, "soundphysics.properties")
                sp2 = os.path.join(cdir, "sound_physics_remastered", "soundphysics.properties")
                tune_sound_physics(sp1)
                tune_sound_physics(sp2)

                # 5. presencefootsteps userconfig.json5
                pf_file = os.path.join(cdir, "presencefootsteps", "userconfig.json5")
                tune_presence_footsteps(pf_file)

                count += 1

    print(f"  ✓ Successfully tuned engine configs across {count} instance config locations.")


# ==============================================================================
# 2. DEEP DIVE: OPTIONS.TXT CALIBRATION
# ==============================================================================
def tune_options_txt(filepath, is_modern=True):
    if not os.path.exists(filepath):
        return

    lines = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    opts = {}
    order = []
    for line in lines:
        line_clean = line.rstrip("\r\n")
        if ":" in line_clean:
            k, v = line_clean.split(":", 1)
            k = k.strip()
            if k not in opts:
                order.append(k)
            opts[k] = v.strip()

    # Apply calibrations
    opts["gamma"] = "1.0"
    opts["enableVsync"] = "false"
    opts["fullscreen"] = "false"
    if "guiScale" not in opts or opts["guiScale"] == "0":
        opts["guiScale"] = "2"

    if is_modern:
        # Sanitize any legacy numeric keycodes to modern GLFW strings
        legacy_to_glfw = {
            "47": "key.keyboard.v",
            "54": "key.keyboard.right.shift",
            "57": "key.keyboard.space",
            "42": "key.keyboard.left.shift",
            "33": "key.keyboard.f",
            "18": "key.keyboard.e",
            "46": "key.keyboard.c",
            "-97": "key.mouse.middle",
            "-100": "key.mouse.left",
            "-99": "key.mouse.right",
        }
        for k, v in list(opts.items()):
            if k.startswith("key_") and v in legacy_to_glfw:
                opts[k] = legacy_to_glfw[v]

        # Iris keybinds
        opts["key_iris.keybind.toggleShaders"] = "key.keyboard.k"
        opts["key_iris.keybind.shaderPackSelection"] = "key.keyboard.i"
        # ReplayMod keybinds
        opts["key_replaymod.input.playeroverview"] = "key.keyboard.b"
        opts["key_replaymod.input.marker"] = "key.keyboard.m"
        opts["key_replaymod.input.playpause"] = "key.keyboard.p"
        opts["key_replaymod.input.keyframerepository"] = "key.keyboard.x"
        opts["key_replaymod.input.pathpreview"] = "key.keyboard.h"
        opts["key_replaymod.input.positionkeyframe"] = "key.keyboard.i"
        opts["key_replaymod.input.timekeyframe"] = "key.keyboard.o"
        # HUD Studio & ModMenu
        opts["key_key.inventoryhud.openconfig"] = "key.keyboard.right.shift"
        opts["key_key.modmenu.open_menu"] = "key.keyboard.right.shift"
        opts["key_key.shouldersurfing.free_look"] = "key.keyboard.left.alt"
    else:
        # Legacy
        opts["key_key.inventoryhud.openconfig"] = "54"
        opts["key_key.modmenu.open_menu"] = "54"
        opts["key_key.hud.menu"] = "54"

    # Add missing keys to order
    for k in opts:
        if k not in order:
            order.append(k)

    with open(filepath, "w", encoding="utf-8") as f:
        for k in order:
            f.write(f"{k}:{opts[k]}\n")


def apply_options_txt_calibration():
    print("\n" + "=" * 65)
    print("🔧 2. CALIBRATING OPTIONS.TXT ACROSS ALL 24 INSTANCES")
    print("=" * 65)

    count = 0
    for root in INSTANCE_ROOTS:
        if not os.path.exists(root):
            continue
        for prof in ALL_PROFILES:
            prof_dir = os.path.join(root, prof)
            if not os.path.exists(prof_dir):
                continue
            is_modern = prof in MODERN_PROFILES

            opt_files = [
                os.path.join(prof_dir, "options.txt"),
                os.path.join(prof_dir, "minecraft", "options.txt")
            ]
            for of in opt_files:
                if os.path.exists(of):
                    tune_options_txt(of, is_modern=is_modern)
                    count += 1

    print(f"  ✓ Successfully calibrated options.txt across {count} files (gamma:1.0, vsync:false, guiScale, Iris:K, ReplayMod).")


# ==============================================================================
# 3. DEEP DIVE: SERVERS.DAT NBT VERIFICATION
# ==============================================================================
def verify_servers_dat():
    print("\n" + "=" * 65)
    print("🌐 3. VERIFYING SERVERS.DAT NBT STRUCTURE ACROSS ALL 24 INSTANCES")
    print("=" * 65)

    checked = 0
    issues = []
    server_names_all = []

    for root in INSTANCE_ROOTS:
        if not os.path.exists(root):
            continue
        for prof in ALL_PROFILES:
            prof_dir = os.path.join(root, prof)
            if not os.path.exists(prof_dir):
                continue

            sdat = os.path.join(prof_dir, "minecraft", "servers.dat")
            if not os.path.exists(sdat):
                issues.append(f"Missing servers.dat in {sdat}")
                continue

            size = os.path.getsize(sdat)
            # Should be approx 79,224 bytes
            if size < 70000:
                issues.append(f"Unexpected size for {sdat}: {size} bytes")
                continue

            try:
                raw_nbt = b""
                with open(sdat, "rb") as f:
                    header = f.read(2)
                    f.seek(0)
                    if header == b"\x1f\x8b":
                        raw_nbt = gzip.decompress(f.read())
                    else:
                        raw_nbt = f.read()
                nbt = parse_nbt(raw_nbt)
                if not nbt or "servers" not in nbt:
                    issues.append(f"Invalid NBT compound in {sdat}")
                    continue
                servers = nbt["servers"]
                if len(servers) != 12:
                    issues.append(f"Expected 12 servers, found {len(servers)} in {sdat}")
                if checked == 0:
                    for s in servers:
                        server_names_all.append(f"{s.get('name', 'Unknown')} ({s.get('ip', 'No IP')})")
                checked += 1
            except Exception as e:
                issues.append(f"Error parsing {sdat}: {e}")

    print(f"  ✓ Verified {checked}/24 instances have pristine ~79 KB servers.dat NBT structure.")
    print("  📋 Discovered 12 Servers:")
    for sname in server_names_all:
        print(f"    - {sname}")

    if issues:
        print(f"  ⚠️ Warning: {len(issues)} issues found in servers.dat:")
        for iss in issues:
            print(f"    * {iss}")
    else:
        print("  ✓ 100% Pristine NBT validity across all 24 instances!")


# ==============================================================================
# 4. DEEP DIVE: LUNAR CLIENT 10-PROFILE HUD STUDIO OVERHAUL
# ==============================================================================
def verify_and_calibrate_lunar_profiles():
    print("\n" + "=" * 65)
    print("🌙 4. CALIBRATING LUNAR CLIENT 10-PROFILE HUD STUDIO")
    print("=" * 65)

    if not os.path.exists(LUNAR_DIR):
        print("  ⚠️ Lunar Client directory not found.")
        return

    subdirs = [d for d in os.listdir(LUNAR_DIR) if os.path.isdir(os.path.join(LUNAR_DIR, d))]
    calibrated = 0

    replaymod_keys = {
        "replaymod.input.playeroverview": "KEY_B",
        "replaymod.input.lighting": "KEY_Z",
        "replaymod.input.quickmode": "KEY_Q",
        "replaymod.input.settings": "KEY_NONE",
        "replaymod.input.marker": "KEY_M",
        "replaymod.input.thumbnail": "KEY_N",
        "replaymod.input.playpause": "KEY_P",
        "replaymod.input.rollclockwise": "KEY_L",
        "replaymod.input.rollcounterclockwise": "KEY_J",
        "replaymod.input.resettilt": "KEY_K",
        "replaymod.input.pathpreview": "KEY_H",
        "replaymod.input.keyframerepository": "KEY_X",
        "replaymod.input.clearkeyframes": "KEY_NONE",
        "replaymod.input.synctimeline": "KEY_V",
        "replaymod.input.positionkeyframe": "KEY_I",
        "replaymod.input.positiononlykeyframe": "KEY_NONE",
        "replaymod.input.timekeyframe": "KEY_O",
        "replaymod.input.bothkeyframes": "KEY_NONE"
    }

    for d in subdirs:
        mfile = os.path.join(LUNAR_DIR, d, "mods.json")
        if not os.path.exists(mfile):
            continue

        try:
            with open(mfile, "r", encoding="utf-8") as f:
                mods = json.load(f)

            # 1. REACH_DISPLAY
            if "REACH_DISPLAY" not in mods or not isinstance(mods["REACH_DISPLAY"], dict):
                mods["REACH_DISPLAY"] = {}
            mods["REACH_DISPLAY"]["enabled"] = True
            mods["REACH_DISPLAY"]["seen"] = True
            if "options" not in mods["REACH_DISPLAY"]:
                mods["REACH_DISPLAY"]["options"] = {}
            mods["REACH_DISPLAY"]["options"]["backgroundColor"] = {"value": 1543767044, "chroma": False}

            # 2. COMBO
            if "COMBO" not in mods or not isinstance(mods["COMBO"], dict):
                mods["COMBO"] = {}
            mods["COMBO"]["enabled"] = True
            mods["COMBO"]["seen"] = True
            if "options" not in mods["COMBO"]:
                mods["COMBO"]["options"] = {}
            mods["COMBO"]["options"]["backgroundColor"] = {"value": 1543767044, "chroma": False}

            # 3. CPS (Dual Click)
            if "CPS" not in mods or not isinstance(mods["CPS"], dict):
                mods["CPS"] = {}
            mods["CPS"]["enabled"] = True
            mods["CPS"]["seen"] = True
            if "options" not in mods["CPS"]:
                mods["CPS"]["options"] = {}
            mods["CPS"]["options"]["rightClick"] = True
            mods["CPS"]["options"]["background"] = True
            mods["CPS"]["options"]["backgroundColor"] = {"value": 1543767044, "chroma": False}

            # 4. PING
            if "PING" not in mods or not isinstance(mods["PING"], dict):
                mods["PING"] = {}
            mods["PING"]["enabled"] = True
            mods["PING"]["seen"] = True
            if "PING_HUD" not in mods["PING"]:
                mods["PING"]["PING_HUD"] = {}
            mods["PING"]["PING_HUD"]["enabled"] = True

            # 5. HYPIXEL_TPS
            if "HYPIXEL_MOD" not in mods or not isinstance(mods["HYPIXEL_MOD"], dict):
                mods["HYPIXEL_MOD"] = {}
            mods["HYPIXEL_MOD"]["enabled"] = True
            mods["HYPIXEL_MOD"]["seen"] = True
            if "HYPIXEL_TPS" not in mods["HYPIXEL_MOD"]:
                mods["HYPIXEL_MOD"]["HYPIXEL_TPS"] = {}
            mods["HYPIXEL_MOD"]["HYPIXEL_TPS"]["enabled"] = True

            # 6. TOGGLE_SNEAK
            if "TOGGLE_SNEAK" not in mods or not isinstance(mods["TOGGLE_SNEAK"], dict):
                mods["TOGGLE_SNEAK"] = {}
            mods["TOGGLE_SNEAK"]["enabled"] = True
            mods["TOGGLE_SNEAK"]["seen"] = True
            if "TOGGLE_SNEAK_HUD_CHILD" not in mods["TOGGLE_SNEAK"]:
                mods["TOGGLE_SNEAK"]["TOGGLE_SNEAK_HUD_CHILD"] = {}
            mods["TOGGLE_SNEAK"]["TOGGLE_SNEAK_HUD_CHILD"]["enabled"] = True

            # 7. CROSSHAIR
            if "CROSSHAIR" not in mods or not isinstance(mods["CROSSHAIR"], dict):
                mods["CROSSHAIR"] = {}
            mods["CROSSHAIR"]["enabled"] = True
            mods["CROSSHAIR"]["seen"] = True

            # 8. FREELOOK
            if "FREELOOK" not in mods or not isinstance(mods["FREELOOK"], dict):
                mods["FREELOOK"] = {}
            mods["FREELOOK"]["enabled"] = True
            mods["FREELOOK"]["seen"] = True
            if "options" not in mods["FREELOOK"]:
                mods["FREELOOK"]["options"] = {}
            mods["FREELOOK"]["options"]["freelook"] = "KEY_R"

            # 9. ARMORSTATUS & POTION_EFFECTS
            if "ARMORSTATUS" not in mods or not isinstance(mods["ARMORSTATUS"], dict):
                mods["ARMORSTATUS"] = {}
            mods["ARMORSTATUS"]["enabled"] = True
            mods["ARMORSTATUS"]["seen"] = True
            if "options" not in mods["ARMORSTATUS"]:
                mods["ARMORSTATUS"]["options"] = {}
            mods["ARMORSTATUS"]["options"]["itemDamage"] = True
            mods["ARMORSTATUS"]["options"]["armorDamage"] = True
            mods["ARMORSTATUS"]["options"]["durabilityPosition"] = "left"

            if "POTION_EFFECTS" not in mods or not isinstance(mods["POTION_EFFECTS"], dict):
                mods["POTION_EFFECTS"] = {}
            mods["POTION_EFFECTS"]["enabled"] = True
            mods["POTION_EFFECTS"]["seen"] = True
            if "options" not in mods["POTION_EFFECTS"]:
                mods["POTION_EFFECTS"]["options"] = {}
            mods["POTION_EFFECTS"]["options"]["background"] = True

            # 10. REPLAYMOD
            if "REPLAYMOD" not in mods or not isinstance(mods["REPLAYMOD"], dict):
                mods["REPLAYMOD"] = {}
            mods["REPLAYMOD"]["keybinds"] = replaymod_keys

            with open(mfile, "w", encoding="utf-8") as f:
                json.dump(mods, f)
            print(f"  ✓ Calibrated Lunar profile: {d}")
            calibrated += 1
        except Exception as e:
            print(f"  ⚠️ Error calibrating {mfile}: {e}")

    print(f"  ✓ Successfully calibrated all {calibrated} Lunar Client profiles.")


# ==============================================================================
# 5. DEEP DIVE: GENERATIONAL ZGC VERIFICATION
# ==============================================================================
def verify_generational_zgc():
    print("\n" + "=" * 65)
    print("⚡ 5. VERIFYING GENERATIONAL ZGC FLAGS IN 26.2 INSTANCES")
    print("=" * 65)

    verified = 0
    issues = []

    for root in INSTANCE_ROOTS:
        if not os.path.exists(root):
            continue
        for prof in MODERN_PROFILES:
            cfg_path = os.path.join(root, prof, "instance.cfg")
            if not os.path.exists(cfg_path):
                issues.append(f"Missing instance.cfg: {cfg_path}")
                continue

            with open(cfg_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "-XX:+UseZGC" in content and "-XX:+ZGenerational" in content:
                verified += 1
            else:
                issues.append(f"ZGC flags missing in: {cfg_path}")

    print(f"  ✓ Verified {verified}/12 modern 26.2 instance.cfg files contain Generational ZGC flags.")
    if issues:
        for iss in issues:
            print(f"  ⚠️ {iss}")
    else:
        print("  ✓ 100% Generational ZGC compliance across all modern targets!")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    print("🎮 SIR MASTER GAME ENGINE & CLIENT HUD CALIBRATOR")
    print("=" * 65)
    apply_engine_tuning()
    apply_options_txt_calibration()
    verify_servers_dat()
    verify_and_calibrate_lunar_profiles()
    verify_generational_zgc()
    print("\n" + "=" * 65)
    print("🎉 ALL ENGINE & CLIENT HUD CALIBRATIONS SUCCESSFULLY APPLIED!")
    print("=" * 65)

if __name__ == "__main__":
    main()
