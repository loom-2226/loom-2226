"""Narrow 16-leaf two-tier cam test, keeping all Rev7 obstacles.

Does not authorize a new ship design. Samples both armor thickness levels
and the complete 0..62deg rigid rotation under a common cam, with 25mm
pressure/shell margins and 20mm intertier spacing. 1.80m reference vs 1.75m
aperture. Geometry is necessary, NOT closure of bearings or flush face.
"""
import json,math
import numpy as np
from pathlib import Path
import l1_armoured_iris as I
import l1_iris_one_blade_slot as W

ROOT=Path(__file__).resolve().parent.parent
N=16
T=W.T
GAP=I.GAP
CAM_EPS=.001
BOSS_RADIUS=.12
THETAS=list(range(0,63))
R_VALUES=[1.80,1.76,1.75,1.74]

def sample_blade(R):
    phi=np.linspace(-math.pi/16-math.radians(I.OVER_DEG),
       math.pi/16+math.radians(I.OVER_DEG),33)
    radius=np.linspace(BOSS_RADIUS,R,56)
    return np.array([[r*math.cos(p),r*math.sin(p)] for r in radius for p in phi],float)

def bounds(xy,R):
    r=np.linalg.norm(xy,axis=1)
    outer=W.outer(r)
    pressure=W.pressure(r)
    # Source shield occupies r>=R except the round central glazing aperture.
    mask=r>R+1e-5
    low=float(np.max(outer[mask]+W.FRONT_ARMOR_X_THICKNESS+W.MIN_GAP)) if np.any(mask) else None
    high=float(np.min(pressure-(2*T+GAP)-W.MIN_GAP))
    return low,high,r,outer,pressure

def sample(R):
    P=I.sector(R)
    B=sample_blade(R)
    front=W.CLOSED_FRONT_X
    ready=W.READY_FRONT_X
    frames=[]
    # Stage 1: pull both tiers back *while* fully inside circle.
    for idx in range(31):
        u=idx/30
        x=W.CLOSED_FRONT_X+(ready-W.CLOSED_FRONT_X)*u
        xy=B
        lo,hi,r,outer,pressure=bounds(xy,R)
        yx=x+T+GAP
        shell_count=int(np.count_nonzero((r>=R+1e-5)&(x<outer+W.FRONT_ARMOR_X_THICKNESS)&(x+T>outer)))
        press_gap=float(np.min(pressure-(yx+T)))
        frames.append({'stage':'withdraw','stage_fraction':round(u*.25,4),'angle_deg':0,
          'upper_front_x_m':round(x,5),'lower_front_x_m':round(yx,5),
          'min_pressure_gap_m':round(press_gap,5),
          'min_intertier_gap_m':round(yx-(x+T),5),
          'min_fixed_armour_gap_m':None,
          'same_tier_collision':False,
          'fixed_armour_contacts':shell_count,
          'two_tier_signed_interval_m':None,
          'min_open_radius_m':BOSS_RADIUS,'max_radial_m':R,
        })
    # Stage 2: same azimuthal rotation for 16 petals, stacked at 2 x-levels.
    # Per-tier blades are separated by 45deg in azimuth; other-tier blades
    # overlap in projection but 20mm axial gap prevents slab intersection.
    cam_x=ready
    for theta in range(1,63):
        q=I.move(P,R,None,theta)
        moved=I.move(B,R,None,theta)
        lo,hi,r,outer,pressure=bounds(moved,R)
        cam_x=max(cam_x,lo+CAM_EPS) if lo is not None else cam_x
        lower=cam_x+T+GAP
        rmin,rmax=I.radial(q)
        sat_collisions=sum(int(I.collide(q,I.rotate(q,k*360/N)))
          for k in (2,4,6,8,10,12,14))
        same_shell=(r>=R+1e-5)&(cam_x<outer+W.FRONT_ARMOR_X_THICKNESS)&(cam_x+T>outer)
        # front of deeper second tier cannot ever hit fixed shoulder armor if
        # front tier is at/behind the inner shield face and is farther aft.
        rear_shell=(r>=R+1e-5)&(lower<outer+W.FRONT_ARMOR_X_THICKNESS)&(lower+T>outer)
        pressure_gap=float(np.min(pressure-(lower+T)))
        shell_sep=float(np.min(cam_x-(outer[r>=R+1e-5]+W.FRONT_ARMOR_X_THICKNESS))) if np.any(r>=R+1e-5) else None
        frames.append({'stage':'cam','stage_fraction':round(.25+.75*theta/62,4),
          'angle_deg':theta,'upper_front_x_m':round(cam_x,5),
          'lower_front_x_m':round(lower,5),
          'min_pressure_gap_m':round(pressure_gap,5),
          'min_intertier_gap_m':round(lower-(cam_x+T),5),
          'min_fixed_armour_gap_m':round(shell_sep,5) if shell_sep is not None else None,
          'same_tier_collision':sat_collisions>0,
          'fixed_armour_contacts':int(np.count_nonzero(same_shell)+np.count_nonzero(rear_shell)),
          'two_tier_signed_interval_m':round(hi-lo,5) if lo is not None else None,
          'min_open_radius_m':round(rmin,5),
          'max_radial_m':round(rmax,5),
        })
    is_pass=all(f['fixed_armour_contacts']==0 and f['min_pressure_gap_m']>=W.MIN_GAP-1e-4
      and f['min_intertier_gap_m']>=GAP-1e-4 and not f['same_tier_collision'] for f in frames)
    last=frames[-1]
    return {
      'iris_radius_m':R,
      'crown_face_radius_m':2.0,
      'hub_radius_m':BOSS_RADIUS,
      'leaf_count':N,
      'thickness_each_m':round(T,5),
      'tiers':2,
      'intertier_axial_gap_m':GAP,
      'actual_two_tier_total_depth_m':round(2*T+GAP,5),
      'cam_sequence':'withdraw closed two-tier assembly inside circular aperture, then coordinated rotation and common axial cam under existing shoulder',
      'necessary_sampled_path_clear':is_pass,
      'open_center_clear_radius_m':last['min_open_radius_m'],
      'open_max_radius_m':last['max_radial_m'],
      'end_available_x_interval_m':last['two_tier_signed_interval_m'],
      'min_pressure_gap_m':round(min(f['min_pressure_gap_m'] for f in frames),5),
      'min_fixed_armour_gap_m':round(min(f['min_fixed_armour_gap_m'] for f in frames if f['min_fixed_armour_gap_m'] is not None),5),
      'min_axial_gap_between_tiers_m':round(min(f['min_intertier_gap_m'] for f in frames),5),
      'any_same_tier_collision':any(f['same_tier_collision'] for f in frames),
      'any_fixed_armour_contact':any(f['fixed_armour_contacts']>0 for f in frames),
      'frames':frames
    }

def main():
    models=[sample(R) for R in R_VALUES]
    for m in models:
        print(m['iris_radius_m'],'CLEAR PATH',m['necessary_sampled_path_clear'],
          'end margin',m['end_available_x_interval_m'],'min pressure',m['min_pressure_gap_m'],
          'min armour gap',m['min_fixed_armour_gap_m'],
          'open clear radius',m['open_center_clear_radius_m'],
          'outer radius',m['open_max_radius_m'],flush=True)
    # Source-eye visibility with same circular iris radius and 4 side windows,
    # opaque reserved annulus to open radius+.04.
    for m in models:
        try:
            vis=I.visibility('panoramic',W.SHAPE,m['iris_radius_m'],m['open_max_radius_m']+.04)
            m['visibility']={k:v for k,v in vis.items() if k!='stations'}
        except Exception as ex:
            m['visibility_error']=repr(ex)
        print('VISIBLE',m['iris_radius_m'],m.get('visibility',m.get('visibility_error')),flush=True)
    out={'classification':'RESEARCH NON-GOVERNING · NECESSARY GEOMETRY ONLY',
      'head_PR432':'3485830a56dfead79b2ef8bba031a595b536fbb5',
      'material_source':'27 g/cm2 equivalent, effective armour density in Rev7 ledger',
      'shell_model':'hypothetical local 20cm normal solid armour on 50deg exterior; only panel prism against source pressure head + local armour; 25mm margins',
      'mechanism_scope':'all sixteen leaf material point clouds, eight of each tier, with common axial cam, rigid rotation, 20mm independent tier axial separation; identical motion rotated about x',
      'limits':['No physical bearing/armature/cam drive, pressure seal, iris flush closure, impact response, true annular throat load path or real ring supports',
        'Only same-tier SAT collision and two separated axial slabs, not precise 3D mesh continuous contact',
        'Current closed pose is NOT flush: 216mm different exposed blade faces remain',
        'Fixed 0.12m hub has unqualified circular impact lap seam',
        'Room visibility assumes opaque storage ring; the new nose has much worse panoramic viewing than original Rev7',
        'A narrow 25mm nominal gap is not necessarily sufficient for real hardware'],
      'results':models}
    (ROOT/'command/l1_iris_two_tier_cam_results.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
