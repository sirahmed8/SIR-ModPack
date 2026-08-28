import os

shader_dir = r"d:\shader\Aetheris_Shader_Pack\shaders"

def expand_includes(file_path, visited=None):
    if visited is None:
        visited = set()
    if file_path in visited:
        return ""
    visited.add(file_path)
    if not os.path.exists(file_path):
        print("MISSING FILE:", file_path)
        return ""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    out = []
    for line in lines:
        s = line.strip()
        if s.startswith("#include \""):
            inc = s[len('#include "'):-1]
            inc_clean = inc.lstrip("/\\")
            inc_path = os.path.normpath(os.path.join(shader_dir, inc_clean))
            out.append(expand_includes(inc_path, visited))
        else:
            out.append(line)
    return "".join(out)

for prog in ["composite.fsh", "composite.vsh", "composite1.fsh", "composite2.fsh", "composite3.fsh", "gbuffers_terrain.fsh", "gbuffers_water.fsh"]:
    fp = os.path.join(shader_dir, "world0", prog)
    if os.path.exists(fp):
        expanded = expand_includes(fp, set())
        open_braces = expanded.count("{")
        close_braces = expanded.count("}")
        print(f"{prog}: lines={len(expanded.splitlines())}, open_braces={open_braces}, close_braces={close_braces}, diff={open_braces - close_braces}")
