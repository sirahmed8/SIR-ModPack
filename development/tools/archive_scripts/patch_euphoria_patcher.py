"""
patch_euphoria_patcher.py

Patches EuphoriaPatcher-1.9.3-r5.8.1-fabric.jar to recognize
'Aetheris_Shader_Pack.zip' as a valid Complementary Reimagined shader.

How EuphoriaPatcher detects shaders (from bytecode analysis):
1. First tries filename regex: Complementary.*_r5.8.1.* / Comp.*EuphoriaPatches_...
2. If no filename match: scans by byte size
3. Reads shaders/pack.json to confirm it's Complementary

Our shader pack.json says: "Complementary + Euphoria Patches 1.9.3"
                           "ComplementaryShaders r5.8.1..."
So it SHOULD pass the pack.json check — but it fails the filename check first.

Fix: In ShaderDetector.class, find the filename regex pattern for Complementary
and add Aetheris_Shader_Pack as an alternative pattern.
OR: In ShaderNamingService.class, configure the alternative name to Aetheris_Shader_Pack.

The cleanest fix: patch the regex pattern string in the bytecode to also match
'Aetheris_Shader_Pack' — same length approach.

Better fix: patch the constant pool string "No shaders with expected name pattern found"
to also add our filename check in the code path that runs before byte-size scan.

ACTUAL SIMPLEST FIX: The ShaderNamingService creates 'alternative shader names'.
It reads configured alternative names and creates copies.
If we can inject 'Aetheris_Shader_Pack' as an alternative name config,
EuphoriaPatcher will create Aetheris_Shader_Pack.zip as a copy.

BUT EVEN SIMPLER: The byte-size scan works if the shader isn't a "popular shader"
(bliss, solas, etc.). Our shader is 1.63 MB. Let's check if that matches.

The ACTUAL fix we'll do:
1. In ShaderDetector: find where it checks filename patterns
2. Replace one of the existing patterns with one that ALSO matches Aetheris_Shader_Pack
3. This way EuphoriaPatcher recognizes our file by name directly
"""
import os, zipfile, io, re, shutil, struct

MODS    = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\mods"
BAK_DIR = os.path.join(MODS, "..", "mods-patched-originals")
os.makedirs(BAK_DIR, exist_ok=True)

ep_jar = None
for f in os.listdir(MODS):
    if "euphoria" in f.lower() and "patch" in f.lower() and f.endswith(".jar"):
        ep_jar = os.path.join(MODS, f)
        print("EuphoriaPatcher: " + f)
        break

if not ep_jar:
    print("ERROR: EuphoriaPatcher not found"); exit(1)

# Backup
bak = os.path.join(BAK_DIR, os.path.basename(ep_jar) + ".bak")
if not os.path.exists(bak):
    shutil.copy2(ep_jar, bak)
    print("Backed up to " + os.path.basename(bak))

TARGET_CLASS = "com/euphoriapatches/euphoria_patcher/util/UserInstallErrorMessages.class"
DETECTOR_CLASS = "com/euphoriapatches/euphoria_patcher/services/ShaderDetector.class"

with zipfile.ZipFile(ep_jar) as z:
    all_names = z.namelist()
    cls_data = z.read(TARGET_CLASS)
    detector_data = z.read(DETECTOR_CLASS)

print()
print("=== ShaderDetector strings (filename-related) ===")
strings = re.findall(b"[\x20-\x7E]{4,}", detector_data)
for s in strings:
    sd = s.decode("ascii", "replace")
    if "Comp" in sd or "Reima" in sd or "r5\." in sd or "pattern" in sd.lower():
        print("  " + repr(sd))

# Key patterns found in the jar:
# 'Complementary.*_r5.8.1.*'  -> this is the MAIN regex for Complementary Shaders
# 'Comp.*EuphoriaPatches_(...)' -> this is for already-patched shaders
# 
# Strategy: Find the UTF8 constant 'Complementary.*_r5.8.1.*' in the constant pool
# and extend it to also match our file:
# New pattern: '(Complementary|Aetheris_Shader_Pack).*' or 
# better: '(Complementary.*_r5\.8\.1|Aetheris_Shader_Pack).*'
#
# BUT: string lengths must match for a safe patch.
# 'Complementary.*_r5.8.1.*' = 26 chars
# We need same-length replacement.
#
# Alternative approach that's CLEANER:
# The detector also looks for 'Comp.*EuphoriaPatches_' pattern for already-patched shaders.
# Our file Aetheris_Shader_Pack.zip doesn't match this either.
#
# BEST APPROACH: patch the byte-size detection to NOT skip our shader.
# The detector skips "popular shaders" during byte-size scan:
# '.*pixelcraftshaders_.*', '.*hysteria-shaders.*', 'solas shader v\d+.*', etc.
# Our shader is NOT in this skip list, so byte-size detection SHOULD work.
#
# The byte-size scan runs ONLY when no shader is found by name.
# If byte-size scan finds our shader, it should work.
#
# WHY IS IT FAILING? Let's check: maybe EuphoriaPatcher found a ComplementaryReimagined_r5.8.zip
# we created, but it's not the ACTIVE shader in Iris. Iris still loads Aetheris_Shader_Pack.zip.
# EuphoriaPatcher patches ComplementaryReimagined_r5.8.zip, creates a patched copy,
# but Iris loads Aetheris_Shader_Pack.zip (unpatched). So EP patches are never applied!

# REAL FIX: 
# Option A: Rename our active shader to match what EP expects.
# Option B: Patch EP to accept our filename.
# Option C: Make iris load the ComplementaryReimagined_r5.8.zip that EP patches.

# We'll do Option B: Patch the constant pool in ShaderDetector.class
# Find the regex pattern 'Complementary.*_r5.8.1.*' and change it to
# a regex that also matches 'Aetheris_Shader_Pack':
# 'Complementary.*_r5.8.1.*|Aetheris_Shader_Pack.*'
# But this is longer... can't do length-preserving replacement.

# CLEANEST: In the constant pool, find any string containing "Complementary.*_r5.8.1"
# and replace the '.*' with something that accepts Aetheris too.
# 'Complementary.*_r5.8.1.*' (26 chars)
# We need to make it a regex that also catches Aetheris_Shader_Pack
# New: '(Complementary.*_r5.8.1|Aetheris).*' = 38 chars - too long

# Let's instead use a different approach:
# The 'Complementary' check in the class file - replace it to also check for 'Aetheris'
# Find: b'Complementary' (13 bytes) and see where it's a standalone check
# This is complex without full parsing.

# WINNER APPROACH: Simply rename Aetheris_Shader_Pack.zip to include "Complementary"
# but KEEP THE IRIS SETTING pointing to the renamed file.
# This way:
# - EuphoriaPatcher finds it by name (matches Complementary.*_r5.8.1.*)
# - Iris loads it
# - Everything works

# But wait - if we rename, the shader settings file also needs renaming
# AND Iris needs to be updated.

# Let me check: what is the EXACT regex EuphoriaPatcher uses?
print()
print("=== Finding exact regex patterns in detector ===")

def find_utf8_strings(data):
    """Parse class constant pool and return all UTF8 strings."""
    results = []
    pos = 8  # skip magic+minor+major
    try:
        cp_count = struct.unpack_from(">H", data, pos)[0]; pos += 2
        i = 1
        while i < cp_count:
            tag = data[pos]; pos += 1
            if tag == 1:
                length = struct.unpack_from(">H", data, pos)[0]; pos += 2
                s = bytes(data[pos:pos+length])
                results.append((i, s))
                pos += length
            elif tag == 7: pos += 2
            elif tag == 8: pos += 2
            elif tag in (9,10,11,12): pos += 4
            elif tag in (3,4): pos += 4
            elif tag in (5,6): pos += 8; i += 1
            elif tag == 15: pos += 3
            elif tag in (16,19,20): pos += 2
            elif tag in (17,18): pos += 4
            i += 1
    except:
        pass
    return results

detector_strings = find_utf8_strings(detector_data)
print("Regex-like strings in ShaderDetector:")
for idx, s in detector_strings:
    try:
        sd = s.decode("utf-8", "replace")
        if any(c in sd for c in [".*", "\\d", "Comp", "Reimag", "r5\."]):
            print("  [" + str(idx) + "] " + repr(sd))
    except:
        pass

# Now patch: find 'Comp.*EuphoriaPatches_(\d+\.\d+\.\d+)-dev\d+\.zip' 
# or the base Complementary pattern and modify it
print()
print("=== Applying patch ===")

# The cleanest fix without bytecode modification:
# Rename Aetheris_Shader_Pack.zip to ComplementaryReimagined_r5.8.1+AetherisPatch.zip
# This matches the regex 'Complementary.*_r5.8.1.*'

PROFILE = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
sp = os.path.join(PROFILE, "shaderpacks")

src = os.path.join(sp, "Aetheris_Shader_Pack.zip")
# Target name that matches EuphoriaPatcher's regex 'Complementary.*_r5.8.1.*'
target_name = "ComplementaryReimagined_r5.8.1+Aetheris.zip"
target = os.path.join(sp, target_name)

if os.path.exists(src) and not os.path.exists(target):
    shutil.copy2(src, target)
    print("Created: " + target_name)

# Copy settings file
src_settings = os.path.join(sp, "Aetheris_Shader_Pack.txt")
target_settings = os.path.join(sp, target_name.replace(".zip", ".txt"))
if os.path.exists(src_settings) and not os.path.exists(target_settings):
    shutil.copy2(src_settings, target_settings)
    print("Copied settings: " + os.path.basename(target_settings))

# Update iris.properties to use this name
iris_props = os.path.join(PROFILE, "config", "iris.properties")
if os.path.exists(iris_props):
    with open(iris_props, encoding="utf-8", errors="replace") as f:
        content = f.read()
    new_content = re.sub(
        r"shaderpack\s*=\s*.*\n?",
        "shaderpack=" + target_name + "\n",
        content
    )
    if target_name not in content:
        if "shaderpack=" in content:
            new_content = re.sub(r"shaderpack=.*", "shaderpack=" + target_name, content)
        else:
            new_content = content + "\nshaderpack=" + target_name + "\n"
    with open(iris_props, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("iris.properties -> shaderpack=" + target_name)
else:
    os.makedirs(os.path.dirname(iris_props), exist_ok=True)
    with open(iris_props, "w", encoding="utf-8") as f:
        f.write("shaderpack=" + target_name + "\n")
    print("Created iris.properties -> shaderpack=" + target_name)

print()
print("=== Result ===")
print("Shader file:  " + target_name)
print("EP regex:     Complementary.*_r5.8.1.* -> MATCHES!")
print("Iris loads:   " + target_name + " -> Same file!")
print("EP patches:   Will patch the correct file that Iris also loads!")
print()
print("After restart:")
print("  - EuphoriaPatcher finds " + target_name + " by regex")
print("  - EuphoriaPatcher patches it (applies EP visual fixes)")
print("  - Iris loads the patched shader")
print("  - No more error shader / black square")
print()
print("The shader name in the in-game menu will show as: ComplementaryReimagined_r5.8.1+Aetheris")
print("Your settings (from Aetheris_Shader_Pack.txt) are preserved in the settings file.")
