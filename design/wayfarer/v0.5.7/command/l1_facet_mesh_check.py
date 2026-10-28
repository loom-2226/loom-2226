"""Independent triangulated 3D exterior test for selected, unchanged-L1 noses.
Not CAD qualification. Ray/triangle intersections supersede analytic cone rays.
"""
import json,sys,importlib.util,math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('D',P/'l1_design_search.py')
D=importlib.util.module_from_spec(sp);sp.loader.exec_module(D)
sp2=importlib.util.spec_from_file_location('F',P/'l1_refine.py')
F=importlib.util.module_from_spec(sp2);sp2.loader.exec_module(F)
ORIG=D.outer_hit

def vec(x,r,a):return np.array((x,r*math.cos(a),r*math.sin(a)),float)
def build(shape,n=72):
    ext,face,angle=shape
    xf=D.facet_x(face,*shape);xo=D.facet_x(4.5,*shape)
    T=[]
    for j in range(n):
        a=2*math.pi*j/n;b=2*math.pi*(j+1)/n
        f0=vec(xf,face,a);f1=vec(xf,face,b)
        o0=vec(xo,4.5,a);o1=vec(xo,4.5,b)
        c0=vec(2.35,4.5,a);c1=vec(2.35,4.5,b)
        T.extend([(vec(-ext,0,0),f0,f1),(f0,f1,o0),(f1,o0,o1),
                  (o0,o1,c0),(o1,c0,c1)])
    return np.array(T)

def ray_triangle(eye,ds,tri):
    # Moller-Trumbore intersection, 3D facets (actual mesh triangles).
    best=np.full(len(ds),np.inf)
    for a,b,c in tri:
        u=b-a;v=c-a
        p=np.cross(ds,v);det=p@u
        safe=np.where(np.abs(det)>1e-9,det,np.nan)
        inv=1/safe
        delta=eye-a
        q=np.cross(delta,u)
        beta=(p@delta)*inv
        gamma=(ds@q)*inv
        t=float(q@v)*inv
        valid=(beta>=-1e-9)&(gamma>=-1e-9)&(beta+gamma<=1+1e-9)&(t>1e-8)
        best=np.where(valid & (t<best),t,best)
    return np.where(np.isfinite(best),best,np.nan)

def clearance(tri):
    # Check all facet triangles at barycentric 0, 1/2, and centroid.
    A=tri[:,0,:];B=tri[:,1,:];C=tri[:,2,:]
    samples=np.concatenate((A,B,C,(A+B)/2,(A+C)/2,(B+C)/2,(A+B+C)/3))
    rr=np.hypot(samples[:,1],samples[:,2])
    inside=(rr<=4.3)
    pressure_gap=D.pressure_x(rr[inside])-samples[inside,0]
    # Collar is a retrofit to round hull and is EXCLUDED from old-envelope overlay check.
    front=tri.reshape(-1,3)
    rho=np.hypot(front[:,1],front[:,2]);tip=(rho<4.5-1e-6)
    original_margin=D.out_x(rho[tip])-front[tip,0]
    return {'pressure_gap_min_m':round(float(pressure_gap.min()),4),
            'original_envelope_vertex_margin_min_m':round(float(original_margin.min()),4)}

def check(q):
    shape=q['shape'];tri=build(shape)
    before=ORIG
    D.outer_hit=lambda eye,ds,*args:ray_triangle(eye,ds,tri)
    sc=D.L.built_option()['scene']
    by={}
    for j,eye in enumerate(D.EYES):
        tmp={}
        for mode in ('integrated','dual'):
            for kind,ds in (('forward',D.RAYS),('cone60',D.CONE)) if j<2 else (('forward',D.RAYS),):
                mask=D.visibility_one(eye,shape,q['crown'],q['windows'],'ring',
                     cone=(ds is D.CONE),double_frame=(mode=='dual'),return_mask=True)
                good=0
                for idx in np.flatnonzero(mask):
                    hit,_=D.O.dome_hit(sc,tuple(eye),tuple(ds[idx]))
                    good+=(hit is not None and not D.O.blocked(sc,tuple(eye),hit,D.IDS[j]))
                tmp[kind+'_'+mode]=round(good/len(ds),4)
        by[D.IDS[j]]=tmp
    D.outer_hit=before
    return {'shape':shape,'crown':q['crown'],'windows':q['windows'],'pressure':clearance(tri),
            'stations':by,'mesh_triangles':len(tri),'area_m2':q['area_m2'],
            'analytic':q['stations']}

def main():
    inp=json.loads((P/'l1_design_refined.json').read_text())
    items=inp['candidates']
    # Useful diversity: retain strongest for each window family + 1.2m 50-degree proposed
    items=[q for q in items if q['windows'] in ('radial','targeted') and q['crown'] in (3.2,3.5)]
    items.sort(key=lambda q:(-q['min_support'],q['area_m2'],q['extension']))
    chosen=[];ids=set()
    for q in items:
        cat=(q['windows'],q['crown'])
        if cat not in ids:chosen.append(q);ids.add(cat)
    for q in items:
        if q['shape']==[1.2,2,50] and q not in chosen:chosen.append(q)
    for q in items:
        if q['shape']==[.8,1.2,35] and q not in chosen:chosen.append(q)
    out=[check(q) for q in chosen]
    output={'status':'NON-GOVERNING CONCEPT MESH, NOT CERTIFIED','source_sha':inp['source_sha'],
            'runs':out,'mesh_method':'72 azimuth sectors x flat centre, triangulated frustum and radial collar to round shell'}
    (P/'l1_facet_mesh_results.json').write_text(json.dumps(output,indent=2))
    for q in out:
        print(q['shape'],q['windows'],q['crown'],q['pressure'],
              'pilot',min(q['stations'][k]['forward_integrated'] for k in ('PILOT','NAV')),
              'support',min(q['stations'][k]['forward_integrated'] for k in ('S1','S2','S3','S4')),
              'pilot60',min(q['stations'][k]['cone60_integrated'] for k in ('PILOT','NAV')),
              'area',q['area_m2'])
if __name__=='__main__':main()
