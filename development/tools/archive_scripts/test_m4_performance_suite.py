#!/usr/bin/env python3
"""
Aetheris Ecosystem — M4 Performance & Video Settings Verification Suite
Performs deep automated checks on:
- options.txt (VSync, maxFps, gamma, particles, active resourcePacks, keybind K deconfliction)
- sodium-options.json (chunk builder threads 20/6/4, entity culling, rendering flags)
- iris.properties (allowUnknownShaders=true, active shaderpacks)
- JVM launch arguments (8GB memory, optimized G1GC flags) in Prism Launcher instance.cfg, Lunar profiles, and profiles.db
"""

import os
import json
import sqlite3
import re
import sys

def run_tests():
    print("=" * 70)
    print("  AETHERIS PERFORMANCE & VIDEO SETTINGS VERIFICATION SUITE")
    print("=" * 70)

    total_checks = 0
    failures = []

    # --------------------------------------------------------------------------
    # TEST 1: OPTIONS.TXT UNIFORMITY & KEYBIND AUDIT
    # --------------------------------------------------------------------------
    print("\n[TEST 1] Auditing options.txt across all Modern and Legacy profiles...")

    modern_options = [
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\options.txt", "visual", 16, 10),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\options.txt", "balanced", 12, 8),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\options.txt", "performance", 8, 5),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\options.txt", "visual", 16, 10),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\options.txt", "visual", 16, 10),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\.minecraft\options.txt", "visual", 16, 10),
        (r"C:\Users\a7med\AppData\Roaming\.minecraft\options.txt", "visual", 16, 10),
        (r"D:\AetherisShare\profiles\visual\options.txt", "visual", 16, 10),
        (r"D:\AetherisShare\profiles\balanced\options.txt", "balanced", 12, 8),
        (r"D:\AetherisShare\profiles\performance\options.txt", "performance", 8, 5),
    ]

    legacy_options = [
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9\options.txt", "master", 16),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-visual-1.8.9\options.txt", "visual", 16),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-balanced-1.8.9\options.txt", "balanced", 12),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-performance-1.8.9\options.txt", "performance", 8),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\minecraft\options.txt", "master", 16),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\.minecraft\options.txt", "master", 16),
        (r"D:\AetherisShare\profiles\legacy\options.txt", "master", 16),
        (r"D:\AetherisShare\profiles\legacy-visual\options.txt", "visual", 16),
        (r"D:\AetherisShare\profiles\legacy-balanced\options.txt", "balanced", 12),
        (r"D:\AetherisShare\profiles\legacy-performance\options.txt", "performance", 8),
    ]

    for path, tier, rdist, sdist in modern_options:
        total_checks += 1
        if not os.path.exists(path):
            failures.append(f"Missing file: {path}")
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            opts = dict([l.strip().split(":", 1) for l in f if ":" in l])
        
        # Check standard properties
        if opts.get("enableVsync") != "false":
            failures.append(f"{path}: enableVsync is {opts.get('enableVsync')}, expected false")
        if opts.get("maxFps") not in ["260", "0"]:
            failures.append(f"{path}: maxFps is {opts.get('maxFps')}, expected 260")
        if opts.get("gamma") != "0.0":
            failures.append(f"{path}: gamma is {opts.get('gamma')}, expected 0.0")
        if opts.get("particles") != "0":
            failures.append(f"{path}: particles is {opts.get('particles')}, expected 0")
        if opts.get("renderDistance") != str(rdist):
            failures.append(f"{path}: renderDistance is {opts.get('renderDistance')}, expected {rdist}")
        if opts.get("simulationDistance") != str(sdist):
            failures.append(f"{path}: simulationDistance is {opts.get('simulationDistance')}, expected {sdist}")
        
        # Check resource pack
        rpacks_str = opts.get("resourcePacks", "[]")
        try:
            rpacks = json.loads(rpacks_str)
            if not any("Aetheris" in p or "MyCustomPack" in p for p in rpacks):
                failures.append(f"{path}: resourcePacks missing Aetheris pack: {rpacks_str}")
        except Exception as e:
            failures.append(f"{path}: invalid resourcePacks JSON: {e}")

        # Check Iris keybind
        if opts.get("key_iris.keybind.toggleShaders") != "key.keyboard.k":
            failures.append(f"{path}: key_iris.keybind.toggleShaders is {opts.get('key_iris.keybind.toggleShaders')}, expected key.keyboard.k")

        # Check CraftingTweaks deconfliction
        for k, v in opts.items():
            if "craftingtweaks" in k.lower() and v == "key.keyboard.k":
                failures.append(f"{path}: CraftingTweaks collision detected: {k} = {v}")

    for path, tier, rdist in legacy_options:
        total_checks += 1
        if not os.path.exists(path):
            failures.append(f"Missing file: {path}")
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            opts = dict([l.strip().split(":", 1) for l in f if ":" in l])
        
        if opts.get("enableVsync") != "false":
            failures.append(f"{path}: enableVsync is {opts.get('enableVsync')}, expected false")
        if opts.get("maxFps") not in ["260", "0"]:
            failures.append(f"{path}: maxFps is {opts.get('maxFps')}, expected 260")
        if opts.get("gamma") != "0.0":
            failures.append(f"{path}: gamma is {opts.get('gamma')}, expected 0.0")
        if opts.get("particles") != "0":
            failures.append(f"{path}: particles is {opts.get('particles')}, expected 0")
        if opts.get("renderDistance") != str(rdist):
            failures.append(f"{path}: renderDistance is {opts.get('renderDistance')}, expected {rdist}")
        
        rpacks_str = opts.get("resourcePacks", "[]")
        try:
            rpacks = json.loads(rpacks_str)
            if not any("Aetheris" in p or "MyCustomPack" in p for p in rpacks):
                failures.append(f"{path}: resourcePacks missing Aetheris pack: {rpacks_str}")
        except Exception as e:
            failures.append(f"{path}: invalid resourcePacks JSON: {e}")

    print(f"  -> Audited {len(modern_options) + len(legacy_options)} options.txt files. (Failures: {len(failures)})")

    # --------------------------------------------------------------------------
    # TEST 2: SODIUM-OPTIONS.JSON THREAD SCALING & QUALITY PRESETS
    # --------------------------------------------------------------------------
    print("\n[TEST 2] Auditing sodium-options.json across modern profiles...")
    sodium_checks = [
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\config\sodium-options.json", 20, "SAFE"),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\config\sodium-options.json", 6, "SAFE"),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\config\sodium-options.json", 4, "SPEED"),
        (r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\config\sodium-options.json", 20, "SAFE"),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\config\sodium-options.json", 20, "SAFE"),
        (r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\.minecraft\config\sodium-options.json", 20, "SAFE"),
        (r"C:\Users\a7med\AppData\Roaming\.minecraft\config\sodium-options.json", 20, "SAFE"),
        (r"D:\AetherisShare\profiles\visual\config\sodium-options.json", 20, "SAFE"),
        (r"D:\AetherisShare\profiles\balanced\config\sodium-options.json", 6, "SAFE"),
        (r"D:\AetherisShare\profiles\performance\config\sodium-options.json", 4, "SPEED"),
    ]

    sodium_fail_count = 0
    for path, exp_threads, exp_quad in sodium_checks:
        total_checks += 1
        if not os.path.exists(path):
            failures.append(f"Missing sodium config: {path}")
            sodium_fail_count += 1
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            perf = data.get("performance", {})
            threads = perf.get("chunk_builder_threads")
            if threads != exp_threads:
                failures.append(f"{path}: chunk_builder_threads is {threads}, expected {exp_threads}")
                sodium_fail_count += 1
            if perf.get("chunk_build_defer_mode") != "ALWAYS":
                failures.append(f"{path}: chunk_build_defer_mode is {perf.get('chunk_build_defer_mode')}, expected ALWAYS")
                sodium_fail_count += 1
            if perf.get("quad_splitting_mode") != exp_quad:
                failures.append(f"{path}: quad_splitting_mode is {perf.get('quad_splitting_mode')}, expected {exp_quad}")
                sodium_fail_count += 1
            if perf.get("use_no_error_g_l_context") is not True:
                failures.append(f"{path}: use_no_error_g_l_context is not True")
                sodium_fail_count += 1

            qual = data.get("quality", {})
            if qual.get("improved_fluid_shaping") is not True:
                failures.append(f"{path}: improved_fluid_shaping is not True")
                sodium_fail_count += 1
            if qual.get("use_closest_point_entity_sort") is not True:
                failures.append(f"{path}: use_closest_point_entity_sort is not True")
                sodium_fail_count += 1

        except Exception as e:
            failures.append(f"{path}: failed parsing JSON: {e}")
            sodium_fail_count += 1

    print(f"  -> Audited {len(sodium_checks)} sodium-options.json files. (Failures: {sodium_fail_count})")

    # --------------------------------------------------------------------------
    # TEST 3: IRIS.PROPERTIES CONSISTENCY
    # --------------------------------------------------------------------------
    print("\n[TEST 3] Auditing iris.properties across modern profiles...")
    iris_checks = [
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

    iris_fail_count = 0
    for path, exp_shader in iris_checks:
        total_checks += 1
        if not os.path.exists(path):
            failures.append(f"Missing iris config: {path}")
            iris_fail_count += 1
            continue
        with open(path, "r", encoding="utf-8") as f:
            props = dict([l.strip().split("=", 1) for l in f if "=" in l and not l.startswith("#")])
        
        if props.get("allowUnknownShaders") != "true":
            failures.append(f"{path}: allowUnknownShaders is {props.get('allowUnknownShaders')}, expected true")
            iris_fail_count += 1
        if props.get("enableShaders") != "true":
            failures.append(f"{path}: enableShaders is {props.get('enableShaders')}, expected true")
            iris_fail_count += 1
        if props.get("colorSpace") != "SRGB":
            failures.append(f"{path}: colorSpace is {props.get('colorSpace')}, expected SRGB")
            iris_fail_count += 1
        if props.get("shaderPack") != exp_shader:
            failures.append(f"{path}: shaderPack is {props.get('shaderPack')}, expected {exp_shader}")
            iris_fail_count += 1

    print(f"  -> Audited {len(iris_checks)} iris.properties files. (Failures: {iris_fail_count})")

    # --------------------------------------------------------------------------
    # TEST 4: JVM LAUNCH ARGUMENTS & MEMORY ALLOCATION
    # --------------------------------------------------------------------------
    print("\n[TEST 4] Auditing JVM Arguments (Prism instance.cfg, Lunar/Share jvm-options.txt, profiles.db)...")
    prism_cfgs = [
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\instance.cfg",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\instance.cfg",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\instance.cfg",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\instance.cfg",
    ]

    jvm_fail_count = 0
    for path in prism_cfgs:
        total_checks += 1
        if not os.path.exists(path):
            failures.append(f"Missing Prism instance.cfg: {path}")
            jvm_fail_count += 1
            continue
        with open(path, "r", encoding="utf-8") as f:
            cfg = dict([l.strip().split("=", 1) for l in f if "=" in l and not l.startswith("[")])
        
        if cfg.get("OverrideMemory") != "true":
            failures.append(f"{path}: OverrideMemory is {cfg.get('OverrideMemory')}, expected true")
            jvm_fail_count += 1
        if cfg.get("MaxMemAlloc") != "8192":
            failures.append(f"{path}: MaxMemAlloc is {cfg.get('MaxMemAlloc')}, expected 8192")
            jvm_fail_count += 1
        if cfg.get("MinMemAlloc") != "4096":
            failures.append(f"{path}: MinMemAlloc is {cfg.get('MinMemAlloc')}, expected 4096")
            jvm_fail_count += 1
        if cfg.get("OverrideJavaArgs") != "true":
            failures.append(f"{path}: OverrideJavaArgs is {cfg.get('OverrideJavaArgs')}, expected true")
            jvm_fail_count += 1
        jvm_args = cfg.get("JvmArgs", "")
        if "-XX:+UseG1GC" not in jvm_args or "-XX:G1HeapRegionSize=8M" not in jvm_args:
            failures.append(f"{path}: JvmArgs missing G1GC optimization flags")
            jvm_fail_count += 1

    # Check jvm-options.txt
    jvm_txts = [
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

    for path in jvm_txts:
        total_checks += 1
        if not os.path.exists(path):
            failures.append(f"Missing jvm-options.txt: {path}")
            jvm_fail_count += 1
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "-XX:+UseG1GC" not in content or "-Xmx8G" not in content:
            failures.append(f"{path}: jvm-options.txt missing G1GC or 8GB flag")
            jvm_fail_count += 1

    # Check Lunar profiles.db
    db_path = r"C:\Users\a7med\.lunarclient\db\profiles.db"
    if os.path.exists(db_path):
        total_checks += 1
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, name, allocated_memory, jvm_arguments FROM profiles WHERE name LIKE '%aetheris%' OR path LIKE '%aetheris%'")
        rows = c.fetchall()
        for rid, rname, rmem, rargs in rows:
            if rmem != 8192:
                failures.append(f"profiles.db profile '{rname}': allocated_memory is {rmem}, expected 8192")
                jvm_fail_count += 1
            if not rargs or "-XX:+UseG1GC" not in rargs:
                failures.append(f"profiles.db profile '{rname}': jvm_arguments missing G1GC flags")
                jvm_fail_count += 1
        conn.close()

    print(f"  -> Audited {len(prism_cfgs) + len(jvm_txts) + 1} JVM configurations. (Failures: {jvm_fail_count})")

    # --------------------------------------------------------------------------
    # SUMMARY REPORT
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    if not failures:
        print("  ALL VERIFICATION CHECKS PASSED: 100% COMPLIANT & SYNCHRONIZED!")
        print(f"  Total verified configurations: {total_checks}")
        print("=" * 70)
        return 0
    else:
        print(f"  VERIFICATION FAILED: {len(failures)} issues detected!")
        for fail in failures:
            print(f"    - {fail}")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
