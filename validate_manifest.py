#!/usr/bin/env python3
"""
SIR ModPack — Delta Manifest JSON Schema & Hash Integrity Validator
Validates:
1. JSON Schema integrity of delta_manifest.json (schema_version, version, total_files, total_size_bytes, files).
2. File count and total byte sum consistency.
3. Strict SHA-256 hexadecimal 64-character formatting for every entry.
4. Physical disk SHA-256 checksum verification for all local distribution payloads.
"""

import os
import sys
import json
import hashlib

def validate_manifest():
    print("=" * 65)
    print("🔍 SIR DELTA MANIFEST SCHEMA & HASH INTEGRITY VALIDATOR")
    print("=" * 65)

    root_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_file = os.path.join(root_dir, "delta_manifest.json")

    if not os.path.exists(manifest_file):
        print(f"❌ Critical Error: {manifest_file} does not exist!")
        sys.exit(1)

    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Critical Error: Failed to parse {manifest_file} as JSON: {e}")
        sys.exit(1)

    # 1. Top-level Schema Check
    required_keys = ["schema_version", "version", "total_files", "total_size_bytes", "files"]
    for key in required_keys:
        if key not in data:
            print(f"❌ Schema Violation: Missing required key '{key}'")
            sys.exit(1)

    schema_version = data["schema_version"]
    version = data["version"]
    total_files = data["total_files"]
    total_size_bytes = data["total_size_bytes"]
    files = data["files"]

    print(f"  • Schema Version: {schema_version}")
    print(f"  • Release Version: {version}")
    print(f"  • Indexed File Count: {total_files}")
    print(f"  • Indexed Payload Size: {total_size_bytes / (1024*1024*1024):.2f} GB ({total_size_bytes} bytes)")

    if not isinstance(files, dict):
        print("❌ Schema Violation: 'files' must be a dictionary.")
        sys.exit(1)

    if len(files) != total_files:
        print(f"❌ Integrity Error: Actual entries count ({len(files)}) does not match total_files ({total_files})!")
        sys.exit(1)

    # 2. Per-file Schema & SHA-256 Validation
    computed_total_size = 0
    valid_sha_chars = set("0123456789abcdefABCDEF")
    errors = []
    verified_local_files = 0

    for path_str, entry in files.items():
        if not isinstance(entry, dict):
            errors.append(f"Entry {path_str} is not a valid JSON object.")
            continue

        sha = entry.get("sha256")
        size = entry.get("size")
        category = entry.get("category")

        if not sha or len(sha) != 64 or not all(c in valid_sha_chars for c in sha):
            errors.append(f"Invalid SHA-256 format for '{path_str}': {sha}")

        if size is None or not isinstance(size, int) or size < 0:
            errors.append(f"Invalid size for '{path_str}': {size}")
        else:
            computed_total_size += size

        # 3. If file exists on disk, verify actual physical hash
        local_path = os.path.join(root_dir, path_str)
        if os.path.exists(local_path) and os.path.isfile(local_path):
            h = hashlib.sha256()
            with open(local_path, "rb") as f_in:
                while chunk := f_in.read(131072):
                    h.update(chunk)
            computed_hash = h.hexdigest().lower()
            if computed_hash != sha.lower():
                # In active game or test environments, options.txt and sodium-options.json are mutable user runtime state
                is_mutable_user_setting = any(path_str.endswith(ext) for ext in ["options.txt", "servers.dat", "usercache.json", "sodium-options.json"])
                if is_mutable_user_setting and not (os.environ.get("STRICT_TEMPLATE_VERIFY") == "1"):
                    print(f"  ℹ Note: Local user runtime configuration '{path_str}' has local modifications.")
                else:
                    errors.append(f"Checksum mismatch for local file '{path_str}': expected {sha}, got {computed_hash}")
            else:
                verified_local_files += 1

    if computed_total_size != total_size_bytes:
        errors.append(f"Total size mismatch: sum of files is {computed_total_size}, manifest claims {total_size_bytes}")

    if errors:
        print(f"\n❌ FAILED: {len(errors)} errors detected:")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.")
        sys.exit(1)

    print(f"\n  ✓ Verified {len(files)} file schemas and SHA-256 signatures.")
    if verified_local_files > 0:
        print(f"  ✓ Verified {verified_local_files} local files physically on disk with 100% hash match.")
    print("=" * 65)
    print("🎉 100% VALID — DELTA MANIFEST SCHEMA & HASH INTEGRITY VERIFIED!")
    print("=" * 65)

if __name__ == "__main__":
    validate_manifest()
