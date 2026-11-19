#!/usr/bin/env python3
"""Exact 30/37-part candidate B4-S GLBs, ship-coordinate +90 stowed attitude.
Released canon GLBs and pointer never written.
"""
import sys,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"v2_lifting_body"))
import build_b4s as B
ROOT=HERE.parent.parent
OUT=ROOT/"render/out/b4s_candidates"
OUT.mkdir(parents=True,exist_ok=True)
files={}
for state,slug in (("flight","standard"),("venus","venus_kit_payload")):
 model=B.shuttle(state)
 rotated={}
 for key,(V,F) in model.items():
  W=np.column_stack((V[:,0]+18.75,-V[:,2],V[:,1]))
  rotated[key]=(W,F)
 dest=OUT/f"wayfarer_b4s_rolled90_{slug}.glb"
 B.B.write_glb(rotated,str(dest))
 files[state]=dict(path=str(dest.relative_to(ROOT)),part_count=len(rotated),size_bytes=dest.stat().st_size)
print("B4S_CANDIDATES",json.dumps(files),flush=True)
