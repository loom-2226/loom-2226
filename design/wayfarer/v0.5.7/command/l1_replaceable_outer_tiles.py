"""Non-canon Wayfarer r3.5 exterior replaceable transparent tile experiment.

Compare radial trapezoids, staggered trapezoids, and hexagons using the same
source pressure hull, angular hypothetical outer surface, six crew eye poses.
Measure actual exterior surface mass, count, seam area, and visibility losses
under an explicitly illustrative *opaque* seam band. No load testing.
"""
from pathlib import Path
import json,math
import numpy as np
import l1_refine as REF

ROOT=Path(__file__).resolve().parent.parent
D=REF.D
SHAPE=(1.2,2.,50.)
CROWN=3.5
RHO_ARMOR_PER_AREA=270. # kg/m2
RINGS=[.90,2.,2.75,3.5]
PRESETS={
 'radial_trapezoids_12':{'type':'radial','rings':[0.,.90,2.,3.5],'ns':[1,12,12],'offsets':[0,0,0]},
 'staggered_trapezoids_12':{'type':'radial','rings':[0.,.90,2.,2.75,3.5],'ns':[1,12,12,12],'offsets':[0,0,0,math.pi/12]},
 'staggered_trapezoids_compact_12':{'type':'radial','rings':[0.,.75,2.,2.75,3.5],'ns':[1,12,12,12],'offsets':[0,0,0,math.pi/12]},
 'large_hex_1p6':{'type':'hex','spacing':1.6},
 'medium_hex_1p2':{'type':'hex','spacing':1.2},
 'large_hex_shifted_1p6':{'type':'hex','spacing':1.6,'origin_xy_m':[0.,.5333]},
 'medium_hex_shifted_1p2':{'type':'hex','spacing':1.2,'origin_xy_m':[0.,.8]},
}
SEAMS_MM=[5,10,20]
N_R=700
N_TH=720
N_PILOT_RAYS=4096
N_SUPPORT_RAYS=1536

def rhoplus(r):
    return np.where(np.asarray(r)<=2,1.,1/math.cos(math.radians(50)))

def polar_id_gaps(r,phi,preset):
    """IDs and minimum XY distance to seams in metres on projected aperture.

    For hexagons, polygons are projected Voronoi cells of a triangular
    lattice. A curved/bent cut follows the 50deg facet in physical 3D.
    For radial variants, circles at ring boundaries and sector edges
    define nominal independently removable pieces.
    """
    r=np.asarray(r);phi=np.asarray(phi)
    if preset['type']=='radial':
        rings=preset['rings'];ns=preset['ns'];offs=preset['offsets']
        group=np.clip(np.searchsorted(rings[1:],r,side='right'),0,len(ns)-1)
        ids=np.zeros(r.shape,dtype=np.int64)
        seam=np.full(r.shape,999.,dtype=float)
        for g,n in enumerate(ns):
            mask=group==g
            if not np.any(mask):continue
            q=(phi[mask]-offs[g])%(2*np.pi)
            sector=np.floor(q/(2*np.pi/n)).astype(int)
            ids[mask]=g*1000+sector
            if n>1:
                angle_dist=np.abs((q+np.pi/n)%(2*np.pi/n)-np.pi/n)
                seam[mask]=np.minimum(seam[mask],r[mask]*angle_dist)
        for b in rings[1:-1]:
            seam=np.minimum(seam,np.abs(r-b))
        return ids,seam
    # Nearest Voronoi lattice point: a hex tile around each triangular
    # lattice site; only six neighbour bisectors need be screened.
    a=preset['spacing'];shift=preset.get('origin_xy_m',[0.,0.]);x=r*np.cos(phi)-shift[0];y=r*np.sin(phi)-shift[1]
    jf=2*y/(math.sqrt(3)*a);ifloat=x/a-jf/2
    # Cube-rounded axial coords (i,j) avoiding full nearest-center search.
    cf=-ifloat-jf
    qi=np.rint(ifloat);rj=np.rint(jf);sc=np.rint(cf)
    di=np.abs(qi-ifloat);dj=np.abs(rj-jf);ds=np.abs(sc-cf)
    mi=(di>dj)&(di>ds);mj=~mi&(dj>ds)
    qi=np.where(mi,-rj-sc,qi);rj=np.where(mj,-qi-sc,rj)
    sc=np.where(~mi&~mj,-qi-rj,sc)
    i=qi.astype(np.int64);j=rj.astype(np.int64)
    cx=a*(i+j/2);cy=a*math.sqrt(3)/2*j
    dist=np.full(r.shape,np.inf)
    for u,v in [(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]:
        nx=cx+a*(u+v/2);ny=cy+a*math.sqrt(3)/2*v
        edge=((x-nx)**2+(y-ny)**2-(x-cx)**2-(y-cy)**2)/(2*a)
        dist=np.minimum(dist,np.abs(edge))
    ids=(i+128)*1024+(j+128)
    return ids,dist

def area_mesh(preset):
    rs=(np.arange(N_R)+.5)*(CROWN/N_R)
    ph=(np.arange(N_TH)+.5)*2*math.pi/N_TH
    rr,pp=np.meshgrid(rs,ph,indexing='ij')
    w=rr*(CROWN/N_R)*(2*math.pi/N_TH)*rhoplus(rr)
    ids,dist=polar_id_gaps(rr.flatten(),pp.flatten(),preset)
    flatw=w.flatten()
    groups,rev=np.unique(ids,return_inverse=True)
    area=np.bincount(rev,weights=flatw)
    # Projected seam approximates a strip width on XY, with exterior surface
    # area weighted by cone stretch. 5/10/20mm = TOTAL strip width.
    blocked={}
    for width in SEAMS_MM:
        b=dist<(width/2000)
        blocked[str(width)]={'seam_band_area_m2':round(float(np.sum(flatw[b])),4),
                             'surface_fraction':round(float(np.sum(flatw[b])/np.sum(flatw)),6)}
    return {'panel_count':len(groups),
            'total_surface_area_m2':round(float(area.sum()),3),
            'smallest_panel_area_m2':round(float(area.min()),4),
            'largest_panel_area_m2':round(float(area.max()),4),
            'median_panel_area_m2':round(float(np.median(area)),4),
            'largest_panel_armor_mass_kg':round(float(area.max()*RHO_ARMOR_PER_AREA),1),
            'median_panel_armor_mass_kg':round(float(np.median(area)*RHO_ARMOR_PER_AREA),1),
            'panel_area_m2':{str(int(g)):round(float(a),4) for g,a in zip(groups,area)},
            'width_sensitivity':blocked}

def rays_from_seat(j):
    eye=D.EYES[j];station=D.IDS[j]
    ds=D.directions(N_PILOT_RAYS if j<2 else N_SUPPORT_RAYS)
    ti=D.ellipse_hit(eye,ds,D.RUSABLE)
    tp=D.ellipse_hit(eye,ds,D.RP)
    to=D.outer_hit(eye,ds,*SHAPE)
    inner=eye+ds*np.nan_to_num(tp,nan=0)[:,None]
    outer=eye+ds*np.nan_to_num(to,nan=0)[:,None]
    ri,ai=D.polar(inner)
    ro,ao=D.polar(outer)
    check=np.isfinite(ti)&np.isfinite(tp)&np.isfinite(to)&(tp>=ti-1e-5)&(to>=tp+1e-5)
    check&=(ri<=CROWN)&(ro<=CROWN)
    check&=~D.frame_hit(ri,ai,CROWN,'radial')
    check&=~D.ray_sensor_mask(eye,ds,ti)
    # keep source crew obstructions, without redoing for every layout
    for i in np.flatnonzero(check):
        hit,_=D.O.dome_hit(REF.SC,tuple(eye),tuple(ds[i]))
        if not hit or D.O.blocked(REF.SC,tuple(eye),hit,station):check[i]=False
    return ro[check],np.radians(ao[check]),len(ds),int(check.sum())

def main():
    areas={}
    for key,p in PRESETS.items():
        area=area_mesh(p)
        areas[key]=area
        print('TILE',key,area['panel_count'],'large area',area['largest_panel_area_m2'],
              'mass kg',area['largest_panel_armor_mass_kg'],
              'seam area per widths',[area['width_sensitivity'][str(s)]['surface_fraction'] for s in SEAMS_MM],flush=True)
    rays={s:rays_from_seat(j) for j,s in enumerate(D.IDS)}
    scores={}
    for key,p in PRESETS.items():
        stations={}
        for station,(r,phi,total,base) in rays.items():
            _,dist=polar_id_gaps(r,phi,p)
            per_width={}
            for w in SEAMS_MM:
                n=int((dist<w/2000).sum())
                per_width[str(w)]={'blocked_visible_rays':n,'still_visible':base-n,
                      'forward_visible_fraction':round((base-n)/total,6),
                      'lost_forward_percentage_points':round(100*n/total,4)}
            stations[station]={'sample_count':total,'baseline_visible_rays':base,
                'base_fraction':round(base/total,6),
                'seam_width_mm':per_width}
        scores[key]=stations
        print('RAY',key,'PILOT',stations['PILOT'],flush=True)
    out={'classification':'RESEARCH NON-CANON NOT STRUCTURALLY OR BALLISTICALLY QUALIFIED',
       'source_pr432_head':'3485830a56dfead79b2ef8bba031a595b536fbb5',
       'geometry':'Outer +1.2m 50deg conical nose, central flat 2m, crown r3.5m. Inner pressure hull and interior unchanged.',
       'panels':'Nominally individually removable outward with independent perimeter retainers; no actual retainers/bearings/window mounts tested.',
       'outer_armor_mass_allocation_kg_per_m2':270,
       'tile_presets':PRESETS,
       'tile_areas_and_seams':areas,
       'forward_hemisphere_sightline_scores':scores,
       'model_limits':[
        'Seam bands are artificially totally opaque, with 5/10/20mm total projected-XY strip width; metal mount geometry and optical seam scattering unspecified.',
        'Large trapezoids on a conical surface must be curved/molded or faceted: a mathematical r-phi patch is not automatically a flat planar pane.',
        'Hex cells are planar-XY projected cells traced onto nose surface and can straddle the flat-to-conical transition at r=2m; not guaranteed manufacturable as single flat panels.',
        'Panel count includes cropped boundary slivers. Tiny edge tiles may be practically unacceptable and could be merged.',
        '270kg/m2 is an incumbent *mass allocation* for opaque equivalent armour, not certified protective ability of transparent tile.',
        'Replacing an outer tile from outside need not disturb the inner pressure boundary, but retaining hardware and service access are unverified.',
        'Rasterized panel areas approximate curved outer area; no ray refraction or actual pressure panel structural redesign.',
        'The inner pressure frame continues to obstruct vision in every comparison; no magical frameless pressure hull assumed.' ]}
    (ROOT/'command/l1_replaceable_outer_tiles_results.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
