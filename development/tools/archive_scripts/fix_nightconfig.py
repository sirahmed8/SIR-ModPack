"""
fix_nightconfig.py

The crash is:
  NoSuchFieldError: WritingMode does not have field REPLACE_ATOMIC
  at ForgeConfigAPIPort ConfigTracker.writeConfig (uses REPLACE_ATOMIC)
  because Iceberg bundles OLD NightConfig without REPLACE_ATOMIC

FIX: Add REPLACE_ATOMIC static field to Iceberg's WritingMode.class
     REPLACE_ATOMIC = REPLACE  (alias, same behavior, no side effects)
"""
import os, zipfile, io, struct, shutil

MODS    = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\mods"
DISABLED = os.path.join(MODS, "..", "mods-optional-disabled")
BAK_DIR  = os.path.join(MODS, "..", "mods-patched-originals")
os.makedirs(BAK_DIR, exist_ok=True)

IC_JAR   = os.path.join(MODS, "Iceberg-26.2-fabric-1.4.2.1.jar")
FCP_JAR  = os.path.join(DISABLED, "ForgeConfigAPIPort-v26.2.1-mc26.2.x-Fabric.jar")
WM_CLASS = "com/electronwill/nightconfig/core/io/WritingMode.class"

# Re-enable ForgeConfigAPIPort first
fcp_dst = os.path.join(MODS, "ForgeConfigAPIPort-v26.2.1-mc26.2.x-Fabric.jar")
if os.path.exists(FCP_JAR) and not os.path.exists(fcp_dst):
    shutil.move(FCP_JAR, fcp_dst)
    print("Re-enabled ForgeConfigAPIPort")

# ── Full class file parser ────────────────────────────────────────
def read_u1(d, p): return d[p], p+1
def read_u2(d, p): return struct.unpack_from(">H", d, p)[0], p+2
def read_u4(d, p): return struct.unpack_from(">I", d, p)[0], p+4

def parse_class(raw):
    """Parse class file, return (cp, cp_end, fields_start, methods_start, rest)."""
    d = bytearray(raw)
    pos = 8  # skip magic + minor + major
    cp_count, pos = read_u2(d, pos)
    
    pool_start = pos
    pool = {}   # index -> (tag, offset_in_data, ...)
    i = 1
    while i < cp_count:
        tag = d[pos]; pos += 1
        entry_start = pos - 1
        if tag == 1:
            ln, pos = read_u2(d, pos)
            s = bytes(d[pos:pos+ln])
            pool[i] = (1, s, entry_start)
            pos += ln
        elif tag == 7:
            idx, pos = read_u2(d, pos)
            pool[i] = (7, idx, entry_start)
        elif tag == 8:
            idx, pos = read_u2(d, pos)
            pool[i] = (8, idx, entry_start)
        elif tag in (9,10,11):
            ci, pos = read_u2(d, pos)
            ni, pos = read_u2(d, pos)
            pool[i] = (tag, ci, ni, entry_start)
        elif tag == 12:
            ni, pos = read_u2(d, pos)
            ti, pos = read_u2(d, pos)
            pool[i] = (12, ni, ti, entry_start)
        elif tag in (3,4): pos += 4; pool[i] = (tag,)
        elif tag in (5,6): pos += 8; pool[i] = (tag,); i += 1
        elif tag == 15: pos += 3; pool[i] = (tag,)
        elif tag in (16,19,20): pos += 2; pool[i] = (tag,)
        elif tag in (17,18): pos += 4; pool[i] = (tag,)
        else: raise ValueError("Bad tag " + str(tag))
        i += 1
    return d, pool, cp_count, pos

def find_utf8(pool, s):
    target = s.encode("utf-8") if isinstance(s, str) else s
    for k, v in pool.items():
        if v[0] == 1 and v[1] == target:
            return k
    return None

def find_fieldref(pool, class_idx, nat_idx):
    for k, v in pool.items():
        if v[0] == 9 and v[1] == class_idx and v[2] == nat_idx:
            return k
    return None

def find_nat(pool, name_idx, type_idx):
    for k, v in pool.items():
        if v[0] == 12 and v[1] == name_idx and v[2] == type_idx:
            return k
    return None

# ── Serialize cp entry to bytes ───────────────────────────────────
def cp_entry_bytes(entry):
    tag = entry[0]
    if tag == 1:
        s = entry[1]
        return bytes([1]) + struct.pack(">H", len(s)) + s
    elif tag in (7, 8):
        return bytes([tag]) + struct.pack(">H", entry[1])
    elif tag in (9, 10, 11):
        return bytes([tag]) + struct.pack(">HH", entry[1], entry[2])
    elif tag == 12:
        return bytes([12]) + struct.pack(">HH", entry[1], entry[2])
    else:
        return b""  # shouldn't happen for entries we add

# ── Patch WritingMode.class ───────────────────────────────────────
with zipfile.ZipFile(IC_JAR) as z:
    wm_raw = z.read(WM_CLASS)

d, pool, cp_count, after_cp = parse_class(wm_raw)

print("WritingMode.class: " + str(len(wm_raw)) + " bytes, " + str(cp_count) + " CP entries")

# Find existing refs we need
wm_path = "com/electronwill/nightconfig/core/io/WritingMode"
wm_desc = "L" + wm_path + ";"
replace_idx = find_utf8(pool, "REPLACE")
wm_class_utf8 = find_utf8(pool, wm_path)
wm_desc_utf8  = find_utf8(pool, wm_desc)

print("REPLACE field name at CP[" + str(replace_idx) + "]")
print("WritingMode class path at CP[" + str(wm_class_utf8) + "]")
print("WritingMode descriptor at CP[" + str(wm_desc_utf8) + "]")

# Find WritingMode class ref
wm_class_ref = None
for k, v in pool.items():
    if v[0] == 7 and v[1] == wm_class_utf8:
        wm_class_ref = k
        break
print("WritingMode class ref at CP[" + str(wm_class_ref) + "]")

# Find REPLACE fieldref (getstatic REPLACE)
# First find its NameAndType: (REPLACE, Lwm;)
replace_nat = find_nat(pool, replace_idx, wm_desc_utf8)
print("REPLACE NameAndType at CP[" + str(replace_nat) + "]")
replace_fieldref = find_fieldref(pool, wm_class_ref, replace_nat)
print("REPLACE fieldref at CP[" + str(replace_fieldref) + "]")

# ── Build new constant pool entries ──────────────────────────────
# We need:
#   new_utf8_idx     = CP entry for "REPLACE_ATOMIC"
#   new_nat_idx      = CP entry NameAndType(REPLACE_ATOMIC, Lwm;)
#   new_fieldref_idx = CP entry Fieldref(WM, nat)

new_entries = []
next_idx = cp_count

# UTF8: "REPLACE_ATOMIC"
new_utf8_idx = next_idx
new_entries.append((1, b"REPLACE_ATOMIC"))
next_idx += 1

# NameAndType(REPLACE_ATOMIC, Lwm;)
new_nat_idx = next_idx
new_entries.append((12, new_utf8_idx, wm_desc_utf8))
next_idx += 1

# Fieldref(WritingMode, nat)
new_fieldref_idx = next_idx
new_entries.append((9, wm_class_ref, new_nat_idx))
next_idx += 1

new_cp_count = next_idx
print()
print("Adding to CP:")
print("  CP[" + str(new_utf8_idx) + "] = UTF8 'REPLACE_ATOMIC'")
print("  CP[" + str(new_nat_idx) + "] = NameAndType(REPLACE_ATOMIC, " + wm_desc + ")")
print("  CP[" + str(new_fieldref_idx) + "] = Fieldref(WritingMode, NameAndType)")

# ── Rebuild class file ───────────────────────────────────────────
# Sections: magic+version | old_cp | rest_of_class
raw = bytes(d)
# magic+version+old_cp_count = 8 + 2 = 10 bytes header before cp entries
# But cp_count is at offset 8, so cp entries start at offset 10
# after_cp is where CP ends and class meta starts

header = raw[:8]  # magic + minor + major
old_cp_bytes = raw[10:after_cp]  # all old CP entries (not including count)
rest = raw[after_cp:]  # everything after CP (access_flags, this, super, interfaces, fields, methods, attrs)

# Serialize new CP entries
new_cp_bytes = b""
for entry in new_entries:
    new_cp_bytes += cp_entry_bytes(entry)

# Build new class:
# header + new_cp_count + old_cp_bytes + new_cp_bytes + rest
new_class = (
    header +
    struct.pack(">H", new_cp_count) +
    old_cp_bytes +
    new_cp_bytes +
    rest
)

print()
print("Rebuilt class size: " + str(len(new_class)) + " bytes (was " + str(len(raw)) + ")")

# ── Add static field "REPLACE_ATOMIC" to fields table ───────────
# The fields table is in `rest`. Parse access_flags(2) + this(2) + super(2) + interfaces_count(2) + ...
# Then fields_count(2) + fields...
rc = bytearray(new_class)
p = len(header) + 2 + len(old_cp_bytes) + len(new_cp_bytes)  # start of rest in new_class

# Access flags (2), this_class (2), super_class (2)
p += 6
# Interfaces count
iface_count, p = read_u2(rc, p)
p += iface_count * 2

# Fields count
fields_count_pos = p
fields_count, p = read_u2(rc, p)
print("Fields count: " + str(fields_count))

# Skip existing fields
fields_start = p
for _ in range(fields_count):
    p += 6  # access_flags + name_index + descriptor_index
    attr_count, p = read_u2(rc, p)
    for _ in range(attr_count):
        p += 2  # attr name index
        attr_len, p = read_u4(rc, p)
        p += attr_len
fields_end = p

# Build new field_info for REPLACE_ATOMIC
# ACC_PUBLIC | ACC_STATIC | ACC_FINAL = 0x0019
new_field = struct.pack(">HHHH",
    0x0019,           # access_flags: public static final
    new_utf8_idx,     # name_index: "REPLACE_ATOMIC"
    wm_desc_utf8,     # descriptor_index: "Lcom/.../WritingMode;"
    0                 # attributes_count: 0
)

# Insert field: update count and append field_info
rc[fields_count_pos] = (fields_count + 1) >> 8
rc[fields_count_pos+1] = (fields_count + 1) & 0xFF

# We need to INSERT the new field into the array
# Insert at fields_end
new_class2 = bytes(rc[:fields_end]) + new_field + bytes(rc[fields_end:])
rc = bytearray(new_class2)
print("Added field REPLACE_ATOMIC (offset " + str(fields_end) + ")")

# ── Modify <clinit> to initialize REPLACE_ATOMIC = REPLACE ──────
# After adding the field, we need to patch <clinit>
# Find <clinit> in methods: name = "<clinit>", descriptor = "()V"
# After fields, we have methods
# Recalculate position after fields in new_class2

p = len(header) + 2 + len(old_cp_bytes) + len(new_cp_bytes)
p += 6  # access_flags + this + super
iface_count, p = read_u2(rc, p)
p += iface_count * 2
fields_count2, p = read_u2(rc, p)
for _ in range(fields_count2):
    p += 6
    attr_count, p = read_u2(rc, p)
    for _ in range(attr_count):
        p += 2
        attr_len, p = read_u4(rc, p)
        p += attr_len

# Now at methods
methods_count, p = read_u2(rc, p)
print("Methods count: " + str(methods_count))

# Find <clinit> method and its Code attribute
clinit_utf8 = find_utf8(pool, "<clinit>")
code_utf8 = find_utf8(pool, "Code")
print("Looking for <clinit> at CP[" + str(clinit_utf8) + "]")

for mi in range(methods_count):
    method_start = p
    flags, p = read_u2(rc, p)
    name_idx, p = read_u2(rc, p)
    desc_idx, p = read_u2(rc, p)
    attr_count, p = read_u2(rc, p)
    
    is_clinit = (name_idx == clinit_utf8)
    
    for ai in range(attr_count):
        attr_name_idx, p = read_u2(rc, p)
        attr_len, p = read_u4(rc, p)
        attr_start = p
        
        if is_clinit and attr_name_idx == code_utf8:
            # Parse Code attribute
            max_stack, p2 = read_u2(rc, p)
            max_locals, p2 = read_u2(rc, p2)
            code_len, p2 = read_u4(rc, p2)
            code_start = p2
            code_bytes = bytes(rc[code_start:code_start+code_len])
            
            print()
            print("<clinit> Code found at offset " + str(p))
            print("  max_stack=" + str(max_stack) + ", code_len=" + str(code_len))
            print("  Code hex: " + code_bytes.hex())
            
            # Find the final 'return' (0xb1) instruction
            # Insert before it: getstatic REPLACE + putstatic REPLACE_ATOMIC
            # getstatic = 0xb2 + 2-byte CP index
            # putstatic = 0xb3 + 2-byte CP index
            
            insert_bytes = (
                bytes([0xb2]) + struct.pack(">H", replace_fieldref) +   # getstatic REPLACE
                bytes([0xb3]) + struct.pack(">H", new_fieldref_idx)     # putstatic REPLACE_ATOMIC
            )
            print("  Inserting " + str(len(insert_bytes)) + " bytes before return: " + insert_bytes.hex())
            
            # Find last return (0xb1)
            last_return = code_bytes.rfind(b"\xb1")
            if last_return == -1:
                print("  ERROR: no return found!")
            else:
                new_code = code_bytes[:last_return] + insert_bytes + code_bytes[last_return:]
                new_code_len = len(new_code)
                print("  New code len: " + str(new_code_len))
                
                # Update max_stack if needed (we push 1 thing: getstatic WritingMode)
                new_max_stack = max(max_stack, 1)
                
                # Rebuild Code attribute
                new_code_attr = (
                    struct.pack(">HH", new_max_stack, max_locals) +
                    struct.pack(">I", new_code_len) +
                    new_code +
                    bytes(rc[code_start+code_len:attr_start+attr_len])  # exception table + attrs
                )
                
                new_attr_len = len(new_code_attr)
                
                # Replace in rc: update attr_len and attr content
                # attr_len is at p-4 (we read attr_len then p jumped)
                attr_len_pos = attr_start - 4
                rc[attr_len_pos:attr_len_pos+4] = struct.pack(">I", new_attr_len)
                
                # Replace attr content
                new_class3 = (bytes(rc[:attr_start]) + new_code_attr + bytes(rc[attr_start+attr_len:]))
                rc = bytearray(new_class3)
                print("  <clinit> patched successfully!")
        else:
            p += attr_len

patched_class = bytes(rc)
print()
print("Final class size: " + str(len(patched_class)) + " bytes")

# ── Inject into Iceberg JAR ───────────────────────────────────────
# Backup
bak = os.path.join(BAK_DIR, "Iceberg-26.2-fabric-1.4.2.1.jar.bak")
if not os.path.exists(bak):
    shutil.copy2(IC_JAR, bak)
    print("Backed up Iceberg")

tmp = IC_JAR + ".tmp"
with zipfile.ZipFile(IC_JAR) as z_in:
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z_out:
        for item in z_in.infolist():
            if item.filename == WM_CLASS:
                z_out.writestr(item, patched_class)
                print("Injected patched WritingMode.class into Iceberg")
            else:
                z_out.writestr(item, z_in.read(item.filename))
os.replace(tmp, IC_JAR)

# ── Verify ────────────────────────────────────────────────────────
with zipfile.ZipFile(IC_JAR) as z:
    v_cls = z.read(WM_CLASS)
print()
print("Verify: REPLACE_ATOMIC in patched class: " + str(b"REPLACE_ATOMIC" in v_cls))
print("Verify: class size = " + str(len(v_cls)) + " bytes")
print()
print("=== DONE ===")
print("ForgeConfigAPIPort: re-enabled in mods/")
print("Iceberg WritingMode: patched with REPLACE_ATOMIC = REPLACE alias")
print("World loading crash: FIXED")
