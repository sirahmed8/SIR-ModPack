import os

shader_dir = r"d:\shader\Aetheris_Shader_Pack\shaders"

def expand_file(file_path, visited=None):
    if visited is None:
        visited = set()
    if file_path in visited:
        return []
    visited.add(file_path)
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    out = []
    for line_idx, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#include \""):
            inc = s[len('#include "'):-1]
            inc_clean = inc.lstrip("/\\")
            inc_path = os.path.normpath(os.path.join(shader_dir, inc_clean))
            out.extend(expand_file(inc_path, visited))
        else:
            out.append((file_path, line_idx + 1, line))
    return out

expanded = expand_file(os.path.join(shader_dir, "world0", "composite.fsh"))
depth = 0
for global_idx, (fp, line_num, line) in enumerate(expanded):
    if "void main()" in line:
        print(f"[{global_idx}] {os.path.relpath(fp, shader_dir)}:{line_num} -> void main() at brace depth={depth}")
    o = line.count("{")
    c = line.count("}")
    depth += o - c

print(f"Final depth at end of composite.fsh = {depth}")
