#!/usr/bin/env python3
"""LOOM 2226 updater/bootstrap.

Downloads the release manifest and required artifacts from the private GitHub
repository, verifies SHA-256, installs canonical code/data atomically, and leaves
mutable campaign/runtime state untouched.

Authentication is local-only. Set LOOM_GITHUB_TOKEN in the environment or place
a token in ~/.loom_github_token. Never commit a token to the repository.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
import tempfile
from urllib.request import Request, urlopen

OWNER = "loom-2226"
REPO = "loom-2226"
REF = os.environ.get("LOOM_REF", "staging/initial-baseline")
API_ROOT = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

ANDROID_ROOT = Path("/storage/emulated/0/Documents/LOOM")
WINDOWS_ROOT = Path.home() / "Documents" / "LOOM"


def platform_root() -> Path:
    if ANDROID_ROOT.parent.exists():
        return ANDROID_ROOT
    return Path(os.environ.get("LOOM_HOME", WINDOWS_ROOT))


def token() -> str:
    value = os.environ.get("LOOM_GITHUB_TOKEN", "").strip()
    if value:
        return value
    token_file = Path.home() / ".loom_github_token"
    if token_file.exists():
        return token_file.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "GitHub token not configured. Set LOOM_GITHUB_TOKEN or create ~/.loom_github_token"
    )


def request_bytes(path: str) -> bytes:
    url = f"{API_ROOT}/{path}?ref={REF}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token()}",
            "Accept": "application/vnd.github.raw+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "LOOM-2226-Updater",
        },
    )
    with urlopen(req, timeout=120) as r:
        return r.read()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def target_for(root: Path, artifact: dict) -> Path:
    src_path = Path(artifact["path"])
    group = artifact["install_group"]
    if group == "code":
        return root / "src" / src_path.name
    if group in {"canonical_data", "media"}:
        return root / "data" / src_path.name
    raise ValueError(f"Unknown install_group: {group}")


def atomic_write(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tf:
        tmp = Path(tf.name)
        tf.write(data)
        tf.flush()
        os.fsync(tf.fileno())
    if target.exists():
        backup = target.with_suffix(target.suffix + ".preupdate")
        shutil.copy2(target, backup)
    os.replace(tmp, target)


def main() -> int:
    root = platform_root()
    print(f"LOOM ROOT: {root}")
    print(f"SOURCE REF: {REF}")

    manifest_raw = request_bytes("manifests/release_manifest.json")
    manifest = json.loads(manifest_raw.decode("utf-8"))
    print(f"RELEASE: {manifest['release_id']} ({manifest['release_state']})")

    pending = []
    installed = []
    for artifact in manifest["artifacts"]:
        expected = artifact.get("sha256")
        required = bool(artifact.get("required", False))
        if not expected:
            if required:
                pending.append(artifact["path"])
            continue

        print(f"FETCH: {artifact['path']}")
        payload = request_bytes(artifact["path"])
        actual = sha256_bytes(payload)
        if actual != expected:
            raise RuntimeError(
                f"HASH MISMATCH for {artifact['path']}\nexpected={expected}\nactual={actual}"
            )
        target = target_for(root, artifact)
        atomic_write(target, payload)
        installed.append(str(target))
        print(f"OK: {target}")

    if pending:
        print("\nNOT RELEASE-COMPLETE. Required artifacts still pending:")
        for item in pending:
            print(f"  - {item}")
        print("Existing installed files were hash-verified and updated safely.")
        return 2

    print("\nLOOM UPDATE COMPLETE")
    for item in installed:
        print(f"  {item}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"UPDATE FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
