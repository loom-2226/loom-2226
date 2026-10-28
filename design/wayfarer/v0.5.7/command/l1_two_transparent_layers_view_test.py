"""Two transparent boundaries: seat-by-seat joint visibility and physical space.

NON-CANON, research only. Uses Rev7 source L1 head/seat/sensor geometry,
original elliptical pressure shape, and hypothetical +1.2m 50deg exterior.
Transparent materials are *not* impact/optically/structurally qualified.
"""
from pathlib import Path
import math,json
import numpy as np
import l1_refine as REF

ROOT=Path(__file__).resolve().parent.parent
D=REF.D
SHAPE=(1.2,2.0,50)
CROWNS=(2.8,3.2,3.5)
AREAL_OUTER=270.0
RHO_OUTER=3670.0  # illustrative ALON
AREAL_INNER=2130.0/25.0  # source aggregate ~2.13t pressure panes per ~25m2
RHO_INNER=2210.0  # illustrative fused silica
T_OUTER=AREAL_OUTER/RHO_OUTER
T_INNER=AREAL_INNER/RHO_INNER
RAYS=D.RAYS
CONE=D.CONE

def norm_rows(V):
    return V/(np.linalg.norm(V,axis=1)[:,None]+1e-30)

def incidence(ds,pts,kind):
    r=np.linalg.norm(pts[:,1:],axis=1)
    n=np.zeros_like(pts)
    if kind=='inner':
        n[:,0]=(pts[:,0]-D.XB)/(D.HD**2)
        n[:,1:]=pts[:,1:]/D.RP**2
    else:
        slope=math.tan(math.radians(SHAPE[2]))
        n[:,0]=1
        fac=np.where(r>SHAPE[1],-slope/(r+1e-30),0.)
        n[:,1:]=pts[:,1:]*fac[:,None]
    n=norm_rows(n)
    dot=np.clip(np.abs(np.sum(ds*n,axis=1)),0,1)
    return np.degrees(np.arccos(dot))

def classify_one(eye,station,ds,crown):
    ti=D.ellipse_hit(eye,ds,D.RUSABLE)
    tp=D.ellipse_hit(eye,ds,D.RP)
    to=D.outer_hit(eye,ds,*SHAPE)
    pi=eye+ds*np.nan_to_num(tp,nan=0)[:,None]
    po=eye+ds*np.nan_to_num(to,nan=0)[:,None]
    ri,ai=D.polar(pi)
    ro,ao=D.polar(po)
    okay=np.isfinite(ti)&np.isfinite(tp)&np.isfinite(to)&(tp>=ti-1e-5)&(to>=tp+1e-5)
    stage=np.full(len(ds),'geometry',dtype=object)
    pa=ri<=crown
    oa=ro<=crown
    stage[okay & ~pa]='inner_opaque'
    stage[okay & pa & ~oa]='outer_opaque'
    valid=okay&pa&oa
    frames=D.frame_hit(ri,ai,crown,'radial')
    stage[valid & frames]='pressure_frame'
    valid&=~frames
    sensor=D.ray_sensor_mask(eye,ds,ti)
    stage[valid & sensor]='sensor'
    valid&=~sensor
    # same interior furniture collision method REF.metric
    for idx in np.flatnonzero(valid):
        hit,kind=D.O.dome_hit(REF.SC,tuple(eye),tuple(ds[idx]))
        if not hit or D.O.blocked(REF.SC,tuple(eye),hit,station):
            stage[idx]='interior'
        else:
            stage[idx]='visible'
    innerang=incidence(ds,pi,'inner')
    outerang=incidence(ds,po,'outer')
    screen=[]
    for i in range(len(ds)):
        u=-float(ds[i,0])
        phi=math.atan2(float(ds[i,2]),float(ds[i,1]))
        radius=math.acos(np.clip(u,0,1))/(math.pi/2)
        screen.append({'u':round(radius*math.cos(phi),5),'v':round(radius*math.sin(phi),5),
            'stage':str(stage[i]),
            'inner_radius_m':round(float(ri[i]),4),
            'outer_radius_m':round(float(ro[i]),4),
            'inner_inc_deg':round(float(innerang[i]),2),
            'outer_inc_deg':round(float(outerang[i]),2),
            'pressure_hit_xyz':[round(float(v),4) for v in pi[i]],
            'outer_hit_xyz':[round(float(v),4) for v in po[i]]})
    valid=stage=='visible'
    vals={'fraction_visible':round(float(np.mean(valid)),6),
          'visible_ray_count':int(valid.sum()),
          'count':len(stage),
          'blocked_breakdown':{s:int((stage==s).sum()) for s in
             ('geometry','inner_opaque','outer_opaque','pressure_frame','sensor','interior')},
          'visible_inner_incidence_median_deg':round(float(np.median(innerang[valid])),2) if valid.any() else None,
          'visible_inner_incidence_max_deg':round(float(np.max(innerang[valid])),2) if valid.any() else None,
          'visible_outer_incidence_median_deg':round(float(np.median(outerang[valid])),2) if valid.any() else None,
          'visible_outer_incidence_max_deg':round(float(np.max(outerang[valid])),2) if valid.any() else None,
          'visible_either_surface_over_60deg_count':int((valid&((innerang>=60)|(outerang>=60))).sum()),
          'visible_either_surface_over_75deg_count':int((valid&((innerang>=75)|(outerang>=75))).sum()),
          'rays':screen}
    return vals

def fit(crown):
    r=np.linspace(0,crown,4001)
    x_outer=np.asarray(D.facet_x(r,*SHAPE))
    x_inner=np.asarray(D.pressure_x(r))
    slope_i=D.HD*r/(D.RP*D.RP*np.sqrt(np.maximum(1e-10,1-(r/D.RP)**2)))
    thickness_outer_x=np.where(r<=SHAPE[1],T_OUTER,T_OUTER/math.cos(math.radians(SHAPE[2])))
    # This OVERCOUNTS a bit at the angled flat/facet join, deliberately narrow conservative 1D check.
    thickness_inner_x=T_INNER*np.sqrt(1+slope_i**2)
    clear=x_inner-x_outer-thickness_outer_x-thickness_inner_x
    idx=int(np.argmin(clear))
    return {'outer_ALON_normal_equiv_cm':round(T_OUTER*100,4),
        'inner_silica_normal_equiv_cm':round(T_INNER*100,4),
        'min_clearance_between_solid_materials_m':round(float(np.min(clear)),5),
        'critical_r_m':round(float(r[idx]),4),
        'clear_with_10cm_empty_reserve':bool(np.all(clear>=.10)),
        'assumption':'Inner pressure panes placed forward of original mathematical pressure surface; same source aggregate per-area mass. Hypothetical layering and zero actual frame allowance.'}

def main():
    allrows=[]
    for crown in CROWNS:
        eyes={}
        for j,eye in enumerate(D.EYES):
            fw=classify_one(eye,D.IDS[j],RAYS,crown)
            if j<2:
                fw['forward_cone60']=classify_one(eye,D.IDS[j],CONE,crown)['fraction_visible']
            eyes[D.IDS[j]]=fw
            print('CROWN',crown,D.IDS[j],'vis',fw['fraction_visible'],
                  'counts',fw['blocked_breakdown'],
                  'medianinc',fw['visible_inner_incidence_median_deg'],fw['visible_outer_incidence_median_deg'],
                  'highinc',fw['visible_either_surface_over_60deg_count'],flush=True)
        gap=fit(crown)
        print('FIT',crown,gap,flush=True)
        allrows.append({'crown_radius_m':crown,'fit':gap,'stations':eyes})
    out={'classification':'RESEARCH NON-CANON NON-RUNTIME NON-QUALIFICATION',
      'source_PR432_sha':'3485830a56dfead79b2ef8bba031a595b536fbb5',
      'geometry':'Rev7 crew/pressure shape and sensor ring, angular +1.2m flat-r2m 50deg outer shell',
      'outer_protection_kg_m2':AREAL_OUTER,
      'inner_press_panes_combined_kg_m2':AREAL_INNER,
      'hypothetical_materials':'ALON-density outer solid, fused-silica-density inner pane, each scaled to reference areal allocation',
      'sample_count_forward':len(RAYS),'sample_count_cone':len(CONE),
      'note':'Visibility counts are straight-ray intersections with transparent ext+pressure surfaces; no refraction/scatter or real window mounting. Causal optics/ballistics NOT measured.',
      'results':allrows}
    (ROOT/'command/l1_two_transparent_layers_results.json').write_text(json.dumps(out,separators=(',',':')))
    return out
if __name__=='__main__':main()
