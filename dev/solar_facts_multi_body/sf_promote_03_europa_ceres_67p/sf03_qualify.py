"""SF-PROMOTE-02's frozen canonical digest functions, reused unchanged."""
import sys,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'dev/solar_facts_multi_body/sf_promote_02_ceres_67p'
sys.path.insert(0,str(P));old=sys.modules.pop('promote',None)
try:
 spec=importlib.util.spec_from_file_location('_sf_promote_02_digest',P/'qualify.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
finally:
 if old is not None:sys.modules['promote']=old
body_digest=m.body_digest
whole_digest=m.whole_digest
