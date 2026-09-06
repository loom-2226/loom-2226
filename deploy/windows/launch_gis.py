#!/usr/bin/env python3
from pathlib import Path
import os,subprocess,sys
DEFAULT=Path.home()/"Documents"/"LOOM"
APP=Path(os.environ.get("LOOM_APP_ROOT") or os.environ.get("LOOM_HOME") or str(DEFAULT)).expanduser().resolve()
DATA=Path(os.environ.get("LOOM_DATA_ROOT") or str(APP/"data")).expanduser().resolve()
CAMPAIGN=Path(os.environ.get("LOOM_CAMPAIGN_ROOT") or str(APP/"campaign")).expanduser().resolve()
os.environ.update(LOOM_APP_ROOT=str(APP),LOOM_DATA_ROOT=str(DATA),LOOM_CAMPAIGN_ROOT=str(CAMPAIGN),LOOM_HOME=str(APP))
GIS=APP/"src"/"loom_gis.py"; DB=DATA/"LOOM_2226.sqlite3"; CIV=DATA/"LOOM_2226_CIVSTATE.sqlite3"
for p in (GIS,DB,CIV):
    if not p.exists():raise SystemExit(f"LOOM file missing: {p}")
raise SystemExit(subprocess.call([sys.executable,str(GIS),"--db",str(DB),"--civ-db",str(CIV),"--nav-runtime-root",str(APP),"--nav-planning-offline"]))
