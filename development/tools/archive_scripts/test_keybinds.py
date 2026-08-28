"""
Mission Task 3: Keybind Mapping & Collision Audit across all Options Files (Zero Collision on 'K')
"""

import os
import sys
import json

def run_keybind_tests():
    print("=" * 80, flush=True)
    print("MISSION TASK 3: KEYBIND MAPPINGS & COLLISION AUDIT (ZERO CONFLICT ON 'K')", flush=True)
    print("=" * 80, flush=True)

    search_roots = [
        r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances",
        r"C:\Users\a7med\AppData\Roaming\.minecraft",
        r"C:\Users\a7med\.lunarclient\offline\multiver\profiles",
        r"D:\AetherisShare\profiles",
        r"D:\AetherisShare\lunar_profiles",
        r"D:\mods"
    ]

    found_files = []
    for sroot in search_roots:
        if not os.path.exists(sroot):
            continue
        for root, _, files in os.walk(sroot):
            for f in files:
                if f.lower() in ("options.txt", "optionslc.txt", "optionsof.txt", "optionsshaders.txt"):
                    found_files.append(os.path.join(root, f))

    unique_files = sorted(list(set(found_files)))
    print(f"Found {len(unique_files)} options/config files to audit for keybind collisions:\n", flush=True)

    audit_results = {
        "files_scanned": len(unique_files),
        "total_k_conflicts": 0,
        "profiles": {},
        "verdict": "PASS"
    }

    for opt_path in unique_files:
        profile_label = f"{os.path.basename(os.path.dirname(opt_path))}/{os.path.basename(opt_path)}"
        rep = {
            "path": opt_path,
            "total_keys_mapped": 0,
            "k_keybinds": [],
            "craftingtweaks_keys": [],
            "iris_toggle_key": None,
            "conflicts_on_k": 0,
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

                if k.startswith("key_") or k.startswith("key.") or "key" in k.lower():
                    rep["total_keys_mapped"] += 1

                    # Check if mapped to key 'K':
                    # Modern (1.13+ / 26.2): key.keyboard.k
                    # Legacy (1.8.9): 37 (LWJGL 2 KEY_K)
                    is_k = (v == "key.keyboard.k" or v == "37" or v.lower() == "k")

                    if is_k:
                        rep["k_keybinds"].append((k, v))

                    if "craftingtweaks" in k.lower():
                        rep["craftingtweaks_keys"].append((k, v))

                    if "iris.toggleshaders" in k.lower():
                        rep["iris_toggle_key"] = v

            # Collision logic:
            # If multiple key actions are mapped to 'K', collision = len(k_keybinds) - 1
            # If CraftingTweaks is mapped to 'K' alongside Iris, collision is flagged
            k_count = len(rep["k_keybinds"])
            ct_on_k = [k for k, v in rep["craftingtweaks_keys"] if v in ("key.keyboard.k", "37", "k")]

            if k_count > 1:
                rep["conflicts_on_k"] = k_count - 1
                rep["status"] = "FAIL"
            elif len(ct_on_k) > 0 and rep["iris_toggle_key"] in ("key.keyboard.k", "37", "k"):
                rep["conflicts_on_k"] = len(ct_on_k)
                rep["status"] = "FAIL"
            else:
                rep["conflicts_on_k"] = 0
                rep["status"] = "PASS"

        except Exception as e:
            rep["status"] = "FAIL"
            rep["error"] = str(e)

        if rep["status"] == "FAIL":
            audit_results["total_k_conflicts"] += rep["conflicts_on_k"]

        audit_results["profiles"][profile_label] = rep

        k_str = ", ".join(f"{k} = {v}" for k, v in rep["k_keybinds"]) if rep["k_keybinds"] else "None"
        ct_summary = ", ".join(f"{k} = {v}" for k, v in rep["craftingtweaks_keys"][:2]) if rep["craftingtweaks_keys"] else "None"

        print(f"  [{rep['status']}] {profile_label}:", flush=True)
        print(f"       - 'K' Keybinds ({len(rep['k_keybinds'])}): [{k_str}]", flush=True)
        print(f"       - Iris Toggle Shader: {rep['iris_toggle_key'] or 'N/A'}", flush=True)
        print(f"       - CraftingTweaks Sample: [{ct_summary}]", flush=True)
        print(f"       - Conflicts on 'K': {rep['conflicts_on_k']}", flush=True)

    if audit_results["total_k_conflicts"] > 0:
        audit_results["verdict"] = "FAIL"
    else:
        audit_results["verdict"] = "PASS"

    print("\n" + "-" * 80, flush=True)
    print(f"TASK 3 SUMMARY: Total Files Audited = {len(unique_files)}, Total Keybind Conflicts on 'K' = {audit_results['total_k_conflicts']}", flush=True)
    print(f"VERDICT: {'PASS (0 CONFLICTS DETECTED)' if audit_results['total_k_conflicts'] == 0 else 'FAIL (CONFLICTS DETECTED)'}", flush=True)
    print("-" * 80, flush=True)

    with open(r"D:\mods\keybind_test_results.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

if __name__ == "__main__":
    run_keybind_tests()
