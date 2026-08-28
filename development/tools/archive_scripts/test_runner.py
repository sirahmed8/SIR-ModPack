import os, sys, zipfile, json, re, struct, io
from collections import defaultdict

print("="*75)
print("  MILESTONE 1: MOD JAR & BYTECODE HYGIENE EMPIRICAL ADVERSARIAL SUITE")
print("="*75)

# 1. Archive Corruption & Zero-Byte Scan
print("\n[TEST 1/5] Scanning all JAR and ZIP archives for corruption & zero-byte files...")
target_dirs = [
    r"D:\mods", r"D:\AetherisShare", r"D:\shader",
    r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances",
    r"C:\Users\a7med\.lunarclient\profiles",
    r"C:\Users\a7med\AppData\Roaming\.minecraft"
]
all_archives = []
for d in target_dirs:
    if not os.path.exists(d): continue
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith(".jar") or f.endswith(".zip"):
                all_archives.append(os.path.join(root, f))
all_archives = sorted(list(set(all_archives)))
print(f"Discovered {len(all_archives)} distinct archive files.")

corrupted_files, zero_byte_files, crc_error_files, empty_archives = [], [], [], []
for p in all_archives:
    try:
        sz = os.path.getsize(p)
        if sz == 0:
            zero_byte_files.append(p)
            continue
        with zipfile.ZipFile(p, "r") as zf:
            bad_file = zf.testzip()
            if bad_file:
                crc_error_files.append((p, bad_file))
            if len(zf.infolist()) == 0:
                empty_archives.append(p)
    except Exception as e:
        corrupted_files.append((p, str(e)))

print(f"  -> Zero-byte archives: {len(zero_byte_files)}")
print(f"  -> Corrupted headers / BadZipFile: {len(corrupted_files)}")
print(f"  -> CRC-32 integrity errors: {len(crc_error_files)}")
print(f"  -> Empty archives: {len(empty_archives)}")

# 2. Duplicate Mod IDs & Class Definition Conflicts Scan
print("\n[TEST 2/5] Scanning profiles for duplicate mod IDs and conflicting class definitions...")
profiles = [
    ("Master 26.2", r"D:\mods"),
    ("AetherisShare Modern Visual", r"D:\AetherisShare\profiles\visual\mods"),
    ("AetherisShare Modern Balanced", r"D:\AetherisShare\profiles\balanced\mods"),
    ("AetherisShare Modern Performance", r"D:\AetherisShare\profiles\performance\mods"),
    ("Lunar Modern Visual", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\mods"),
    ("Lunar Modern Balanced", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\mods"),
    ("Lunar Modern Performance", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\mods"),
    ("Lunar Modern Modpack", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\mods"),
    ("Prism 26.2", r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\mods"),
    ("Default .minecraft", r"C:\Users\a7med\AppData\Roaming\.minecraft\mods"),
    ("AetherisShare Legacy Visual", r"D:\AetherisShare\profiles\legacy-visual\mods"),
    ("AetherisShare Legacy Balanced", r"D:\AetherisShare\profiles\legacy-balanced\mods"),
    ("AetherisShare Legacy Performance", r"D:\AetherisShare\profiles\legacy-performance\mods"),
    ("AetherisShare Legacy Generic", r"D:\AetherisShare\profiles\legacy\mods"),
    ("Lunar Legacy Visual", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-visual-1.8.9\mods"),
    ("Lunar Legacy Balanced", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-balanced-1.8.9\mods"),
    ("Lunar Legacy Performance", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-performance-1.8.9\mods"),
    ("Lunar Legacy Generic", r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9\mods"),
    ("Prism 1.8.9", r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\minecraft\mods"),
    ("Prism Minecraft 1.8.9", r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\.minecraft\mods")
]

def get_mod_id(zf, filename):
    for entry in ["fabric.mod.json", "quilt.mod.json"]:
        if entry in zf.namelist():
            try:
                data = json.loads(zf.read(entry).decode("utf-8", errors="ignore"))
                return data.get("id") or data.get("modid")
            except Exception: pass
    if "mcmod.info" in zf.namelist():
        try:
            content = zf.read("mcmod.info").decode("utf-8", errors="ignore").strip()
            data = json.loads(content)
            if isinstance(data, list) and len(data) > 0 and "modid" in data[0]:
                return data[0]["modid"]
            elif isinstance(data, dict) and "modList" in data:
                return data["modList"][0].get("modid")
        except Exception: pass
    if "META-INF/mods.toml" in zf.namelist():
        try:
            content = zf.read("META-INF/mods.toml").decode("utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("modId") and "=" in line:
                    return line.split("=", 1)[1].strip().strip("\"'")
        except Exception: pass
    return None

def is_ignorable_library(cpath):
    prefixes = [
        "org/spongepowered/asm/", "org/objectweb/asm/", "com/google/gson/",
        "org/apache/", "com/electronwill/nightconfig/", "com/moandjiezana/toml/",
        "org/slf4j/", "net/fabricmc/tinyremapper/", "org/jetbrains/annotations/",
        "kotlin/", "org/intellij/", "javax/", "jakarta/", "com/typesafe/",
        "io/netty/", "com/google/common/", "it/unimi/dsi/fastutil/",
        "org/joml/", "org/antlr/", "org/reflections/", "javassist/",
        "com/github/bancodourado/", "org/bouncycastle/", "io/github/cottonmc/",
        "me/shedaniel/autoconfig/", "net/bytebuddy/", "com/mojang/brigadier/",
        "com/google/j2objc/", "com/google/errorprone/", "com/google/thirdparty/",
        "org/checkerframework/", "org/codehaus/", "net/jodah/typetools/",
        "org/dyn4j/", "net/objecthunter/exp4j/", "com/llamalad7/mixinextras/",
        "com/github/bsideup/jabel/", "net/neoforged/bus/"
    ]
    return any(cpath.startswith(p) for p in prefixes)

duplicate_id_reports = {}
class_conflict_reports = {}
for name, p_dir in profiles:
    if not os.path.exists(p_dir): continue
    jars = [os.path.join(p_dir, f) for f in os.listdir(p_dir) if f.endswith(".jar")]
    mod_id_to_jars = defaultdict(list)
    class_to_jars = defaultdict(list)
    for jar in jars:
        jname = os.path.basename(jar)
        try:
            with zipfile.ZipFile(jar, "r") as zf:
                mid = get_mod_id(zf, jname)
                if mid: mod_id_to_jars[mid].append(jname)
                for entry in zf.namelist():
                    if entry.endswith(".class"):
                        class_to_jars[entry].append(jname)
        except Exception: pass
    dup_mod_ids = {mid: j_list for mid, j_list in mod_id_to_jars.items() if len(j_list) > 1}
    if dup_mod_ids:
        duplicate_id_reports[name] = dup_mod_ids
    mod_class_conflicts = defaultdict(set)
    for cpath, j_list in class_to_jars.items():
        unique_jars = set(j_list)
        if len(unique_jars) > 1:
            if not is_ignorable_library(cpath):
                mod_class_conflicts[tuple(sorted(list(unique_jars)))].add(cpath)
    if mod_class_conflicts:
        class_conflict_reports[name] = mod_class_conflicts

print(f"  -> Profiles with duplicate Mod IDs: {len(duplicate_id_reports)}")
for p_name, dups in duplicate_id_reports.items():
    print(f"     [!] {p_name}:")
    for mid, j_list in dups.items():
        print(f"         - mod id {mid}: {j_list}")
print(f"  -> Profiles with mod-specific class definition conflicts: {len(class_conflict_reports)}")
for p_name, conflicts in class_conflict_reports.items():
    print(f"     [!] {p_name}:")
    for pair, clist in list(conflicts.items())[:5]:
        pair_str = f"{pair[0]} vs {pair[1]}" if len(pair) > 1 else pair[0]
        print(f"         - JAR pair: {pair_str} ({len(clist)} classes, sample: {list(clist)[0]})")

# 3. OPAC JAR & Mod JSON / Metadata Validation
print("\n[TEST 3/5] Validating OPAC JARs and mod JSON files...")
opac_jars = sorted(list(set([p for p in all_archives if "open-parties-and-claims" in os.path.basename(p).lower() or "opac" in os.path.basename(p).lower()])))
print(f"Found {len(opac_jars)} OPAC JAR files across the ecosystem.")
opac_json_errors = []
opac_inspected_files = 0
for ojar in opac_jars:
    try:
        with zipfile.ZipFile(ojar, "r") as zf:
            for item in zf.namelist():
                if item.endswith(".json") or item.endswith(".mcmeta") or item.endswith(".json5"):
                    opac_inspected_files += 1
                    content = zf.read(item).decode("utf-8", errors="replace")
                    if item.endswith(".json5"):
                        content = re.sub(r"//.*?$|/\*.*?\*/", "", content, flags=re.S|re.M)
                    try:
                        json.loads(content)
                    except json.JSONDecodeError as jde:
                        opac_json_errors.append((ojar, item, str(jde)))
            if "fabric.mod.json" in zf.namelist():
                fmj = json.loads(zf.read("fabric.mod.json").decode("utf-8", errors="replace"))
                if "id" not in fmj or "version" not in fmj:
                    opac_json_errors.append((ojar, "fabric.mod.json", "Missing id or version field"))
    except Exception as ex:
        opac_json_errors.append((ojar, "JAR_READ", str(ex)))
print(f"  -> Total OPAC JSON files validated: {opac_inspected_files} across {len(opac_jars)} JARs")
print(f"  -> OPAC JSON syntax & schema errors: {len(opac_json_errors)}")
for ojar, item, err in opac_json_errors:
    print(f"     [!] {os.path.basename(ojar)} -> {item}: {err}")

# 4. Shaderpack block.properties AST & Syntax Parsing
print("\n[TEST 4/5] Parsing and validating block.properties across all shader packs...")
shader_dirs = [
    r"D:\mods\shader", r"D:\shader", r"D:\AetherisShare\shaders",
    r"D:\AetherisShare\profiles\visual\shaderpacks",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\shaderpacks",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-visual-1.8.9\shaderpacks"
]
all_shader_zips = sorted(list(set([os.path.join(root, f) for sd in shader_dirs if os.path.exists(sd) for root, dirs, files in os.walk(sd) for f in files if f.endswith(".zip")])))
print(f"Discovered {len(all_shader_zips)} shader pack archives.")
class BlockPropertiesASTParser:
    def __init__(self, content, source_name):
        self.content = content; self.source_name = source_name; self.ast = []; self.errors = []
    def parse(self):
        lines = self.content.splitlines()
        for idx, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"): continue
            if "=" not in line:
                self.errors.append((idx, line, "Missing assignment operator (=)")); continue
            parts = line.split("=", 1)
            key = parts[0].strip(); value = parts[1].strip()
            if not key.startswith("block."):
                self.errors.append((idx, line, f"Invalid key prefix: {key}")); continue
            tokens = value.split()
            for tok in tokens:
                if tok.count("[") != tok.count("]"):
                    self.errors.append((idx, line, f"Unmatched bracket in token: {tok}"))
                if tok.count("(") != tok.count(")"):
                    self.errors.append((idx, line, f"Unmatched parenthesis in token: {tok}"))
            self.ast.append({"line": idx, "key": key, "tokens": len(tokens)})
        return len(self.errors) == 0
shader_prop_results = []
for szip in all_shader_zips:
    try:
        with zipfile.ZipFile(szip, "r") as zf:
            for name in zf.namelist():
                if name.endswith("block.properties"):
                    content = zf.read(name).decode("utf-8", errors="replace")
                    parser = BlockPropertiesASTParser(content, f"{os.path.basename(szip)}::{name}")
                    parser.parse()
                    shader_prop_results.append({"archive": szip, "entry": name, "rules": len(parser.ast), "errors": parser.errors})
    except Exception as e:
        shader_prop_results.append({"archive": szip, "entry": "N/A", "rules": 0, "errors": [(-1, "", str(e))]})
print(f"  -> Tested {len(shader_prop_results)} block.properties files across shader packs.")
total_shader_ast_errors = 0
for res in shader_prop_results:
    err_count = len(res["errors"])
    total_shader_ast_errors += err_count
    bname = os.path.basename(res["archive"]); entry_name = res["entry"]; rcount = res["rules"]
    if err_count > 0:
        print(f"     [!] {bname} ({entry_name}): {err_count} AST syntax errors")
        for lnum, ltxt, msg in res["errors"][:3]:
            print(f"         Line {lnum}: {msg} | Text: {ltxt[:50]}")
    else:
        print(f"     [OK] {bname} ({entry_name}) -> {rcount} AST rules valid.")
print(f"  -> Total block.properties AST errors: {total_shader_ast_errors}")

# 5. Aetheris_Modpack_Legacy_1.8.9.zip Forensic & Bytecode Deep Dive
print("\n[TEST 5/5] Forensic and bytecode deep dive on Aetheris_Modpack_Legacy_1.8.9.zip...")
legacy_zip_path = r"D:\mods\Aetheris_Modpack_Legacy_1.8.9.zip"
if not os.path.exists(legacy_zip_path):
    print(f"[ERROR] {legacy_zip_path} does not exist!")
else:
    print(f"Archive size: {os.path.getsize(legacy_zip_path)} bytes")
    hidden_files, corrupted_entries, root_entries, nested_jars = [], [], set(), []
    with zipfile.ZipFile(legacy_zip_path, "r") as zf:
        bad = zf.testzip()
        if bad: corrupted_entries.append(bad)
        for info in zf.infolist():
            fname = info.filename; parts = fname.split("/")
            root_entries.add(parts[0])
            if any(part.startswith(".") and part not in [".", "..", ".minecraft"] for part in parts) or "Thumbs.db" in fname or "__MACOSX" in fname:
                hidden_files.append(fname)
            if fname.endswith(".jar"): nested_jars.append(fname)
    print(f"  -> Root directories/entries: {root_entries}")
    print(f"  -> Hidden / OS junk files: {len(hidden_files)}")
    print(f"  -> Corrupted zip entries: {len(corrupted_entries)}")
    print(f"  -> Contained mod JARs: {len(nested_jars)}")
    incompatible_jars, cross_version_classes, manifest_errors, total_classes_checked = [], [], [], 0
    with zipfile.ZipFile(legacy_zip_path, "r") as zf:
        for jname in nested_jars:
            jbytes = zf.read(jname); jbase = os.path.basename(jname)
            if any(banned in jbase for banned in ["1.10.2", "1.12.2", "MC1.8.8", "Baubles-1.10.2", "IGCM_v1.12.2", "ResourceLoader-MC1.8.8"]):
                incompatible_jars.append(jbase)
            try:
                with zipfile.ZipFile(io.BytesIO(jbytes), "r") as nzf:
                    if "mcmod.info" in nzf.namelist():
                        try:
                            json.loads(nzf.read("mcmod.info").decode("utf-8", errors="replace").strip())
                        except Exception as jerr: manifest_errors.append((jbase, "mcmod.info", str(jerr)))
                    for centry in nzf.namelist():
                        if centry.endswith(".class"):
                            total_classes_checked += 1
                            cdata = nzf.read(centry)
                            if len(cdata) >= 8:
                                magic, minor, major = struct.unpack(">IHH", cdata[:8])
                                if magic == 0xCAFEBABE and major > 52:
                                    cross_version_classes.append((jbase, centry, major))
            except Exception as jex:
                corrupted_entries.append(f"{jbase}: {jex}")
    print(f"  -> Total bytecode .class files checked: {total_classes_checked} across {len(nested_jars)} JARs")
    print(f"  -> Incompatible legacy mod JARs (e.g. 1.10/1.12): {len(incompatible_jars)}")
    for ij in incompatible_jars:
        print(f"     [!] Incompatible JAR detected: {ij}")
    print(f"  -> Cross-version class files (> Java 8 / major > 52): {len(cross_version_classes)}")
    for jb, ce, mj in cross_version_classes[:5]:
        print(f"     [!] Class major {mj} in {jb} :: {ce}")
    print(f"  -> Manifest / mcmod.info errors: {len(manifest_errors)}")
    for jb, mf, err in manifest_errors:
        print(f"     [!] {jb} :: {mf} -> {err}")

print("\n" + "="*75)
print("  ADVERSARIAL VERIFICATION SUITE EXECUTION SUMMARY")
print("="*75)
print(f"1. Corrupted / Zero-byte Archives: {len(corrupted_files) + len(zero_byte_files) + len(crc_error_files)}")
print(f"2. Duplicate Mod IDs in active profiles: {len(duplicate_id_reports)}")
print(f"3. OPAC JSON / Schema Errors: {len(opac_json_errors)}")
print(f"4. Shader block.properties AST Errors: {total_shader_ast_errors}")
print(f"5. Legacy 1.8.9 Modpack Defects: {len(hidden_files) + len(corrupted_entries) + len(incompatible_jars) + len(cross_version_classes)}")
print("="*75)

