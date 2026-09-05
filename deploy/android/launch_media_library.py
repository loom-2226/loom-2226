#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(os.environ.get("LOOM_HOME", "/storage/emulated/0/Download/LOOM_TEST"))
APP = ROOT / "src" / "loom_media_library.py"
DB = ROOT / "data" / "LOOM_2226.sqlite3"
MEDIA = ROOT / "data" / "LOOM_2226_media.sqlite3"
for p in (APP, DB, MEDIA):
    if not p.exists():
        raise SystemExit(f"LOOM file missing: {p}")
raise SystemExit(subprocess.call([sys.executable, str(APP), "--root", str(ROOT)]))
