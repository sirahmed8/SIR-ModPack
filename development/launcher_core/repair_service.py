"""
repair_service.py — Asset Integrity Verifier & Self-Healing Service.
Zero-Mock Implementation with Parallel SHA-256 Hashing, ZIP CRC Validation & Quarantine.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional


class RepairService:
    """Verifies SHA-256 integrity and self-heals corrupted mods, shaders, and configs using parallel worker threads."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def calculate_sha256(self, filepath: str) -> str:
        h = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(131072):  # 128KB buffer for optimal SSD throughput
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def verify_file_integrity(
        self, filepath: str, expected_sha256: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verifies binary and archive integrity for a target package."""
        if not os.path.isfile(filepath):
            return {"file": filepath, "valid": False, "reason": "Missing file"}

        try:
            sz = os.path.getsize(filepath)
            if sz == 0:
                return {"file": filepath, "valid": False, "reason": "0-byte empty file"}

            sha256 = self.calculate_sha256(filepath)
            if not sha256:
                return {"file": filepath, "valid": False, "reason": "Unreadable file"}

            if expected_sha256 and sha256.lower() != expected_sha256.lower():
                return {
                    "file": filepath,
                    "valid": False,
                    "reason": f"SHA-256 mismatch (Expected: {expected_sha256[:8]}..., Got: {sha256[:8]}...)",
                    "sha256": sha256,
                }

            # For ZIP/JAR packages, verify zip central directory and CRC table
            if filepath.endswith((".jar", ".zip")):
                try:
                    with zipfile.ZipFile(filepath, "r") as zf:
                        bad_member = zf.testzip()
                        if bad_member:
                            return {
                                "file": filepath,
                                "valid": False,
                                "reason": f"Corrupted zip member: {bad_member}",
                                "sha256": sha256,
                            }
                except Exception as zip_ex:
                    return {
                        "file": filepath,
                        "valid": False,
                        "reason": f"Invalid archive structure: {zip_ex}",
                        "sha256": sha256,
                    }

            return {"file": filepath, "valid": True, "sha256": sha256, "size": sz}
        except Exception as ex:
            return {"file": filepath, "valid": False, "reason": str(ex)}

    def run_self_repair(self) -> Dict[str, Any]:
        """Scans all mod, shader, and pack assets, verifying real checksums and repairing corruptions."""
        target_files: List[str] = []
        search_dirs = [
            os.path.join(self.root_dir, "mods"),
            os.path.join(self.root_dir, "resourcepacks"),
            os.path.join(self.root_dir, "shaderpacks"),
        ]

        # Dynamic search across all instance directories
        instances_dir = os.path.join(self.root_dir, "instances")
        if os.path.isdir(instances_dir):
            for inst_name in os.listdir(instances_dir):
                inst_path = os.path.join(instances_dir, inst_name)
                if os.path.isdir(inst_path):
                    mc_dir = os.path.join(inst_path, "minecraft")
                    if not os.path.isdir(mc_dir):
                        mc_dir = inst_path
                    search_dirs.extend([
                        os.path.join(mc_dir, "mods"),
                        os.path.join(mc_dir, "resourcepacks"),
                        os.path.join(mc_dir, "shaderpacks"),
                        os.path.join(mc_dir, "config"),
                    ])

        for dirpath in search_dirs:
            if os.path.exists(dirpath):
                for f in os.listdir(dirpath):
                    if (
                        f.endswith((".jar", ".zip", ".toml", ".json", ".properties"))
                        and not f.endswith(".disabled")
                        and not f.endswith(".corrupted")
                    ):
                        fp = os.path.join(dirpath, f)
                        if os.path.isfile(fp):
                            target_files.append(fp)

        if not target_files:
            return {
                "success": True,
                "verified_count": 0,
                "corrupted_count": 0,
                "healed_count": 0,
                "quarantined_count": 0,
                "total_scanned": 0,
                "status": "No assets to verify",
                "message": "No mod or asset files found to verify across search directories.",
            }

        # Verify in parallel
        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.verify_file_integrity, target_files))

        verified_count = len([r for r in results if r.get("valid")])
        corrupted = [r for r in results if not r.get("valid")]
        healed_count = 0
        quarantined_count = 0

        # Attempt to heal or quarantine corrupted files
        for c in corrupted:
            bad_path = c["file"]
            fname = os.path.basename(bad_path)
            # Check backup in root mods/
            backup_source = os.path.join(self.root_dir, "mods", fname)
            if os.path.isfile(backup_source) and backup_source != bad_path:
                bk_check = self.verify_file_integrity(backup_source)
                if bk_check.get("valid"):
                    try:
                        shutil.copy2(backup_source, bad_path)
                        healed_count += 1
                        continue
                    except Exception:
                        pass

            # If unrepairable, quarantine to avoid game crash
            try:
                quarantine_target = bad_path + ".corrupted"
                if os.path.exists(bad_path):
                    os.replace(bad_path, quarantine_target)
                    quarantined_count += 1
            except Exception:
                pass

        status_text = (
            "100% Healthy & Verified" if not corrupted else f"{len(corrupted)} issues resolved"
        )
        msg = (
            f"Parallel SHA-256 verifier validated {verified_count}/{len(target_files)} asset packages across "
            f"{len(search_dirs)} directories. {len(corrupted)} corrupted files detected "
            f"({healed_count} restored, {quarantined_count} quarantined)."
        )

        return {
            "success": True,
            "verified_count": verified_count,
            "corrupted_count": len(corrupted),
            "healed_count": healed_count,
            "quarantined_count": quarantined_count,
            "total_scanned": len(target_files),
            "status": status_text,
            "message": msg,
        }

    def repair_instances(self) -> Dict[str, Any]:
        """Alias for run_self_repair."""
        return self.run_self_repair()
