#!/usr/bin/env python3
"""LOOM 2226 development source sync.

Copies an explicitly allowlisted set of mutable application sources from a local
Git checkout into LOOM_APP_ROOT. It is intentionally separate from the pinned
release updater: development sync never installs canonical DATA and never reads,
writes, copies, or deletes CAMPAIGN authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ANDROID_APP_ROOT = Path("/storage/emulated/0/Documents/LOOM/runtime")
WINDOWS_APP_ROOT = Path.home() / "Documents" / "LOOM"
STATE_FILE = ".loom_dev_state.json"
SOURCE_SUFFIXES = {".py", ".js", ".html", ".css", ".json"}


@dataclass(frozen=True)
class SyncItem:
    path: str
    state: str
    source_sha256: str
    target_sha256: str | None


def _is_android(env: dict[str, str] | os._Environ[str]) -> bool:
    return bool(env.get("ANDROID_ROOT") or env.get("TERMUX_VERSION"))


def default_app_root(environ=None) -> Path:
    env = os.environ if environ is None else environ
    explicit = str(env.get("LOOM_APP_ROOT", "")).strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    legacy = str(env.get("LOOM_HOME", "")).strip()
    if legacy:
        return Path(legacy).expanduser().resolve()
    return (ANDROID_APP_ROOT if _is_android(env) else WINDOWS_APP_ROOT).resolve()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _allowed_source(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root)
    parts = rel.parts
    if not parts:
        return False
    if parts[0] == "src":
        if len(parts) >= 2 and parts[1] == "loom":
            return path.suffix.lower() in SOURCE_SUFFIXES
        return len(parts) == 2 and path.name.startswith("loom_") and path.suffix.lower() == ".py"
    if parts[0] == "web":
        return path.suffix.lower() in SOURCE_SUFFIXES
    if parts[:2] in {("deploy", "android"), ("deploy", "windows")}:
        return path.suffix.lower() == ".py"
    return False


def discover_sources(repo_root: Path) -> list[Path]:
    roots = [repo_root / "src", repo_root / "web", repo_root / "deploy" / "android", repo_root / "deploy" / "windows"]
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and _allowed_source(path, repo_root):
                found.append(path)
    return sorted(found, key=lambda p: p.relative_to(repo_root).as_posix())


def _git_identity(repo_root: Path) -> dict[str, str | None]:
    def run(*args: str) -> str | None:
        try:
            return subprocess.check_output(["git", "-C", str(repo_root), *args], text=True, stderr=subprocess.DEVNULL).strip() or None
        except (OSError, subprocess.CalledProcessError):
            return None
    return {"branch": run("branch", "--show-current"), "commit": run("rev-parse", "HEAD")}


def _atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
        shutil.copyfileobj(src, tmp)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    try:
        os.replace(tmp_path, target)
    finally:
        tmp_path.unlink(missing_ok=True)


def sync(repo_root: Path, app_root: Path, *, dry_run: bool = False) -> list[SyncItem]:
    repo_root = repo_root.resolve()
    app_root = app_root.resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = app_root / ".loom_dev_backups" / timestamp
    results: list[SyncItem] = []
    for source in discover_sources(repo_root):
        rel = source.relative_to(repo_root)
        target = app_root / rel
        source_hash = sha256_file(source)
        target_hash = sha256_file(target) if target.exists() else None
        if target_hash == source_hash:
            results.append(SyncItem(rel.as_posix(), "UNCHANGED", source_hash, target_hash))
            continue
        if not dry_run:
            if target.exists():
                backup = backup_root / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
            _atomic_copy(source, target)
        results.append(SyncItem(rel.as_posix(), "DRY_RUN" if dry_run else "SYNCED", source_hash, target_hash))
    if not dry_run:
        app_root.mkdir(parents=True, exist_ok=True)
        state = {
            "mode": "development_sync",
            "synced_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "repo_root": str(repo_root),
            "app_root": str(app_root),
            "git": _git_identity(repo_root),
            "files": [item.__dict__ for item in results],
            "authority_guards": {
                "campaign": "never touched",
                "canonical_data": "never touched",
                "release_updater": "unchanged/pinned",
            },
        }
        (app_root / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return results


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Sync mutable LOOM development code from local Git checkout into APP root")
    parser.add_argument("command", nargs="?", choices=["sync", "status"], default="sync")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--app-root")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    app_root = Path(args.app_root).expanduser().resolve() if args.app_root else default_app_root()
    results = sync(repo_root, app_root, dry_run=(args.dry_run or args.command == "status"))
    print(f"LOOM DEV SOURCE: {repo_root}")
    print(f"LOOM APP ROOT:   {app_root}")
    print("CAMPAIGN/DATA:   EXCLUDED")
    for item in results:
        print(f"{item.state:10} {item.path}")
    changed = sum(item.state in {"SYNCED", "DRY_RUN"} for item in results)
    print(f"\nDEV SYNC {'WOULD CHANGE' if args.command == 'status' or args.dry_run else 'CHANGED'} {changed} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
