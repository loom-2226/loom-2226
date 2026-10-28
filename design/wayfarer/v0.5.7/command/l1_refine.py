"""Consistent baseline and 24 diverse, unchanged-L1 nose candidates.
Non-governing experiment. Existing crown counted for ALL six stations.
"""
import json,importlib.util,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('D',P/'l1_design_search.py')
D=importlib.util.module_from_spec(sp);sp.loader.exec_module(D)
ORIG=D.outer_hit

def original_outer(eye,ds,*args):
    # Rev 7 actual 2.35-m ellipsoidal outer shell, R=4.50 m.
    X=2.35;H=2.35;R=4.5;ex,ey,ez=eye
    A=(ds[:,0]/H)**2+(ds[:,1]**2+ds[:,2]**2)/R**2
    B=2*((ex-X)*ds[:,0]/H**2+(ey*ds[:,1]+ez*ds[:,2])/R**2)
    C=((ex-X)/H)**2+(ey**2+ez**2)/R**2-1
    disc=B*B-4*A*C
    root=np.sqrt(np.maximum(0,disc))
    t1=(-B-root)/(2*A);t2=(-B+root)/(2*A)
    q1=(t1>0)&(ex+t1*ds[:,0]<=X)&(disc>=0)
    q2=(t2>0)&(ex+t2*ds[:,0]<=X)&(disc>=0)
    return np.where(q1,t1,np.where(q2,t2,np.nan))

SC=D.L.built_option()['scene']
def metric(eye,j,shape,crown,pattern,ds,mode,base=False):
    D.outer_hit=original_outer if base else ORIG
    geom=D.visibility_one(eye,shape,crown,pattern,'ring',
                          cone=(ds is D.CONE),double_frame=(mode=='dual'),return_mask=True)
    count=0
    for idx in np.flatnonzero(geom):
        hit,kind=D.O.dome_hit(SC,tuple(eye),tuple(ds[idx]))
        if hit and not D.O.blocked(SC,tuple(eye),hit,D.IDS[j]):count+=1
    D.outer_hit=ORIG
    return round(count/len(ds),4)

def detail(shape,crown,pattern,base=False):
    m={}
    for j,eye in enumerate(D.EYES):
        v={}
        for mode in ('integrated','dual'):
            v['forward_'+mode]=metric(eye,j,shape,crown,pattern,D.RAYS,mode,base)
            if j<2:
                v['cone60_'+mode]=metric(eye,j,shape,crown,pattern,D.CONE,mode,base)
        m[D.IDS[j]]=v
    return m

def coarse():
    allc=[]
    for s in D.profile_screen():
        for crown in D.CROWNS:
            for w in D.WINDOWS:
                shape=s[:3]
                fw=[D.visibility_one(e,shape,crown,w,'ring') for e in D.EYES]
                cone=min(D.visibility_one(e,shape,crown,w,'ring',cone=True) for e in D.EYES[:2])
                if cone<.9:continue
                allc.append({'shape':list(shape),'crown':crown,'windows':w,'sensors':'ring',
                             'shift':[0,0,0],
                             'coarse':fw,'cone':cone,'area_m2':D.area_m2(crown,w),
                             'extension':s[0]})
    return allc

def pick(allc):
    # Distinct crown/window combinations, and varied extension/facet cases,
    # rather than only glazing-heavy 3.5-m winners.
    out=[];keys=set()
    def push(q):
        key=(tuple(q['shape']),q['crown'],q['windows'])
        if key not in keys:
            out.append(q);keys.add(key)
    for w in D.WINDOWS:
        for c in D.CROWNS:
            candidates=[z for z in allc if z['windows']==w and z['crown']==c]
            if candidates:
                push(max(candidates,key=lambda z:(min(z['coarse'][2:]),min(z['coarse'][:2]),-z['extension'])))
    # Include attractive 50-degree facet and compact 1.2-m extension,
    # and the minimal extension for each crown.
    for w in D.WINDOWS:
        for c in (3.2,3.5):
            subset=[z for z in allc if z['windows']==w and z['crown']==c and
                    z['shape'][0] in (.4,.8,1.2,1.6) and z['shape'][2]>=42.5]
            if subset: push(max(subset,key=lambda z:(min(z['coarse'][2:]),-z['extension'])))
    # Guarantee our central working candidate.
    for w,c,sh in [('radial',3.5,[1.2,2,50]),('targeted',3.5,[1.2,2,50]),
                   ('radial',3.2,[1.2,2,50]),('targeted',3.2,[1.2,2,50])]:
        z=next((q for q in allc if q['shape']==sh and q['crown']==c and q['windows']==w),None)
        if z:push(z)
    return out

def main():
    allc=coarse()
    chosen=pick(allc)
    reference=detail((0,2,50),2.8,'current',base=True)
    detailed=[]
    for i,q in enumerate(chosen):
        z={**q,'stations':detail(tuple(q['shape']),q['crown'],q['windows']),
           'pressure_surface_glazing_m2':q['area_m2'],
           'shutter_equiv_t':round(.27*q['area_m2'],2),
           'shutter_material_m3':round(.27*q['area_m2']/1.375,2),
           'access':'Rev 7 unchanged PASS',
           'pressure_window_structural_fit':'NOT TESTED',
           'sensor_packaging':'Rev 7 ring physically retained',
           'shutter_swept_volume':'NOT DEMONSTRATED'}
        z['min_support']=min(z['stations'][k]['forward_integrated'] for k in D.IDS[2:])
        z['pilot_forward']=min(z['stations'][k]['forward_integrated'] for k in D.IDS[:2])
        z['pilot_60']=min(z['stations'][k]['cone60_integrated'] for k in D.IDS[:2])
        z['min_support_dual']=min(z['stations'][k]['forward_dual'] for k in D.IDS[2:])
        z['pilot_60_dual']=min(z['stations'][k]['cone60_dual'] for k in D.IDS[:2])
        detailed.append(z)
        print(i+1,'/',len(chosen),q['shape'],q['windows'],q['crown'],'support',z['min_support'],'pilot hem',z['pilot_forward'],'cone',z['pilot_60'],'area',z['area_m2'],flush=True)
    obj={'status':'RESEARCH, NON-CANON, NOT QUALIFIED',
         'baseline_note':'Rev 7 l1_study supports counted SHOULDER windows only; corrected reference counts crown pressure and exterior glazing for all stations with same assumptions as candidate',
         'source_sha':D.GEO.get('version','') and '3485830a56dfead79b2ef8bba031a595b536fbb5',
         'original_baseline':D.L.run() if False else json.loads((D.ROOT/'command/l1_study_results.json').read_text())['stations'],
         'consistent_baseline':reference,'coarse_count':len(allc),
         'detailed_count':len(detailed),'candidates':detailed,
         'qualifications':['The pressure head remains in its original geometry, but the new apertures are NOT qualified for pressure loading.',
           'The original ring sensor geometry is retained, but multi-layer transparent openings at changed positions still need spatial equipment check.',
           'Shutter material mass is a minimum areal allocation, not actual actuator/stowage mass. No validated stow volume.',
           'Results are per-ray sampled, not a probabilistic impact assessment.',
           'The analytic cone surface is not yet an intersection-certified 3D facet mesh.']}
    (P/'l1_design_refined.json').write_text(json.dumps(obj,indent=2))
    print('BASELINE consistent',reference)
    print('TOP',[(q['shape'],q['windows'],q['crown'],q['min_support'],q['pilot_forward'],q['pilot_60'],q['area_m2']) for q in sorted(detailed,key=lambda q:(-q['min_support'],q['area_m2']))[:12]])
if __name__=='__main__':main()
