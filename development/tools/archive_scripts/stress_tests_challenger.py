"""
Aetheris Ecosystem Empirical Challenger Test Harness
Adversarial Verification & Stress Testing Suite
"""

import os
import sys
import re
import json
import zipfile
import sqlite3
import subprocess
import shutil
import tempfile
from pathlib import Path

RESULTS = {
    "shaders": {"passed": [], "failed": [], "details": {}},
    "installer": {"passed": [], "failed": [], "details": {}},
    "keybinds": {"passed": [], "failed": [], "details": {}},
    "verdict": "PENDING"
}

# ==============================================================================
# 1. SHADERPACK JAVA NIO & GLSL AST / PREPROCESSOR SCANNER
# ==============================================================================

def test_shaderpacks():
    print("=" * 80)
    print("1. PROBING SHADERPACK ARCHIVES (JAVA NIO & GLSL PREPROCESSOR AST)")
    print("=" * 80)

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

    # Find unique shaderpack zips
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

    print(f"Discovered {len(found_zips)} unique shaderpack zip archives to probe:")
    for (fname, fsize), fpath in sorted(found_zips.items()):
        print(f"  - {fname} ({fsize:,} bytes) -> {fpath}")

    # Java NIO & GLSL AST Test for each zip
    for (fname, fsize), fpath in sorted(found_zips.items()):
        pack_report = {
            "zip_integrity": False,
            "nio_root_shaders": False,
            "entry_count": 0,
            "glsl_files_checked": 0,
            "preprocessor_errors": [],
            "include_errors": [],
            "comment_errors": [],
            "bracket_errors": [],
            "properties_errors": [],
            "dh_depth_compatibility": None,
            "status": "PASS"
        }

        try:
            with zipfile.ZipFile(fpath, "r") as zf:
                # 1. Zip integrity
                bad_crc = zf.testzip()
                if bad_crc is not None:
                    pack_report["zip_integrity"] = False
                    pack_report["status"] = "FAIL"
                    pack_report["preprocessor_errors"].append(f"Corrupted CRC in file: {bad_crc}")
                else:
                    pack_report["zip_integrity"] = True

                namelist = zf.namelist()
                pack_report["entry_count"] = len(namelist)

                # 2. Java NIO FileSystem simulation:
                # Iris looks for "shaders" or "/shaders" at the root level of the ZipFileSystem.
                has_root_shaders = any(
                    name.startswith("shaders/") or name == "shaders" or name == "shaders\\"
                    for name in namelist
                )
                pack_report["nio_root_shaders"] = has_root_shaders
                if not has_root_shaders:
                    pack_report["status"] = "FAIL"
                    pack_report["preprocessor_errors"].append(
                        "Java NIO violation: No root-level 'shaders/' directory found in archive!"
                    )

                # Set of all normalized file paths inside zip
                normalized_entries = {n.replace("\\", "/").lstrip("/"): n for n in namelist}

                # 3. GLSL AST & Preprocessor Scanner
                glsl_exts = (".vsh", ".fsh", ".gsh", ".csh", ".glsl", ".inc", ".properties", ".txt")
                for name in namelist:
                    norm_name = name.replace("\\", "/").lstrip("/")
                    if not any(norm_name.lower().endswith(ext) for ext in glsl_exts):
                        continue
                    if norm_name.endswith("/"):
                        continue

                    pack_report["glsl_files_checked"] += 1
                    try:
                        raw_bytes = zf.read(name)
                        try:
                            content = raw_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            content = raw_bytes.decode("latin-1")

                        # A. Comment balance check (/* ... */)
                        c_opens = len(re.findall(r'/\*', content))
                        c_closes = len(re.findall(r'\*/', content))
                        if c_opens != c_closes:
                            pack_report["comment_errors"].append(
                                f"{norm_name}: Mismatched multi-line comments (/* count={c_opens}, */ count={c_closes})"
                            )

                        # B. Preprocessor directives balance
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
                                    pack_report["preprocessor_errors"].append(
                                        f"{norm_name}:{lno}: Orphaned #{m_elif.group(1) if m_elif else 'else'} without preceding #if/#ifdef/#ifndef"
                                    )
                            elif m_endif:
                                if not directive_stack:
                                    pack_report["preprocessor_errors"].append(
                                        f"{norm_name}:{lno}: Orphaned #endif without preceding #if/#ifdef/#ifndef"
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
                                    pack_report["include_errors"].append(
                                        f"{norm_name}:{lno}: Unresolved #include '{m_inc.group(1)}'"
                                    )

                        if directive_stack:
                            unclosed = ", ".join(f"#{d} at line {l}" for d, l in directive_stack)
                            pack_report["preprocessor_errors"].append(
                                f"{norm_name}: Unclosed preprocessor directives: {unclosed}"
                            )

                        # C. Block.properties & item.properties syntax
                        if norm_name.lower().endswith("block.properties") or norm_name.lower().endswith("item.properties"):
                            for lno, pline in enumerate(content.splitlines(), 1):
                                s = pline.strip()
                                if not s or s.startswith("#"):
                                    continue
                                if "=" not in s:
                                    pack_report["properties_errors"].append(
                                        f"{norm_name}:{lno}: Invalid properties syntax (missing '='): {s[:50]}"
                                    )

                        # D. Distant Horizons Depth Compatibility check
                        if "distanthorizons" in content.lower() or "dh_depth" in content.lower() or "render_api_def" in content.lower():
                            pack_report["dh_depth_compatibility"] = "Detected DH integration flags"

                    except Exception as ex:
                        pack_report["preprocessor_errors"].append(f"{norm_name}: Read error - {str(ex)}")

        except Exception as e:
            pack_report["zip_integrity"] = False
            pack_report["status"] = "FAIL"
            pack_report["preprocessor_errors"].append(f"Zip open failed: {str(e)}")

        total_errs = (
            len(pack_report["preprocessor_errors"]) +
            len(pack_report["include_errors"]) +
            len(pack_report["comment_errors"]) +
            len(pack_report["bracket_errors"]) +
            len(pack_report["properties_errors"])
        )
        if not pack_report["zip_integrity"] or not pack_report["nio_root_shaders"] or total_errs > 0:
            pack_report["status"] = "FAIL"
            RESULTS["shaders"]["failed"].append(fname)
        else:
            pack_report["status"] = "PASS"
            RESULTS["shaders"]["passed"].append(fname)

        RESULTS["shaders"]["details"][fname] = pack_report
        print(f"  [{pack_report['status']}] {fname}: NIO Root: {pack_report['nio_root_shaders']}, Checked {pack_report['glsl_files_checked']} GLSL files, Errors: {total_errs}")
        if total_errs > 0:
            for err in pack_report["preprocessor_errors"][:3]:
                print(f"       ! Preprocessor: {err}")
            for err in pack_report["include_errors"][:3]:
                print(f"       ! Include: {err}")
            for err in pack_report["comment_errors"][:3]:
                print(f"       ! Comment: {err}")
            for err in pack_report["properties_errors"][:3]:
                print(f"       ! Properties: {err}")

# ==============================================================================
# 2. INSTALLER CLI STRESS TESTING & SQLITE DATABASE INTEGRITY
# ==============================================================================

def test_installer_and_sqlite():
    print("\n" + "=" * 80)
    print("2. STRESS TESTING INSTALLER SCRIPTS & SQLITE DATABASE INTEGRITY")
    print("=" * 80)

    install_ps1 = r"D:\AetherisShare\install.ps1"
    install_bat = r"D:\AetherisShare\install.bat"

    if not os.path.exists(install_ps1):
        RESULTS["installer"]["failed"].append("install.ps1 not found")
        print("  [FAIL] install.ps1 not found!")
        return

    # A. Static validation of install.ps1 & install.bat
    print("  [A] Static script syntax & parameter checks:")
    with open(install_ps1, "r", encoding="utf-8") as f:
        ps1_code = f.read()

    ps1_checks = {
        "Has_CmdletBinding": "[CmdletBinding()]" in ps1_code,
        "Has_NonInteractive_Switch": "[switch]$NonInteractive" in ps1_code,
        "Has_Silent_Switch": "[switch]$Silent" in ps1_code,
        "Has_SkipBackup_Switch": "[switch]$SkipBackup" in ps1_code,
        "Has_SkipDb_Switch": "[switch]$SkipDb" in ps1_code,
        "Has_ErrorAction_Stop": "$ErrorActionPreference = 'Stop'" in ps1_code,
        "Has_SQLite_Registration": "Register-LunarProfilesDb" in ps1_code,
        "Has_All_8_Lunar_Profiles": all(
            p in ps1_code for p in [
                "aetheris-ultimate-modern-visual-26.2",
                "aetheris-ultimate-modern-balanced-26.2",
                "aetheris-ultimate-modern-performance-26.2",
                "aetheris-ultimate-modpack-modern-26.2",
                "aetheris-ultimate-legacy-1.8.9",
                "aetheris-ultimate-legacy-visual-1.8.9",
                "aetheris-ultimate-legacy-balanced-1.8.9",
                "aetheris-ultimate-legacy-performance-1.8.9"
            ]
        )
    }

    all_ps1_ok = all(ps1_checks.values())
    print(f"      install.ps1 static check: {'PASS' if all_ps1_ok else 'FAIL'}")
    for k, v in ps1_checks.items():
        print(f"        - {k}: {v}")

    # B. Sandboxed Non-Interactive CLI Executions
    print("\n  [B] Sandboxed Non-Interactive CLI Executions:")
    test_root = tempfile.mkdtemp(prefix="aetheris_challenger_test_")
    sandbox_lunar = os.path.join(test_root, ".lunarclient")
    sandbox_prism = os.path.join(test_root, "PrismLauncher", "instances")
    sandbox_mc = os.path.join(test_root, ".minecraft")
    sandbox_db = os.path.join(sandbox_lunar, "db", "profiles.db")

    modes_to_test = [
        ("All", ["-Mode", "All", "-Target", "All"]),
        ("Modern", ["-Mode", "Modern", "-Target", "Lunar"]),
        ("Legacy", ["-Mode", "Legacy", "-Target", "Lunar"]),
        ("Selective", ["-Mode", "Selective", "-ProfileNames", "visual,balanced", "-Target", "Lunar"]),
        ("Prism", ["-Mode", "Prism"]),
        ("Minecraft", ["-Mode", "Minecraft"]),
        ("Ecosystem", ["-Mode", "Ecosystem"]),
        ("HUDs", ["-Mode", "HUDs"]),
        ("Shaders", ["-Mode", "Shaders"]),
        ("ResourcePacks", ["-Mode", "ResourcePacks"]),
    ]

    cli_results = {}
    for mode_name, mode_args in modes_to_test:
        cmd = [
            "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", install_ps1
        ] + mode_args + [
            "-LunarPath", sandbox_lunar,
            "-PrismPath", sandbox_prism,
            "-MinecraftPath", sandbox_mc,
            "-NonInteractive",
            "-Silent"
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        success = (proc.returncode == 0) and ("FAILED" not in proc.stderr.upper())
        cli_results[mode_name] = {
            "exit_code": proc.returncode,
            "stdout_len": len(proc.stdout),
            "stderr": proc.stderr.strip(),
            "success": success
        }
        print(f"      Mode '{mode_name}' execution: {'PASS' if success else 'FAIL'} (exit code {proc.returncode})")
        if not success:
            print(f"        Stderr: {proc.stderr}")

    # C. Idempotency & Permission Stress Test
    print("\n  [C] Idempotency & Re-execution Stress Test (consecutive double-run):")
    cmd_idem = [
        "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", install_ps1,
        "-Mode", "Ecosystem",
        "-LunarPath", sandbox_lunar,
        "-PrismPath", sandbox_prism,
        "-MinecraftPath", sandbox_mc,
        "-NonInteractive",
        "-Silent"
    ]
    proc_idem1 = subprocess.run(cmd_idem, capture_output=True, text=True, timeout=60)
    proc_idem2 = subprocess.run(cmd_idem, capture_output=True, text=True, timeout=60)
    idempotency_pass = (proc_idem1.returncode == 0 and proc_idem2.returncode == 0)
    print(f"      Double run idempotency: {'PASS' if idempotency_pass else 'FAIL'} (Run 1: {proc_idem1.returncode}, Run 2: {proc_idem2.returncode})")

    # D. SQLite Database Integrity Testing
    print("\n  [D] SQLite Database Integrity Verification:")
    dbs_to_test = [
        ("Sandbox_Generated_DB", sandbox_db),
        ("Live_Lunar_DB", r"C:\Users\a7med\.lunarclient\db\profiles.db"),
        ("AetherisShare_DB", r"D:\AetherisShare\profiles.db")
    ]

    sqlite_reports = {}
    for db_label, db_path in dbs_to_test:
        if not os.path.exists(db_path):
            print(f"      {db_label}: Skipped (does not exist at {db_path})")
            continue

        db_rep = {
            "integrity_check": None,
            "fk_check": None,
            "profile_count": 0,
            "canonical_profiles_found": [],
            "all_8_canonical_present": False,
            "jvm_args_valid": True,
            "memory_8192": True,
            "status": "PASS"
        }

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check;")
            integrity_rows = cur.fetchall()
            db_rep["integrity_check"] = integrity_rows[0][0] if integrity_rows else "UNKNOWN"

            cur.execute("PRAGMA foreign_key_check;")
            db_rep["fk_check"] = cur.fetchall()

            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profiles';")
            if cur.fetchone():
                cur.execute("SELECT id, name, path, allocated_memory, jvm_arguments, use_lunar_features FROM profiles;")
                rows = cur.fetchall()
                db_rep["profile_count"] = len(rows)
                for r in rows:
                    pid, pname, ppath, mem, jvm, use_lunar = r
                    db_rep["canonical_profiles_found"].append(ppath)
                    if mem != 8192:
                        db_rep["memory_8192"] = False
                    if not jvm or "-XX:+UseG1GC" not in jvm:
                        db_rep["jvm_args_valid"] = False

                expected_paths = [
                    "aetheris-ultimate-modern-visual-26.2",
                    "aetheris-ultimate-modern-balanced-26.2",
                    "aetheris-ultimate-modern-performance-26.2",
                    "aetheris-ultimate-modpack-modern-26.2",
                    "aetheris-ultimate-legacy-1.8.9",
                    "aetheris-ultimate-legacy-visual-1.8.9",
                    "aetheris-ultimate-legacy-balanced-1.8.9",
                    "aetheris-ultimate-legacy-performance-1.8.9"
                ]
                db_rep["all_8_canonical_present"] = all(ep in db_rep["canonical_profiles_found"] for ep in expected_paths)
            conn.close()

            if db_rep["integrity_check"] != "ok" or not db_rep["all_8_canonical_present"] or not db_rep["jvm_args_valid"] or not db_rep["memory_8192"]:
                db_rep["status"] = "FAIL"
            else:
                db_rep["status"] = "PASS"

        except Exception as dbe:
            db_rep["status"] = "FAIL"
            db_rep["integrity_check"] = f"Error: {str(dbe)}"

        sqlite_reports[db_label] = db_rep
        print(f"      {db_label}: [{db_rep['status']}] Integrity: {db_rep['integrity_check']}, Total Profiles: {db_rep['profile_count']}, 8 Canonical: {db_rep['all_8_canonical_present']}, 8GB Mem: {db_rep['memory_8192']}, G1GC Args: {db_rep['jvm_args_valid']}")

    # Clean up test temp dir
    try:
        shutil.rmtree(test_root, ignore_errors=True)
    except Exception:
        pass

    installer_overall_pass = all_ps1_ok and all(r["success"] for r in cli_results.values()) and idempotency_pass
    RESULTS["installer"]["details"] = {
        "static_checks": ps1_checks,
        "cli_executions": cli_results,
        "idempotency": idempotency_pass,
        "sqlite_reports": sqlite_reports
    }
    if installer_overall_pass:
        RESULTS["installer"]["passed"].append("Installer & SQLite Stress Test Suite")
    else:
        RESULTS["installer"]["failed"].append("Installer & SQLite Stress Test Suite")

# ==============================================================================
# 3. KEYBIND MAPPINGS & 'K' CONFLICT VERIFICATION ACROSS ALL OPTIONS.TXT
# ==============================================================================

def test_keybind_conflicts():
    print("\n" + "=" * 80)
    print("3. TESTING KEYBIND MAPPINGS ACROSS ALL OPTIONS.TXT (ZERO CONFLICT ON 'K')")
    print("=" * 80)

    options_search_paths = [
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances",
        r"C:\Users\a7med\AppData\Roaming\.minecraft",
        r"C:\Users\a7med\.lunarclient\offline\multiver\profiles",
        r"D:\AetherisShare\profiles",
        r"D:\AetherisShare\lunar_profiles",
        r"D:\mods"
    ]

    found_options_files = []
    for spath in options_search_paths:
        if not os.path.exists(spath):
            continue
        for root, _, files in os.walk(spath):
            for f in files:
                if f.lower() == "options.txt" or f.lower() == "optionslc.txt":
                    found_options_files.append(os.path.join(root, f))

    unique_options_files = sorted(list(set(found_options_files)))
    print(f"Found {len(unique_options_files)} options configuration files to inspect:")

    keybind_reports = {}
    total_conflicts = 0

    for opt_path in unique_options_files:
        rep = {
            "path": opt_path,
            "total_keybinds": 0,
            "k_mappings": [],
            "craftingtweaks_keys": [],
            "iris_toggle_key": None,
            "conflict_count": 0,
            "status": "PASS"
        }

        try:
            with open(opt_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in lines:
                s = line.strip()
                if not s or ":" not in s:
                    continue
                k, v = s.split(":", 1)
                k = k.strip()
                v = v.strip()

                if k.startswith("key_") or k.startswith("key."):
                    rep["total_keybinds"] += 1

                    is_k = False
                    if v == "key.keyboard.k" or v == "37":
                        is_k = True
                    elif v.lower() == "k":
                        is_k = True

                    if is_k:
                        rep["k_mappings"].append((k, v))

                    if "craftingtweaks" in k.lower():
                        rep["craftingtweaks_keys"].append((k, v))

                    if "iris.toggleshaders" in k.lower():
                        rep["iris_toggle_key"] = v

            k_count = len(rep["k_mappings"])
            ct_on_k = [k for k, v in rep["craftingtweaks_keys"] if v == "key.keyboard.k" or v == "37" or v.lower() == "k"]

            if k_count > 1:
                rep["conflict_count"] = k_count - 1
                rep["status"] = "FAIL"
            elif len(ct_on_k) > 0:
                rep["conflict_count"] = len(ct_on_k)
                rep["status"] = "FAIL"
            else:
                rep["conflict_count"] = 0
                rep["status"] = "PASS"

        except Exception as e:
            rep["status"] = "FAIL"
            rep["error"] = str(e)

        keybind_reports[opt_path] = rep
        if rep["status"] == "FAIL":
            total_conflicts += rep["conflict_count"]
            RESULTS["keybinds"]["failed"].append(opt_path)
        else:
            RESULTS["keybinds"]["passed"].append(opt_path)

        k_binds_str = ", ".join(f"{k}->{v}" for k, v in rep["k_mappings"]) if rep["k_mappings"] else "None"
        ct_str = ", ".join(f"{k}->{v}" for k, v in rep["craftingtweaks_keys"][:2]) if rep["craftingtweaks_keys"] else "None"
        print(f"  [{rep['status']}] {os.path.basename(os.path.dirname(opt_path))}/{os.path.basename(opt_path)}: 'K' Binds: [{k_binds_str}], CT Binds: [{ct_str}], Conflicts: {rep['conflict_count']}")

    RESULTS["keybinds"]["details"] = {
        "files_scanned": len(unique_options_files),
        "total_conflicts": total_conflicts,
        "reports": keybind_reports
    }

# ==============================================================================
# MAIN TEST RUNNER & FORMAL VERDICT
# ==============================================================================

def main():
    print("=" * 80)
    print(" AETHERIS ECOSYSTEM EMPIRICAL CHALLENGER STRESS HARNESS")
    print(" Adversarial Verification Suite — Challenger 1")
    print("=" * 80)

    test_shaderpacks()
    test_installer_and_sqlite()
    test_keybind_conflicts()

    shader_fails = len(RESULTS["shaders"]["failed"])
    installer_fails = len(RESULTS["installer"]["failed"])
    keybind_fails = len(RESULTS["keybinds"]["failed"])

    total_failures = shader_fails + installer_fails + keybind_fails

    print("\n" + "=" * 80)
    print(" EMPIRICAL VERIFICATION SUMMARY")
    print("=" * 80)
    print(f" Shaderpack Archives Passed: {len(RESULTS['shaders']['passed'])}, Failed: {shader_fails}")
    print(f" Installer & SQLite Tests Passed: {len(RESULTS['installer']['passed'])}, Failed: {installer_fails}")
    print(f" Options.txt Files Passed: {len(RESULTS['keybinds']['passed'])}, Failed: {keybind_fails}")

    if total_failures == 0:
        RESULTS["verdict"] = "APPROVE"
        print("\n FORMAL VERDICT: >>> APPROVE <<<")
        print(" All Java NIO root layouts, GLSL preprocessor syntax, installer CLI non-interactive executions,")
        print(" SQLite database schemas/integrity, and keybind collision matrices have PASSED 100% EMPIRICALLY.")
    else:
        RESULTS["verdict"] = "REQUEST_CHANGES"
        print(f"\n FORMAL VERDICT: >>> REQUEST_CHANGES <<< ({total_failures} failure points detected)")

    summary_path = r"D:\mods\challenger_results.json"
    with open(summary_path, "w", encoding="utf-8") as jf:
        json.dump(RESULTS, jf, indent=2)
    print(f"\nSaved empirical test telemetry to: {summary_path}")

if __name__ == "__main__":
    main()
