#!/usr/bin/env python3
"""LOOM 2226 updater/bootstrap v0.2.

Fetches the release manifest and canonical artifacts from the private LOOM GitHub
repository, verifies SHA-256, installs atomically, preserves mutable runtime state,
and supports validation/status-only operation on Android and Windows.

Authentication is local-only. Set LOOM_GITHUB_TOKEN in the environment or place
a token in ~/.loom_github_token. Never commit a token to the repository.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from typing import Callable
from urllib.request import Request, urlopen

OWNER = "loom-2226"
REPO = "loom-2226"
DEFAULT_REF = "staging/initial-baseline"
API_ROOT = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
ANDROID_ROOT = Path("/storage/emulated/0/Documents/LOOM")
WINDOWS_ROOT = Path.home() / "Documents" / "LOOM"
MANIFEST_PATH = "manifests/release_manifest.json"
INSTALL_STATE = ".loom_install_state.json"


@dataclass(frozen=True)
class ArtifactResult:
    path: str
    target: str | None
    state: str
    expected_sha256: str | None
    actual_sha256: str | None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def platform_root(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env_home = os.environ.get("LOOM_HOME", "").strip()
    if env_home:
        return Path(env_home).expanduser()
    if Path("/storage/emulated/0").exists():
        return ANDROID_ROOT
    return WINDOWS_ROOT


def token() -> str:
    value = os.environ.get("LOOM_GITHUB_TOKEN", "").strip()
    if value:
        return value
    token_file = Path.home() / ".loom_github_token"
    if token_file.exists():
        value = token_file.read_text(encoding="utf-8").strip()
        if value:
            return value
    raise RuntimeError(
        "GitHub token not configured. Set LOOM_GITHUB_TOKEN or create ~/.loom_github_token"
    )


def github_request_bytes(path: str, ref: str) -> bytes:
    url = f"{API_ROOT}/{path}?ref={ref}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token()}",
            "Accept": "application/vnd.github.raw+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "LOOM-2226-Updater/0.2",
        },
    )
    with urlopen(req, timeout=180) as response:
        return response.read()


def target_for(root: Path, artifact: dict) -> Path:
    src_path = Path(artifact["path"])
    group = artifact["install_group"]
    if group == "code":
        return root / "src" / src_path.name
    if group in {"canonical_data", "media"}:
        return root / "data" / src_path.name
    raise ValueError(f"Unknown install_group: {group}")


def atomic_write(target: Path, data: bytes, backup_root: Path | None = None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tf:
        tmp = Path(tf.name)
        tf.write(data)
        tf.flush()
        os.fsync(tf.fileno())
    try:
        if target.exists() and backup_root is not None:
            rel = target.name if target.parent.name not in {"src", "data"} else f"{target.parent.name}/{target.name}"
            backup = backup_root / rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def load_manifest(fetcher: Callable[[str, str], bytes], ref: str) -> dict:
    raw = fetcher(MANIFEST_PATH, ref)
    manifest = json.loads(raw.decode("utf-8"))
    if not isinstance(manifest.get("artifacts"), list):
        raise RuntimeError("Release manifest is missing artifacts list")
    source_ref = manifest.get("source_ref")
    if source_ref and source_ref != ref:
        raise RuntimeError(f"Manifest source_ref={source_ref!r} does not match requested ref={ref!r}")
    return manifest


def validate_local(root: Path, manifest: dict) -> list[ArtifactResult]:
    results: list[ArtifactResult] = []
    for artifact in manifest["artifacts"]:
        expected = artifact.get("sha256")
        target = target_for(root, artifact)
        if not expected:
            state = "PENDING_REQUIRED" if artifact.get("required") else "PENDING_OPTIONAL"
            results.append(ArtifactResult(artifact["path"], str(target), state, None, None))
            continue
        if not target.exists():
            results.append(ArtifactResult(artifact["path"], str(target), "MISSING", expected, None))
            continue
        actual = sha256_file(target)
        state = "OK" if actual == expected else "MISMATCH"
        results.append(ArtifactResult(artifact["path"], str(target), state, expected, actual))
    return results


def install_release(root: Path, manifest: dict, ref: str,
                    fetcher: Callable[[str, str], bytes], dry_run: bool = False) -> list[ArtifactResult]:
    release_id = manifest["release_id"]
    backup_root = root / ".loom_backups" / release_id
    results: list[ArtifactResult] = []

    for artifact in manifest["artifacts"]:
        expected = artifact.get("sha256")
        required = bool(artifact.get("required"))
        target = target_for(root, artifact)
        if not expected:
            state = "PENDING_REQUIRED" if required else "PENDING_OPTIONAL"
            results.append(ArtifactResult(artifact["path"], str(target), state, None, None))
            continue

        payload = fetcher(artifact["path"], ref)
        actual = sha256_bytes(payload)
        if actual != expected:
            raise RuntimeError(
                f"HASH MISMATCH for {artifact['path']}\nexpected={expected}\nactual={actual}"
            )
        if not dry_run:
            if target.exists() and sha256_file(target) == expected:
                state = "UNCHANGED"
            else:
                atomic_write(target, payload, backup_root=backup_root)
                state = "INSTALLED"
        else:
            state = "DRY_RUN_OK"
        results.append(ArtifactResult(artifact["path"], str(target), state, expected, actual))

    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)
        install_state = {
            "release_id": release_id,
            "release_state": manifest.get("release_state"),
            "source_ref": ref,
            "artifacts": [r.__dict__ for r in results],
        }
        (root / INSTALL_STATE).write_text(json.dumps(install_state, indent=2) + "\n", encoding="utf-8")
    return results


def print_results(results: list[ArtifactResult]) -> None:
    for result in results:
        print(f"{result.state:16} {result.path}")


def has_blockers(results: list[ArtifactResult]) -> bool:
    return any(r.state in {"PENDING_REQUIRED", "MISSING", "MISMATCH"} for r in results)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LOOM 2226 GitHub updater and validator")
    p.add_argument("command", nargs="?", choices=["update", "validate", "status"], default="update")
    p.add_argument("--ref", default=os.environ.get("LOOM_REF", DEFAULT_REF))
    p.add_argument("--root", help="Override LOOM installation root")
    p.add_argument("--dry-run", action="store_true", help="Fetch and hash-check without changing files")
    return p.parse_args(argv)


def main(argv: list[str] | None = None, fetcher: Callable[[str, str], bytes] = github_request_bytes) -> int:
    args = parse_args(argv)
    root = platform_root(args.root)
    manifest = load_manifest(fetcher, args.ref)
    print(f"LOOM ROOT: {root}")
    print(f"SOURCE REF: {args.ref}")
    print(f"RELEASE: {manifest['release_id']} ({manifest['release_state']})")

    if args.command in {"validate", "status"}:
        results = validate_local(root, manifest)
        print_results(results)
        return 2 if has_blockers(results) else 0

    results = install_release(root, manifest, args.ref, fetcher, dry_run=args.dry_run)
    print_results(results)
    if has_blockers(results):
        print("\nNOT RELEASE-COMPLETE: one or more required artifacts are pending or invalid.")
        return 2
    print("\nLOOM UPDATE COMPLETE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"UPDATE FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
