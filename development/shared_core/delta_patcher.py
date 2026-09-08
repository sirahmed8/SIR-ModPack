"""
delta_patcher.py — Binary Differential Synchronization & OTA Patching Engine for SIR.
Generates SHA-256 asset manifests, computes differential sync plans, and executes
atomic differential updates locally or via HTTP/CDN, eliminating multi-gigabyte re-downloads.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

try:
    from shared_core.manifest import is_user_owned, sha256_file
    from shared_core.runtime import atomic_write_json, download_file_resilient
except ImportError:
    # Standalone fallback if shared_core is directly imported
    def sha256_file(path: str | os.PathLike[str], chunk_size: int = 131072) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                digest.update(chunk)
        return digest.hexdigest()

    def is_user_owned(rel_path: Path) -> bool:
        parts = [p.lower() for p in rel_path.parts]
        basename = parts[-1] if parts else ""
        if basename in {"accounts.json", "options.txt", "servers.dat", "launcher_settings.json"}:
            return True
        return any(p in {"saves", "screenshots", "logs", "crash-reports"} for p in parts)

    def atomic_write_json(path: str, data: Any) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)

    def download_file_resilient(url: str, dest_path: str, progress_callback=None, max_retries=3, timeout=15.0):
        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "SIR-ModPack-DeltaPatcher/1.0.0"})
        tmp_dst = dest_path + ".tmp"
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(tmp_dst, "wb") as f:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            while chunk := resp.read(65536):
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total > 0:
                    pct = (downloaded / total) * 100.0
                    progress_callback(pct, downloaded, total)
        os.replace(tmp_dst, dest_path)


DEFAULT_IGNORED_DIRS: Set[str] = {
    ".git", ".github", "__pycache__", ".vscode", ".idea", "node_modules",
    "build_apps", "dist_build", "dist_payloads", "cache", "logs", "crash-reports",
    "saves", "screenshots", "web_env", "public_repo", "website-next"
}

DEFAULT_IGNORED_EXTENSIONS: Set[str] = {
    ".pyc", ".pyo", ".tmp", ".log", ".bak", ".swp", ".lock"
}


class DeltaPatcher:
    """Calculates and executes binary delta updates for the SIR ecosystem."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    @staticmethod
    def categorize_path(rel_path: str) -> str:
        """Determines the semantic component category of a file."""
        norm = rel_path.replace("\\", "/").lower()
        if "shaderpacks" in norm:
            return "shader"
        if "resourcepacks" in norm:
            return "resourcepack"
        if "mods/" in norm or norm.startswith("mods"):
            return "mod"
        if "config/" in norm or norm.startswith("config"):
            return "config"
        if "instances/" in norm or norm.startswith("instances"):
            if "/mods/" in norm:
                return "instance_mod"
            if "/config/" in norm:
                return "instance_config"
            return "instance_meta"
        if "capes" in norm:
            return "cape"
        if norm.endswith(".exe"):
            return "binary"
        return "misc"

    def generate_manifest(
        self,
        base_dir: Optional[str] = None,
        include_rel_dirs: Optional[List[str]] = None,
        output_file: Optional[str] = None,
        max_workers: int = 8
    ) -> Dict[str, Any]:
        """
        Scans managed files under base_dir in parallel, computes SHA-256 digests,
        and constructs a deterministic delta manifest.
        """
        scan_root = os.path.abspath(base_dir or self.root_dir)
        target_subdirs = include_rel_dirs or [
            "mods", "config", "shaderpacks", "resourcepacks", "capes",
            "instances/26.2", "instances/26.2-ultra", "instances/26.2-balanced", "instances/26.2-performance",
            "instances/1.8.9", "instances/1.8.9-ultra", "instances/1.8.9-balanced", "instances/1.8.9-performance"
        ]

        files_to_hash: List[Tuple[str, str]] = []  # (abs_path, rel_path)

        for sub in target_subdirs:
            sub_path = os.path.join(scan_root, sub)
            if not os.path.exists(sub_path):
                continue
            if os.path.isfile(sub_path):
                rel = os.path.relpath(sub_path, scan_root).replace("\\", "/")
                files_to_hash.append((sub_path, rel))
                continue

            for root, dirs, files in os.walk(sub_path):
                dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORED_DIRS and not d.startswith(".")]
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in DEFAULT_IGNORED_EXTENSIONS or f.startswith("."):
                        continue
                    abs_p = os.path.join(root, f)
                    rel = os.path.relpath(abs_p, scan_root).replace("\\", "/")
                    files_to_hash.append((abs_p, rel))

        manifest_entries: Dict[str, Dict[str, Any]] = {}
        total_bytes = 0

        def _hash_worker(item: Tuple[str, str]) -> Tuple[str, Dict[str, Any]]:
            abs_p, rel_p = item
            try:
                sz = os.path.getsize(abs_p)
                mtime = int(os.path.getmtime(abs_p))
                digest = sha256_file(abs_p)
                cat = self.categorize_path(rel_p)
                return rel_p, {
                    "sha256": digest,
                    "size": sz,
                    "mtime": mtime,
                    "category": cat
                }
            except Exception as e:
                return rel_p, {"error": str(e)}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(_hash_worker, item): item for item in files_to_hash}
            for future in as_completed(future_to_file):
                rel_p, data = future.result()
                if "error" not in data and data.get("sha256"):
                    manifest_entries[rel_p] = data
                    total_bytes += data["size"]

        # Sort entries alphabetically for deterministic output
        sorted_files = {k: manifest_entries[k] for k in sorted(manifest_entries.keys())}

        manifest = {
            "schema_version": 1,
            "version": "1.0.0",
            "generated_at": int(time.time()),
            "iso_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_files": len(sorted_files),
            "total_size_bytes": total_bytes,
            "files": sorted_files
        }

        if output_file:
            atomic_write_json(output_file, manifest)

        return manifest

    def plan_delta(
        self,
        target_dir: str,
        manifest: Dict[str, Any],
        filter_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compares an existing target installation against the delta manifest.
        Returns the differential plan: files to add, update, delete, or leave untouched.
        """
        target = os.path.abspath(target_dir)
        files_map = manifest.get("files", {})
        
        to_add: List[Dict[str, Any]] = []
        to_update: List[Dict[str, Any]] = []
        unchanged: List[str] = []
        bytes_to_transfer = 0
        total_manifest_bytes = 0

        for rel_path, meta in files_map.items():
            cat = meta.get("category", "misc")
            if filter_category and cat != filter_category:
                continue

            expected_sha = meta.get("sha256", "").lower()
            expected_size = meta.get("size", 0)
            total_manifest_bytes += expected_size

            local_path = os.path.join(target, rel_path)
            if not os.path.isfile(local_path):
                to_add.append({
                    "path": rel_path,
                    "target_path": local_path,
                    "sha256": expected_sha,
                    "size": expected_size,
                    "category": cat
                })
                bytes_to_transfer += expected_size
            else:
                # Fast size check first
                local_size = os.path.getsize(local_path)
                if local_size != expected_size:
                    to_update.append({
                        "path": rel_path,
                        "target_path": local_path,
                        "sha256": expected_sha,
                        "size": expected_size,
                        "category": cat,
                        "reason": f"size_mismatch ({local_size} vs {expected_size})"
                    })
                    bytes_to_transfer += expected_size
                else:
                    # Deep SHA-256 check
                    local_sha = sha256_file(local_path).lower()
                    if local_sha != expected_sha:
                        to_update.append({
                            "path": rel_path,
                            "target_path": local_path,
                            "sha256": expected_sha,
                            "size": expected_size,
                            "category": cat,
                            "reason": f"hash_mismatch ({local_sha[:8]} vs {expected_sha[:8]})"
                        })
                        bytes_to_transfer += expected_size
                    else:
                        unchanged.append(rel_path)

        # Detect obsolete files in managed directories that are safe to remove
        to_delete: List[str] = []
        managed_roots = {"mods", "shaderpacks", "resourcepacks"}
        for root_name in managed_roots:
            sub = os.path.join(target, root_name)
            if os.path.isdir(sub):
                for r, _, fnames in os.walk(sub):
                    for fn in fnames:
                        fp = os.path.join(r, fn)
                        rel = os.path.relpath(fp, target).replace("\\", "/")
                        if is_user_owned(Path(rel)):
                            continue
                        if rel not in files_map:
                            to_delete.append(fp)

        bandwidth_saved_bytes = max(0, total_manifest_bytes - bytes_to_transfer)
        saved_pct = (bandwidth_saved_bytes / total_manifest_bytes * 100.0) if total_manifest_bytes > 0 else 0.0

        return {
            "to_add": to_add,
            "to_update": to_update,
            "to_delete": to_delete,
            "unchanged_count": len(unchanged),
            "total_files_in_manifest": len(files_map),
            "files_to_transfer_count": len(to_add) + len(to_update),
            "bytes_to_transfer": bytes_to_transfer,
            "total_manifest_bytes": total_manifest_bytes,
            "bandwidth_saved_bytes": bandwidth_saved_bytes,
            "bandwidth_saved_pct": round(saved_pct, 1),
            "is_fully_synchronized": (len(to_add) == 0 and len(to_update) == 0)
        }

    def apply_delta_local(
        self,
        source_dir: str,
        target_dir: str,
        plan: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Applies a local delta update: copies only diff files, writes atomically,
        and verifies post-transfer SHA-256 integrity.
        """
        source = os.path.abspath(source_dir)
        target = os.path.abspath(target_dir)
        queue = plan.get("to_add", []) + plan.get("to_update", [])
        total_items = len(queue)
        applied = 0
        failed = 0
        errors: List[str] = []

        for idx, item in enumerate(queue, 1):
            rel = item["path"]
            src_file = os.path.join(source, rel)
            dst_file = os.path.join(target, rel)
            expected_sha = item.get("sha256", "").lower()

            if not os.path.isfile(src_file):
                failed += 1
                errors.append(f"Source file missing: {rel}")
                continue

            try:
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                tmp_file = dst_file + ".delta.tmp"
                shutil.copy2(src_file, tmp_file)

                # Verify written file hash before replacing
                if expected_sha:
                    written_sha = sha256_file(tmp_file).lower()
                    if written_sha != expected_sha:
                        os.remove(tmp_file)
                        failed += 1
                        errors.append(f"SHA mismatch after copy for {rel}")
                        continue

                os.replace(tmp_file, dst_file)
                applied += 1
                if progress_callback:
                    progress_callback(idx, total_items, rel)
            except Exception as e:
                failed += 1
                errors.append(f"Copy failure for {rel}: {e}")

        # Purge obsolete files if safe
        for del_path in plan.get("to_delete", []):
            try:
                if os.path.isfile(del_path):
                    os.remove(del_path)
            except Exception:
                pass

        return {
            "success": (failed == 0),
            "applied_count": applied,
            "failed_count": failed,
            "errors": errors
        }

    def apply_delta_remote(
        self,
        base_url: str,
        target_dir: str,
        plan: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Downloads missing/updated diffs directly from a remote HTTP base URL or CDN.
        Uses resilient retries and verifies SHA-256 after download.
        """
        target = os.path.abspath(target_dir)
        queue = plan.get("to_add", []) + plan.get("to_update", [])
        total_items = len(queue)
        total_bytes = plan.get("bytes_to_transfer", 0)
        bytes_done = 0
        applied = 0
        failed = 0
        errors: List[str] = []

        clean_base = base_url.rstrip("/")

        for idx, item in enumerate(queue, 1):
            rel = item["path"]
            dst_file = os.path.join(target, rel)
            expected_sha = item.get("sha256", "").lower()
            expected_sz = item.get("size", 0)
            url = f"{clean_base}/{urllib.parse.quote(rel)}"

            try:
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                tmp_file = dst_file + ".dl.tmp"

                def _item_cb(pct, downloaded, total):
                    nonlocal bytes_done
                    current_total_done = bytes_done + downloaded
                    if progress_callback:
                        progress_callback(idx, total_items, current_total_done, rel)

                download_file_resilient(url, tmp_file, progress_callback=_item_cb)

                if expected_sha:
                    dl_sha = sha256_file(tmp_file).lower()
                    if dl_sha != expected_sha:
                        os.remove(tmp_file)
                        failed += 1
                        errors.append(f"Remote SHA mismatch for {rel}")
                        continue

                os.replace(tmp_file, dst_file)
                bytes_done += expected_sz
                applied += 1
            except Exception as e:
                failed += 1
                errors.append(f"Remote download failed for {rel}: {e}")

        return {
            "success": (failed == 0),
            "applied_count": applied,
            "failed_count": failed,
            "errors": errors
        }
