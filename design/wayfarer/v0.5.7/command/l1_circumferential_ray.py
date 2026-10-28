"""A fair ray/area screen for concealed circumferential shutters.

A ring of alternating glass and opaque sectors gives each glass sector
one neighbouring opaque sector for sideways storage. The centre stays fixed
armour; there is no fictitious central shutter. Source 6 L1 eyes, furniture,
ring sensors and pressure surface are retained.
"""
import json, math
from pathlib import Path
import numpy as np
import l1_design_search as D
import l1_refine as R
D=R.D # the independently loaded visibility module actually used by R.metric
import l1_fair_shutter_comparison as F

ROOT=Path(__file__).resolve().parent.parent
ORIG_A,ORIG_F=D.aperture,D.frame_hit

def diff(a,b):
    return np.abs((a-b+180)%360-180)

def openings(radius,phi,inner,crown,ns,phase,centre_open=False):
    widths=360/ns/2
    centers=np.arange(ns)*360/ns+phase
    dd=np.min(np.array([diff(phi,c) for c in centers]),axis=0)
    return ((radius<=inner) if centre_open else False)|((radius>=inner)&(radius<=crown)&(dd<=widths/2))

def frames(radius,phi,inner,crown,ns,phase,strip=.08):
    centers=np.arange(ns)*360/ns+phase
    dd=np.min(np.array([diff(phi,c) for c in centers]),axis=0)
    limit=360/ns/4
    boundary=np.abs(dd-limit)*np.pi/180*radius<strip/2
    radial=(np.abs(radius-inner)<strip/2)|(np.abs(radius-crown)<strip/2)
    return radial|boundary

def run_case(name,shape,crown,inner,ns,phase,centre_open=False):
    D.aperture=lambda r,a,c,p:openings(r,a,inner,crown,ns,phase,centre_open)
    D.frame_hit=lambda r,a,c,p:frames(r,a,inner,crown,ns,phase)
    try:
        stations=R.detail(shape or (0,2,50),crown,'radial',base=(shape is None))
    finally:
        D.aperture, D.frame_hit=ORIG_A, ORIG_F
    out_a,mer=F.area_meridian(inner,crown,shape)
    center_area=F.area_meridian(0,inner,shape)[0] if centre_open else 0
    glass=out_a/2+center_area
    return {
      'name':name,'shape':shape,'crown_m':crown,'inner_opaque_r_m':inner,
      'window_count':ns,'centre_open':centre_open,'window_angle_width_deg':180/ns,'phase_deg':phase,
      'outer_glazing_area_m2':round(glass,2),
      'outer_opaque_storage_area_m2':round(glass,2),
      'armour_t':round(glass*.27,2),
      'material_volume_m3':round(glass*F.T,2),
      'worst_pilot_hemisphere_fraction':min(stations[k]['forward_integrated'] for k in ('PILOT','NAV')),
      'worst_pilot_cone60_fraction':min(stations[k]['cone60_integrated'] for k in ('PILOT','NAV')),
      'worst_support_forward_fraction':min(stations[k]['forward_integrated'] for k in ('S1','S2','S3','S4')),
      'stations':stations
    }


def run_reserved_case(name,shape,crown,centre_radius,width):
    # Four symmetric nose-sector panes, next to two 50-degree arc storage pockets.
    centers=(45.,135.,225.,315.) if width>=35 else (55.,125.,235.,305.)
    dtheta=lambda phi:np.minimum.reduce([diff(phi,k) for k in centers])
    def ap(r,ph,c,w):return (r<=centre_radius)|((r<=crown)&(dtheta(ph)<=width/2))
    def fr(r,ph,c,w):
        edge=(np.abs(r-centre_radius)<.04)|(np.abs(r-crown)<.04)
        end=np.abs(dtheta(ph)-width/2)*np.pi/180*r<.04
        return edge|((r>centre_radius)&end)
    D.aperture,D.frame_hit=ap,fr
    try: stations=R.detail(shape or (0,2,50),crown,'radial',base=(shape is None))
    finally:D.aperture,D.frame_hit=ORIG_A,ORIG_F
    area0=F.area_meridian(0,centre_radius,shape)[0]
    area1=F.area_meridian(centre_radius,crown,shape)[0]*(4*width/360)
    return dict(name=name,shape=shape,crown_m=crown,centre_radius_m=centre_radius,
        window_width_deg=width,window_centres_deg=centers,
        exterior_central_area_m2=round(area0,2),exterior_outer_area_m2=round(area1,2),
        total_exterior_area_m2=round(area0+area1,2),shield_equivalent_t=round((area0+area1)*.27,2),
        pilot_cone60=min(stations[k]['cone60_integrated'] for k in ('PILOT','NAV')),
        pilot_forward=min(stations[k]['forward_integrated'] for k in ('PILOT','NAV')),
        support_forward=min(stations[k]['forward_integrated'] for k in ('S1','S2','S3','S4')),
        stations=stations)

def reserved_main():
    opts=[]
    for name,shape,crown in [('Rev7',None,2.8),('Compact',(.8,1.2,35),3.2),('Panorama',(1.2,2,50),3.5)]:
        for centre in (1.2,1.45,1.8):
            for width in (22.,40.):
                q=run_reserved_case(name,shape,crown,centre,width)
                opts.append(q)
                print(name,centre,'WIDTH',width,'CONE',q['pilot_cone60'],'pilot',q['pilot_forward'],'support',q['support_forward'],'exterior',q['total_exterior_area_m2'],flush=True)
    (ROOT/'command/l1_lateral_reserved_visibility.json').write_text(json.dumps({'status':'RESEARCH','options':opts},indent=2))

if __name__=='__main__':reserved_main()
