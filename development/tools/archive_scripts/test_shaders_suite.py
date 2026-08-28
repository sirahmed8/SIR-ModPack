"""
Automated Comprehensive Validation Test Suite for Shader Architecture & Compatibility Pipeline (Worker M2)
"""

import os, sys, zipfile, hashlib, re

def run_suite():
    print("=" * 70)
    print("  AETHERIS SHADER ARCHITECTURE & COMPATIBILITY VERIFICATION SUITE")
    print("=" * 70)
    
    failures = []
    
    # 1. Java NIO isValidShaderpack Test
    print("\n[TEST 1] Java NIO isValidShaderpack Evaluation...")
    checked_zips = 0
    search_dirs = [
        r'D:\shader',
        r'D:\mods\shader',
        r'D:\AetherisShare\shaders',
        r'D:\AetherisShare\shaders\shaderpacks',
        r'C:\Users\a7med\AppData\Roaming\.minecraft\shaderpacks',
        r'C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\shaderpacks',
        r'C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\minecraft\shaderpacks',
        r'C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\.minecraft\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-visual-1.8.9\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-balanced-1.8.9\shaderpacks',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-performance-1.8.9\shaderpacks',
        r'D:\AetherisShare\profiles\visual\shaderpacks',
        r'D:\AetherisShare\profiles\balanced\shaderpacks',
        r'D:\AetherisShare\profiles\performance\shaderpacks',
        r'D:\AetherisShare\profiles\modpack\shaderpacks',
        r'D:\AetherisShare\profiles\legacy\shaderpacks',
        r'D:\AetherisShare\profiles\legacy-visual\shaderpacks',
        r'D:\AetherisShare\profiles\legacy-balanced\shaderpacks',
        r'D:\AetherisShare\profiles\legacy-performance\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-modern-visual-26.2\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-modern-balanced-26.2\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-modern-performance-26.2\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-modpack-modern-26.2\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-legacy-1.8.9\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-legacy-visual-1.8.9\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-legacy-balanced-1.8.9\shaderpacks',
        r'D:\AetherisShare\lunar_profiles\aetheris-ultimate-legacy-performance-1.8.9\shaderpacks',
    ]
    
    # Collect all shader archives dynamically across instances & share roots
    all_shader_archives = []
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith('.zip') or f.endswith('.zip.disabled'):
                all_shader_archives.append(os.path.join(d, f))
                
    all_shader_archives = sorted(list(set(all_shader_archives)))
    
    for fp in all_shader_archives:
        checked_zips += 1
        try:
            with zipfile.ZipFile(fp, 'r') as zf:
                names = zf.namelist()
                has_root_shaders = any(n.startswith('shaders/') for n in names)
                has_backslash = any('\\' in n for n in names)
                top_dirs = set(n.split('/')[0] for n in names if '/' in n)
                if not has_root_shaders or has_backslash:
                    msg = f"Java NIO FAIL: {fp} (has_root_shaders={has_root_shaders}, bs={has_backslash}, top={top_dirs})"
                    print(f"  [X] {msg}")
                    failures.append(msg)
                else:
                    # print(f"  [OK] {os.path.basename(fp)} in {os.path.basename(os.path.dirname(fp))}")
                    pass
        except Exception as e:
            msg = f"Corrupt ZIP: {fp} ({e})"
            print(f"  [X] {msg}")
            failures.append(msg)
                    
    print(f"  -> Checked {checked_zips} shader archives across all instances. (Failures: {len(failures)})")
    
    # 2. GLSL AST & Preprocessor Cleanliness Test
    print("\n[TEST 2] GLSL Preprocessor and block.properties Cleanliness across ALL Deployed Shaders...")
    glsl_checked = 0
    prop_checked = 0
    
    def check_glsl_proper(content):
        no_line_comments = re.sub(r'//.*', '', content)
        no_block_comments = re.sub(r'/\*.*?\*/', lambda m: '\n' * m.group(0).count('\n'), no_line_comments, flags=re.DOTALL)
        lines = [l.strip() for l in no_block_comments.splitlines()]
        ifs = [l for l in lines if re.match(r'^#\s*(if|ifdef|ifndef)\b', l)]
        endifs = [l for l in lines if re.match(r'^#\s*endif\b', l)]
        return len(ifs), len(endifs)
    
    for p in all_shader_archives:
        if not os.path.exists(p):
            failures.append(f"Missing shader pack: {p}")
            continue
        try:
            with zipfile.ZipFile(p, 'r') as zf:
                for n in zf.namelist():
                    if n.endswith(('.vsh', '.fsh', '.gsh', '.csh', '.glsl')):
                        glsl_checked += 1
                        data = zf.read(n).decode('utf-8', errors='ignore')
                        ifs, endifs = check_glsl_proper(data)
                        if ifs != endifs:
                            msg = f"GLSL Mismatch in {p}:{n} (#if={ifs} vs #endif={endifs})"
                            print(f"  [X] {msg}")
                            failures.append(msg)
                    elif n.endswith('.properties') and 'block' in n:
                        prop_checked += 1
                        data = zf.read(n).decode('utf-8', errors='ignore')
                        for line in data.splitlines():
                            line_clean = line.strip()
                            if line_clean and not line_clean.startswith('#') and '=' in line_clean:
                                k, v = line_clean.split('=', 1)
                                if re.search(r':\s*\d+\s*(,\s*\d+)+', v):
                                    msg = f"Legacy Comma in {p}:{n} -> {line_clean}"
                                    print(f"  [X] {msg}")
                                    failures.append(msg)
        except Exception as e:
            failures.append(f"Error checking {p}: {e}")
                                
    print(f"  -> Checked {glsl_checked} GLSL files and {prop_checked} block properties files across {len(all_shader_archives)} archives. (Failures: {len(failures)})")
    
    # 3. RTX 40-Series Mobile & High-Refresh Tuning Test
    print("\n[TEST 3] RTX 40-Series Mobile Tuning Configuration Test...")
    presets = {
        'Visual': r'D:\shader\Aetheris_Visual_Shader.zip.txt',
        'Balanced': r'D:\shader\Aetheris_Balanced_Shader.zip.txt',
        'Extreme': r'D:\shader\Aetheris_Extreme_Shader.zip.txt',
        'Shader_Pack': r'D:\shader\Aetheris_Shader_Pack.zip.txt',
        'Legacy': r'D:\shader\Aetheris_Legacy_Shader_Pack.zip.txt',
    }
    
    for name, path in presets.items():
        if not os.path.exists(path):
            failures.append(f"Missing preset config: {path}")
            continue
        content = open(path).read()
        if name == 'Balanced':
            if 'shadowMapResolution=2048' not in content and 'shadowMapResolution=1536' not in content:
                failures.append(f"Balanced missing shadowMapResolution setting")
            if 'VL_SAMPLES=6' not in content:
                failures.append(f"Balanced missing VL_SAMPLES=6")
        elif name == 'Visual':
            if 'shadowMapResolution=4096' not in content and 'shadowMapResolution=2048' not in content:
                failures.append(f"Visual missing shadowMapResolution setting")
            if 'VL_SAMPLES=12' not in content:
                failures.append(f"Visual missing VL_SAMPLES=12")
        elif name == 'Legacy':
            if 'shadowMapResolution=' not in content:
                failures.append(f"Legacy missing shadowMapResolution setting")
                
    print(f"  -> Verified 5 RTX 40-Series Mobile Presets. (Failures: {len(failures)})")
    
    # 4. Instant Shader Toggle ('K') & Keybind Audit
    print("\n[TEST 4] Keybinding Conflict and Iris Properties Audit...")
    modern_opts = [
        r'C:\Users\a7med\AppData\Roaming\.minecraft\options.txt',
        r'C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\options.txt',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\options.txt',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\options.txt',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\options.txt',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\options.txt',
    ]
    
    for opt in modern_opts:
        if not os.path.exists(opt):
            continue
        txt = open(opt).read()
        if 'key_iris.keybind.toggleShaders:key.keyboard.k' not in txt:
            failures.append(f"Missing Iris toggle 'K' in {opt}")
        if 'key_key.craftingtweaks.compress_one:key.keyboard.k' in txt or \
           'key_key.craftingtweaks.compress_stack:key.keyboard.k' in txt or \
           'key_key.craftingtweaks.compress_all:key.keyboard.k' in txt:
            failures.append(f"CraftingTweaks 'K' collision detected in {opt}")
            
    iris_props = [
        r'C:\Users\a7med\AppData\Roaming\.minecraft\config\iris.properties',
        r'C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\26.2\minecraft\config\iris.properties',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\config\iris.properties',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\config\iris.properties',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\config\iris.properties',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\config\iris.properties',
    ]
    
    for ip in iris_props:
        if not os.path.exists(ip):
            continue
        txt = open(ip).read()
        if 'allowUnknownShaders=true' not in txt:
            failures.append(f"allowUnknownShaders != true in {ip}")
        if 'enableShaders=true' not in txt:
            failures.append(f"enableShaders != true in {ip}")
            
    print(f"  -> Audited {len(modern_opts)} options.txt and {len(iris_props)} iris.properties files. (Failures: {len(failures)})")
    
    # 5. Legacy 1.8.9 Synchronization Audit
    print("\n[TEST 5] Legacy 1.8.9 Shader & Options Parity Audit...")
    legacy_zip_src = r'D:\shader\Aetheris_Legacy_Shader_Pack.zip'
    src_hash = hashlib.sha256(open(legacy_zip_src, 'rb').read()).hexdigest()
    
    legacy_destinations = [
        r'D:\mods\shader\Aetheris_Legacy_Shader_Pack.zip',
        r'D:\AetherisShare\shaders\Aetheris_Legacy_Shader_Pack.zip',
        r'C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\minecraft\shaderpacks\Aetheris_Legacy_Shader_Pack.zip',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9\shaderpacks\Aetheris_Legacy_Shader_Pack.zip',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-visual-1.8.9\shaderpacks\Aetheris_Legacy_Shader_Pack.zip',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-balanced-1.8.9\shaderpacks\Aetheris_Legacy_Shader_Pack.zip',
        r'C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-performance-1.8.9\shaderpacks\Aetheris_Legacy_Shader_Pack.zip',
    ]
    
    for dst in legacy_destinations:
        if not os.path.exists(dst):
            failures.append(f"Missing legacy shader zip: {dst}")
            continue
        dst_hash = hashlib.sha256(open(dst, 'rb').read()).hexdigest()
        if dst_hash != src_hash:
            failures.append(f"Legacy shader hash mismatch in {dst} (got {dst_hash[:8]}, expected {src_hash[:8]})")
            
    print(f"  -> Verified 1.8.9 Legacy Shader parity across {len(legacy_destinations)} instances. (Failures: {len(failures)})")
    
    print("\n" + "=" * 70)
    if not failures:
        print("  ALL VERIFICATION TESTS PASSED: 100% COMPLIANT & SYNCHRONIZED!")
        print("=" * 70)
        return True
    else:
        print(f"  TESTS FAILED WITH {len(failures)} VIOLATIONS:")
        for f in failures:
            print(f"    - {f}")
        print("=" * 70)
        return False

if __name__ == '__main__':
    success = run_suite()
    sys.exit(0 if success else 1)
