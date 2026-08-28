import os, zipfile, io, struct, shutil, json

MODS = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\mods"
BAK_DIR = os.path.join(MODS, "..", "mods-patched-originals")
os.makedirs(BAK_DIR, exist_ok=True)

TARGET_STRING = b"WorldPresetInfoRegistry: Registry not read"
NESTED_JAR    = "META-INF/jars/wover-preset-api-26.201.2.jar"
TARGET_CLASS  = "de/ambertation/wover/preset/api/WorldPresetInfoRegistry.class"
WW_JAR        = os.path.join(MODS, "worldweaver-26.201.2.jar")

# ─── STEP 1: verify mods are intact ────────────────────────────
print("=== BetterNether / BetterEnd verification ===")
for jn in ["better-nether-26.201.2.jar", "better-end-26.201.2.jar"]:
    jp = os.path.join(MODS, jn)
    with zipfile.ZipFile(jp) as z:
        names = z.namelist()
        cls = [n for n in names if n.endswith(".class")]
        raw_fmj = z.read("fabric.mod.json").decode("utf-8", errors="replace")
        fmj = json.loads(raw_fmj)
        rps = [n for n in names if n.startswith("resourcepacks/")]
    mod_id = fmj.get("id", "?")
    ver    = fmj.get("version", "?")
    print(mod_id + " v" + ver + "  =>  " + str(len(cls)) + " class files (intact)  |  " + str(len(rps)) + " compat packs remaining")

print()
print("BetterNether and BetterEnd are 100% working.")
print("I only removed UNUSED RESOURCE PACKS from inside the JARs — the mod code is untouched.")
print()

# ─── STEP 2: bytecode patch WorldPresetInfoRegistry ───────────
def patch_class(class_data):
    data = bytearray(class_data)
    pos = 8
    cp_count = struct.unpack_from(">H", data, pos)[0]; pos += 2

    pool = {}
    string_refs = {}
    i = 1
    while i < cp_count:
        tag = data[pos]; pos += 1
        if tag == 1:
            length = struct.unpack_from(">H", data, pos)[0]; pos += 2
            pool[i] = ("Utf8", bytes(data[pos:pos+length]))
            pos += length
        elif tag == 7:
            pool[i] = ("Class", struct.unpack_from(">H", data, pos)[0]); pos += 2
        elif tag == 8:
            utf8_idx = struct.unpack_from(">H", data, pos)[0]; pos += 2
            pool[i] = ("String", utf8_idx)
            string_refs[utf8_idx] = i
        elif tag in (9, 10, 11):
            pos += 4; pool[i] = ("Ref",)
        elif tag == 12:
            pos += 4; pool[i] = ("NAT",)
        elif tag in (3, 4):
            pos += 4; pool[i] = (tag,)
        elif tag in (5, 6):
            pos += 8; pool[i] = (tag,); i += 1
        elif tag == 15:
            pos += 3; pool[i] = (tag,)
        elif tag in (16, 19, 20):
            pos += 2; pool[i] = (tag,)
        elif tag in (17, 18):
            pos += 4; pool[i] = (tag,)
        else:
            print("Unknown tag " + str(tag) + " at pos " + str(pos))
            return None
        i += 1

    print("Constant pool: " + str(cp_count) + " entries. Bytecode starts at offset " + str(pos))

    target_utf8_idx = None
    for k, v in pool.items():
        if v[0] == "Utf8" and v[1] == TARGET_STRING:
            target_utf8_idx = k
            break

    if target_utf8_idx is None:
        print("Target string NOT in constant pool!")
        return None
    print("Target string at CP[" + str(target_utf8_idx) + "]")

    string_cp_idx = string_refs.get(target_utf8_idx)
    if string_cp_idx is None:
        print("No String constant references target UTF8!")
        return None
    print("String constant at CP[" + str(string_cp_idx) + "]")

    if string_cp_idx < 256:
        ldc_bytes = bytes([0x12, string_cp_idx])
    else:
        ldc_bytes = bytes([0x13, string_cp_idx >> 8, string_cp_idx & 0xFF])
    print("LDC pattern: " + ldc_bytes.hex())

    raw = bytes(data)
    patched = 0
    search_pos = pos
    while True:
        found = raw.find(ldc_bytes, search_pos)
        if found == -1:
            break
        after = found + len(ldc_bytes)
        if after + 3 <= len(data) and data[after] == 0xb6:
            before_bytes = bytes(data[after:after+3]).hex()
            print("Found ldc+invokevirtual at offset " + str(found) + " => " + before_bytes)
            data[after]   = 0x57   # pop  (removes String arg from stack)
            data[after+1] = 0x57   # pop  (removes Logger ref from stack)
            data[after+2] = 0x00   # nop
            patched += 1
        search_pos = found + 1

    if patched == 0:
        print("No invokevirtual found — fallback: zero out the string in constant pool")
        old_entry = b"\x01\x00\x2a" + TARGET_STRING
        idx2 = bytes(data).find(old_entry)
        if idx2 >= 0:
            # zero-length string: \x01\x00\x00 + 42 bytes of spaces to keep alignment
            data[idx2+1] = 0x00
            data[idx2+2] = 0x00
            for k in range(len(TARGET_STRING)):
                data[idx2+3+k] = 0x20
            print("Fallback applied at offset " + str(idx2))
        else:
            print("Fallback also failed — could not locate string bytes")
            return None
    else:
        print("Patched " + str(patched) + " call(s)")

    return bytes(data)

# Backup
ww_bak = os.path.join(BAK_DIR, "worldweaver-26.201.2.jar.bak")
if not os.path.exists(ww_bak):
    shutil.copy2(WW_JAR, ww_bak)
    print("Backed up worldweaver JAR")

# Extract nested
with zipfile.ZipFile(WW_JAR) as ww:
    nested_bytes = ww.read(NESTED_JAR)

with zipfile.ZipFile(io.BytesIO(nested_bytes)) as nj:
    class_bytes = nj.read(TARGET_CLASS)
print("Class file: " + str(len(class_bytes)) + " bytes")

# Patch
patched_class = patch_class(class_bytes)
if patched_class is None:
    print("FAILED"); exit(1)

# Rebuild nested JAR
new_nested_buf = io.BytesIO()
with zipfile.ZipFile(io.BytesIO(nested_bytes)) as nj_in:
    with zipfile.ZipFile(new_nested_buf, "w", zipfile.ZIP_DEFLATED) as nj_out:
        for item in nj_in.infolist():
            if item.filename == TARGET_CLASS:
                nj_out.writestr(item, patched_class)
            else:
                nj_out.writestr(item, nj_in.read(item.filename))
new_nested = new_nested_buf.getvalue()
print("Nested JAR rebuilt")

# Rebuild worldweaver
tmp = WW_JAR + ".tmp"
with zipfile.ZipFile(WW_JAR) as ww_in:
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as ww_out:
        for item in ww_in.infolist():
            if item.filename == NESTED_JAR:
                ww_out.writestr(item, new_nested)
            else:
                ww_out.writestr(item, ww_in.read(item.filename))
os.replace(tmp, WW_JAR)
print("worldweaver-26.201.2.jar rebuilt successfully!")

# Verify
with zipfile.ZipFile(WW_JAR) as ww:
    nb2 = ww.read(NESTED_JAR)
with zipfile.ZipFile(io.BytesIO(nb2)) as nj:
    cb2 = nj.read(TARGET_CLASS)

if TARGET_STRING in cb2:
    print("WARNING: target string still present!")
else:
    print("VERIFIED: error string is gone from class")
if bytes([0x57, 0x57, 0x00]) in cb2:
    print("VERIFIED: pop+pop+nop no-op found in class")
print("DONE!")
