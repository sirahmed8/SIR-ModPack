#!/usr/bin/env python3
"""
Aetheris Ecosystem — M4 Performance & Video Settings Engine
Automates standardization and synchronization of:
1. options.txt across all Modern and Legacy profiles (VSync, maxFps, gamma, particles, active resourcePacks, keybind K).
2. sodium-options.json across modern profiles (chunk builder threads 20/6/4, entity culling, rendering flags).
3. iris.properties across modern profiles (allowUnknownShaders=true, active shaderpacks).
4. JVM launch arguments (8GB memory, optimized G1GC flags) in Prism Launcher instance.cfg, Lunar profiles, and profiles.db.
"""

import os
import json
import sqlite3
import re

# ==============================================================================
# JVM FLAGS TEMPLATE
# ==============================================================================

G1GC_FLAGS_STR = (
    "-XX:+UseG1GC "
    "-XX:+ParallelRefProcEnabled "
    "-XX:MaxGCPauseMillis=200 "
    "-XX:+UnlockExperimentalVMOptions "
    "-XX:+DisableExplicitGC "
    "-XX:+AlwaysPreTouch "
    "-XX:G1NewSizePercent=30 "
    "-XX:G1MaxNewSizePercent=40 "
    "-XX:G1HeapRegionSize=8M "
    "-XX:G1ReservePercent=20 "
    "-XX:G1HeapWastePercent=5 "
    "-XX:G1MixedGCCountTarget=4 "
    "-XX:InitiatingHeapOccupancyPercent=15 "
    "-XX:G1MixedGCLiveThresholdPercent=90 "
    "-XX:G1RSetUpdatingPauseTimePercent=5 "
    "-XX:SurvivorRatio=32 "
    "-XX:+PerfDisableSharedMem "
    "-XX:MaxTenuringThreshold=1 "
    "-XX:+OptimizeStringConcat "
    "-XX:+UseStringDeduplication "
    "-Djava.net.preferIPv4Stack=true "
    "-Dfile.encoding=UTF-8"
)

JVM_OPTIONS_TXT_CONTENT = """# Aetheris — JVM Optimization Arguments
# Hardware: i7-13650HX | 24GB RAM | 8192MB allocated to MC

# ── Garbage Collector ─────────────────────────────────────────────
# G1GC is best for Minecraft's allocation patterns
-XX:+UseG1GC
-XX:+ParallelRefProcEnabled
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:+DisableExplicitGC
-XX:+AlwaysPreTouch
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
-XX:G1HeapRegionSize=8M
-XX:G1ReservePercent=20
-XX:G1HeapWastePercent=5
-XX:G1MixedGCCountTarget=4
-XX:InitiatingHeapOccupancyPercent=15
-XX:G1MixedGCLiveThresholdPercent=90
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:SurvivorRatio=32
-XX:+PerfDisableSharedMem
-XX:MaxTenuringThreshold=1

# ── JIT Compiler ─────────────────────────────────────────────────
-XX:+OptimizeStringConcat
-XX:+UseStringDeduplication

# ── Memory ───────────────────────────────────────────────────────
-Xms4G
-Xmx8G

# ── System ───────────────────────────────────────────────────────
-Djava.net.preferIPv4Stack=true
-Dfile.encoding=UTF-8
"""

# ==============================================================================
# SODIUM OPTIONS PRESETS
# ==============================================================================

SODIUM_VISUAL = {
    "quality": {
        "hidden_fluid_culling": False,
        "improved_fluid_shaping": True,
        "use_closest_point_entity_sort": True,
        "pixel_filtering_mode": "NEAREST"
    },
    "performance": {
        "chunk_builder_threads": 20,
        "chunk_build_defer_mode": "ALWAYS",
        "animate_only_visible_textures": False,
        "use_entity_culling": False,
        "use_fog_occlusion": True,
        "use_block_face_culling": False,
        "use_no_error_g_l_context": True,
        "quad_splitting_mode": "SAFE"
    },
    "advanced": {
        "enable_memory_tracing": False
    },
    "debug": {
        "terrain_sorting_enabled": True
    },
    "notifications": {
        "has_cleared_donation_button": True,
        "has_seen_donation_prompt": True,
        "has_edited_fullscreen_option": True
    }
}

SODIUM_BALANCED = {
    "quality": {
        "hidden_fluid_culling": False,
        "improved_fluid_shaping": True,
        "use_closest_point_entity_sort": True,
        "pixel_filtering_mode": "MIPMAP_LINEAR"
    },
    "performance": {
        "chunk_builder_threads": 6,
        "chunk_build_defer_mode": "ALWAYS",
        "animate_only_visible_textures": False,
        "use_entity_culling": False,
        "use_fog_occlusion": False,
        "use_block_face_culling": False,
        "use_no_error_g_l_context": True,
        "quad_splitting_mode": "SAFE"
    },
    "advanced": {
        "enable_memory_tracing": False
    },
    "debug": {
        "terrain_sorting_enabled": True
    },
    "notifications": {
        "has_cleared_donation_button": True,
        "has_seen_donation_prompt": True,
        "has_edited_fullscreen_option": True
    }
}

SODIUM_PERFORMANCE = {
    "quality": {
        "hidden_fluid_culling": False,
        "improved_fluid_shaping": True,
        "use_closest_point_entity_sort": True,
        "pixel_filtering_mode": "NEAREST"
    },
    "performance": {
        "chunk_builder_threads": 4,
        "chunk_build_defer_mode": "ALWAYS",
        "animate_only_visible_textures": False,
        "use_entity_culling": False,
        "use_fog_occlusion": False,
        "use_block_face_culling": False,
        "use_no_error_g_l_context": True,
        "quad_splitting_mode": "SPEED"
    },
    "advanced": {
        "enable_memory_tracing": False
    },
    "debug": {
        "terrain_sorting_enabled": True
    },
    "notifications": {
        "has_cleared_donation_button": True,
        "has_seen_donation_prompt": True,
        "has_edited_fullscreen_option": True
    }
}

# ==============================================================================
# IRIS PROPERTIES PRESET GENERATOR
# ==============================================================================

def make_iris_props(shader_pack_name: str) -> str:
    return (
        "allowUnknownShaders=true\n"
        "colorSpace=SRGB\n"
        "disableUpdateMessage=true\n"
        "enableDebugOptions=false\n"
        "enableShaders=true\n"
        "maxShadowRenderDistance=32\n"
        f"shaderPack={shader_pack_name}\n"
    )

# ==============================================================================
# OPTIONS.TXT UPDATER HELPER
# ==============================================================================

def update_options_txt(file_path: str, is_modern: bool, tier: str, resource_packs: list = None):
    """
    Safely parses and updates options.txt to ensure:
    - enableVsync:false
    - maxFps:260
    - gamma:0.0
    - particles:0
    - renderDistance & simulationDistance calibrated by tier
    - resourcePacks configured
    - hotkey K deconflicted from craftingtweaks and assigned to Iris
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    lines = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.rstrip("\r\n") for l in f.readlines()]

    # Parse existing keys
    ordered_keys = []
    opt_map = {}
    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k not in opt_map:
                ordered_keys.append(k)
            opt_map[k] = v

    # Apply core universal standards
    opt_map["enableVsync"] = "false"
    opt_map["maxFps"] = "260"
    opt_map["gamma"] = "0.0"
    opt_map["particles"] = "0"

    # Tier-specific render distance & simulation distance
    if tier == "visual" or tier == "master":
        opt_map["renderDistance"] = "16"
        if is_modern:
            opt_map["simulationDistance"] = "10"
    elif tier == "balanced":
        opt_map["renderDistance"] = "12"
        if is_modern:
            opt_map["simulationDistance"] = "8"
    elif tier == "performance":
        opt_map["renderDistance"] = "8"
        if is_modern:
            opt_map["simulationDistance"] = "5"

    # Resource Packs
    if resource_packs is not None:
        opt_map["resourcePacks"] = json.dumps(resource_packs)

    # Keybinding standardization (Modern)
    if is_modern:
        # Remap any CraftingTweaks key bound to 'k' to 'unknown'
        for k in list(opt_map.keys()):
            if "craftingtweaks" in k.lower():
                if opt_map[k] == "key.keyboard.k" or opt_map[k] == "48" or opt_map[k] == "37":
                    opt_map[k] = "key.keyboard.unknown"

        # Explicitly set safe CraftingTweaks defaults
        ct_keys = [
            "key_key.craftingtweaks.compress_one",
            "key_key.craftingtweaks.compress_stack",
            "key_key.craftingtweaks.compress_all",
            "key_key.craftingtweaks.decompress_one",
            "key_key.craftingtweaks.decompress_stack",
            "key_key.craftingtweaks.decompress_all",
            "key_key.craftingtweaks.rotate",
            "key_key.craftingtweaks.rotate_counter_clockwise",
            "key_key.craftingtweaks.balance",
            "key_key.craftingtweaks.spread",
            "key_key.craftingtweaks.clear",
            "key_key.craftingtweaks.force_clear",
            "key_key.craftingtweaks.transfer_stack"
        ]
        for ctk in ct_keys:
            if ctk in opt_map:
                opt_map[ctk] = "key.keyboard.unknown"

        # Set Iris keybinds
        opt_map["key_iris.keybind.toggleShaders"] = "key.keyboard.k"
        opt_map["key_iris.keybind.reload"] = "key.keyboard.r"
        opt_map["key_iris.keybind.shaderPackSelection"] = "key.keyboard.i"
        opt_map["key_iris.keybind.wireframe"] = "key.keyboard.unknown"

    # Ensure all keys in opt_map are preserved in output
    for k in opt_map:
        if k not in ordered_keys:
            ordered_keys.append(k)

    new_lines = [f"{k}:{opt_map[k]}" for k in ordered_keys]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")
    print(f"[OK] Updated options.txt: {file_path}")

# ==============================================================================
# PRISM INSTANCE.CFG UPDATER HELPER
# ==============================================================================

def update_prism_instance_cfg(cfg_path: str):
    """
    Sets 8GB RAM allocation and G1GC flags in Prism instance.cfg
    """
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    lines = []
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            lines = [l.rstrip("\r\n") for l in f.readlines()]

    kv = {}
    other_lines = []
    has_general_header = False

    for line in lines:
        if line.strip() == "[General]":
            has_general_header = True
            continue
        if "=" in line and not line.startswith("["):
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
        else:
            other_lines.append(line)

    # Set memory and JVM args
    kv["OverrideMemory"] = "true"
    kv["MinMemAlloc"] = "4096"
    kv["MaxMemAlloc"] = "8192"
    kv["OverrideJavaArgs"] = "true"
    kv["JvmArgs"] = G1GC_FLAGS_STR

    output_lines = ["[General]"]
    for k, v in kv.items():
        output_lines.append(f"{k}={v}")
    if other_lines:
        output_lines.append("")
        output_lines.extend(other_lines)

    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")
    print(f"[OK] Updated Prism instance.cfg: {cfg_path}")

# ==============================================================================
# MAIN ENGINE EXECUTION
# ==============================================================================

def main():
    print("=" * 70)
    print("  AETHERIS WORKER M4: PERFORMANCE & VIDEO SETTINGS ENGINE")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # 1. STANDARDIZE OPTIONS.TXT ACROSS ALL INSTANCES
    # --------------------------------------------------------------------------
    print("\n[STEP 1] Standardizing options.txt...")

    # Modern Profiles
    modern_targets = [
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\options.txt", "visual", ["vanilla", "file/Aetheris_Ultimate_Pack.zip", "eatinganimationid:supporteatinganimation", "punchy:punchy"]),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\options.txt", "balanced", ["vanilla", "file/Aetheris_Ultimate_Pack.zip"]),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\options.txt", "performance", ["vanilla", "file/Aetheris_Ultimate_Pack.zip"]),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\options.txt", "visual", ["vanilla", "file/Aetheris_Ultimate_Pack.zip"]),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\options.txt", "visual", ["vanilla", "file/Aetheris_Ultimate_Pack.zip", "punchy:punchy"]),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\.minecraft\options.txt", "visual", ["vanilla", "file/Aetheris_Ultimate_Pack.zip", "punchy:punchy"]),
        (r"C:\Users\a7med\AppData\Roaming\.minecraft\options.txt", "visual", ["vanilla", "file/Aetheris_Ultimate_Pack.zip", "file/Aetheris_Ultimate_32x.zip"]),
        (r"D:\AetherisShare\profiles\visual\options.txt", "visual", ["vanilla", "file/Aetheris_Ultimate_Pack.zip", "eatinganimationid:supporteatinganimation", "punchy:punchy"]),
        (r"D:\AetherisShare\profiles\balanced\options.txt", "balanced", ["vanilla", "file/Aetheris_Ultimate_Pack.zip"]),
        (r"D:\AetherisShare\profiles\performance\options.txt", "performance", ["vanilla", "file/Aetheris_Ultimate_Pack.zip"]),
    ]

    for path, tier, rpacks in modern_targets:
        update_options_txt(path, is_modern=True, tier=tier, resource_packs=rpacks)

    # Legacy Profiles
    legacy_targets = [
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9\options.txt", "master", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-visual-1.8.9\options.txt", "visual", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-balanced-1.8.9\options.txt", "balanced", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-performance-1.8.9\options.txt", "performance", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\minecraft\options.txt", "master", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\.minecraft\options.txt", "master", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"D:\AetherisShare\profiles\legacy\options.txt", "master", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"D:\AetherisShare\profiles\legacy-visual\options.txt", "visual", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"D:\AetherisShare\profiles\legacy-balanced\options.txt", "balanced", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
        (r"D:\AetherisShare\profiles\legacy-performance\options.txt", "performance", ["vanilla", "file/MyCustomPack_1.8.9_32x.zip"]),
    ]

    for path, tier, rpacks in legacy_targets:
        update_options_txt(path, is_modern=False, tier=tier, resource_packs=rpacks)

    # --------------------------------------------------------------------------
    # 2. STANDARDIZE SODIUM-OPTIONS.JSON ACROSS MODERN PROFILES
    # --------------------------------------------------------------------------
    print("\n[STEP 2] Standardizing sodium-options.json...")

    sodium_targets = [
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\config\sodium-options.json", SODIUM_VISUAL),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\config\sodium-options.json", SODIUM_BALANCED),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\config\sodium-options.json", SODIUM_PERFORMANCE),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\config\sodium-options.json", SODIUM_VISUAL),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\config\sodium-options.json", SODIUM_VISUAL),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\.minecraft\config\sodium-options.json", SODIUM_VISUAL),
        (r"C:\Users\a7med\AppData\Roaming\.minecraft\config\sodium-options.json", SODIUM_VISUAL),
        (r"D:\AetherisShare\profiles\visual\config\sodium-options.json", SODIUM_VISUAL),
        (r"D:\AetherisShare\profiles\balanced\config\sodium-options.json", SODIUM_BALANCED),
        (r"D:\AetherisShare\profiles\performance\config\sodium-options.json", SODIUM_PERFORMANCE),
    ]

    for path, conf in sodium_targets:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(conf, f, indent=2)
        print(f"[OK] Written sodium-options.json (threads: {conf['performance']['chunk_builder_threads']}): {path}")

    # --------------------------------------------------------------------------
    # 3. STANDARDIZE IRIS.PROPERTIES ACROSS MODERN PROFILES
    # --------------------------------------------------------------------------
    print("\n[STEP 3] Standardizing iris.properties...")

    iris_targets = [
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\config\iris.properties", "Aetheris_Visual_Shader.zip"),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\config\iris.properties", "Aetheris_Balanced_Shader.zip"),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\config\iris.properties", "Aetheris_Shader_Pack.zip"),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\config\iris.properties", "Aetheris_Shader_Pack.zip"),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\config\iris.properties", "Aetheris_Visual_Shader.zip"),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\.minecraft\config\iris.properties", "Aetheris_Visual_Shader.zip"),
        (r"C:\Users\a7med\AppData\Roaming\.minecraft\config\iris.properties", "Aetheris_Shader_Pack.zip"),
        (r"D:\AetherisShare\profiles\visual\config\iris.properties", "Aetheris_Visual_Shader.zip"),
        (r"D:\AetherisShare\profiles\balanced\config\iris.properties", "Aetheris_Balanced_Shader.zip"),
        (r"D:\AetherisShare\profiles\performance\config\iris.properties", "Aetheris_Shader_Pack.zip"),
    ]

    for path, pack in iris_targets:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = make_iris_props(pack)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] Written iris.properties (shader: {pack}): {path}")

    # --------------------------------------------------------------------------
    # 4. STANDARDIZE PRISM INSTANCE.CFG (8GB ALLOCATION + G1GC FLAGS)
    # --------------------------------------------------------------------------
    print("\n[STEP 4] Standardizing Prism Launcher instance.cfg files...")

    prism_instances = [
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\instance.cfg",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\instance.cfg",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\instance.cfg",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\instance.cfg",
    ]

    for path in prism_instances:
        update_prism_instance_cfg(path)

    # --------------------------------------------------------------------------
    # 5. STANDARDIZE JVM-OPTIONS.TXT ACROSS LUNAR AND SHARE PROFILES
    # --------------------------------------------------------------------------
    print("\n[STEP 5] Deploying jvm-options.txt across Lunar & Share profiles...")

    jvm_txt_targets = [
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\jvm-options.txt",
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\jvm-options.txt",
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\jvm-options.txt",
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\jvm-options.txt",
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9\jvm-options.txt",
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-visual-1.8.9\jvm-options.txt",
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-balanced-1.8.9\jvm-options.txt",
        r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-performance-1.8.9\jvm-options.txt",
        r"D:\AetherisShare\profiles\visual\jvm-options.txt",
        r"D:\AetherisShare\profiles\balanced\jvm-options.txt",
        r"D:\AetherisShare\profiles\performance\jvm-options.txt",
        r"D:\AetherisShare\profiles\legacy\jvm-options.txt",
        r"D:\AetherisShare\profiles\legacy-visual\jvm-options.txt",
        r"D:\AetherisShare\profiles\legacy-balanced\jvm-options.txt",
        r"D:\AetherisShare\profiles\legacy-performance\jvm-options.txt",
    ]

    for path in jvm_txt_targets:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(JVM_OPTIONS_TXT_CONTENT)
        print(f"[OK] Deployed jvm-options.txt: {path}")

    # --------------------------------------------------------------------------
    # 6. STANDARDIZE LUNAR PROFILES.DB (8GB ALLOCATION + JVM ARGUMENTS)
    # --------------------------------------------------------------------------
    print("\n[STEP 6] Updating Lunar Client profiles.db...")
    db_path = r"C:\Users\a7med\.lunarclient\db\profiles.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE profiles 
            SET allocated_memory = 8192,
                jvm_arguments = ?
            WHERE name LIKE '%aetheris%' OR path LIKE '%aetheris%'
        """, (G1GC_FLAGS_STR,))
        rows_updated = c.rowcount
        conn.commit()
        conn.close()
        print(f"[OK] Updated {rows_updated} Aetheris profiles in profiles.db (8192 MB, G1GC args).")
    else:
        print("[WARN] profiles.db not found, skipped DB update.")

    print("\n" + "=" * 70)
    print("  ALL M4 PERFORMANCE & VIDEO SETTINGS STANDARDIZATIONS APPLIED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
