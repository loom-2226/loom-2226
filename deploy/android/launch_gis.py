#!/usr/bin/env python3
"""Android GIS launcher using the LOOM runtime-root contract."""
from pathlib import Path
import os
import subprocess
import sys

# Post-migration Android defaults. Explicit environment roots always win.
LOOM_ROOT = Path("/storage/emulated/0/Documents/LOOM")
APP = Path(os.environ.get("LOOM_APP_ROOT") or os.environ.get("LOOM_HOME") or str(LOOM_ROOT / "runtime")).expanduser().resolve()
DATA = Path(os.environ.get("LOOM_DATA_ROOT") or str(LOOM_ROOT / "data")).expanduser().resolve()
CAMPAIGN = Path(os.environ.get("LOOM_CAMPAIGN_ROOT") or str(LOOM_ROOT / "campaign")).expanduser().resolve()
GIS = APP / "src" / "loom_gis.py"
DB = DATA / "LOOM_2226.sqlite3"
CIV = DATA / "LOOM_2226_CIVSTATE.sqlite3"

for p in (GIS, DB, CIV):
    if not p.exists():
        raise SystemExit(f"LOOM file missing: {p}")

env = os.environ.copy()
env.update({
    "LOOM_APP_ROOT": str(APP),
    "LOOM_DATA_ROOT": str(DATA),
    "LOOM_CAMPAIGN_ROOT": str(CAMPAIGN),
    "LOOM_HOME": str(APP),
})

argv = [
    sys.executable, str(GIS),
    "--db", str(DB),
    "--civ-db", str(CIV),
    "--nav-runtime-root", str(APP),
]

# Provider-backed acquisition is the Android default. Cache-only planning is
# available explicitly for deterministic/offline qualification runs.
offline = str(os.environ.get("LOOM_NAV_PLANNING_OFFLINE") or "").strip().lower()
if offline in {"1", "true", "yes", "on"}:
    argv.append("--nav-planning-offline")

raise SystemExit(subprocess.call(argv, env=env))
