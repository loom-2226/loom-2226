"""Read-only runtime diagnostics for LOOM.

The collector reports what exists and what the runtime resolved. It does not create,
move, delete, repair, or otherwise mutate runtime data.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import os
import platform
import subprocess
import sys

from loom.runtime import RuntimeRoots, resolve_runtime_roots

CONTRACT = "LOOM_RUNTIME_DIAGNOSTICS_V1"


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _file_identity(path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path),
        "exists": exists,
        "is_file": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else None,
        "sha256": _sha256(path),
    }


def _git_head(app_root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(app_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = proc.stdout.strip()
    return value if proc.returncode == 0 and value else None


def collect_runtime_manifest(*, roots: RuntimeRoots | None = None) -> dict[str, Any]:
    roots = roots or resolve_runtime_roots()
    app = roots.app_root
    data = roots.data_root
    campaign = roots.campaign_root

    db_names = ("LOOM_2226.sqlite3", "LOOM_2226_media.sqlite3", "LOOM_2226_CIVSTATE.sqlite3")
    databases = []
    seen: set[str] = set()
    for root_name, root in (("data_root", data), ("app_data", app / "data")):
        for name in db_names:
            path = root / name
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            item = _file_identity(path)
            item["root"] = root_name
            item["name"] = name
            databases.append(item)

    campaign_state = _file_identity(campaign / "LOOM_STATE_V1.json")
    if not campaign_state["exists"] and campaign != app:
        campaign_state = _file_identity(app / "LOOM_STATE_V1.json")
        campaign_state["compatibility_fallback"] = True

    return {
        "contract": CONTRACT,
        "runtime": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "executable": sys.executable,
            "cwd": str(Path.cwd().resolve()),
            "git_head": _git_head(app),
        },
        "roots": roots.to_dict(),
        "environment": {
            key: os.environ.get(key)
            for key in ("LOOM_APP_ROOT", "LOOM_DATA_ROOT", "LOOM_CAMPAIGN_ROOT", "LOOM_HOME")
        },
        "source": {
            "loom_gis": _file_identity(app / "src" / "loom_gis.py"),
            "runtime": _file_identity(app / "src" / "loom" / "runtime.py"),
        },
        "databases": databases,
        "campaign": {
            "state": campaign_state,
            "navigator_cache": {
                "path": str(campaign / "LOOM_Navigator_Cache_v1"),
                "exists": (campaign / "LOOM_Navigator_Cache_v1").exists(),
            },
        },
    }


def render_runtime_audit(manifest: dict[str, Any]) -> str:
    roots = manifest["roots"]
    runtime = manifest["runtime"]
    lines = [
        "LOOM RUNTIME AUDIT",
        "==================",
        f"Contract      {manifest['contract']}",
        f"Platform      {runtime['platform']}",
        f"Python        {runtime['python']}",
        f"Git head      {runtime['git_head'] or 'unavailable'}",
        f"APP ROOT      {roots['app_root']} [{roots['app_source']}]",
        f"DATA ROOT     {roots['data_root']} [{roots['data_source']}]",
        f"CAMPAIGN ROOT {roots['campaign_root']} [{roots['campaign_source']}]",
        "",
        "DATABASES",
    ]
    for db in manifest["databases"]:
        status = "PRESENT" if db["exists"] else "missing"
        digest = db["sha256"][:12] if db["sha256"] else "-"
        lines.append(f"{status:7} {db['root']:9} {db['name']} sha256={digest} path={db['path']}")
    state = manifest["campaign"]["state"]
    lines.extend(["", f"CAMPAIGN STATE {'PRESENT' if state['exists'] else 'missing'} {state['path']}"])
    return "\n".join(lines) + "\n"


def manifest_json(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"
