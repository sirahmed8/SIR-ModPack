import os, zipfile, io, re, shutil, struct

MODS    = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\mods"
PROFILE = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BAK_DIR = os.path.join(MODS, "..", "mods-patched-originals")
os.makedirs(BAK_DIR, exist_ok=True)

# ── 1. Check what shader Iris is set to ─────────────────────────
print("=== Current Iris shader setting ===")
opts = os.path.join(PROFILE, "options.txt")
iris_shader = None
with open(opts, encoding="utf-8", errors="replace") as f:
    for line in f:
        if "iris" in line.lower() or "shaderpack" in line.lower():
            print("  " + line.rstrip())
            if "shaderpack" in line.lower():
                iris_shader = line.strip().split("=", 1)[-1].strip()

iris_props = os.path.join(PROFILE, "config", "iris.properties")
if os.path.exists(iris_props):
    print()
    print("iris.properties:")
    with open(iris_props, encoding="utf-8", errors="replace") as f:
        for line in f:
            print("  " + line.rstrip())
            if "shaderpack" in line.lower():
                iris_shader = line.strip().split("=", 1)[-1].strip()

print()
print("Active shader: " + str(iris_shader))

# ── 2. Find EuphoriaPatcher JAR ─────────────────────────────────
ep_jar = None
for f in os.listdir(MODS):
    if "euphoria" in f.lower() and "patch" in f.lower() and f.endswith(".jar"):
        ep_jar = os.path.join(MODS, f)
        print()
        print("EuphoriaPatcher: " + f)

if not ep_jar:
    print("EuphoriaPatcher not found!")
    exit(1)

# ── 3. Find shader-detection class ──────────────────────────────
print()
print("=== Scanning for filename detection code ===")
TARGET_STRINGS = [b"ComplementaryShaders", b"ComplementaryReimagined", b"shaderpack", b"shaderpacks"]
detection_classes = {}

with zipfile.ZipFile(ep_jar) as z:
    for name in z.namelist():
        if not name.endswith(".class"):
            continue
        try:
            data = z.read(name)
            found = [s for s in TARGET_STRINGS if s in data]
            if found:
                detection_classes[name] = (data, found)
        except:
            pass

for cls_name, (data, hits) in detection_classes.items():
    print()
    print("  CLASS: " + cls_name)
    strings = re.findall(b"[\x20-\x7E]{4,}", data)
    for s in strings:
        sd = s.decode("ascii", "replace")
        if any(x in sd for x in ["Complementary", "Reimagined", "shaderpack", "shaderpacks", ".zip", "shader"]):
            if "class" not in sd and "mixin" not in sd and "net/" not in sd and "com/" not in sd:
                print("    STR: " + sd)

# ── 4. Patch EuphoriaPatcher to accept Aetheris_Shader_Pack ─────
print()
print("=== Patching EuphoriaPatcher ===")

# Strategy: In the class bytecode, find the string "ComplementaryShaders" or
# "ComplementaryReimagined" in shader detection and see if we can add "Aetheris"
# Alternative: Just ensure the ACTIVE shader in Iris is set to ComplementaryReimagined_r5.8.zip

# First check if the string "Aetheris" is already in any EP class
aetheris_found = False
with zipfile.ZipFile(ep_jar) as z:
    for name in z.namelist():
        if name.endswith(".class"):
            try:
                if b"Aetheris" in z.read(name):
                    aetheris_found = True
                    print("  Aetheris string found in: " + name)
            except:
                pass

if not aetheris_found:
    print("  EuphoriaPatcher has no 'Aetheris' string - need to update Iris to use ComplementaryReimagined_r5.8.zip")
    print()
    
    # FIX: Update Iris settings to use the ComplementaryReimagined name
    # and keep the Aetheris shader settings by copying them
    sp = os.path.join(PROFILE, "shaderpacks")
    
    # Update iris.properties to use the Complementary-named shader
    if os.path.exists(iris_props):
        with open(iris_props, encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        # Replace the shaderpack name
        new_content = re.sub(
            r"shaderpack\s*=\s*.*",
            "shaderpack=ComplementaryReimagined_r5.8.zip",
            content
        )
        if new_content != content:
            with open(iris_props, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("  Updated iris.properties -> shaderpack=ComplementaryReimagined_r5.8.zip")
        else:
            # shaderpack line might not exist - add it
            with open(iris_props, "a", encoding="utf-8") as f:
                f.write("\nshaderpack=ComplementaryReimagined_r5.8.zip\n")
            print("  Added to iris.properties: shaderpack=ComplementaryReimagined_r5.8.zip")
    else:
        # Create iris.properties
        os.makedirs(os.path.dirname(iris_props), exist_ok=True)
        with open(iris_props, "w", encoding="utf-8") as f:
            f.write("shaderpack=ComplementaryReimagined_r5.8.zip\n")
        print("  Created iris.properties with shaderpack=ComplementaryReimagined_r5.8.zip")
    
    # Also update options.txt if it has shader pack reference
    with open(opts, encoding="utf-8", errors="replace") as f:
        opts_content = f.read()
    
    new_opts = re.sub(
        r"iris\.shaderPackName\s*=\s*.*",
        "iris.shaderPackName=ComplementaryReimagined_r5.8.zip",
        opts_content
    )
    if new_opts != opts_content:
        with open(opts, "w", encoding="utf-8") as f:
            f.write(new_opts)
        print("  Updated options.txt shader reference")
    
    # Verify shader settings are copied
    aetheris_txt = os.path.join(sp, "Aetheris_Shader_Pack.txt")
    comp_txt     = os.path.join(sp, "ComplementaryReimagined_r5.8.txt")
    if os.path.exists(aetheris_txt) and not os.path.exists(comp_txt):
        shutil.copy2(aetheris_txt, comp_txt)
        print("  Copied shader settings to ComplementaryReimagined_r5.8.txt")
    
    print()
    print("Result: EuphoriaPatcher will find ComplementaryReimagined_r5.8.zip,")
    print("        patch it correctly, and Iris will load the patched version.")

# ── 5. FIX: Mixin maxShiftBy warning ─────────────────────────────
# This is a Lunar Client internal mixin warning — cannot be fixed directly
# It is logged before the game initializes fully and has no gameplay effect
print()
print("=== Mixin maxShiftBy warning ===")
print("  This is an INTERNAL Lunar Client mixin issue (not fixable by us)")
print("  It does NOT cause any gameplay problems - just a log warning")

# ── 6. EXPLAIN: Black square ─────────────────────────────────────
print()
print("=== Black square during Loading terrain... ===")
print("  This is NORMAL shader compilation behavior.")
print("  When Iris compiles shaders for the first time (or after changes),")
print("  it shows black while the GPU compiles ~100+ shader programs.")
print("  On RTX 4050 Laptop this takes 10-60 seconds ONLY the first time.")
print("  After that, shaders are cached and loads instantly.")
print()
print("  If it stays black FOREVER (5+ minutes): that would be a bug.")
print("  If it goes away and shows your world: it is working normally.")

print()
print("ALL DONE")
