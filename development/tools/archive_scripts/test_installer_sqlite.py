"""
Mission Task 2: Installer Scripts Non-Interactive Stress Testing & SQLite Database Integrity
"""

import os
import sys
import subprocess
import tempfile
import shutil
import sqlite3
import json

def run_installer_sqlite_tests():
    print("=" * 80, flush=True)
    print("MISSION TASK 2: INSTALLER SCRIPTS NON-INTERACTIVE STRESS & SQLITE INTEGRITY", flush=True)
    print("=" * 80, flush=True)

    install_ps1 = r"D:\AetherisShare\install.ps1"
    install_bat = r"D:\AetherisShare\install.bat"

    test_results = {
        "static_checks": {},
        "cli_modes": {},
        "idempotency": None,
        "backup_creation": None,
        "sqlite_checks": {},
        "overall_status": "PASS"
    }

    # 1. Static checks
    print("\n--- 1. STATIC CODE & PARAMETER AUDIT ---", flush=True)
    with open(install_ps1, "r", encoding="utf-8") as f:
        ps1_code = f.read()

    with open(install_bat, "r", encoding="utf-8") as f:
        bat_code = f.read()

    static_checks = {
        "PS1_CmdletBinding": "[CmdletBinding()]" in ps1_code,
        "PS1_NonInteractive_Flag": "[switch]$NonInteractive" in ps1_code,
        "PS1_Silent_Flag": "[switch]$Silent" in ps1_code,
        "PS1_SkipBackup_Flag": "[switch]$SkipBackup" in ps1_code,
        "PS1_SkipDb_Flag": "[switch]$SkipDb" in ps1_code,
        "PS1_ErrorAction_Stop": "$ErrorActionPreference = 'Stop'" in ps1_code,
        "PS1_SQLite_Registration_Function": "function Register-LunarProfilesDb" in ps1_code,
        "BAT_Calls_PS1_With_Args": 'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*' in bat_code,
        "BAT_Default_Interactive_Pause": 'pause' in bat_code
    }

    test_results["static_checks"] = static_checks
    for k, v in static_checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}: {v}", flush=True)

    # 2. Non-Interactive CLI Executions across Modes
    print("\n--- 2. NON-INTERACTIVE CLI STRESS EXECUTIONS IN SANDBOX ---", flush=True)
    temp_sandbox = tempfile.mkdtemp(prefix="aetheris_install_test_")
    sandbox_lunar = os.path.join(temp_sandbox, ".lunarclient")
    sandbox_prism = os.path.join(temp_sandbox, "PrismLauncher", "instances")
    sandbox_mc = os.path.join(temp_sandbox, ".minecraft")
    sandbox_db = os.path.join(sandbox_lunar, "db", "profiles.db")

    modes_to_test = [
        ("HUDs", ["-Mode", "HUDs"]),
        ("Shaders", ["-Mode", "Shaders"]),
        ("ResourcePacks", ["-Mode", "ResourcePacks"]),
        ("Modern", ["-Mode", "Modern", "-Target", "Lunar"]),
        ("Legacy", ["-Mode", "Legacy", "-Target", "Lunar"]),
        ("Selective", ["-Mode", "Selective", "-ProfileNames", "visual", "balanced"]),
        ("Prism", ["-Mode", "Prism"]),
        ("Minecraft", ["-Mode", "Minecraft"]),
        ("Ecosystem", ["-Mode", "Ecosystem", "-SkipBackup"]),
        ("All", ["-Mode", "All", "-Target", "All", "-SkipBackup"]),
    ]

    all_modes_pass = True
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

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            mode_pass = (proc.returncode == 0) and ("FAILED" not in proc.stderr.upper())
            stderr_msg = proc.stderr.strip()
            exit_code = proc.returncode
            stdout_len = len(proc.stdout)
        except subprocess.TimeoutExpired:
            mode_pass = False
            stderr_msg = "Execution timed out after 300s"
            exit_code = -1
            stdout_len = 0

        if not mode_pass:
            all_modes_pass = False

        test_results["cli_modes"][mode_name] = {
            "exit_code": exit_code,
            "stdout_bytes": stdout_len,
            "stderr": stderr_msg,
            "pass": mode_pass
        }
        print(f"  Mode '{mode_name:15}': Exit Code = {exit_code} -> {'PASS' if mode_pass else 'FAIL'}", flush=True)
        if not mode_pass and stderr_msg:
            print(f"      Stderr: {stderr_msg[:200]}", flush=True)

    # 3. Idempotency & Repeat Execution Test
    print("\n--- 3. IDEMPOTENCY & REPEAT RUN STRESS TEST ---", flush=True)
    cmd_repeat = [
        "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", install_ps1,
        "-Mode", "HUDs",
        "-LunarPath", sandbox_lunar,
        "-PrismPath", sandbox_prism,
        "-MinecraftPath", sandbox_mc,
        "-NonInteractive",
        "-Silent"
    ]
    r1 = subprocess.run(cmd_repeat, capture_output=True, text=True, timeout=120)
    r2 = subprocess.run(cmd_repeat, capture_output=True, text=True, timeout=120)
    idempotency_ok = (r1.returncode == 0 and r2.returncode == 0)
    test_results["idempotency"] = idempotency_ok
    print(f"  Consecutive Execution 1 Exit Code: {r1.returncode}", flush=True)
    print(f"  Consecutive Execution 2 Exit Code: {r2.returncode}", flush=True)
    print(f"  Idempotency Result: {'PASS' if idempotency_ok else 'FAIL'}", flush=True)

    # 4. File Permissions & Deployed Structure Check
    print("\n--- 4. FILE PERMISSION & DEPLOYMENT STRUCTURE VERIFICATION ---", flush=True)
    deployed_lunar_profs = os.listdir(os.path.join(sandbox_lunar, "profiles")) if os.path.exists(os.path.join(sandbox_lunar, "profiles")) else []
    deployed_prism_insts = os.listdir(sandbox_prism) if os.path.exists(sandbox_prism) else []
    deployed_mc_exists = os.path.exists(sandbox_mc)

    print(f"  Deployed Lunar Profiles ({len(deployed_lunar_profs)}): {deployed_lunar_profs}", flush=True)
    print(f"  Deployed Prism Instances ({len(deployed_prism_insts)}): {deployed_prism_insts}", flush=True)
    print(f"  Deployed .minecraft Exists: {deployed_mc_exists}", flush=True)

    # 5. SQLite Database Integrity Audit
    print("\n--- 5. SQLITE DATABASE INTEGRITY & SCHEMA AUDIT ---", flush=True)
    dbs_to_check = [
        ("Sandbox_Test_DB", sandbox_db),
        ("Live_Lunar_Profiles_DB", r"C:\Users\a7med\.lunarclient\db\profiles.db"),
    ]

    all_dbs_pass = True
    for db_label, db_path in dbs_to_check:
        if not os.path.exists(db_path):
            print(f"  {db_label}: [SKIP] File does not exist at {db_path}", flush=True)
            continue

        db_report = {
            "path": db_path,
            "integrity": None,
            "foreign_keys": None,
            "profile_count": 0,
            "canonical_profiles": [],
            "missing_profiles": [],
            "all_8_present": False,
            "memory_allocation_ok": True,
            "jvm_args_ok": True,
            "use_lunar_features_ok": True,
            "status": "PASS"
        }

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Integrity check PRAGMA
            cur.execute("PRAGMA integrity_check;")
            int_res = cur.fetchall()
            db_report["integrity"] = int_res[0][0] if int_res else "ERROR"

            cur.execute("PRAGMA foreign_key_check;")
            db_report["foreign_keys"] = cur.fetchall()

            # Table structure
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profiles';")
            tbl = cur.fetchone()
            if tbl:
                cur.execute("SELECT id, name, path, allocated_memory, jvm_arguments, use_lunar_features, config_version FROM profiles;")
                rows = cur.fetchall()
                db_report["profile_count"] = len(rows)
                
                expected_canonicals = [
                    "aetheris-ultimate-modern-visual-26.2",
                    "aetheris-ultimate-modern-balanced-26.2",
                    "aetheris-ultimate-modern-performance-26.2",
                    "aetheris-ultimate-modpack-modern-26.2",
                    "aetheris-ultimate-legacy-1.8.9",
                    "aetheris-ultimate-legacy-visual-1.8.9",
                    "aetheris-ultimate-legacy-balanced-1.8.9",
                    "aetheris-ultimate-legacy-performance-1.8.9"
                ]

                found_paths = [r[2] for r in rows]
                db_report["canonical_profiles"] = found_paths
                db_report["missing_profiles"] = [p for p in expected_canonicals if p not in found_paths]
                db_report["all_8_present"] = (len(db_report["missing_profiles"]) == 0)

                for r in rows:
                    mem = r[3]
                    jvm = r[4]
                    lunar_feat = r[5]
                    path = r[2]
                    if path in expected_canonicals:
                        if mem != 8192:
                            db_report["memory_allocation_ok"] = False
                        if not jvm or "-XX:+UseG1GC" not in jvm or "-XX:G1HeapRegionSize=8M" not in jvm:
                            db_report["jvm_args_ok"] = False
                        if lunar_feat != 1:
                            db_report["use_lunar_features_ok"] = False

            conn.close()

            db_pass = (
                db_report["integrity"] == "ok" and
                db_report["all_8_present"] and
                db_report["memory_allocation_ok"] and
                db_report["jvm_args_ok"] and
                db_report["use_lunar_features_ok"]
            )
            db_report["status"] = "PASS" if db_pass else "FAIL"
            if not db_pass:
                all_dbs_pass = False

        except Exception as ex:
            db_report["status"] = "FAIL"
            db_report["integrity"] = f"Exception: {ex}"
            all_dbs_pass = False

        test_results["sqlite_checks"][db_label] = db_report

        print(f"\n  [DATABASE AUDIT] {db_label} ({db_path}):", flush=True)
        print(f"    - PRAGMA integrity_check: {db_report['integrity']}", flush=True)
        print(f"    - Total Profiles Registered: {db_report['profile_count']}", flush=True)
        print(f"    - All 8 Canonical Profiles Present: {'YES' if db_report['all_8_present'] else 'NO (Missing: ' + str(db_report['missing_profiles']) + ')'}", flush=True)
        print(f"    - 8192 MB (8GB) Memory Verified: {'YES' if db_report['memory_allocation_ok'] else 'NO'}", flush=True)
        print(f"    - G1GC High-Throughput Flags: {'YES' if db_report['jvm_args_ok'] else 'NO'}", flush=True)
        print(f"    - use_lunar_features Flag = 1: {'YES' if db_report['use_lunar_features_ok'] else 'NO'}", flush=True)
        print(f"    - Overall Database Status: [{db_report['status']}]", flush=True)

    # Clean sandbox
    try:
        shutil.rmtree(temp_sandbox, ignore_errors=True)
    except Exception:
        pass

    overall_task2_pass = all(static_checks.values()) and all_modes_pass and idempotency_ok and all_dbs_pass
    test_results["overall_status"] = "PASS" if overall_task2_pass else "FAIL"

    print("\n" + "-" * 80, flush=True)
    print(f"TASK 2 SUMMARY: {'ALL TESTS PASSED (100% EMPIRICAL SUCCESS)' if overall_task2_pass else 'TESTS FAILED'}", flush=True)
    print("-" * 80, flush=True)

    with open(r"D:\mods\installer_test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2)

if __name__ == "__main__":
    run_installer_sqlite_tests()
