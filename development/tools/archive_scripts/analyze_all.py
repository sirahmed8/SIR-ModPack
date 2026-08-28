import os, zipfile, json

SH_DIR = r"D:\shader"
RP_DIR = r"D:\resource pack"
VISUAL   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BALANCED = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2"
LEGACY   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9"

# === 1. FULL MOD LIST ===
print("=== VISUAL MODS ===")
mods = sorted(os.listdir(os.path.join(VISUAL, "mods")))
for m in mods:
    print("  " + m)
print(f"  TOTAL: {len(mods)}")

print()
print("=== BALANCED MODS (diff from Visual) ===")
b_mods = set(os.listdir(os.path.join(BALANCED, "mods")))
v_mods = set(mods)
only_balanced = b_mods - v_mods
only_visual = v_mods - b_mods
print("  Only in Balanced: " + str(sorted(only_balanced)))
print("  Only in Visual:   " + str(sorted(only_visual)))
print(f"  Balanced total: {len(b_mods)}")

print()
# === 2. KEY PERFORMANCE CONFIGS ===
print("=== SODIUM CONFIG ===")
sodium_cfg = os.path.join(VISUAL, "config", "sodium-options.json")
if os.path.exists(sodium_cfg):
    with open(sodium_cfg, encoding="utf-8", errors="replace") as f:
        print(f.read()[:3000])
else:
    print("  NOT FOUND: " + sodium_cfg)

print()
print("=== C2ME CONFIG ===")
for cfg_name in ["c2me.toml", "c2me-config.toml", "c2me.json"]:
    cp = os.path.join(VISUAL, "config", cfg_name)
    if os.path.exists(cp):
        with open(cp, encoding="utf-8", errors="replace") as f:
            print(f.read()[:2000])
        break
else:
    import glob
    c2me_files = glob.glob(os.path.join(VISUAL, "config", "*c2me*"))
    print("  c2me files: " + str(c2me_files))

print()
print("=== LITHIUM CONFIG ===")
li_cfg = os.path.join(VISUAL, "config", "lithium.properties")
if os.path.exists(li_cfg):
    with open(li_cfg, encoding="utf-8", errors="replace") as f:
        print(f.read()[:2000])
else:
    print("  NOT FOUND")

print()
# === 3. ALL SHADERS ANALYSIS ===
print("=== ALL SHADERS ===")
for f in sorted(os.listdir(SH_DIR)):
    if not f.endswith(".zip"):
        continue
    fp = os.path.join(SH_DIR, f)
    sz = os.path.getsize(fp) / 1024 / 1024
    try:
        with zipfile.ZipFile(fp) as z:
            names = z.namelist()
            sp = next((n for n in names if n.endswith("shaders.properties")), None)
            if sp:
                props = z.read(sp).decode("utf-8", errors="replace")
                profiles = [l.strip() for l in props.splitlines() if l.strip().startswith("profile.") and "=" in l]
                profile_str = ", ".join(p.split("=")[0].replace("profile.", "") for p in profiles[:5])
                features = []
                if "LPV" in props: features.append("LPV")
                if "COMPUTE_SHADERS" in props: features.append("COMPUTE")
                if "DISTANT_HORIZONS" in props: features.append("DH")
                if "TAA_UPSCALING" in props: features.append("TAA-UPSCALE")
                if "AUTO_EXPOSURE" in props: features.append("AUTO-EXP")
                if "POM" in props: features.append("POM")
                if "TRANSLUCENT_COLORED" in props: features.append("LEAF-LIGHT")
                glsl = len([n for n in names if n.endswith((".glsl", ".fsh", ".vsh", ".csh"))])
                print(f"  {f} ({sz:.1f}MB)")
                print(f"    Profiles: {profile_str if profile_str else '(custom/none)'}")
                print(f"    GLSL files: {glsl}  |  Features: {', '.join(features)}")
            else:
                print(f"  {f} ({sz:.1f}MB) - no shaders.properties")
    except Exception as e:
        print(f"  {f}: {e}")

print()
# === 4. OPTIMUM REALISM STRUCTURE (deep check) ===
print("=== OPTIMUM REALISM STRUCTURE ===")
OR_ZIP = os.path.join(RP_DIR, "Optimum Realism R3.9.0 64x.zip")
with zipfile.ZipFile(OR_ZIP) as z:
    names = z.namelist()
    # Check for height maps in normal alpha (check file sizes vs names)
    normals = [n for n in names if n.endswith("_n.png")]
    speculars = [n for n in names if n.endswith("_s.png")]
    models3d = [n for n in names if "models/block" in n and n.endswith(".json")]
    ctm_props = [n for n in names if n.endswith(".properties") and "ctm" in n.lower()]
    cem = [n for n in names if n.endswith(".jem")]
    print(f"  Normal maps: {len(normals)}")
    print(f"  Specular maps: {len(speculars)}")
    print(f"  3D block models: {len(models3d)}")
    print(f"  CTM properties: {len(ctm_props)}")
    print(f"  CEM entity models: {len(cem)}")
    print("  Sample 3D models:")
    for m in models3d[:8]:
        print("    " + m)
    print("  Sample CEM:")
    for m in cem[:5]:
        print("    " + m)
    # Check a normal map size to see if it likely has alpha
    if normals:
        sample = normals[0]
        data = z.read(sample)
        print(f"  Sample normal ({sample}): {len(data)} bytes")

print()
# === 5. PHYSICS MOD CONFIG ===
print("=== PHYSICS MOD CONFIG ===")
phys = os.path.join(VISUAL, "config", "physicsmod", "physics_client_config.json")
if os.path.exists(phys):
    with open(phys, encoding="utf-8", errors="replace") as f:
        print(f.read()[:1000])

print()
# === 6. OPTIONS.TXT KEY SETTINGS ===
print("=== OPTIONS.TXT ===")
opts = os.path.join(VISUAL, "options.txt")
with open(opts, encoding="utf-8", errors="replace") as f:
    for line in f:
        print(line.rstrip())
