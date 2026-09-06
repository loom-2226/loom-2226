#!/usr/bin/env python3
from pathlib import Path
import os,runpy
root=Path(os.environ.get('LOOM_HOME') or ('/storage/emulated/0/Download/LOOM_TEST' if Path('/storage/emulated/0').exists() else Path.home()/'Documents'/'LOOM'))
os.environ['LOOM_HOME']=str(root)
runpy.run_path(str(root/'src'/'loom_media_library.py'),run_name='__main__')
