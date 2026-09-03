#!/usr/bin/env python3
from pathlib import Path
import os
import runpy

ROOT = Path('/storage/emulated/0/Download/LOOM_TEST')
os.environ['LOOM_HOME'] = str(ROOT)
os.environ['LOOM_DATA_DIR'] = str(ROOT / 'data')
runpy.run_path(str(ROOT / 'src' / 'loom_navigator.py'), run_name='__main__')
