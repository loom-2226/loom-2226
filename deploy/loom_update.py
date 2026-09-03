#!/usr/bin/env python3
"""LOOM 2226 updater/bootstrap v0.3.

Fetches a pinned release manifest and canonical artifacts from the private LOOM
GitHub repository. Repository artifacts and GitHub Release assets are supported.
All payloads are SHA-256 verified before atomic installation. Mutable runtime
state is preserved.

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
DEFAULT_REF = "main"
CONTENTS_API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
RELEASE_ASSET_API = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/assets"
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


def github_bytes(url: str, accept: str) -> bytes:
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token()}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "LOOM-2226-Updater/0.3",
        },
    )
    with urlopen(req, timeout=900) as response:
        return response.read()


def github_contents_bytes(path: str, ref: str) -> bytes:
    return github_bytes(
        f"{CONTENTS_API}/{path}?ref={ref}",
        "application/vnd.github.raw+json",
    )


def github_artifact_bytes(artifact: dict, ref: str) -> bytes:
    source = artifact.get("source", "repository")
    if source == "repository":
        return github_contents_bytes(artifact["path"], ref)
    if source == "release_asset":
        asset_id = artifact.get("asset_id")
        if not isinstance(asset_id, int):
            raise RuntimeError(f"Release asset missing numeric asset_id: {artifact['path']}")
        return github_bytes(
            f"{RELEASE_ASSET_API}/{asset_id}",
            "application/octet-stream",
        )
    raise RuntimeError(f"Unknown artifact source {source!r}: {artifact['path']}")


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
            rel = (
                target.name
                if target.parent.name not in {"src", "data"}
                else f"{target.parent.name}/{target.name}"
            )
            backup = backup_root / rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def validate_manifest(manifest: dict) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise RuntimeError("Release manifest is missing artifacts list")
    for artifact in artifacts:
        for key in ("path", "install_group", "required"):
            if key not in artifact:
                raise RuntimeError(f"Artifact missing {key}: {artifact}")
        source = artifact.get("source", "repository")
        if source not in {"repository", "release_asset"}:
            raise RuntimeError(f"Unknown artifact source {source!r}")
        if source == "release_asset" and not isinstance(artifact.get("asset_id"), int):
            raise RuntimeError(f"Release asset missing numeric asset_id: {artifact['path']}")
        expected_size = artifact.get("size_bytes")
        if expected_size is not None and (not isinstance(expected_size, int) or expected_size < 0):
            raise RuntimeError(f"Invalid size_bytes for {artifact['path']}")


def load_manifest(ref: str) -> dict:
    raw = github_contents_bytes(MANIFEST_PATH, ref)
    manifest = json.loads(raw.decode("utf-8"))
    validate_manifest(manifest)
    source_ref = manifest.get("source_ref")
    if source_ref and source_ref != ref:
        raise RuntimeError(
            f"Manifest source_ref={source_ref!r} does not match requested ref={ref!r}"
        )
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
        expected_size = artifact.get("size_bytes")
        if expected_size is not None and target.stat().st_size != expected_size:
            actual = sha256_file(target)
            results.append(ArtifactResult(artifact["path"], str(target), "MISMATCH", expected, actual))
            continue
        actual = sha256_file(target)
        state = "OK" if actual == expected else "MISMATCH"
        results.append(ArtifactResult(artifact["path"], str(target), state, expected, actual))
    return results


def install_release(
    root: Path,
    manifest: dict,
    ref: str,
    artifact_fetcher: Callable[[dict, str], bytes] = github_artifact_bytes,
    dry_run: bool = False,
) -> list[ArtifactResult]:
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

        if target.exists():
            expected_size = artifact.get("size_bytes")
            size_ok = expected_size is None or target.stat().st_size == expected_size
            if size_ok and sha256_file(target) == expected:
                results.append(
                    ArtifactResult(artifact["path"], str(target), "UNCHANGED", expected, expected)
                )
                continue

        payload = artifact_fetcher(artifact, ref)
        expected_size = artifact.get("size_bytes")
        if expected_size is not None and len(payload) != expected_size:
            raise RuntimeError(
                f"SIZE MISMATCH for {artifact['path']}\n"
                f"expected={expected_size}\nactual={len(payload)}"
            )
        actual = sha256_bytes(payload)
        if actual != expected:
            raise RuntimeError(
                f"HASH MISMATCH for {artifact['path']}\nexpected={expected}\nactual={actual}"
            )

        if not dry_run:
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
        (root / INSTALL_STATE).write_text(
            json.dumps(install_state, indent=2) + "\n", encoding="utf-8"
        )
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


def main(
    argv: list[str] | None = None,
    manifest_loader: Callable[[str], dict] = load_manifest,
    artifact_fetcher: Callable[[dict, str], bytes] = github_artifact_bytes,
) -> int:
    args = parse_args(argv)
    root = platform_root(args.root)
    manifest = manifest_loader(args.ref)
    print(f"LOOM ROOT: {root}")
    print(f"SOURCE REF: {args.ref}")
    print(f"RELEASE: {manifest['release_id']} ({manifest['release_state']})")

    if args.command in {"validate", "status"}:
        results = validate_local(root, manifest)
        print_results(results)
        return 2 if has_blockers(results) else 0

    results = install_release(
        root, manifest, args.ref, artifact_fetcher=artifact_fetcher, dry_run=args.dry_run
    )
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
