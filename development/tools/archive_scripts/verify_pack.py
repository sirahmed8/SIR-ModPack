import zipfile, json, os

pack_zip = r"D:\resource pack\MyCustomPack_Modern_32x.zip"
print("=== FINAL VERIFICATION ===")

with zipfile.ZipFile(pack_zip, "r") as z:
    names = z.namelist()

    # 1. Check pack.mcmeta
    meta = json.loads(z.read("pack.mcmeta").decode("utf-8"))
    desc = meta["pack"]["description"]
    print(f"[1] pack.mcmeta description: {desc}")

    # 2. Check pack.png is real PNG
    png = z.read("pack.png")
    is_png = png[:4] == bytes([0x89,0x50,0x4E,0x47])
    print(f"[2] pack.png is real PNG: {is_png} ({len(png)} bytes)")

    # 3. Check minecraft.png
    title_key = "assets/minecraft/textures/gui/title/minecraft.png"
    if title_key in names:
        mpng = z.read(title_key)
        is_png2 = mpng[:4] == bytes([0x89,0x50,0x4E,0x47])
        print(f"[3] title/minecraft.png is real PNG: {is_png2} ({len(mpng)} bytes)")
    else:
        print("[3] title/minecraft.png: not in pack (vanilla default shows)")

    # 4. Validate ALL JSON files
    bad = []
    for n in names:
        if n.endswith(".json"):
            try:
                json.loads(z.read(n).decode("utf-8", errors="replace"))
            except Exception as e:
                bad.append((n, str(e)[:60]))
    print(f"[4] Bad JSON files: {len(bad)}")
    for b, err in bad[:15]:
        print(f"    {b}: {err}")

    print(f"\nTotal files: {len(names)}")
    if not bad and is_png:
        print("=== ALL CHECKS PASSED! Pack is clean and ready. ===")
    else:
        print("=== ISSUES FOUND - need another fix pass ===")
