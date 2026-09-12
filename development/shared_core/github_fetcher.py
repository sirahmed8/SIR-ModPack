"""
github_fetcher.py — Resilient GitHub Single-File Delta Fetcher & Auto-Healer.
Enables SIR Launcher and SIR Installer to automatically detect missing individual files
(mods, shaders, resourcepacks, configurations) and fetch ONLY the delta directly from GitHub
without re-downloading entire profiles or overwriting user data.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

RAW_BASE_URL = "https://raw.githubusercontent.com/sirahmed8/SIR-ModPack/main"
CDN_BASE_URL = "https://cdn.jsdelivr.net/gh/sirahmed8/SIR-ModPack@main"
RELEASES_BASE_URL = "https://github.com/sirahmed8/SIR-ModPack/releases/download/v1.0.0"

USER_AGENT = "SIR-Ecosystem-DeltaFetcher/1.0.0 (Windows; x64)"


def sha256_file(path: str, chunk_size: int = 65536) -> str:
    """Calculates streaming SHA-256 digest of a local file."""
    if not os.path.isfile(path):
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


class GitHubDeltaFetcher:
    """Single-file delta fetcher and self-healing engine backed by GitHub."""

    def __init__(
        self,
        repo_owner: str = "sirahmed8",
        repo_name: str = "SIR-ModPack",
        branch: str = "main",
        root_dir: Optional[str] = None,
    ):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.root_dir = os.path.abspath(root_dir or os.getcwd())
        self.raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}"
        self.cdn_url = f"https://cdn.jsdelivr.net/gh/{repo_owner}/{repo_name}@{branch}"
        self.manifest_cache: Optional[Dict[str, Any]] = None

    def load_local_manifest(self) -> Dict[str, Any]:
        """Loads delta_manifest.json from root or public_repo."""
        if self.manifest_cache:
            return self.manifest_cache

        candidates = [
            os.path.join(self.root_dir, "delta_manifest.json"),
            os.path.join(self.root_dir, "public_repo", "delta_manifest.json"),
            os.path.join(os.path.dirname(self.root_dir), "delta_manifest.json"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                try:
                    with open(c, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.manifest_cache = data
                    return data
                except Exception:
                    pass
        return {"files": {}}

    def fetch_file(
        self,
        rel_path: str,
        dest_abs_path: str,
        expected_hash: Optional[str] = None,
        progress_cb: Optional[Callable[[int, int, float], None]] = None,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> bool:
        """
        Fetches an individual file directly from GitHub.
        Falls back through GitHub Raw, jsDelivr CDN, and GitHub Releases.
        """
        clean_rel = rel_path.replace("\\", "/").lstrip("/")
        basename = os.path.basename(clean_rel)
        encoded_rel = urllib.parse.quote(clean_rel)

        urls = [
            f"{self.raw_url}/{encoded_rel}",
            f"{self.cdn_url}/{encoded_rel}",
            f"{RELEASES_BASE_URL}/{urllib.parse.quote(basename)}",
        ]

        os.makedirs(os.path.dirname(os.path.abspath(dest_abs_path)), exist_ok=True)
        tmp_dst = dest_abs_path + ".tmp"

        for attempt in range(1, max_retries + 1):
            for url in urls:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        status = getattr(resp, "status", 200)
                        if status not in (200, 206):
                            continue

                        total_bytes = int(resp.headers.get("Content-Length", 0))
                        downloaded = 0
                        hasher = hashlib.sha256() if expected_hash else None

                        with open(tmp_dst, "wb") as f:
                            while chunk := resp.read(65536):
                                f.write(chunk)
                                downloaded += len(chunk)
                                if hasher:
                                    hasher.update(chunk)
                                if progress_cb:
                                    progress_cb(downloaded, total_bytes, (downloaded / total_bytes * 100.0) if total_bytes > 0 else 0.0)

                        if expected_hash and hasher:
                            digest = hasher.hexdigest().lower()
                            if digest != expected_hash.lower():
                                try: os.remove(tmp_dst)
                                except Exception: pass
                                continue

                        # Atomic placement
                        if os.path.exists(dest_abs_path):
                            try: os.remove(dest_abs_path)
                            except Exception: pass
                        os.replace(tmp_dst, dest_abs_path)
                        return True
                except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
                    if os.path.exists(tmp_dst):
                        try: os.remove(tmp_dst)
                        except Exception: pass
                    continue
            time.sleep(0.5 * attempt)

        return False

    def ensure_instance_files(
        self,
        instance_id: str,
        instance_dir: str,
        progress_cb: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Inspects all required files for an instance against the delta manifest.
        If any mod, shader, resourcepack, or config is missing, downloads ONLY that file from GitHub.
        """
        manifest = self.load_local_manifest()
        files = manifest.get("files", {})
        if not files:
            return {"success": True, "downloaded": 0, "missing": 0, "errors": []}

        inst_prefix = f"instances/{instance_id}/"
        target_files: List[Tuple[str, str, Optional[str]]] = []

        for rel_manifest_path, meta in files.items():
            norm_rel = rel_manifest_path.replace("\\", "/")
            if norm_rel.startswith(inst_prefix):
                sub_path = norm_rel[len(inst_prefix):]
                dest_path = os.path.join(instance_dir, sub_path.replace("/", os.sep))
                exp_hash = meta.get("sha256")
                target_files.append((norm_rel, dest_path, exp_hash))

        missing_list: List[Tuple[str, str, Optional[str]]] = []
        for rel_url, dest_p, exp_h in target_files:
            if not os.path.isfile(dest_p) or os.path.getsize(dest_p) == 0:
                missing_list.append((rel_url, dest_p, exp_h))

        if not missing_list:
            return {"success": True, "downloaded": 0, "missing": 0, "errors": []}

        downloaded_count = 0
        errors: List[str] = []
        total_missing = len(missing_list)

        for idx, (rel_url, dest_p, exp_h) in enumerate(missing_list, start=1):
            file_name = os.path.basename(dest_p)
            if progress_cb:
                progress_cb(file_name, idx, total_missing)

            ok = self.fetch_file(rel_url, dest_p, expected_hash=exp_h)
            if ok:
                downloaded_count += 1
            else:
                errors.append(file_name)

        return {
            "success": len(errors) == 0,
            "downloaded": downloaded_count,
            "missing": total_missing,
            "errors": errors,
        }

    def ensure_single_file(
        self,
        rel_path: str,
        dest_abs_path: str,
        expected_hash: Optional[str] = None,
    ) -> bool:
        """Checks if a file exists with non-zero size, fetching from GitHub if missing."""
        if os.path.isfile(dest_abs_path) and os.path.getsize(dest_abs_path) > 0:
            if not expected_hash or sha256_file(dest_abs_path).lower() == expected_hash.lower():
                return True
        return self.fetch_file(rel_path, dest_abs_path, expected_hash=expected_hash)
