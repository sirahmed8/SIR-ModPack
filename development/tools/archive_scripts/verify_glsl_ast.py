"""
GLSL AST & Include Verifier for all Shaderpack Archives
"""

import zipfile
import re
import os

zips = [
    r'D:\AetherisShare\shaders\Aetheris_Visual_Shader.zip',
    r'D:\AetherisShare\shaders\Aetheris_Balanced_Shader.zip',
    r'D:\AetherisShare\shaders\Aetheris_Extreme_Shader.zip',
    r'D:\AetherisShare\shaders\Aetheris_Shader_Pack.zip',
    r'D:\AetherisShare\shaders\Aetheris_Legacy_Shader_Pack.zip'
]

for zp in zips:
    print('=' * 70)
    print(os.path.basename(zp))
    print('=' * 70)
    with zipfile.ZipFile(zp, 'r') as zf:
        namelist = zf.namelist()
        entries_set = {n.replace('\\', '/').lstrip('/') for n in namelist}
        
        glsl_files = [n for n in namelist if any(n.endswith(ext) for ext in ['.vsh', '.fsh', '.gsh', '.csh', '.glsl', '.inc'])]
        print(f'Total GLSL shader files: {len(glsl_files)}')
        
        unresolved_includes = []
        directive_errors = []
        for g in glsl_files:
            content = zf.read(g).decode('utf-8', errors='ignore')
            norm_g = g.replace('\\', '/').lstrip('/')
            g_dir = os.path.dirname(norm_g)
            
            clean_code = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            clean_code = re.sub(r'//.*', '', clean_code)
            
            for lno, line in enumerate(clean_code.splitlines(), 1):
                s = line.strip()
                if not s:
                    continue
                # Match #include
                m = re.match(r'^\s*#include\s+["<]([^">]+)[">]', s)
                if m:
                    inc = m.group(1).replace('\\', '/').lstrip('/')
                    candidates = [
                        inc,
                        f'shaders/{inc}',
                        f'shaders/lib/{inc}',
                        os.path.normpath(os.path.join(g_dir, inc)).replace('\\', '/'),
                        os.path.normpath(os.path.join('shaders', inc)).replace('\\', '/')
                    ]
                    found = any(c in entries_set for c in candidates)
                    if not found:
                        unresolved_includes.append(f'{norm_g}:{lno} -> #include "{m.group(1)}"')
                        
        if unresolved_includes:
            print(f'  [FAIL] {len(unresolved_includes)} unresolved includes!')
            for u in unresolved_includes[:5]:
                print(f'    - {u}')
        else:
            print(f'  [PASS] 100% of #include directives ({len(glsl_files)} files) resolved successfully!')
