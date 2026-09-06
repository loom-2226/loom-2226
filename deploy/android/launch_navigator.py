#!/usr/bin/env python3
"""Android Navigator launcher using the explicit convergence root contract."""
from pathlib import Path
import os
import runpy

APP = Path(os.environ.get("LOOM_APP_ROOT") or os.environ.get("LOOM_HOME") or "/storage/emulated/0/Download/LOOM_TEST").expanduser().resolve()
DATA = Path(os.environ.get("LOOM_DATA_ROOT") or "/storage/emulated/0/Documents/LOOM/data").expanduser().resolve()
CAMPAIGN = Path(os.environ.get("LOOM_CAMPAIGN_ROOT") or APP).expanduser().resolve()

os.environ["LOOM_APP_ROOT"] = str(APP)
os.environ["LOOM_DATA_ROOT"] = str(DATA)
os.environ["LOOM_CAMPAIGN_ROOT"] = str(CAMPAIGN)
os.environ["LOOM_HOME"] = str(APP)  # legacy frozen-core compatibility
os.environ["LOOM_DATA_DIR"] = str(DATA)  # legacy frozen-core compatibility

runpy.run_path(str(APP / "src" / "loom_navigator.py"), run_name="__main__")
