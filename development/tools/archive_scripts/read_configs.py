import os, zipfile, glob

VISUAL = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
SH_DIR = r"D:\shader"

for f in sorted(os.listdir(SH_DIR)):
    if not f.endswith(".zip"): continue
    try:
        with zipfile.ZipFile(os.path.join(SH_DIR, f)) as z:
            sp = next((n for n in z.namelist() if n.endswith("shaders.properties")), None)
            if not sp: continue
            props = z.read(sp).decode("utf-8", "replace")
            glsl = len([n for n in z.namelist() if any(n.endswith(x) for x in [".glsl",".fsh",".vsh",".csh"])])
            feat = []
            checks = [("LPV","LPV_ENABLED"),("Compute","COMPUTE_SHADERS"),("DH","DISTANT_HORIZONS"),
                      ("TAA-Up","TAA_UPSCALING"),("AutoExp","AUTO_EXPOSURE"),("POM","POM"),
                      ("LeafLight","TRANSLUCENT_COLORED"),("SSR","Screen_Space_Reflections"),
                      ("VoluFog","VL_SAMPLES"),("Seasons","Seasons"),("DoF","DOF_QUALITY"),
                      ("MotionBlur","MOTION_BLUR"),("ContactShadow","SCREENSPACE_CONTACT")]
            for name, key in checks:
                if key in props: feat.append(name)
            size = os.path.getsize(os.path.join(SH_DIR, f)) / 1024 / 1024
            feat_str = " ".join(feat)
            print(f + " (" + str(round(size)) + "MB) GLSL:" + str(glsl) + " | " + feat_str)
    except Exception as e:
        print(f + ": " + str(e))

print()
print("=== SODIUM CONFIG ===")
for p in glob.glob(os.path.join(VISUAL, "config", "*sodium*")):
    print("FILE: " + p)
    with open(p, encoding="utf-8", errors="replace") as fh:
        print(fh.read()[:2000])

print()
print("=== C2ME CONFIG ===")
for p in glob.glob(os.path.join(VISUAL, "config", "*c2me*")) + glob.glob(os.path.join(VISUAL, "config", "c2me*")):
    print("FILE: " + p)
    with open(p, encoding="utf-8", errors="replace") as fh:
        print(fh.read()[:2000])

print()
print("=== LITHIUM CONFIG ===")
for p in glob.glob(os.path.join(VISUAL, "config", "lithium*")):
    print("FILE: " + p)
    with open(p, encoding="utf-8", errors="replace") as fh:
        print(fh.read()[:1500])

print()
print("=== PHYSICS CLIENT CONFIG ===")
phys = os.path.join(VISUAL, "config", "physicsmod", "physics_client_config.json")
if os.path.exists(phys):
    with open(phys, encoding="utf-8", errors="replace") as fh:
        print(fh.read())

print()
print("=== OPTIONS.TXT KEY VIDEO SETTINGS ===")
opts = os.path.join(VISUAL, "options.txt")
video_keys = ["renderDistance","simulationDistance","graphicsMode","entityDistanceMul",
               "chunkBuilderMode","fullscreen","guiScale","fov","gamma","biomeBlend",
               "maxFps","particles","smooth","ao","bobView","cloudLevel","vSync"]
with open(opts, encoding="utf-8", errors="replace") as fh:
    for line in fh:
        key = line.split(":")[0]
        if any(k.lower() in key.lower() for k in video_keys):
            print(line.rstrip())
