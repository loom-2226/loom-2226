#!/usr/bin/env python3
"""Conservative closed installed-solid envelope of the authored B4-S flight mesh.
The separate B4-S GLB retains all 30 actual visible meshes; this convex
envelope intentionally cannot understate an external collision. No kit in dry.
"""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from build_b4s import shuttle
ROOT=Path(__file__).resolve().parent
P=shuttle("flight")
full=np.concatenate([p[0] for p in P.values()],axis=0)
# kT: +90deg around x; +Y/starboard becomes +Z/exit.
full=np.column_stack((full[:,0]+18.75,-full[:,2],full[:,1]))
h=ConvexHull(full)
uniq=sorted(set(int(i) for face in h.simplices for i in face))
ref={u:i for i,u in enumerate(uniq)}
V=full[uniq].tolist()
center=full.mean(axis=0)
faces=[]
for face in h.simplices:
  i,j,k=map(int,face)
  a,b,c=full[[i,j,k]]
  if np.dot(np.cross(b-a,c-a),(a+b+c)/3-center)<0:j,k=k,j
  faces.append([ref[i],ref[j],ref[k]])
rmax=float(np.hypot(full[:,1],full[:,2]).max())
ymax=float(np.abs(full[:,1]).max())
assert rmax<2.15 and ymax<1.9
src=ROOT/"viewer/glb/b4s_flight.glb"
D=dict(status="ENGINEERING CANDIDATE; conservative convex exterior collision solid",
       authority="kT B4-S 2026-11-19; rolled +90deg starboard -> +Z",
       source="wayfarer/lab/shuttle/v2_lifting_body/build_b4s.py:shuttle('flight')",
       exact_visual_glb=str(src.relative_to(ROOT)),
       exact_visual_glb_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
       flight_mesh_parts=len(P),roll_deg=90,origin_x_m=18.75,
       stowed_radius_m=rmax,stowed_halfwidth_y_m=ymax,
       bounds_x_m=[float(full[:,0].min()),float(full[:,0].max())],
       enclosed_convex_volume_m3=float(h.volume),vertices_m=V,triangles=faces)
(ROOT/"b4s_source_hull.json").write_text(json.dumps(D,indent=1)+"\n")
print("B4S_SOURCE_HULL",len(V),len(faces),"r",rmax,"y",ymax,"volume",h.volume,flush=True)
