#!/usr/bin/env python3
"""Install the PR99 HUD qualification slice onto Android APP root only.

HUD_TEST_DRIVE_ONLY. This is deliberately separate from the pinned release
updater. It installs only the explicit HUD/Wayfarer qualification allowlist,
backs up replaced files, and never touches canonical DATA or CAMPAIGN authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import tempfile
from urllib.parse import quote
from urllib.request import Request, urlopen

OWNER = "loom-2226"
REPO = "loom-2226"
REF = os.environ.get(
    "LOOM_HUD_TEST_REF",
    "feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11",
)
APP = Path(
    os.environ.get("LOOM_APP_ROOT")
    or "/storage/emulated/0/Documents/LOOM/runtime"
).expanduser().resolve()
STATE_FILE = APP / ".loom_hud_test_drive_state.json"

FILES = [
    "deploy/android/launch_hud.py",
    "engineering/current/LOOM_2226_Wayfarer_Q5_RCS_Attitude_Energy_Bridge_v0.1.md",
    "engineering/current/wayfarer_flight_system_baseline_v0.1.json",
    "engineering/current/wayfarer_q4_hud_attitude_envelope_v0.4.json",
    "engineering/current/wayfarer_q5_attitude_energy_envelope_v0.1.json",
    "engineering/current/wayfarer_q5_power_thermal_envelope_v0.2.json",
    "engineering/current/wayfarer_q7_dispatch_doctrine_v0.1.json",
    "engineering/current/wayfarer_torch_feedstock_screening_v0.2.json",
    "engineering/hud/wayfarer_pr96_hud_engineering_snapshot_v0.1.json",
    "src/loom/hud/demo/earth_moon_qualification.html",
    "src/loom/hud/demo/hud_family_control_v01.js",
    "src/loom/hud/demo/hud_family_profiles_v01.js",
    "src/loom/hud/demo/hud_nav_flight_plan_v01.js",
    "src/loom/hud/demo/hud_tactical_track_v01.js",
    "src/loom/hud/demo/hud_v0_15.js",
    "src/loom/hud/demo/hud_v0_18_range_rate.js",
    "src/loom/hud/demo/hud_v0_20_quality.js",
    "src/loom/hud/demo/hud_wayfarer_engineering_state_v01.js",
    "src/loom/hud/engineering_state_contract.py",
    "src/loom/hud/engineering_state_payload.py",
    "src/loom/hud/hud_family_selector.py",
    "src/loom/hud/realtime_flight_qualification.py",
    "src/loom/hud/rendezvous_qualification.py",
    "src/loom/hud/server.py",
    "src/loom/hud/wayfarer_attitude_envelope.py",
    "src/loom/hud/wayfarer_engineering_state.py",
]


def _token() -> str:
    value = str(os.environ.get("LOOM_GITHUB_TOKEN") or "").strip()
    if value:
        return value
    path = Path.home() / ".loom_github_token"
    if path.is_file():
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value
    raise RuntimeError(
        "GitHub token not configured. Set LOOM_GITHUB_TOKEN or create ~/.loom_github_token"
    )


def _fetch(path: str) -> bytes:
    encoded = quote(path, safe="/")
    ref = quote(REF, safe="")
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{encoded}?ref={ref}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {_token()}",
            "Accept": "application/vnd.github.raw+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "LOOM-HUD-Pixel-Test-Drive/0.1",
        },
    )
    with urlopen(req, timeout=120) as response:
        return response.read()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(target: Path, payload: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as fh:
        tmp = Path(fh.name)
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    try:
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = APP / ".loom_hud_test_drive_backups" / timestamp
    records = []

    print("LOOM HUD PIXEL TEST DRIVE INSTALL")
    print(f"SOURCE REF: {REF}")
    print(f"APP ROOT:   {APP}")
    print("AUTHORITY:  HUD_TEST_DRIVE_ONLY / DATA NONE / CAMPAIGN NONE")

    staged: list[tuple[str, bytes, str]] = []
    for path in FILES:
        print(f"FETCHING     {path}")
        payload = _fetch(path)
        staged.append((path, payload, _sha256(payload)))

    for path, payload, digest in staged:
        target = APP / path
        prior_digest = None
        if target.is_file():
            prior = target.read_bytes()
            prior_digest = _sha256(prior)
            backup = backup_root / path
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
        _atomic_write(target, payload)
        installed_digest = _sha256(target.read_bytes())
        if installed_digest != digest:
            raise RuntimeError(f"post-install digest mismatch: {path}")
        records.append(
            {
                "path": path,
                "sha256": digest,
                "prior_sha256": prior_digest,
                "state": "INSTALLED" if prior_digest != digest else "UNCHANGED_BYTES",
            }
        )
        print(f"INSTALLED    {path}")

    state = {
        "mode": "HUD_TEST_DRIVE_ONLY",
        "installed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_ref": REF,
        "app_root": str(APP),
        "authority_guards": {
            "data": "never touched",
            "campaign": "never touched",
            "release_manifest": "never changed",
        },
        "files": records,
    }
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    print("\nHUD TEST-DRIVE SLICE INSTALLED")
    print(f"STATE: {STATE_FILE}")
    print(f"RUN:   {APP / 'deploy' / 'android' / 'launch_hud.py'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"HUD TEST-DRIVE INSTALL FAILED: {exc}")
        raise SystemExit(1)
