#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(os.environ.get("LOOM_HOME", "/storage/emulated/0/Download/LOOM_TEST"))
GIS = ROOT / "src" / "loom_solar_gis.py"
DB = ROOT / "data" / "LOOM_2226.sqlite3"
CIV = ROOT / "data" / "LOOM_2226_CIVSTATE.sqlite3"

for p in (GIS, DB, CIV):
    if not p.exists():
        raise SystemExit(f"LOOM file missing: {p}")

raise SystemExit(subprocess.call([
    sys.executable, str(GIS),
    "--db", str(DB),
    "--civ-db", str(CIV),
]))
