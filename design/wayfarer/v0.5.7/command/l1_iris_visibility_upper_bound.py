"""Corrected iris aperture upper-bound check with absolutely-valued sector offsets."""
import json,numpy as np
from pathlib import Path
import l1_armoured_iris as I
ROOT=Path(__file__).resolve().parent.parent
R=1.76
STOW_R=2.66176+.04
CROWN=3.5
D=I.D;REF=I.REF
def case(name,complete_ring):
    old_a,old_f=D.aperture,D.frame_hit
    def aperture(r,phi,c,pat):
        sector_angle=np.minimum.reduce([np.abs(D.angdiff(phi,u)) for u in (45,135,225,315)])
        exposed=((r>=STOW_R)&(r<=CROWN))
        if not complete_ring:exposed=exposed&(sector_angle<=20)
        return ((r>=.12)&(r<=R))|exposed
    def frame(r,phi,c,pat):
        sector_angle=np.minimum.reduce([np.abs(D.angdiff(phi,u)) for u in (45,135,225,315)])
        ring=(abs(r-R)<.04)|(abs(r-STOW_R)<.04)|(abs(r-CROWN)<.04)
        boundaries=(abs(sector_angle-20)*np.pi/180*r<.04) if not complete_ring else False
        return ring | ((r>=STOW_R)&boundaries)
    D.aperture,D.frame_hit=aperture,frame
    try:st=REF.detail((1.2,2.,50.),CROWN,'radial')
    finally:D.aperture,D.frame_hit=old_a,old_f
    return dict(name=name,worst_pilot_cone60=min(st[k]['cone60_integrated'] for k in ('PILOT','NAV')),
      worst_pilot_forward=min(st[k]['forward_integrated'] for k in ('PILOT','NAV')),
      worst_support_forward=min(st[k]['forward_integrated'] for k in ('S1','S2','S3','S4')))
if __name__=='__main__':
    cases=[case('four 40-degree externally shuttered sectors',False),
           case('entire exterior annulus fully transparent, not shutter-qualified',True)]
    out={'classification':'RESEARCH: CORRECTED ANGULAR WINDOW MASK',
     'note':'Prior code used min(signed angle offsets) rather than min(abs(angle offsets)), allowing out-of-sector rays. Corrected in l1_armoured_iris.py.',
     'source':'PR432, angular 50-degree 1.76m iris, unchanged source room, rings, sensors',
     'stow_outer_radius_m':round(STOW_R,5),
     'fixed_armoured_hub_radius_m':.12,
     'corrected_cases':cases,
     'rev7_reference_pilot_forward':.6914,
     'importance':'Full ring is optical upper bound ONLY and no external shutter packaging is shown'}
    (ROOT/'command/l1_iris_visibility_upper_bound.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
