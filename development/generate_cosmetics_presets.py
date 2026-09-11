"""
SIR ModPack - Official Cosmetics & HD Wardrobe Studio Preset Generator
Generates pixel-perfect 64x32 Minecraft Cape textures and 64x64 Dual-Layer Skins
Targeting both Desktop Launcher directories and Next.js Web Platform public directories.

Platform: Independent Gaming Platform under SIR Software Agreement
Contact: a7medorabe7@gmail.com
Version: v1.0.0 Official Release
"""

import os
import math
from PIL import Image, ImageDraw

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_CAPES_DIR = os.path.join(ROOT_DIR, "capes")
LOCAL_SKINS_DIR = os.path.join(ROOT_DIR, "skins")
WEB_CAPES_DIR = os.path.join(ROOT_DIR, "website-next", "public", "capes")
WEB_SKINS_DIR = os.path.join(ROOT_DIR, "website-next", "public", "skins")

for d in [LOCAL_CAPES_DIR, LOCAL_SKINS_DIR, WEB_CAPES_DIR, WEB_SKINS_DIR]:
    os.makedirs(d, exist_ok=True)

def hex_rgba(hex_str, alpha=255):
    h = hex_str.lstrip('#')
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    elif len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    return (0, 0, 0, alpha)

def blend(c1, c2, factor):
    """Linearly blend between two RGBA colors."""
    factor = max(0.0, min(1.0, factor))
    return (
        int(c1[0] + (c2[0] - c1[0]) * factor),
        int(c1[1] + (c2[1] - c1[1]) * factor),
        int(c1[2] + (c2[2] - c1[2]) * factor),
        int(c1[3] + (c2[3] - c1[3]) * factor),
    )

# ==============================================================================
# CAPE GENERATOR ENGINE
# ==============================================================================

class CapeBuilder:
    def __init__(self, bg_color):
        self.img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        # Fill whole canvas with subtle base tone
        self.draw.rectangle([0, 0, 63, 31], fill=bg_color)
        self.bg = bg_color

    def set_back_face_pixels(self, pixel_map):
        """
        pixel_map: list of 16 rows, each having 10 RGBA tuples.
        Back face is x in [1..10], y in [1..16].
        Inside face is x in [12..21], y in [1..16].
        """
        for y, row in enumerate(pixel_map):
            for x, col in enumerate(row):
                # Back face (outside, facing world)
                self.img.putpixel((1 + x, 1 + y), col)
                # Front face (inside, facing player's back)
                self.img.putpixel((12 + x, 1 + y), col)

    def set_edges(self, top_col, bottom_col, side_col):
        # Top edge: (1, 0) to (10, 0)
        for x in range(1, 11):
            self.img.putpixel((x, 0), top_col)
            self.img.putpixel((11 + x, 0), bottom_col)
        # Left edge: (0, 1) to (0, 16)
        for y in range(1, 17):
            self.img.putpixel((0, y), side_col)
            self.img.putpixel((11, y), side_col)

    def set_elytra_wings(self, primary_col, accent_col, highlight_col):
        """
        Fills Elytra wing UVs:
        Left wing: u=22, v=0, width=10, height=20, depth=2
        Right wing: u=34, v=0, width=10, height=20, depth=2
        """
        # Outer faces
        for y in range(2, 22):
            progress = (y - 2) / 20.0
            grad_col = blend(primary_col, accent_col, progress)
            for x in range(24, 34):
                self.img.putpixel((x, y), grad_col)
            for x in range(36, 46):
                self.img.putpixel((x, y), grad_col)
            # Edge highlights
            self.img.putpixel((24, y), highlight_col)
            self.img.putpixel((33, y), highlight_col)
            self.img.putpixel((36, y), highlight_col)
            self.img.putpixel((45, y), highlight_col)

        # Wing tips
        for x in range(24, 34):
            self.img.putpixel((x, 0), highlight_col)
            self.img.putpixel((x, 1), accent_col)
        for x in range(36, 46):
            self.img.putpixel((x, 0), highlight_col)
            self.img.putpixel((x, 1), accent_col)

    def save(self, filename):
        p1 = os.path.join(LOCAL_CAPES_DIR, filename)
        p2 = os.path.join(WEB_CAPES_DIR, filename)
        self.img.save(p1, format="PNG")
        self.img.save(p2, format="PNG")
        print(f"✓ Saved cape preset: {filename}")


def generate_all_capes():
    print("\n--- Generating 6 High-Quality Preset Capes (64x32 RGBA) ---")
    
    # --------------------------------------------------------------------------
    # 1. sir_obsidian_neon.png (Cyberpunk obsidian with cyan #00e5ff & amber #f59e0b)
    # --------------------------------------------------------------------------
    c_obs = hex_rgba("#060a12")
    c_obs_light = hex_rgba("#0f172a")
    c_cyan = hex_rgba("#00e5ff")
    c_cyan_glow = hex_rgba("#38bdf8")
    c_amber = hex_rgba("#f59e0b")
    c_amber_glow = hex_rgba("#fbbf24")
    c_core = hex_rgba("#f0fdf4")
    
    cape1 = CapeBuilder(c_obs)
    cape1.set_edges(c_cyan, c_amber, c_cyan_glow)
    cape1.set_elytra_wings(c_obs_light, c_cyan, c_amber_glow)
    
    # 10x16 Back face matrix
    m1 = []
    # Row 0-1: Cyan neon upper header border with corner brackets
    m1.append([c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan])
    m1.append([c_cyan, c_obs,  c_obs,  c_amber, c_amber, c_amber, c_amber, c_obs,  c_obs,  c_cyan])
    # Row 2-4: Circuit traces entering downwards
    m1.append([c_cyan, c_obs,  c_cyan, c_obs,  c_amber, c_amber, c_obs,  c_cyan, c_obs,  c_cyan])
    m1.append([c_cyan, c_obs,  c_cyan, c_cyan, c_obs,   c_obs,   c_cyan, c_cyan, c_obs,  c_cyan])
    m1.append([c_cyan, c_obs,  c_obs,  c_cyan, c_obs,   c_obs,   c_cyan, c_obs,  c_obs,  c_cyan])
    # Row 5-6: Amber circuit crossover
    m1.append([c_cyan, c_amber, c_obs, c_cyan, c_amber, c_amber, c_cyan, c_obs, c_amber, c_cyan])
    m1.append([c_cyan, c_amber, c_amber, c_obs, c_amber, c_amber, c_obs, c_amber, c_amber, c_cyan])
    # Row 7-8: Central glowing quantum power core
    m1.append([c_cyan, c_obs, c_amber, c_amber, c_core, c_core, c_amber, c_amber, c_obs, c_cyan])
    m1.append([c_cyan, c_obs, c_amber, c_amber, c_core, c_core, c_amber, c_amber, c_obs, c_cyan])
    # Row 9-10: Symmetrical lower circuit divergence
    m1.append([c_cyan, c_amber, c_amber, c_obs, c_amber, c_amber, c_obs, c_amber, c_amber, c_cyan])
    m1.append([c_cyan, c_amber, c_obs, c_cyan, c_amber, c_amber, c_cyan, c_obs, c_amber, c_cyan])
    # Row 11-13: Cyber traces routing to bottom bus
    m1.append([c_cyan, c_obs,  c_obs,  c_cyan, c_obs,   c_obs,   c_cyan, c_obs,  c_obs,  c_cyan])
    m1.append([c_cyan, c_obs,  c_cyan, c_cyan, c_obs,   c_obs,   c_cyan, c_cyan, c_obs,  c_cyan])
    m1.append([c_cyan, c_obs,  c_cyan, c_obs,  c_amber, c_amber, c_obs,  c_cyan, c_obs,  c_cyan])
    m1.append([c_cyan, c_obs,  c_obs,  c_amber, c_amber, c_amber, c_amber, c_obs,  c_obs,  c_cyan])
    m1.append([c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan, c_cyan])
    cape1.set_back_face_pixels(m1)
    cape1.save("sir_obsidian_neon.png")

    # --------------------------------------------------------------------------
    # 2. sir_emerald_prism.png (Faceted geometric emerald #10b981 crystal)
    # --------------------------------------------------------------------------
    e_deep = hex_rgba("#022c22")
    e_dark = hex_rgba("#064e3b")
    e_mid = hex_rgba("#059669")
    e_em = hex_rgba("#10b981")
    e_light = hex_rgba("#34d399")
    e_edge = hex_rgba("#6ee7b7")
    e_glint = hex_rgba("#ffffff")

    cape2 = CapeBuilder(e_deep)
    cape2.set_edges(e_edge, e_em, e_light)
    cape2.set_elytra_wings(e_dark, e_em, e_edge)

    m2 = []
    # Prismatic faceted diamond crystal
    m2.append([e_edge, e_edge, e_edge, e_edge, e_glint, e_glint, e_edge, e_edge, e_edge, e_edge])
    m2.append([e_edge, e_dark, e_dark, e_mid,  e_light, e_light, e_mid,  e_dark, e_dark, e_edge])
    m2.append([e_edge, e_dark, e_mid,  e_em,   e_edge,  e_edge,  e_em,   e_mid,  e_dark, e_edge])
    m2.append([e_edge, e_mid,  e_em,   e_light, e_glint, e_glint, e_light, e_em,  e_mid,  e_edge])
    m2.append([e_edge, e_dark, e_em,   e_edge,  e_light, e_light, e_edge,  e_em,  e_dark, e_edge])
    m2.append([e_edge, e_dark, e_mid,  e_em,    e_edge,  e_edge,  e_em,    e_mid, e_dark, e_edge])
    m2.append([e_edge, e_deep, e_dark, e_mid,   e_em,    e_em,    e_mid,   e_dark, e_deep, e_edge])
    m2.append([e_edge, e_deep, e_deep, e_dark,  e_mid,   e_mid,   e_dark,  e_deep, e_deep, e_edge])
    m2.append([e_edge, e_deep, e_deep, e_dark,  e_mid,   e_mid,   e_dark,  e_deep, e_deep, e_edge])
    m2.append([e_edge, e_deep, e_dark, e_mid,   e_em,    e_em,    e_mid,   e_dark, e_deep, e_edge])
    m2.append([e_edge, e_dark, e_mid,  e_em,    e_edge,  e_edge,  e_em,    e_mid, e_dark, e_edge])
    m2.append([e_edge, e_mid,  e_em,   e_light, e_glint, e_glint, e_light, e_em,  e_mid,  e_edge])
    m2.append([e_edge, e_dark, e_em,   e_edge,  e_light, e_light, e_edge,  e_em,  e_dark, e_edge])
    m2.append([e_edge, e_dark, e_mid,  e_em,    e_edge,  e_edge,  e_em,    e_mid, e_dark, e_edge])
    m2.append([e_edge, e_dark, e_dark, e_mid,   e_light, e_light, e_mid,   e_dark, e_dark, e_edge])
    m2.append([e_edge, e_edge, e_edge, e_edge,  e_glint, e_glint, e_edge,  e_edge, e_edge, e_edge])
    cape2.set_back_face_pixels(m2)
    cape2.save("sir_emerald_prism.png")

    # --------------------------------------------------------------------------
    # 3. sir_cyber_pulse.png (Digital audio/heartbeat waveform on carbon fiber)
    # --------------------------------------------------------------------------
    p_bg1 = hex_rgba("#0a0e17")
    p_bg2 = hex_rgba("#131c2e")
    p_wave = hex_rgba("#06b6d4")
    p_cyan = hex_rgba("#22d3ee")
    p_pulse = hex_rgba("#67e8f9")
    p_white = hex_rgba("#ffffff")
    p_violet = hex_rgba("#a855f7")

    cape3 = CapeBuilder(p_bg1)
    cape3.set_edges(p_cyan, p_violet, p_wave)
    cape3.set_elytra_wings(p_bg2, p_wave, p_pulse)

    m3 = []
    for y in range(16):
        row = []
        for x in range(10):
            # Carbon fiber check pattern
            is_weave = (x + y) % 2 == 0
            base = p_bg2 if is_weave else p_bg1
            row.append(base)
        m3.append(row)

    # Add HUD brackets in corners
    for c in [0, 9]:
        m3[0][c] = p_cyan
        m3[1][c] = p_cyan
        m3[14][c] = p_cyan
        m3[15][c] = p_cyan
    for r in [0, 15]:
        m3[r][1] = p_cyan
        m3[r][8] = p_cyan

    # Waveform pattern across rows 5 to 11
    # ECG / Audio peak coordinates (x, y)
    wave_points = [
        (0, 8, p_wave),
        (1, 8, p_wave),
        (2, 7, p_cyan),
        (3, 9, p_cyan),
        (4, 4, p_white),   # Spike top peak
        (4, 5, p_pulse),
        (5, 12, p_violet), # Spike bottom trough
        (5, 11, p_pulse),
        (6, 6, p_pulse),
        (7, 8, p_cyan),
        (8, 8, p_wave),
        (9, 8, p_wave),
    ]
    for x, y, col in wave_points:
        if 0 <= x < 10 and 0 <= y < 16:
            m3[y][x] = col

    # Glow vertical bars
    for x in range(10):
        if m3[8][x] == p_bg1 or m3[8][x] == p_bg2:
            m3[8][x] = p_wave

    cape3.set_back_face_pixels(m3)
    cape3.save("sir_cyber_pulse.png")

    # --------------------------------------------------------------------------
    # 4. sir_void_dragon.png (Deep galactic obsidian with purple/magenta scales & eye)
    # --------------------------------------------------------------------------
    v_bg = hex_rgba("#090414")
    v_dark = hex_rgba("#1d0e3a")
    v_scale1 = hex_rgba("#3b0764")
    v_scale2 = hex_rgba("#7e22ce")
    v_magenta = hex_rgba("#d946ef")
    v_eye = hex_rgba("#f43f5e")
    v_pupil = hex_rgba("#4c0519")
    v_white = hex_rgba("#ffffff")

    cape4 = CapeBuilder(v_bg)
    cape4.set_edges(v_magenta, v_scale2, v_scale1)
    cape4.set_elytra_wings(v_dark, v_scale2, v_magenta)

    m4 = []
    for y in range(16):
        row = []
        for x in range(10):
            # Dragon scale scalloped pattern
            sc = v_scale1 if (x + (y % 3)) % 2 == 0 else v_dark
            row.append(sc)
        m4.append(row)

    # Magenta edge scale trims
    for y in range(16):
        m4[y][0] = v_scale2
        m4[y][9] = v_scale2
    for x in range(10):
        m4[0][x] = v_magenta
        m4[15][x] = v_magenta

    # Radiant Ender Dragon Eye in center (Rows 6-9, Cols 3-6)
    eye_map = [
        [v_magenta, v_magenta, v_magenta, v_magenta],
        [v_magenta, v_eye,     v_pupil,   v_magenta],
        [v_magenta, v_eye,     v_pupil,   v_magenta],
        [v_magenta, v_magenta, v_magenta, v_magenta]
    ]
    for dy, r in enumerate(eye_map):
        for dx, c in enumerate(r):
            m4[6 + dy][3 + dx] = c

    # Dragon horns/wings silhouette
    m4[2][4] = v_magenta
    m4[2][5] = v_magenta
    m4[3][3] = v_magenta
    m4[3][6] = v_magenta
    m4[4][2] = v_scale2
    m4[4][7] = v_scale2

    # Lower tail crest
    m4[12][4] = v_scale2
    m4[12][5] = v_scale2
    m4[13][4] = v_magenta
    m4[13][5] = v_magenta

    cape4.set_back_face_pixels(m4)
    cape4.save("sir_void_dragon.png")

    # --------------------------------------------------------------------------
    # 5. sir_champion_gold.png (Pure esports tournament gold #eab308 and platinum)
    # --------------------------------------------------------------------------
    g_bg = hex_rgba("#0c0d0f")
    g_dark = hex_rgba("#1c1917")
    g_plat = hex_rgba("#f8fafc")
    g_gold_dark = hex_rgba("#854d0e")
    g_gold = hex_rgba("#eab308")
    g_gold_bright = hex_rgba("#fde047")
    g_gold_core = hex_rgba("#ffffff")

    cape5 = CapeBuilder(g_bg)
    cape5.set_edges(g_plat, g_gold, g_gold_bright)
    cape5.set_elytra_wings(g_dark, g_gold, g_plat)

    m5 = []
    # Platinum white borders
    for y in range(16):
        row = [g_bg] * 10
        row[0] = g_plat
        row[9] = g_plat
        m5.append(row)
    for x in range(10):
        m5[0][x] = g_plat
        m5[15][x] = g_plat

    # Championship Trophy & Laurel Wreath
    # Crown spikes top
    m5[2][2] = g_gold
    m5[2][5] = g_gold_bright
    m5[2][7] = g_gold
    m5[3][3] = g_gold_bright
    m5[3][4] = g_gold_core
    m5[3][5] = g_gold_core
    m5[3][6] = g_gold_bright

    # Trophy cup / central shield
    m5[4][2] = g_gold
    m5[4][3] = g_gold_bright
    m5[4][4] = g_gold_core
    m5[4][5] = g_gold_core
    m5[4][6] = g_gold_bright
    m5[4][7] = g_gold

    m5[5][2] = g_gold
    m5[5][3] = g_gold_dark
    m5[5][4] = g_gold_bright
    m5[5][5] = g_gold_bright
    m5[5][6] = g_gold_dark
    m5[5][7] = g_gold

    m5[6][3] = g_gold
    m5[6][4] = g_gold_bright
    m5[6][5] = g_gold_bright
    m5[6][6] = g_gold

    # Stem
    m5[7][4] = g_gold
    m5[7][5] = g_gold
    m5[8][4] = g_gold_bright
    m5[8][5] = g_gold_bright

    # Pedestal base
    m5[9][3] = g_gold
    m5[9][4] = g_gold_bright
    m5[9][5] = g_gold_bright
    m5[9][6] = g_gold
    m5[10][2] = g_gold_bright
    m5[10][3] = g_gold_core
    m5[10][4] = g_gold_core
    m5[10][5] = g_gold_core
    m5[10][6] = g_gold_core
    m5[10][7] = g_gold_bright

    # Laurel branches on sides
    m5[6][1] = g_gold_bright
    m5[7][1] = g_gold
    m5[8][1] = g_gold_bright
    m5[6][8] = g_gold_bright
    m5[7][8] = g_gold
    m5[8][8] = g_gold_bright

    # Esports Stars bottom
    m5[12][3] = g_gold_bright
    m5[12][6] = g_gold_bright
    m5[13][4] = g_gold_core
    m5[13][5] = g_gold_core

    cape5.set_back_face_pixels(m5)
    cape5.save("sir_champion_gold.png")

    # --------------------------------------------------------------------------
    # 6. sir_classic_genesis.png (Official SIR v1.0.0 Genesis insignia)
    # --------------------------------------------------------------------------
    gen_bg = hex_rgba("#040814")
    gen_navy = hex_rgba("#0c1c38")
    gen_cyan = hex_rgba("#00e5ff")
    gen_gold = hex_rgba("#fbbf24")
    gen_white = hex_rgba("#ffffff")
    gen_glow = hex_rgba("#38bdf8")

    cape6 = CapeBuilder(gen_bg)
    cape6.set_edges(gen_cyan, gen_gold, gen_glow)
    cape6.set_elytra_wings(gen_navy, gen_cyan, gen_gold)

    m6 = []
    # Outer frame
    for y in range(16):
        row = [gen_bg] * 10
        row[0] = gen_cyan
        row[9] = gen_cyan
        m6.append(row)
    for x in range(10):
        m6[0][x] = gen_cyan
        m6[15][x] = gen_gold

    # Genesis glowing crest: "S I R" stylized monogram
    # Top crown/crest
    m6[2][4] = gen_gold
    m6[2][5] = gen_gold
    m6[3][3] = gen_cyan
    m6[3][4] = gen_white
    m6[3][5] = gen_white
    m6[3][6] = gen_cyan

    # 'S' letter / crest left
    m6[5][2] = gen_cyan
    m6[5][3] = gen_cyan
    m6[6][2] = gen_cyan
    m6[7][2] = gen_cyan
    m6[7][3] = gen_cyan
    m6[8][3] = gen_cyan
    m6[9][2] = gen_cyan
    m6[9][3] = gen_cyan

    # 'I' pillar center
    m6[5][5] = gen_gold
    m6[6][5] = gen_gold
    m6[7][5] = gen_white
    m6[8][5] = gen_gold
    m6[9][5] = gen_gold

    # 'R' arch right
    m6[5][7] = gen_cyan
    m6[5][8] = gen_cyan
    m6[6][7] = gen_cyan
    m6[6][8] = gen_cyan
    m6[7][7] = gen_cyan
    m6[7][8] = gen_cyan
    m6[8][7] = gen_cyan
    m6[9][7] = gen_cyan
    m6[9][8] = gen_cyan

    # Genesis wings lower shield
    m6[11][3] = gen_gold
    m6[11][4] = gen_cyan
    m6[11][5] = gen_cyan
    m6[11][6] = gen_gold
    m6[12][4] = gen_gold
    m6[12][5] = gen_gold
    m6[13][4] = gen_white
    m6[13][5] = gen_white

    cape6.set_back_face_pixels(m6)
    cape6.save("sir_classic_genesis.png")


# ==============================================================================
# SKIN GENERATOR ENGINE (64x64 Dual-Layer RGBA)
# ==============================================================================

class SkinBuilder:
    def __init__(self, is_slim=False):
        self.img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.is_slim = is_slim
        self.arm_w = 3 if is_slim else 4

    def fill_box(self, x, y, w, h, col):
        for cy in range(y, y + h):
            for cx in range(x, x + w):
                self.img.putpixel((cx, cy), col)

    def fill_shaded(self, x, y, w, h, base_col, shade_factor=0.08):
        """Adds natural Minecraft procedural texture noise and edge lighting."""
        for cy in range(y, y + h):
            for cx in range(x, x + w):
                noise = (((cx * 13) ^ (cy * 37)) % 11 - 5) / 50.0
                edge_bias = 0.05 if (cx == x or cy == y) else (-0.05 if (cx == x + w - 1 or cy == y + h - 1) else 0.0)
                factor = 1.0 + noise + edge_bias
                col = (
                    max(0, min(255, int(base_col[0] * factor))),
                    max(0, min(255, int(base_col[1] * factor))),
                    max(0, min(255, int(base_col[2] * factor))),
                    base_col[3]
                )
                self.img.putpixel((cx, cy), col)

    def paint_head(self, skin_tone, hair_col, eye_col, mouth_col=None):
        """
        Head Base (0, 0) to (32, 16):
        Top: (8, 0, 8, 8)
        Bottom: (16, 0, 8, 8)
        Right: (0, 8, 8, 8)
        Front: (8, 8, 8, 8)
        Left: (16, 8, 8, 8)
        Back: (24, 8, 8, 8)
        """
        # Hair base on top, back, sides
        self.fill_shaded(8, 0, 8, 8, hair_col)   # Top
        self.fill_shaded(16, 0, 8, 8, skin_tone) # Bottom (neck)
        self.fill_shaded(0, 8, 8, 8, hair_col)   # Right
        self.fill_shaded(16, 8, 8, 8, hair_col)  # Left
        self.fill_shaded(24, 8, 8, 8, hair_col)  # Back

        # Front Face (8, 8, 8, 8)
        self.fill_shaded(8, 8, 8, 8, skin_tone)
        # Hair bangs on top 2 rows of front face
        for x in range(8, 16):
            self.img.putpixel((x, 8), hair_col)
            if x % 2 == 0:
                self.img.putpixel((x, 9), hair_col)
        # Eyes
        # Left eye: (10, 12), Right eye: (13, 12)
        self.img.putpixel((9, 12), (255, 255, 255, 255))
        self.img.putpixel((10, 12), eye_col)
        self.img.putpixel((13, 12), eye_col)
        self.img.putpixel((14, 12), (255, 255, 255, 255))
        # Mouth
        m_col = mouth_col or blend(skin_tone, (100, 30, 30, 255), 0.3)
        self.img.putpixel((11, 14), m_col)
        self.img.putpixel((12, 14), m_col)

    def paint_head_overlay(self, hat_col, accent_col=None):
        """
        Head Overlay (32, 0) to (64, 16):
        Top: (40, 0, 8, 8)
        Front: (40, 8, 8, 8)
        Back: (56, 8, 8, 8)
        Sides: Right (32, 8, 8, 8), Left (48, 8, 8, 8)
        """
        self.fill_shaded(40, 0, 8, 8, hat_col)
        self.fill_shaded(32, 8, 8, 8, hat_col)
        self.fill_shaded(48, 8, 8, 8, hat_col)
        self.fill_shaded(56, 8, 8, 8, hat_col)
        # Visor or helmet frame on front
        self.fill_shaded(40, 8, 8, 2, hat_col)
        if accent_col:
            for x in range(41, 47):
                self.img.putpixel((x, 11), accent_col)
                self.img.putpixel((x, 12), accent_col)

    def paint_torso(self, base_col, armor_col=None, core_col=None):
        """
        Body Base: (16, 16) to (40, 32)
        Top: (20, 16, 8, 4)
        Bottom: (28, 16, 8, 4)
        Right: (16, 20, 4, 12)
        Front: (20, 20, 8, 12)
        Left: (28, 20, 4, 12)
        Back: (32, 20, 8, 12)
        """
        self.fill_shaded(20, 16, 8, 4, base_col)
        self.fill_shaded(28, 16, 8, 4, base_col)
        self.fill_shaded(16, 20, 4, 12, base_col)
        self.fill_shaded(28, 20, 4, 12, base_col)
        self.fill_shaded(32, 20, 8, 12, base_col)
        self.fill_shaded(20, 20, 8, 12, base_col)

        # Front chest armor / insignia
        if armor_col:
            # Chest plate
            for y in range(21, 28):
                for x in range(21, 27):
                    self.img.putpixel((x, y), armor_col)
        if core_col:
            # Power core at (23, 24) to (24, 25)
            self.img.putpixel((23, 23), core_col)
            self.img.putpixel((24, 23), core_col)
            self.img.putpixel((23, 24), core_col)
            self.img.putpixel((24, 24), core_col)

    def paint_torso_overlay(self, jacket_col, trim_col=None):
        """
        Body Overlay: (16, 32) to (40, 48)
        Front: (20, 36, 8, 12)
        Back: (32, 36, 8, 12)
        """
        self.fill_shaded(20, 32, 8, 4, jacket_col)
        self.fill_shaded(20, 36, 8, 12, jacket_col)
        self.fill_shaded(32, 36, 8, 12, jacket_col)
        self.fill_shaded(16, 36, 4, 12, jacket_col)
        self.fill_shaded(28, 36, 4, 12, jacket_col)
        if trim_col:
            for y in range(36, 48):
                self.img.putpixel((20, y), trim_col)
                self.img.putpixel((27, y), trim_col)

    def paint_arms(self, sleeve_col, glove_col=None, trim_col=None):
        """
        Right Arm: (40, 16) to (56, 32)
        Left Arm: (32, 48) to (48, 64)
        """
        w = self.arm_w
        # Right arm
        self.fill_shaded(44, 16, w, 4, sleeve_col)
        self.fill_shaded(48, 16, w, 4, sleeve_col)
        self.fill_shaded(40, 20, 4, 12, sleeve_col)
        self.fill_shaded(44, 20, w, 12, sleeve_col)
        self.fill_shaded(44 + w, 20, 4, 12, sleeve_col)
        self.fill_shaded(48 + w, 20, w, 12, sleeve_col)

        # Left arm
        self.fill_shaded(36, 48, w, 4, sleeve_col)
        self.fill_shaded(40, 48, w, 4, sleeve_col)
        self.fill_shaded(32, 52, 4, 12, sleeve_col)
        self.fill_shaded(36, 52, w, 12, sleeve_col)
        self.fill_shaded(36 + w, 52, 4, 12, sleeve_col)
        self.fill_shaded(40 + w, 52, w, 12, sleeve_col)

        if glove_col:
            # Bottom 3 pixels of arms are combat gloves
            for x in range(44, 44 + w):
                for y in range(29, 32):
                    self.img.putpixel((x, y), glove_col)
            for x in range(36, 36 + w):
                for y in range(61, 64):
                    self.img.putpixel((x, y), glove_col)
        if trim_col:
            for x in range(44, 44 + w):
                self.img.putpixel((x, 26), trim_col)
            for x in range(36, 36 + w):
                self.img.putpixel((x, 58), trim_col)

    def paint_legs(self, pants_col, boot_col=None, knee_col=None):
        """
        Right Leg: (0, 16) to (16, 32)
        Left Leg: (16, 48) to (32, 64)
        """
        # Right Leg
        self.fill_shaded(4, 16, 4, 4, pants_col)
        self.fill_shaded(8, 16, 4, 4, pants_col)
        self.fill_shaded(0, 20, 4, 12, pants_col)
        self.fill_shaded(4, 20, 4, 12, pants_col)
        self.fill_shaded(8, 20, 4, 12, pants_col)
        self.fill_shaded(12, 20, 4, 12, pants_col)

        # Left Leg
        self.fill_shaded(20, 48, 4, 4, pants_col)
        self.fill_shaded(24, 48, 4, 4, pants_col)
        self.fill_shaded(16, 52, 4, 12, pants_col)
        self.fill_shaded(20, 52, 4, 12, pants_col)
        self.fill_shaded(24, 52, 4, 12, pants_col)
        self.fill_shaded(28, 52, 4, 12, pants_col)

        if boot_col:
            # Boots on bottom 4 pixels
            for y in range(28, 32):
                for x in range(4, 8):
                    self.img.putpixel((x, y), boot_col)
            for y in range(60, 64):
                for x in range(20, 24):
                    self.img.putpixel((x, y), boot_col)
        if knee_col:
            # Knee pads
            for x in range(5, 7):
                self.img.putpixel((x, 25), knee_col)
                self.img.putpixel((x, 26), knee_col)
            for x in range(21, 23):
                self.img.putpixel((x, 57), knee_col)
                self.img.putpixel((x, 58), knee_col)

    def paint_legs_overlay(self, holsters_col):
        """Overlays on right leg (0, 32) and left leg (0, 48)."""
        # Tactical holster bands
        for x in range(4, 8):
            self.img.putpixel((x, 38), holsters_col)
        for x in range(4, 8):
            self.img.putpixel((x, 54), holsters_col)

    def save(self, filename):
        p1 = os.path.join(LOCAL_SKINS_DIR, filename)
        p2 = os.path.join(WEB_SKINS_DIR, filename)
        self.img.save(p1, format="PNG")
        self.img.save(p2, format="PNG")
        print(f"✓ Saved skin preset: {filename}")


def generate_all_skins():
    print("\n--- Curating 6 Premium PvP & Cyber Skins (64x64 RGBA) ---")

    # 1. sir_cyber_warrior.png (Steve Classic 4px)
    skin1 = SkinBuilder(is_slim=False)
    skin1.paint_head(hex_rgba("#d4a373"), hex_rgba("#111827"), hex_rgba("#00e5ff"))
    skin1.paint_head_overlay(hex_rgba("#0f172a"), hex_rgba("#00e5ff"))
    skin1.paint_torso(hex_rgba("#1e293b"), hex_rgba("#0f172a"), hex_rgba("#00e5ff"))
    skin1.paint_torso_overlay(hex_rgba("#0f172a", 180), hex_rgba("#00e5ff"))
    skin1.paint_arms(hex_rgba("#1e293b"), hex_rgba("#0f172a"), hex_rgba("#00e5ff"))
    skin1.paint_legs(hex_rgba("#0f172a"), hex_rgba("#0284c7"), hex_rgba("#00e5ff"))
    skin1.paint_legs_overlay(hex_rgba("#00e5ff"))
    skin1.save("sir_cyber_warrior.png")

    # 2. sir_neon_shadow.png (Alex Slim 3px)
    skin2 = SkinBuilder(is_slim=True)
    skin2.paint_head(hex_rgba("#c59b6d"), hex_rgba("#18181b"), hex_rgba("#d946ef"))
    skin2.paint_head_overlay(hex_rgba("#18181b"), hex_rgba("#d946ef"))
    skin2.paint_torso(hex_rgba("#09090b"), hex_rgba("#27272a"), hex_rgba("#a855f7"))
    skin2.paint_torso_overlay(hex_rgba("#18181b", 200), hex_rgba("#d946ef"))
    skin2.paint_arms(hex_rgba("#18181b"), hex_rgba("#09090b"), hex_rgba("#d946ef"))
    skin2.paint_legs(hex_rgba("#18181b"), hex_rgba("#27272a"), hex_rgba("#a855f7"))
    skin2.paint_legs_overlay(hex_rgba("#d946ef"))
    skin2.save("sir_neon_shadow.png")

    # 3. sir_emerald_ninja.png (Steve Classic 4px)
    skin3 = SkinBuilder(is_slim=False)
    skin3.paint_head(hex_rgba("#e0ac69"), hex_rgba("#064e3b"), hex_rgba("#10b981"))
    skin3.paint_head_overlay(hex_rgba("#022c22"), hex_rgba("#10b981"))
    skin3.paint_torso(hex_rgba("#064e3b"), hex_rgba("#047857"), hex_rgba("#34d399"))
    skin3.paint_torso_overlay(hex_rgba("#022c22", 190), hex_rgba("#10b981"))
    skin3.paint_arms(hex_rgba("#064e3b"), hex_rgba("#022c22"), hex_rgba("#10b981"))
    skin3.paint_legs(hex_rgba("#022c22"), hex_rgba("#059669"), hex_rgba("#34d399"))
    skin3.paint_legs_overlay(hex_rgba("#10b981"))
    skin3.save("sir_emerald_ninja.png")

    # 4. sir_void_walker.png (Steve Classic 4px)
    skin4 = SkinBuilder(is_slim=False)
    skin4.paint_head(hex_rgba("#b8a2cc"), hex_rgba("#2e1065"), hex_rgba("#ec4899"))
    skin4.paint_head_overlay(hex_rgba("#1e0a3d"), hex_rgba("#ec4899"))
    skin4.paint_torso(hex_rgba("#1e0a3d"), hex_rgba("#3b0764"), hex_rgba("#f43f5e"))
    skin4.paint_torso_overlay(hex_rgba("#2e1065", 190), hex_rgba("#c084fc"))
    skin4.paint_arms(hex_rgba("#2e1065"), hex_rgba("#1e0a3d"), hex_rgba("#ec4899"))
    skin4.paint_legs(hex_rgba("#1e0a3d"), hex_rgba("#581c87"), hex_rgba("#c084fc"))
    skin4.paint_legs_overlay(hex_rgba("#ec4899"))
    skin4.save("sir_void_walker.png")

    # 5. sir_esports_pro.png (Steve Classic 4px)
    skin5 = SkinBuilder(is_slim=False)
    skin5.paint_head(hex_rgba("#e8beac"), hex_rgba("#292524"), hex_rgba("#38bdf8"))
    skin5.paint_head_overlay(hex_rgba("#1c1917"), hex_rgba("#eab308")) # Golden gaming headset
    skin5.paint_torso(hex_rgba("#0c0a09"), hex_rgba("#eab308"), hex_rgba("#fde047")) # Esports jersey
    skin5.paint_torso_overlay(hex_rgba("#1c1917", 160), hex_rgba("#eab308"))
    skin5.paint_arms(hex_rgba("#1c1917"), hex_rgba("#0c0a09"), hex_rgba("#eab308"))
    skin5.paint_legs(hex_rgba("#1c1917"), hex_rgba("#f8fafc"), hex_rgba("#eab308"))
    skin5.paint_legs_overlay(hex_rgba("#eab308"))
    skin5.save("sir_esports_pro.png")

    # 6. sir_steve_tactical.png (Steve Classic 4px)
    skin6 = SkinBuilder(is_slim=False)
    skin6.paint_head(hex_rgba("#c59b6d"), hex_rgba("#4a3728"), hex_rgba("#3b82f6")) # Classic Steve tones
    skin6.paint_head_overlay(hex_rgba("#1e293b"), hex_rgba("#0284c7")) # Tactical comms headset
    skin6.paint_torso(hex_rgba("#0095a8"), hex_rgba("#1e293b"), hex_rgba("#38bdf8")) # Tactical cyan shirt with vest
    skin6.paint_torso_overlay(hex_rgba("#0f172a", 220), hex_rgba("#38bdf8"))
    skin6.paint_arms(hex_rgba("#0095a8"), hex_rgba("#0f172a"), hex_rgba("#38bdf8"))
    skin6.paint_legs(hex_rgba("#253a66"), hex_rgba("#0f172a"), hex_rgba("#475569")) # Tactical jeans & boots
    skin6.paint_legs_overlay(hex_rgba("#0f172a"))
    skin6.save("sir_steve_tactical.png")


def generate_all_avatars():
    print("\n--- Generating 48x48 Head Avatars for Presets ---")
    skins = [
        "sir_cyber_warrior",
        "sir_neon_shadow",
        "sir_emerald_ninja",
        "sir_void_walker",
        "sir_esports_pro",
        "sir_steve_tactical"
    ]
    for s in skins:
        skin_path = os.path.join(LOCAL_SKINS_DIR, f"{s}.png")
        if not os.path.isfile(skin_path):
            continue
        im = Image.open(skin_path).convert("RGBA")
        head_base = im.crop((8, 8, 16, 16))
        head_overlay = im.crop((40, 8, 48, 16))
        head = Image.alpha_composite(head_base, head_overlay)
        head_48 = head.resize((48, 48), resample=Image.Resampling.NEAREST)
        p1 = os.path.join(LOCAL_SKINS_DIR, f"avatar_{s}.png")
        p2 = os.path.join(WEB_SKINS_DIR, f"avatar_{s}.png")
        head_48.save(p1, format="PNG")
        head_48.save(p2, format="PNG")
        print(f"✓ Saved avatar preset: avatar_{s}.png")


if __name__ == "__main__":
    generate_all_capes()
    generate_all_skins()
    generate_all_avatars()
    print("\n✓ Successfully generated all 6 Capes, 6 Skins, and Avatars in local & web directories!")
