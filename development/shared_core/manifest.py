"""Small, dependency-free manifest and atomic tree synchronizer for SIR.

The installer uses this module for repeatable repairs.  Files are compared by
SHA-256 before they are replaced, and user-owned Minecraft data is never
overwritten by a managed payload sync.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Iterable


SkipPredicate = Callable[[Path], bool]


def sha256_file(path: str | os.PathLike[str], chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: str | os.PathLike[str]) -> Iterable[Path]:
    base = Path(root)
    if not base.is_dir():
        return
    for path in base.rglob("*"):
        if path.is_file():
            yield path


def is_user_owned(relative_path: Path) -> bool:
    """Return true for saves, logs, and local preferences that repairs protect."""

    parts = [part.lower() for part in relative_path.parts]
    basename = parts[-1] if parts else ""
    protected_root_files = {
        "accounts.json",
        "ias_accounts.json",
        "launcher_settings.json",
        "server_orchestrator_settings.json",
        "install-state.json",
    }
    protected_names = {
        "options.txt",
        "optionsof.txt",
        "servers.dat",
        "servers.dat_old",
        "resourcepacks.txt",
        "shaderpacks.txt",
    }
    if len(parts) == 1 and basename in protected_root_files:
        return True
    if basename in protected_names:
        return True
    return any(part in {"saves", "screenshots", "logs", "crash-reports"} for part in parts)


def atomic_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".sir-copy-", suffix=".tmp", dir=str(dst.parent))
    try:
        with os.fdopen(fd, "wb") as target, src.open("rb") as source:
            shutil.copyfileobj(source, target, length=1024 * 1024)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temp_name, dst)
    finally:
        if os.path.exists(temp_name):
            try:
                os.remove(temp_name)
            except OSError:
                pass


def sync_tree(src_root: str | os.PathLike[str], dst_root: str | os.PathLike[str], skip: SkipPredicate | None = None, on_progress: Any = None) -> dict:
    """Synchronize missing/changed files and return deterministic counters."""

    source = Path(src_root)
    destination = Path(dst_root)
    result = {"added": 0, "changed": 0, "unchanged": 0, "preserved": 0, "failed": 0, "files": {}}
    if not source.is_dir():
        return result

    all_files = sorted(iter_files(source), key=lambda item: str(item).lower())
    total_files = len(all_files)

    for idx, file_path in enumerate(all_files, 1):
        relative = file_path.relative_to(source)
        if skip and skip(relative):
            result["preserved"] += 1
            continue
        target = destination / relative
        if on_progress:
            try:
                on_progress(file_path.name, idx, total_files)
            except Exception:
                pass
        try:
            source_stat = file_path.stat()
            target_stat = target.stat() if target.is_file() else None
            
            # Fast check: If destination file exists with same size and mtime, consider unchanged
            if target_stat and target_stat.st_size == source_stat.st_size and abs(target_stat.st_mtime - source_stat.st_mtime) < 1.0:
                result["unchanged"] += 1
                continue

            source_hash = sha256_file(file_path)
            result["files"][str(relative).replace("\\", "/")] = source_hash
            if target.is_file():
                if target_stat and target_stat.st_size == source_stat.st_size and sha256_file(target) == source_hash:
                    # Update mtime on destination to match source for future instant checks
                    try: os.utime(target, (source_stat.st_atime, source_stat.st_mtime))
                    except Exception: pass
                    result["unchanged"] += 1
                    continue
                changed = True
            else:
                changed = False
            atomic_copy(file_path, target)
            try: os.utime(target, (source_stat.st_atime, source_stat.st_mtime))
            except Exception: pass
            result["changed" if changed else "added"] += 1
        except OSError:
            result["failed"] += 1
    return result


def merge_counts(total: dict, current: dict) -> None:
    for key in ("added", "changed", "unchanged", "preserved", "failed"):
        total[key] = total.get(key, 0) + int(current.get(key, 0))
    total.setdefault("files", {}).update(current.get("files", {}))

