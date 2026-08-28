"""
Generate a professional 3D blocky "AETHERIS EDITION" texture for edition.png.
Matches Minecraft / Sapixcraft's 3D extruded subtitle style:
- High resolution (512x64)
- 3D extruded isometric drop shadow (bottom-right extrusion)
- Distinct face highlights, front face gradient, dark outline
- Fully transparent background (no pink/magenta line, no artifacts)
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_aetheris_edition_texture(out_path):
    W, H = 512, 64
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # We will construct 3D voxel letters for "AETHERIS EDITION"
    # Letter matrix definition: 5 wide x 7 high grid per letter
    FONT_5x7 = {
        'A': [
            "01110",
            "10001",
            "10001",
            "11111",
            "10001",
            "10001",
            "10001"
        ],
        'B': [
            "11110",
            "10001",
            "10001",
            "11110",
            "10001",
            "10001",
            "11110"
        ],
        'C': [
            "01111",
            "10000",
            "10000",
            "10000",
            "10000",
            "10000",
            "01111"
        ],
        'D': [
            "11110",
            "10001",
            "10001",
            "10001",
            "10001",
            "10001",
            "11110"
        ],
        'E': [
            "11111",
            "10000",
            "10000",
            "11110",
            "10000",
            "10000",
            "11111"
        ],
        'F': [
            "11111",
            "10000",
            "10000",
            "11110",
            "10000",
            "10000",
            "10000"
        ],
        'G': [
            "01111",
            "10000",
            "10000",
            "10111",
            "10001",
            "10001",
            "01110"
        ],
        'H': [
            "10001",
            "10001",
            "10001",
            "11111",
            "10001",
            "10001",
            "10001"
        ],
        'I': [
            "111",
            "010",
            "010",
            "010",
            "010",
            "010",
            "111"
        ],
        'J': [
            "00111",
            "00010",
            "00010",
            "00010",
            "10010",
            "10010",
            "01100"
        ],
        'K': [
            "10001",
            "10010",
            "10100",
            "11000",
            "10100",
            "10010",
            "10001"
        ],
        'L': [
            "10000",
            "10000",
            "10000",
            "10000",
            "10000",
            "10000",
            "11111"
        ],
        'M': [
            "10001",
            "11011",
            "10101",
            "10001",
            "10001",
            "10001",
            "10001"
        ],
        'N': [
            "10001",
            "11001",
            "10101",
            "10011",
            "10001",
            "10001",
            "10001"
        ],
        'O': [
            "01110",
            "10001",
            "10001",
            "10001",
            "10001",
            "10001",
            "01110"
        ],
        'P': [
            "11110",
            "10001",
            "10001",
            "11110",
            "10000",
            "10000",
            "10000"
        ],
        'Q': [
            "01110",
            "10001",
            "10001",
            "10001",
            "10101",
            "10010",
            "01101"
        ],
        'R': [
            "11110",
            "10001",
            "10001",
            "11110",
            "10100",
            "10010",
            "10001"
        ],
        'S': [
            "01111",
            "10000",
            "10000",
            "01110",
            "00001",
            "00001",
            "11110"
        ],
        'T': [
            "11111",
            "00100",
            "00100",
            "00100",
            "00100",
            "00100",
            "00100"
        ],
        'U': [
            "10001",
            "10001",
            "10001",
            "10001",
            "10001",
            "10001",
            "01110"
        ],
        'V': [
            "10001",
            "10001",
            "10001",
            "10001",
            "10001",
            "01010",
            "00100"
        ],
        'W': [
            "10001",
            "10001",
            "10001",
            "10101",
            "10101",
            "11011",
            "10001"
        ],
        'X': [
            "10001",
            "10001",
            "01010",
            "00100",
            "01010",
            "10001",
            "10001"
        ],
        'Y': [
            "10001",
            "10001",
            "01010",
            "00100",
            "00100",
            "00100",
            "00100"
        ],
        'Z': [
            "11111",
            "00001",
            "00010",
            "00100",
            "01000",
            "10000",
            "11111"
        ],
        ' ': [
            "000",
            "000",
            "000",
            "000",
            "000",
            "000",
            "000"
        ],
        '-': [
            "0000",
            "0000",
            "0000",
            "1111",
            "0000",
            "0000",
            "0000"
        ]
    }
    
    scale = 3  # Each font pixel is 3x3 screen pixels
    
    # Calculate total width of "AETHERIS EDITION"
    words = ["AETHERIS", "EDITION"]
    
    def get_word_width(word):
        w = 0
        for ch in word:
            matrix = FONT_5x7.get(ch, FONT_5x7[' '])
            w += (len(matrix[0]) + 1) * scale
        return w - scale  # remove trailing space
        
    w1 = get_word_width("AETHERIS")
    w2 = get_word_width("EDITION")
    space_w = 4 * scale
    total_w = w1 + space_w + w2
    
    start_x = (W - total_w) // 2
    start_y = (H - 7 * scale) // 2 - 3  # slight vertical offset for 3D extrusion
    
    # Colors for AETHERIS (Vibrant Cyan / Diamond 3D theme):
    # Front face: Gradient from bright cyan (top) to rich teal (bottom)
    # 3D Depth / Bevels: Dark navy/cyan shadow + Pure black 3D outline
    
    # Colors for EDITION (Golden / Yellow 3D theme):
    # Front face: Gradient from bright gold (top) to deep orange (bottom)
    # 3D Depth / Bevels: Dark brown shadow + Pure black 3D outline
    
    def draw_3d_text(word, start_pos_x, theme="cyan"):
        cur_x = start_pos_x
        
        # 1. First pass: Collect all active pixels for the word
        active_pixels = []
        for ch in word:
            matrix = FONT_5x7.get(ch, FONT_5x7[' '])
            for r_idx, row in enumerate(matrix):
                for c_idx, val in enumerate(row):
                    if val == '1':
                        active_pixels.append((cur_x + c_idx * scale, start_y + r_idx * scale, r_idx))
            cur_x += (len(matrix[0]) + 1) * scale
            
        # 2. Black 3D Outer Outline (Offset 0 to 4 px down-right)
        for depth in range(4, -1, -1):
            for px, py, r_idx in active_pixels:
                for ox in (-1, 0, 1, 2):
                    for oy in (-1, 0, 1, 2):
                        draw.rectangle(
                            [px + ox + depth, py + oy + depth, px + scale - 1 + ox + depth, py + scale - 1 + oy + depth],
                            fill=(0, 0, 0, 255)
                        )
                        
        # 3. 3D Extruded Depth Layers (Darker shades)
        for depth in range(3, 0, -1):
            for px, py, r_idx in active_pixels:
                if theme == "cyan":
                    # Depth color
                    d_col = (10, 50 + depth * 15, 80 + depth * 20, 255)
                else: # gold
                    d_col = (90 + depth * 20, 45 + depth * 15, 5, 255)
                draw.rectangle(
                    [px + depth, py + depth, px + scale - 1 + depth, py + scale - 1 + depth],
                    fill=d_col
                )
                
        # 4. Front Face Pixels (with gradient + top highlight)
        for px, py, r_idx in active_pixels:
            if theme == "cyan":
                if r_idx <= 1:
                    # Top highlight
                    f_col = (210, 255, 255, 255)
                elif r_idx <= 3:
                    f_col = (90, 235, 245, 255)
                elif r_idx <= 5:
                    f_col = (40, 185, 215, 255)
                else:
                    # Bottom shade
                    f_col = (15, 130, 175, 255)
            else: # gold
                if r_idx <= 1:
                    # Top highlight
                    f_col = (255, 250, 190, 255)
                elif r_idx <= 3:
                    f_col = (255, 215, 40, 255)
                elif r_idx <= 5:
                    f_col = (240, 160, 20, 255)
                else:
                    # Bottom shade
                    f_col = (190, 100, 10, 255)
                    
            draw.rectangle(
                [px, py, px + scale - 1, py + scale - 1],
                fill=f_col
            )
            # Add inner highlight dot at top-left of each block
            draw.point((px, py), fill=(255, 255, 255, 200))
            
        return cur_x
        
    x_after_aetheris = draw_3d_text("AETHERIS", start_x, theme="cyan")
    draw_3d_text("EDITION", x_after_aetheris + space_w - scale, theme="gold")
    
    img.save(out_path, "PNG", optimize=True)
    print(f"✅ Created 3D edition.png at {out_path} ({os.path.getsize(out_path)} bytes)")

create_aetheris_edition_texture(r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\gui\title\edition.png")
