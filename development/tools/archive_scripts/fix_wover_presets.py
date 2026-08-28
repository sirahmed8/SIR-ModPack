"""
fix_wover_presets.py

WoVer bug: registers wover:large, wover:amplified etc. as world presets
but does NOT include the WorldPresetInfo JSON files for them.
Result: "Unbound values in registry [wover:large]" ERROR at world creation.

Fix: inject the missing JSON files into wover-preset-api.jar (inside worldweaver.jar).
"""
import zipfile, io, os

MODS_V  = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\mods"
MODS_B  = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\mods"
NESTED  = "META-INF/jars/wover-preset-api-26.201.2.jar"
JAR     = "worldweaver-26.201.2.jar"

# Missing preset info for wover:* presets.
# Path = data/{namespace}/wover/world_preset_info/{name}.json
# wover:large      -> data/wover/wover/world_preset_info/large.json
# wover:amplified  -> data/wover/wover/world_preset_info/amplified.json
PRESET_FILES = {
    "data/wover/wover/world_preset_info/large.json":
        '{\n  "sort_order": 3000\n}',
    "data/wover/wover/world_preset_info/amplified.json":
        '{\n  "end_preset": "minecraft:normal",\n  "nether_preset": "minecraft:normal",\n  "sort_order": 2000\n}',
    "data/wover/wover/world_preset_info/normal.json":
        '{}',
    "data/wover/wover/world_preset_info/single_biome_surface.json":
        '{\n  "end_preset": "minecraft:normal",\n  "nether_preset": "minecraft:normal",\n  "sort_order": 4000\n}',
}

def patch(jar_path):
    if not os.path.exists(jar_path):
        print("  SKIP (not found): " + jar_path)
        return

    # Read outer jar
    with zipfile.ZipFile(jar_path) as ww:
        if NESTED not in ww.namelist():
            print("  SKIP: nested jar not found")
            return
        nested_bytes = ww.read(NESTED)

    # Check which files are missing from nested jar
    with zipfile.ZipFile(io.BytesIO(nested_bytes)) as nj:
        existing = set(nj.namelist())

    to_add = {k: v for k, v in PRESET_FILES.items() if k not in existing}
    if not to_add:
        print("  already fully patched, nothing to add")
        return

    print("  Adding " + str(len(to_add)) + " missing preset info files:")
    for k in to_add:
        print("    " + k)

    # Rebuild nested jar
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(nested_bytes)) as ni:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as no:
            for it in ni.infolist():
                no.writestr(it, ni.read(it.filename))
            for path, content in to_add.items():
                no.writestr(path, content.encode("utf-8"))
    new_nested = buf.getvalue()

    # Rebuild outer jar
    tmp = jar_path + ".tmp"
    with zipfile.ZipFile(jar_path) as wi:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as wo:
            for it in wi.infolist():
                data = new_nested if it.filename == NESTED else wi.read(it.filename)
                wo.writestr(it, data)
    os.replace(tmp, jar_path)
    print("  Patched: " + jar_path)

print("=== Visual profile ===")
patch(os.path.join(MODS_V, JAR))
print()
print("=== Balanced profile ===")
patch(os.path.join(MODS_B, JAR))
print()
print("Done! wover:large / wover:amplified unbound errors fixed.")
