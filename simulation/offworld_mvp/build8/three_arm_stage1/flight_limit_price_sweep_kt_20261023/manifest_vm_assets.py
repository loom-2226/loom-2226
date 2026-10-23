"""Read-only inventory of VM ephemeris kernels and position tables."""
from pathlib import Path
import hashlib,os
ROOTS=[Path('/home/ubuntu/loom_solar_assets'),Path('/home/ubuntu/LOOM-output')]
EXT={'.bsp','.bpc','.tpc','.tls','.tf','.tsc','.bc','.npy','.npz'}
OUT=Path(__file__).resolve().parent/'VM_KERNEL_POSITION_MANIFEST.txt'
paths=set()
for root in ROOTS:
 for directory,dirs,files in os.walk(root):
  dirs[:]=[d for d in dirs if d not in {'.git','.venv','node_modules','__pycache__'}]
  for name in files:
   p=Path(directory)/name
   if p.suffix.lower() in EXT:paths.add(p)
with OUT.open('x') as f:
 f.write('VM KERNEL AND POSITION TABLE INVENTORY | SHA-256 | TEXT ONLY\n')
 f.write('Scope: /home/ubuntu/loom_solar_assets and /home/ubuntu/LOOM-output; extensions: '+','.join(sorted(EXT))+'\n')
 f.write('path\tsize_bytes\tsha256\n')
 for p in sorted(paths):
  h=hashlib.sha256()
  with p.open('rb') as src:
   for block in iter(lambda:src.read(8*1024*1024),b''):h.update(block)
  f.write(f'{p}\t{p.stat().st_size}\t{h.hexdigest()}\n');f.flush()
print('INVENTORY_FILES',len(paths),'OUTPUT',OUT,flush=True)
