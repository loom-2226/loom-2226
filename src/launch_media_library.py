#!/usr/bin/env python3
from pathlib import Path
import os, runpy

root = Path(os.environ.get("LOOM_HOME") or Path(__file__).resolve().parent.parent).expanduser().resolve()
os.environ["LOOM_HOME"] = str(root)
runpy.run_path(str(root / "src" / "loom_media_library.py"), run_name="__main__")
