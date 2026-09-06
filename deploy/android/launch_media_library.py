#!/usr/bin/env python3
"""Android media/canon browser launcher using split LOOM roots."""
from pathlib import Path
import os,subprocess,sys
LOOM_ROOT=Path('/storage/emulated/0/Documents/LOOM')
APP=Path(os.environ.get('LOOM_APP_ROOT') or os.environ.get('LOOM_HOME') or str(LOOM_ROOT/'runtime')).expanduser().resolve()
DATA=Path(os.environ.get('LOOM_DATA_ROOT') or str(LOOM_ROOT/'data')).expanduser().resolve()
SCRIPT=APP/'src'/'loom_media_library.py'
for p in (SCRIPT,DATA/'LOOM_2226.sqlite3',DATA/'LOOM_2226_media.sqlite3'):
    if not p.exists():raise SystemExit(f'LOOM file missing: {p}')
env=os.environ.copy();env.update({'LOOM_APP_ROOT':str(APP),'LOOM_DATA_ROOT':str(DATA),'LOOM_HOME':str(APP)})
# loom_media_library --root expects the topology root containing data/.
root=DATA.parent
raise SystemExit(subprocess.call([sys.executable,str(SCRIPT),'--root',str(root)],env=env))
