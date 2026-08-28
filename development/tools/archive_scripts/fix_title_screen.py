"""
Aetheris - Title Screen Text Editor
Replaces:
  - edition.png: Sapixcraft → "AETHERIS EDITION" in Minecraft pixel style
  - minecraft.png: Use Sapixcraft's clean MINECRAFT logo (it's perfect already)

The edition.png is 512x64 px, RGBA.
We draw "AETHERIS EDITION" using the Minecraft bitmap font style.
"""

from PIL import Image, ImageDraw, ImageFont
import os, zipfile, io, struct, zlib

PACK_DIR = r"D:\resource pack\MyCustomPack_Modern_32x"
SAPIX_ZIP = r"D:\resource pack\Sapixcraft 32x r1.5 26.2.zip"
OUT_TITLE_DIR = os.path.join(PACK_DIR, r"assets\minecraft\textures\gui\title")
os.makedirs(OUT_TITLE_DIR, exist_ok=True)

print("=" * 60)
print("AETHERIS TITLE SCREEN TEXT FIXER")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# STEP 1: Use Sapixcraft's CLEAN minecraft.png (the MINECRAFT logo itself)
#         It's 1024x256 RGBA, beautiful - just copy it as-is
# ─────────────────────────────────────────────────────────────
print("\n[1] Copying Sapixcraft's clean MINECRAFT logo...")
with zipfile.ZipFile(SAPIX_ZIP) as z:
    mc_data = z.read("assets/minecraft/textures/gui/title/minecraft.png")

mc_dest = os.path.join(OUT_TITLE_DIR, "minecraft.png")
with open(mc_dest, "wb") as f:
    f.write(mc_data)

# Verify
with open(mc_dest, "rb") as f:
    magic = f.read(4)
print(f"  ✅ minecraft.png: PNG={magic==bytes([0x89,0x50,0x4E,0x47])} ({len(mc_data)} bytes)")

# ─────────────────────────────────────────────────────────────
# STEP 2: Create new edition.png with "AETHERIS EDITION" text
#         Match the 512x64 size of Sapixcraft's original
#         Use Minecraft pixel font look-alike
# ─────────────────────────────────────────────────────────────
print("\n[2] Creating Aetheris edition.png...")

W, H = 512, 64

# Create RGBA canvas (transparent background like vanilla)
edition = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(edition)

# Try to use a font that looks Minecraft-like
# Options: use PIL's default bitmap font at large size, or draw pixel text manually

# Minecraft font uses 8px grid characters
# We'll draw pixel-art letters manually for "AETHERIS EDITION"
# Using a pre-defined pixel font pattern

def draw_pixel_text(draw, text, x, y, color_main, color_shadow, scale=4):
    """Draw Minecraft-style pixel text"""
    # Basic Minecraft-style font - 5x7 pixel characters
    CHARS = {
        'A': ["01110","10001","10001","11111","10001","10001","10001"],
        'B': ["11110","10001","10001","11110","10001","10001","11110"],
        'C': ["01111","10000","10000","10000","10000","10000","01111"],
        'D': ["11110","10001","10001","10001","10001","10001","11110"],
        'E': ["11111","10000","10000","11110","10000","10000","11111"],
        'F': ["11111","10000","10000","11110","10000","10000","10000"],
        'G': ["01111","10000","10000","10111","10001","10001","01110"],
        'H': ["10001","10001","10001","11111","10001","10001","10001"],
        'I': ["01110","00100","00100","00100","00100","00100","01110"],
        'J': ["00111","00010","00010","00010","10010","10010","01100"],
        'K': ["10001","10010","10100","11000","10100","10010","10001"],
        'L': ["10000","10000","10000","10000","10000","10000","11111"],
        'M': ["10001","11011","10101","10001","10001","10001","10001"],
        'N': ["10001","11001","10101","10011","10001","10001","10001"],
        'O': ["01110","10001","10001","10001","10001","10001","01110"],
        'P': ["11110","10001","10001","11110","10000","10000","10000"],
        'Q': ["01110","10001","10001","10001","10101","10010","01101"],
        'R': ["11110","10001","10001","11110","10100","10010","10001"],
        'S': ["01111","10000","10000","01110","00001","00001","11110"],
        'T': ["11111","00100","00100","00100","00100","00100","00100"],
        'U': ["10001","10001","10001","10001","10001","10001","01110"],
        'V': ["10001","10001","10001","10001","10001","01010","00100"],
        'W': ["10001","10001","10001","10101","10101","11011","10001"],
        'X': ["10001","10001","01010","00100","01010","10001","10001"],
        'Y': ["10001","10001","01010","00100","00100","00100","00100"],
        'Z': ["11111","00001","00010","00100","01000","10000","11111"],
        ' ': ["00000","00000","00000","00000","00000","00000","00000"],
    }
    
    cx = x
    for ch in text.upper():
        bitmap = CHARS.get(ch, CHARS[' '])
        for row_i, row in enumerate(bitmap):
            for col_i, pixel in enumerate(row):
                if pixel == '1':
                    px = cx + col_i * scale
                    py = y + row_i * scale
                    # Shadow (offset by scale)
                    draw.rectangle([px+scale, py+scale, px+scale*2-1, py+scale*2-1], fill=color_shadow)
                    # Main color
                    draw.rectangle([px, py, px+scale-1, py+scale-1], fill=color_main)
        cx += 6 * scale  # 5 wide + 1 gap

    return cx  # return end x position

# Draw "AETHERIS" in cyan-blue (Minecraft diamond color)
# Center it horizontally
text1 = "AETHERIS"
text2 = "EDITION"

# Calculate widths (each char is 6*scale wide, text has len(text)*6*scale - scale width)
scale = 4
char_w = 6 * scale
text1_w = len(text1) * char_w
text2_w = len(text2) * char_w

# "AETHERIS EDITION" combined centered
combined = text1 + " " + text2
combined_w = len(combined) * char_w

x_start = (W - combined_w) // 2
y_start = (H - 7 * scale) // 2 - 2  # Vertically centered

# Draw shadow then main text
# Color: cyan-blue like diamond/water (#55FFFF in Minecraft chat = aqua)
color_shadow = (0, 100, 100, 255)      # Dark teal shadow
color_main = (85, 255, 255, 255)        # Bright cyan (Minecraft aqua)

draw_pixel_text(draw, combined, x_start, y_start, color_main, color_shadow, scale)

# Add a thin glowing underline
line_y = y_start + 7 * scale + scale + 2
for lx in range(x_start - 4, x_start + combined_w + 4):
    edition.putpixel((lx, line_y), (85, 200, 255, 180))
    edition.putpixel((lx, line_y + 1), (40, 120, 200, 80))

# Save
edition_dest = os.path.join(OUT_TITLE_DIR, "edition.png")
edition.save(edition_dest, "PNG", optimize=True)

with open(edition_dest, "rb") as f:
    magic = f.read(4)
print(f"  ✅ edition.png: PNG={magic==bytes([0x89,0x50,0x4E,0x47])} ({os.path.getsize(edition_dest)} bytes)")
print(f"  Size: {edition.size}")

# Also delete our old broken minecraft.png and replace with the Sapixcraft clean one
print("\n[3] Verifying both title files...")
for fname in ["minecraft.png", "edition.png"]:
    fp = os.path.join(OUT_TITLE_DIR, fname)
    if os.path.exists(fp):
        with open(fp, "rb") as f:
            m = f.read(4)
        is_png = m == bytes([0x89,0x50,0x4E,0x47])
        img = Image.open(fp)
        print(f"  {fname}: PNG={is_png} size={img.size} bytes={os.path.getsize(fp)}")
    else:
        print(f"  {fname}: MISSING!")

print("\n✅ Title screen textures ready!")
print("Run the sync script next to rebuild ZIPs.")
