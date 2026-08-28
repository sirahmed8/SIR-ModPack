from PIL import Image
import os

brain = r'C:\Users\a7med\.gemini\antigravity\brain\a311e7e5-c0b6-47b7-bcf7-7dcc1dba5d4c'

# Find artwork files
artworks = {}
for f in os.listdir(brain):
    if not f.endswith('.jpg'):
        continue
    fl = f.lower()
    if 'balanced' in fl:
        artworks['balanced'] = os.path.join(brain, f)
    elif 'performance' in fl:
        artworks['performance'] = os.path.join(brain, f)
    elif 'visual' in fl:
        artworks['visual'] = os.path.join(brain, f)
    elif 'legacy' in fl:
        artworks['legacy'] = os.path.join(brain, f)
    elif 'icon' in fl and 'banner' not in fl and 'title' not in fl and 'cover' not in fl:
        artworks.setdefault('main_icon', os.path.join(brain, f))

print("Found artworks:", {k: os.path.basename(v) for k, v in artworks.items()})

def jpg_to_png(src, dest, size=(128,128)):
    img = Image.open(src).convert('RGBA')
    img = img.resize(size, Image.LANCZOS)
    img.save(dest, 'PNG', optimize=True)
    with open(dest, 'rb') as f:
        m = f.read(4)
    ok = m == bytes([0x89,0x50,0x4E,0x47])
    print(f'  Saved {os.path.basename(dest)}: PNG={ok} ({os.path.getsize(dest)} bytes)')

# Pack icons
if 'main_icon' in artworks:
    jpg_to_png(artworks['main_icon'], r'D:\resource pack\MyCustomPack_Modern_32x\pack.png')
    jpg_to_png(artworks['main_icon'], r'D:\resource pack\MyCustomPack_1.8.9_32x\pack.png')
    print()

# Profile icons - proper PNG conversion
profiles_base = r'C:\Users\a7med\.lunarclient\profiles'
profile_map = [
    ('aetheris-ultimate-modpack-modern-26.2', artworks.get('main_icon')),
    ('aetheris-ultimate-modern-balanced-26.2', artworks.get('balanced')),
    ('aetheris-ultimate-modern-performance-26.2', artworks.get('performance')),
    ('aetheris-ultimate-modern-visual-26.2', artworks.get('visual')),
    ('aetheris-ultimate-legacy-1.8.9', artworks.get('legacy')),
]

for profile, src in profile_map:
    if not src or not os.path.exists(src):
        print(f'  SKIP (no artwork): {profile}')
        continue
    profile_dir = os.path.join(profiles_base, profile)
    if not os.path.exists(profile_dir):
        print(f'  SKIP (no dir): {profile}')
        continue
    print(f'Converting {profile}:')
    jpg_to_png(src, os.path.join(profile_dir, 'icon.png'), (256, 256))
    jpg_to_png(src, os.path.join(profile_dir, 'featured_image.png'), (512, 288))

print('\nAll PNG conversions complete!')
