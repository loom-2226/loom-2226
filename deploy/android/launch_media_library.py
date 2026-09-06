#!/usr/bin/env python3
from pathlib import Path
import os,runpy
root=Path(os.environ.get('LOOM_HOME','/storage/emulated/0/Download/LOOM_TEST'))
os.environ['LOOM_HOME']=str(root)
runpy.run_path(str(root/'src'/'loom_media_library.py'),run_name='__main__')
