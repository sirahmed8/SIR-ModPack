from PIL import Image

img = Image.open(r"D:\shader\_temp_merge\sapix_edition.png")
bbox = img.getbbox()
print("Sapix edition size:", img.size)
print("Bounding box:", bbox)

# Let's inspect the height and structure
w, h = img.size
print(f"Image mode: {img.mode}")

# Let's check where the letters are located
for y in range(0, h, 4):
    row_chars = []
    for x in range(0, w, 8):
        p = img.getpixel((x, y))
        if p[3] > 128:
            row_chars.append("#")
        else:
            row_chars.append(" ")
    line = "".join(row_chars)
    if line.strip():
        print(f"y={y:2d}: {line}")
