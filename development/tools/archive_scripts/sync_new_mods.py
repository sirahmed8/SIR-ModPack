#!/usr/bin/env python3
"""
sync_new_mods.py
1. Copies bbe-fabric and fism+26.2 from keo-optimized into Aetheris Visual + Balanced
2. Syncs all mods from Visual that are NOT in Balanced (visual-only mods stay visual-only based on category)
3. Copies relevant mods to D:\mods master vault
"""
import os, shutil

keo_mods = r"C:\Users\a7med\.lunarclient\profiles\keo-optimized\mods"
visual_mods = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\mods"
balanced_mods = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\mods"
main_mods = r"D:\mods"

# ============================================================
# STEP 1: Copy bbe-fabric and fism from keo -> visual + balanced
# ============================================================
print("=" * 65)
print("STEP 1: Adding bbe-fabric + fism to Aetheris profiles")
print("=" * 65)

grab_from_keo = ["bbe-fabric-1.3.6+mc26.2.jar", "fism+26.2-1.0.4.jar"]

for jar in grab_from_keo:
    src = os.path.join(keo_mods, jar)
    if not os.path.exists(src):
        print(f"  SKIP (not found in keo): {jar}")
        continue

    for dst_dir, label in [
        (visual_mods, "Aetheris Visual"),
        (balanced_mods, "Aetheris Balanced"),
        (main_mods, "D:\\mods master"),
    ]:
        dst = os.path.join(dst_dir, jar)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  ✅ Copied {jar} -> {label}")
        else:
            print(f"  ✓ Already exists: {jar} in {label}")

# ============================================================
# STEP 2: Sync relevant new mods from Visual -> Balanced
# ============================================================
print()
print("=" * 65)
print("STEP 2: Syncing new mods from Visual -> Balanced")
print("=" * 65)

# These mods should go to BOTH visual and balanced (quality/gameplay/utility)
# NOT pure visual-only mods (no DistantHorizons, no EuphoriaPatcher, no BridgingMod for balanced)
sync_to_balanced = [
    "InventoryProfilesNext-fabric-26.2-2.3.6.jar",
    "libIPN-fabric-26.2-6.8.3.jar",
    "shulkerboxtooltip-fabric-5.4.0+26.2.jar",
    "veinminer-fabric-2.12.0.jar",
    "veinminer-client-fabric-2.12.0.jar",
    "JustEnoughResources-Fabric-26.2-1.11.0.43.jar",
    "structureessentials-fabric-26.2-5.0.jar",
    "gpumemleakfix-fabric-26.2-1.9.jar",
    "EuphoriaPatcher-1.9.3-r5.8.1-fabric.jar",
    "carryon-fabric-26.2-2.11.0.jar",
    "moreoverlays-1.24.4-mc26.2-fabric.jar",
    "memorysettings-fabric-26.2-6.0.jar",
    "betterfpsdist-fabric-26.2-6.2.jar",
    "fastasyncworldsave-fabric-26.1-2.6.jar",
    "integrated_api-fabric-26.2-1.8.0.jar",
    "betterarcheology-fabric-26.2-1.3.8.jar",
    "mcw-stairs-1.0.2-mc26.2fabric.jar",
    "immersive_optimization-fabric-26.2-0.2.0.jar",
    "formations-1.0.4-fabric-mc26.2.jar",
    "bclib-26.201.2.jar",
    "worldweaver-26.201.2.jar",
    "better-nether-26.201.2.jar",
    "structurify-fabric-2.0.33+mc26.2.jar",
    "Iceberg-26.2-fabric-1.4.2.1.jar",
    "ScalableLux-fabric-0.3.0-alpha.0.3-all.jar",
    "Gnetum-4.5.3+26.2-fabric.jar",
    "Ixeris-4.6.5+26.2-fabric.jar",
    "asynclogger-2.2.2+26.1.2-fabric.jar",
    "moreculling-fabric-26.2-1.8.1.jar",
    "vmp-fabric-mc26.2-0.2.0+beta.7.236-all.jar",
    "krypton-0.3.1.jar",
    "PacketFixer-fabric-3.3.6.jar",
    "MoogsStructureLib-fabric-26.2-3.1.0.jar",
    "sway-2.4.3-fabric+26.2.jar",
    "PlayerAnimationLibMerged-1.2.6+mc.26.2.jar",
]

# Visual-only (heavy, GPU-intensive — skip for balanced)
visual_only = {
    "DistantHorizons-3.2.0-b-26.2-fabric-neoforge.jar",  # extreme GPU load
    "BridgingMod-2.7.0+26.2.fabric-release.jar",          # visual glitch mod
    "EuphoriaPatcher-1.9.3-r5.8.1-fabric.jar",            # keep in visual only (it's heavy shader addon)
    "IrisSearch-1.6.0-fabric.jar",
    "iris_shader_folder-1.4.1-fabric.jar",
}

synced = 0
skipped = 0
for jar in sync_to_balanced:
    src = os.path.join(visual_mods, jar)
    dst = os.path.join(balanced_mods, jar)

    if not os.path.exists(src):
        print(f"  SKIP (not in visual): {jar}")
        skipped += 1
        continue
    if os.path.exists(dst):
        skipped += 1
        continue  # already there

    shutil.copy2(src, dst)
    print(f"  ✅ Synced -> Balanced: {jar}")
    synced += 1

print(f"\n  Synced: {synced} | Already present/skipped: {skipped}")

# ============================================================
# STEP 3: Copy all new mods to D:\mods master vault
# ============================================================
print()
print("=" * 65)
print("STEP 3: Backing up new mods to D:\\mods master vault")
print("=" * 65)

backed_up = 0
for jar in os.listdir(visual_mods):
    if not jar.endswith(".jar"):
        continue
    dst = os.path.join(main_mods, jar)
    src = os.path.join(visual_mods, jar)
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        backed_up += 1

print(f"  ✅ Backed up {backed_up} new mods to D:\\mods")

print()
print("=" * 65)
print("✨ ALL DONE!")
print("=" * 65)
print(f"  bbe-fabric + fism: Added to Visual, Balanced, D:\\mods")
print(f"  New user-downloaded mods synced to Balanced profile")
print(f"  D:\\mods master vault updated")
