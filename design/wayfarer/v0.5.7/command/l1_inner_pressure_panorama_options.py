"""L1 inner pressure-window only view optimization; held 37 outer panels fixed.

NON-CANON geometry sensitivity: no verified structural or optical performance.
Source eyes, furniture, sensor ring, pressure ellipsoid, outer angular nose unchanged.
Outer 37-pane topology and 10mm fully opaque projected seams are immutable.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_replaceable_outer_tiles as T

ROOT=Path(__file__).resolve().parent.parent
D=T.D
SHAPE=T.SHAPE
OUTER_CROWN=3.5
HELD=T.PRESETS['staggered_trapezoids_compact_12']
N_MAIN=4096
N_SUPPORT=1536

# Inner glazing aperture (pressure surface) radius changes from 3.5 to 3.65
# without moving pressure geometry. Frame mount still conceptual.
INNER_RADII=[3.5,3.65,3.8]
# 8x80: source's research frame assumption (ring at 1.15)
# ring0.75 matches 37-panel central outer disc radius, not its physical mount.
FRAME_OPTIONS={
 'current_8x80':dict(spokes=8,width=.08,ring=1.15,rotation_deg=0),
 'slim_8x40':dict(spokes=8,width=.04,ring=1.15,rotation_deg=0),
 'slim_8x40_hub075':dict(spokes=8,width=.04,ring=.75,rotation_deg=0),
 'slim_8x40_ring150':dict(spokes=8,width=.04,ring=1.50,rotation_deg=0),
 'slim_8x40_ring200':dict(spokes=8,width=.04,ring=2.00,rotation_deg=0),
 'slim_8x40_ring300_bound':dict(spokes=8,width=.04,ring=3.00,rotation_deg=0),
 'current_width_8x80_ring200':dict(spokes=8,width=.08,ring=2.00,rotation_deg=0),
 'slim_12x40_hub075':dict(spokes=12,width=.04,ring=.75,rotation_deg=0),
 'slim_12x40_hub075_rot15':dict(spokes=12,width=.04,ring=.75,rotation_deg=15),
 'wide_12x80_hub075':dict(spokes=12,width=.08,ring=.75,rotation_deg=0),
 'sparse_4x80':dict(spokes=4,width=.08,ring=1.15,rotation_deg=0),
 'rim_only_upper_bound':dict(spokes=0,width=.02,ring=None,rotation_deg=0),
}
def angle_diff(a,b):
    return (a-b+180)%360-180
def inner_frame(r,phi,inner_r,option):
    # Preserve rim frame of same width as internal spokes/ring.
    width=option['width'];out=np.abs(r-inner_r)<width/2
    if option['ring'] is not None:
        out|=np.abs(r-option['ring'])<width/2
    n=option['spokes']
    if n>0:
        step=360/n
        ap=np.mod(phi-option['rotation_deg'],step)
        da=np.minimum(ap,step-ap)*np.pi/180*r
        out|=(r> (option['ring'] if option['ring'] is not None else 0))&(da<width/2)
    return out

def from_seat(idx):
    e=D.EYES[idx];station=D.IDS[idx]
    ds=D.directions(N_MAIN if idx<2 else N_SUPPORT)
    ti=D.ellipse_hit(e,ds,D.RUSABLE)
    tp=D.ellipse_hit(e,ds,D.RP)
    to=D.outer_hit(e,ds,*SHAPE)
    ip=e+ds*np.nan_to_num(tp,nan=0)[:,None]
    op=e+ds*np.nan_to_num(to,nan=0)[:,None]
    ri,ai=D.polar(ip);ro,ao=D.polar(op)
    geometric=np.isfinite(ti)&np.isfinite(tp)&np.isfinite(to)&(tp>=ti-1e-5)&(to>=tp+1e-5)
    outer_usable=geometric&(ro<=OUTER_CROWN)
    outer_id,outer_gap=T.polar_id_gaps(ro,np.radians(ao),HELD)
    outer_37_seam=outer_gap<.010/2 # 10mm total illustrative width
    sensor=D.ray_sensor_mask(e,ds,ti)
    # Cache geometry occupancy independently of frame assumptions. Only check
    # paths capable of seeing through the exterior, saves loops for comparisons.
    interior=np.ones(len(ds),dtype=bool)
    for i in np.flatnonzero(outer_usable & ~sensor & ~outer_37_seam):
        hit,_=D.O.dome_hit(T.REF.SC,tuple(e),tuple(ds[i]))
        interior[i]=not (hit and not D.O.blocked(T.REF.SC,tuple(e),hit,station))
    base=outer_usable&~outer_37_seam&~sensor&~interior
    return {'r_inner':ri,'ang_inner':ai,'r_outer':ro,'geometric':geometric,
        'outer_usable':outer_usable,'outer_37_seam':outer_37_seam,'sensor':sensor,
        'interior':interior,'base_clear':base,'n':len(ds),
        'potential_base':int(base.sum())}

def run():
    caches={s:from_seat(i) for i,s in enumerate(D.IDS)}
    result={}
    for inner_r in INNER_RADII:
        for name,opt in FRAME_OPTIONS.items():
            key=f'{name}__innerR{inner_r:g}'
            stations={}
            for station,c in caches.items():
                pa=c['r_inner']<=inner_r
                frame=inner_frame(c['r_inner'],c['ang_inner'],inner_r,opt)
                visible=c['base_clear']&pa&~frame
                # waterfall counts: geometric -> outer -> inner -> seam -> sensor
                # -> interior -> interior frame -> visible (ordered, disjoint)
                rem=c['geometric'].copy()
                outside_geom=int((~rem).sum())
                exterior_block=rem & ~c['outer_usable']
                rem &= c['outer_usable']
                inner_block=rem & ~pa
                rem &= pa
                seam_block=rem & c['outer_37_seam']
                rem &=~c['outer_37_seam']
                sensor_block=rem & c['sensor']
                rem &=~c['sensor']
                furniture_block=rem & c['interior']
                rem &=~c['interior']
                frame_block=rem & frame
                rem &=~frame
                assert np.array_equal(visible,rem)
                counts={'geometry':outside_geom,'exterior_opaque':int(exterior_block.sum()),
                    'inner_pressure_opaque':int(inner_block.sum()),
                    'held_37_outer_seams':int(seam_block.sum()),
                    'sensor':int(sensor_block.sum()),'interior':int(furniture_block.sum()),
                    'inner_frame':int(frame_block.sum()),
                    'visible':int(visible.sum())}
                assert sum(counts.values())==c['n']
                stations[station]={'fraction':round(float(visible.mean()),6),'visible':int(visible.sum()),
                    'sample_count':c['n'],'blockage_breakdown':counts}
            result[key]={'inner_radius_m':inner_r,'frame':name,'configuration':opt,
                'stations':stations,'pilot_NAV_min':min(stations[x]['fraction'] for x in ('PILOT','NAV')),
                'support_min':min(stations[x]['fraction'] for x in ('S1','S2','S3','S4'))}
    base=result['current_8x80__innerR3.5']
    print('BASE inner 3.5, 8x80 and held outer 37',base['pilot_NAV_min'],base['support_min'],
          'blocked Pilot',base['stations']['PILOT']['blockage_breakdown'],flush=True)
    for key,z in result.items():
        print(key,'pilot',z['stations']['PILOT']['fraction'],'nav',z['stations']['NAV']['fraction'],
              'support',z['support_min'],
              'Pilot_frame_blocked',z['stations']['PILOT']['blockage_breakdown']['inner_frame'],flush=True)
    out={'classification':'NON-CANON NON-RUNTIME OPTICAL GEOMETRY SENSITIVITY ONLY',
         'PR432_source_sha':'3485830a56dfead79b2ef8bba031a595b536fbb5',
         'held_37_layout_key':'staggered_trapezoids_compact_12',
         'held_37_layout':HELD,
         'held_outer_crown_radius_m':OUTER_CROWN,
         'held_outer_seam_total_width_m':.010,
         'inner_window_modes':FRAME_OPTIONS,
         'inner_radii_tested_m':INNER_RADII,
         'baseline':'current_8x80__innerR3.5',
         'results':result,
         'limits':[
          'Only ray geometry; no optical refraction, reflection, stress/fracture or pressure qualification',
          'Outer 37 tile geometry and 10mm opaque seam, actual seat eyes and source sensor/furniture unchanged',
          'Inner opaque-to-transparent substitutions at r3.65 and r3.8 are structural pressure hull changes even though ellipsoid surface stays fixed',
          'Slimmer or fewer inner support members are view upper bounds, not structurally earned',
          'Inner pressure framing must be independently load bearing; do not pretend outer protective tile joints support cabin pressure',
          'Source classifies frames at pressure opening; supporting frames and mounts are only assumed line bands, not actual geometry',
          'At this sample density, absolute percentages differ from previous coarse 256-ray evaluations',
          'No changes to governing source or crew interior'
         ]}
    (ROOT/'command/l1_inner_pressure_panorama_results.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':run()
