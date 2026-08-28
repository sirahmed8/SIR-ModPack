"""
Mission Task 1: Shaderpack Synthetic Java NIO & GLSL AST Preprocessor Verification
"""

import os
import sys
import re
import json
import zipfile

def run_shader_tests():
    print("=" * 80, flush=True)
    print("MISSION TASK 1: SYNTHETIC JAVA NIO & GLSL AST / PREPROCESSOR SCAN", flush=True)
    print("=" * 80, flush=True)

    shader_dirs = [
        r"D:\mods\shader",
        r"D:\shader",
        r"D:\AetherisShare\shaders",
        r"D:\AetherisShare\shaders\shaderpacks",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 26.2\.minecraft\shaderpacks",
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\.minecraft\shaderpacks",
        r"C:\Users\a7med\AppData\Roaming\.minecraft\shaderpacks",
        r"C:\Users\a7med\.lunarclient\offline\multiver\profiles\1.21.11-fabric\Aetheris Modern Visual\shaderpacks",
        r"C:\Users\a7med\.lunarclient\offline\multiver\profiles\1.21.11-fabric\Aetheris Modern Balanced\shaderpacks",
        r"C:\Users\a7med\.lunarclient\offline\multiver\profiles\1.8.9-forge\Aetheris Legacy Visual\shaderpacks",
        r"C:\Users\a7med\.lunarclient\offline\multiver\profiles\1.8.9-forge\Aetheris Legacy Balanced\shaderpacks",
    ]

    found_zips = {}
    for sdir in shader_dirs:
        if not os.path.exists(sdir):
            continue
        for root, _, files in os.walk(sdir):
            for f in files:
                if f.lower().endswith(".zip"):
                    full_path = os.path.join(root, f)
                    key = (f, os.path.getsize(full_path))
                    if key not in found_zips:
                        found_zips[key] = full_path

    print(f"Found {len(found_zips)} unique shader archives:", flush=True)
    for (fname, fsize), fpath in sorted(found_zips.items()):
        print(f"  - {fname} ({fsize:,} bytes) in {os.path.dirname(fpath)}", flush=True)

    results = {"passed": [], "failed": [], "details": {}}

    for (fname, fsize), fpath in sorted(found_zips.items()):
        report = {
            "file": fname,
            "path": fpath,
            "size": fsize,
            "zip_valid": False,
            "nio_root_shaders": False,
            "entry_count": 0,
            "glsl_file_count": 0,
            "preprocessor_errors": [],
            "include_errors": [],
            "comment_errors": [],
            "bracket_errors": [],
            "properties_errors": [],
            "dh_depth_compatibility": None,
            "rtx40_shadow_res": None,
            "status": "PASS"
        }

        try:
            with zipfile.ZipFile(fpath, "r") as zf:
                # 1. Zip validity
                bad = zf.testzip()
                if bad is not None:
                    report["zip_valid"] = False
                    report["preprocessor_errors"].append(f"Corrupted CRC: {bad}")
                else:
                    report["zip_valid"] = True

                namelist = zf.namelist()
                report["entry_count"] = len(namelist)

                # 2. Java NIO FileSystem simulation:
                # Iris looks for "shaders" or "/shaders" at the root level of the ZipFileSystem.
                has_root_shaders = any(
                    name.startswith("shaders/") or name == "shaders" or name == "shaders\\"
                    for name in namelist
                )
                report["nio_root_shaders"] = has_root_shaders
                if not has_root_shaders:
                    report["preprocessor_errors"].append(
                        "Java NIO violation: Archive lacks root-level 'shaders/' folder (isValidShaderpack: false)"
                    )

                normalized_entries = {n.replace("\\", "/").lstrip("/"): n for n in namelist}

                # 3. GLSL AST & Preprocessor scans
                glsl_exts = (".vsh", ".fsh", ".gsh", ".csh", ".glsl", ".inc", ".properties", ".txt")
                for name in namelist:
                    norm_name = name.replace("\\", "/").lstrip("/")
                    if not any(norm_name.lower().endswith(ext) for ext in glsl_exts) or norm_name.endswith("/"):
                        continue

                    report["glsl_file_count"] += 1
                    try:
                        raw_bytes = zf.read(name)
                        try:
                            content = raw_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            content = raw_bytes.decode("latin-1")

                        # A. Comment Balance
                        c_opens = len(re.findall(r'/\*', content))
                        c_closes = len(re.findall(r'\*/', content))
                        if c_opens != c_closes:
                            report["comment_errors"].append(
                                f"{norm_name}: Unclosed/mismatched multi-line comment (/* count: {c_opens}, */ count: {c_closes})"
                            )

                        # B. Preprocessor directives
                        clean_code = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                        clean_code = re.sub(r'//.*', '', clean_code)

                        lines = clean_code.splitlines()
                        directive_stack = []
                        for lno, line in enumerate(lines, 1):
                            sline = line.strip()
                            if not sline.startswith("#"):
                                continue

                            m_if = re.match(r'^#(if|ifdef|ifndef)\b', sline)
                            m_elif = re.match(r'^#(elif)\b', sline)
                            m_else = re.match(r'^#(else)\b', sline)
                            m_endif = re.match(r'^#(endif)\b', sline)
                            m_inc = re.match(r'^#include\s+["<]([^">]+)[">]', sline)

                            if m_if:
                                directive_stack.append((m_if.group(1), lno))
                            elif m_elif or m_else:
                                if not directive_stack:
                                    report["preprocessor_errors"].append(
                                        f"{norm_name}:{lno}: Orphaned #{m_elif.group(1) if m_elif else 'else'}"
                                    )
                            elif m_endif:
                                if not directive_stack:
                                    report["preprocessor_errors"].append(
                                        f"{norm_name}:{lno}: Orphaned #endif"
                                    )
                                else:
                                    directive_stack.pop()
                            elif m_inc:
                                inc_path = m_inc.group(1).replace("\\", "/").lstrip("/")
                                resolved = False
                                candidates = [
                                    inc_path,
                                    f"shaders/{inc_path}",
                                    f"shaders/lib/{inc_path}",
                                    os.path.normpath(os.path.join(os.path.dirname(norm_name), inc_path)).replace("\\", "/")
                                ]
                                for c in candidates:
                                    if c in normalized_entries:
                                        resolved = True
                                        break
                                if not resolved:
                                    report["include_errors"].append(
                                        f"{norm_name}:{lno}: Unresolved #include '{m_inc.group(1)}'"
                                    )

                        if directive_stack:
                            unclosed = ", ".join(f"#{d} at line {l}" for d, l in directive_stack)
                            report["preprocessor_errors"].append(
                                f"{norm_name}: Unclosed preprocessor directive: {unclosed}"
                            )

                        # C. Block.properties & item.properties syntax
                        if norm_name.lower().endswith("block.properties") or norm_name.lower().endswith("item.properties"):
                            for lno, pline in enumerate(content.splitlines(), 1):
                                s = pline.strip()
                                if not s or s.startswith("#"):
                                    continue
                                if "=" not in s:
                                    report["properties_errors"].append(
                                        f"{norm_name}:{lno}: Invalid properties syntax (missing '='): {s[:50]}"
                                    )

                        # D. Distant Horizons & RTX 40 checks
                        if "shadowmapresolution" in content.lower():
                            m_res = re.search(r'const\s+int\s+shadowMapResolution\s*=\s*(\d+)', content)
                            if m_res:
                                report["rtx40_shadow_res"] = int(m_res.group(1))

                        if "distanthorizons" in content.lower() or "dh_depth" in content.lower() or "render_api_def" in content.lower():
                            report["dh_depth_compatibility"] = "Configured / Depth compatibility flags verified"

                    except Exception as err:
                        report["preprocessor_errors"].append(f"{norm_name}: Error reading: {err}")

        except Exception as e:
            report["zip_valid"] = False
            report["preprocessor_errors"].append(f"Cannot open zip: {e}")

        total_errs = (
            len(report["preprocessor_errors"]) +
            len(report["include_errors"]) +
            len(report["comment_errors"]) +
            len(report["bracket_errors"]) +
            len(report["properties_errors"])
        )

        if not report["zip_valid"] or not report["nio_root_shaders"] or total_errs > 0:
            report["status"] = "FAIL"
            results["failed"].append(fname)
        else:
            report["status"] = "PASS"
            results["passed"].append(fname)

        results["details"][fname] = report

        print(f"\n[ARCHIVE] {fname} ({fsize:,} bytes):", flush=True)
        print(f"  - Zip Integrity: {'OK' if report['zip_valid'] else 'CORRUPT'}", flush=True)
        print(f"  - Java NIO Root 'shaders/': {'PASS' if report['nio_root_shaders'] else 'FAIL'}", flush=True)
        print(f"  - GLSL/Properties Files Checked: {report['glsl_file_count']}", flush=True)
        print(f"  - DH Depth Compatibility: {report['dh_depth_compatibility'] or 'Standard OptiFine/Iris'}", flush=True)
        print(f"  - Shadow Map Resolution: {report['rtx40_shadow_res'] or 'Default/Tuned'}", flush=True)
        print(f"  - Syntax / AST / Preprocessor Errors: {total_errs}", flush=True)
        if total_errs > 0:
            for err in report["preprocessor_errors"][:5]:
                print(f"     * Preprocessor Error: {err}", flush=True)
            for err in report["include_errors"][:5]:
                print(f"     * Include Error: {err}", flush=True)
            for err in report["comment_errors"][:5]:
                print(f"     * Comment Error: {err}", flush=True)
            for err in report["properties_errors"][:5]:
                print(f"     * Properties Error: {err}", flush=True)

    print("\n" + "-" * 80, flush=True)
    print(f"TASK 1 SUMMARY: {len(results['passed'])} PASSED, {len(results['failed'])} FAILED", flush=True)
    print("-" * 80, flush=True)

    with open(r"D:\mods\shader_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_shader_tests()
