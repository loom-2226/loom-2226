#!/usr/bin/env python3
"""Build explicitly low-authority nominal parent-relative SPKs.

These products exist to provide a nominal state for visualization/game state.
They are ESTIMATED_RELATIVE, non-navigation-grade, and carry uncertainty large
enough to prevent interpretation as precision ephemerides.
"""
from pathlib import Path
import math,json,hashlib
import numpy as np
import spiceypy as sp

ROOT=Path('/home/ubuntu/loom_solar_assets')
OUT=ROOT/'kernels/spk/phase4f_estimated_relative'
LSK=ROOT/'kernels/lsk/naif0012.tls'
DE440=ROOT/'kernels/spk/de440.bsp'
NEP=ROOT/'kernels/spk/phase4e/nep098_part-3.bsp'
FRAME='ECLIPJ2000'

def write_circular(path,target,center,start,end,r0,v0,period_s,step=3600.0):
    r0=np.asarray(r0,float); v0=np.asarray(v0,float)
    e1=r0/np.linalg.norm(r0)
    h=np.cross(r0,v0); e3=h/np.linalg.norm(h); e2=np.cross(e3,e1)
    n=2*math.pi/period_s
    ts=np.arange(start,end,step)
    if not len(ts) or ts[-1]<end: ts=np.append(ts,end)
    a=np.linalg.norm(r0); q=n*(ts-start)
    states=np.empty((len(ts),6))
    states[:,:3]=a*(np.cos(q)[:,None]*e1+np.sin(q)[:,None]*e2)
    states[:,3:]=a*n*(-np.sin(q)[:,None]*e1+np.cos(q)[:,None]*e2)
    if path.exists(): path.unlink()
    hnd=sp.spkopn(str(path),'LOOM ESTIMATED RELATIVE STATE',1024)
    sp.spkw09(hnd,target,center,FRAME,float(ts[0]),float(ts[-1]),f'LOOM ESTIMATED RELATIVE {target}',7,len(ts),np.ascontiguousarray(states),np.ascontiguousarray(ts))
    sp.spkcls(hnd)
    return len(ts),a

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

OUT.mkdir(parents=True,exist_ok=True)
sp.kclear(); sp.furnsh(str(LSK)); sp.furnsh(str(DE440)); sp.furnsh(str(NEP))
rows=[]
# Proteus: anchor nominal circular continuation to the final direct NEP098 state.
seam=6311304000.0; end=float(sp.str2et('2251 JAN 02 TDB'))
s,_=sp.spkgeo(808,seam,FRAME,8)
p=OUT/'estimated_proteus_808_2199_2251.bsp'
cnt,a=write_circular(p,808,8,seam,end,s[:3],s[3:],1.122315*86400)
rows.append(dict(body_id='PROTEUS',target=808,center=8,path=str(p),samples=cnt,radius_km=a,period_days=1.122315,
 uncertainty_km=2*a,anchor='NEP098 direct endpoint',basis='JPL satellite mean period; nominal circular continuation only'))
# Dactyl: synthetic LOOM target. Historical geometry only; phase is nominal.
start=float(sp.str2et('2026 JAN 01 TDB')); end=float(sp.str2et('2251 JAN 02 TDB'))
p=OUT/'estimated_dactyl_920000243_2026_2251.bsp'
period=24.7*3600; r=[90,0,0]; v=[0,2*math.pi*90/period,0]
cnt,a=write_circular(p,920000243,20000243,start,end,r,v,period)
rows.append(dict(body_id='DACTYL',target=920000243,center=20000243,path=str(p),samples=cnt,radius_km=a,period_hours=24.7,
 uncertainty_km=2*a,anchor='nominal phase at 2026-01-01',basis='Galileo-era approximate separation/period; phase not known at game epoch'))
# Selam: synthetic LOOM target. NASA measured approximate separation/period.
p=OUT/'estimated_selam_920152830_2026_2251.bsp'
period=53*3600; r=[3.1,0,0]; v=[0,2*math.pi*3.1/period,0]
cnt,a=write_circular(p,920152830,20152830,start,end,r,v,period)
rows.append(dict(body_id='SELAM',target=920152830,center=20152830,path=str(p),samples=cnt,radius_km=a,period_hours=53,
 uncertainty_km=2*a,anchor='nominal phase at 2026-01-01',basis='NASA Lucy approximate 3.1 km separation / 53 h synchronous orbit; phase not known at game epoch'))
for r in rows:
 pp=Path(r['path']); r['sha256']=digest(pp); r['byte_count']=pp.stat().st_size
(OUT/'BUILD.json').write_text(json.dumps({'schema':'loom.estimated-relative/1.0','authority':'ESTIMATED_RELATIVE','navigation_grade':False,'rows':rows},indent=2)+'\n')
sp.kclear()
for r in rows: print(r)
