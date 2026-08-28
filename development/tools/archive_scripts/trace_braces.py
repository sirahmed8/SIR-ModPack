import os

shader_dir = r"d:\shader\Aetheris_Shader_Pack\shaders"

def trace_includes(file_path, depth=0):
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    local_open = 0
    local_close = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#include \""):
            inc = s[len('#include "'):-1]
            inc_clean = inc.lstrip("/\\")
            inc_path = os.path.normpath(os.path.join(shader_dir, inc_clean))
            print("  " * depth + f"-> {inc} (at line {i+1})")
            trace_includes(inc_path, depth + 1)
        else:
            local_open += line.count("{")
            local_close += line.count("}")
    
    diff = local_open - local_close
    if diff != 0:
        print("  " * depth + f"** MISMATCH in {os.path.relpath(file_path, shader_dir)}: open={local_open}, close={local_close}, diff={diff} **")

trace_includes(os.path.join(shader_dir, "world0", "composite.fsh"))
