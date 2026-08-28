import os

shader_dir = r"d:\shader\Aetheris_Shader_Pack\shaders"

def expand_file_with_defines(file_path, defines, visited=None):
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
    for line_num, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#include \""):
            inc = s[len('#include "'):-1].lstrip("/\\")
            inc_path = os.path.normpath(os.path.join(shader_dir, inc))
            out.extend(expand_file_with_defines(inc_path, defines, visited))
        else:
            out.append((file_path, line_num + 1, line))
    return out

defines = {"OVERWORLD": True, "FRAGMENT_SHADER": True, "COMPOSITE": True, "SHADOW_QUALITY": "5", "RP_MODE": "2"}
exp = expand_file_with_defines(os.path.join(shader_dir, "world0", "composite.fsh"), defines)

brace_depth = 0
for idx, (fp, line_num, line) in enumerate(exp):
    s = line.strip()
    # If not a preprocessor directive and not comment
    if not s.startswith("#") and not s.startswith("//") and not s.startswith("/*") and len(s) > 0:
        if brace_depth == 0 and (s.startswith("if") or s.startswith("for") or s.startswith("while")):
            print(f"EXTRANEOUS STATEMENT AT GLOBAL SCOPE: line {idx+1} ({os.path.relpath(fp, shader_dir)}:{line_num}): {s}")
    brace_depth += line.count("{") - line.count("}")

print(f"Total lines: {len(exp)}, final brace depth: {brace_depth}")
