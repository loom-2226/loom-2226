"""Read-only lookup by filename and committed SHA256 inventory."""
from pathlib import Path
import csv,json,hashlib
P=Path(__file__).resolve().parent
M=P.parent/'flight_limit_price_sweep_kt_20261023/VM_KERNEL_POSITION_MANIFEST.txt'
entries={}
for line in M.read_text().splitlines()[3:]:
 parts=line.split('\t')
 if len(parts)==3:entries[parts[0]]=(int(parts[1]),parts[2])
roots=[Path('/home/ubuntu/LOOM-output/PHASE4E_RECOVERY_20261020'),Path('/home/ubuntu/loom_solar_assets/kernels/spk')]
names=['arrokoth_2026_2251.bsp','davida_2026_2251.bsp'];rows=[]
for name in names:
 for root in roots:
  for path in root.rglob(name):
   digest=hashlib.sha256(path.read_bytes()).hexdigest();record=entries.get(str(path));rows.append({'file':name,'path':str(path),'exists':path.is_file(),'size_bytes':path.stat().st_size,'sha256':digest,'committed_manifest_match':bool(record and record[1]==digest)})
for name in names:
 registered=Path('/home/ubuntu/loom_solar_assets/kernels/spk/phase4e')/name
 rows.append({'file':name,'path':str(registered),'exists':registered.exists(),'size_bytes':None,'sha256':None,'committed_manifest_match':False})
(P/'kernel_recovery.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
