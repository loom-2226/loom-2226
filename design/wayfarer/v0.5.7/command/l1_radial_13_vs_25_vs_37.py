"""Compare 13 continuous radial tiles with 25-piece transition split, against
unchanged 37-piece staggered outer glazing reference. RESEARCH NON-CANON.
"""
from pathlib import Path
import math,json
import numpy as np
import l1_replaceable_outer_tiles as T

ROOT=Path(__file__).resolve().parent.parent
HUB=.75
R=3.5
TRANSITION=2.
LAYOUTS={
 'single_piece_radial_13':{'type':'radial','rings':[0.,HUB,R],'ns':[1,12],'offsets':[0.,0.]},
 'split_at_facet_25':{'type':'radial','rings':[0.,HUB,TRANSITION,R],'ns':[1,12,12],'offsets':[0.,0.,0.]},
 'held_reference_staggered_37':T.PRESETS['staggered_trapezoids_compact_12'],
}
def pane_geometry(name):
    # Flat/facet exterior is x=-1.2+max(0,r-2)*tan50.
    # Through-radius one-piece panes must be bent/formed at transition,
    # or deviate substantially from the specified surface.
    theta=math.radians(50)
    x=lambda rr:-1.2+max(0,rr-2)*math.tan(theta)
    chord=lambda rr: x(HUB)+(x(R)-x(HUB))*(rr-HUB)/(R-HUB)
    at_transition=abs(x(2)-chord(2))
    # 12-degree? twelve wedges full pitch=30deg.
    # Maximum deviation of tangent-to-midline plane from axisymmetric cone
    # at rim along the 15deg off-axis boundary.
    edge_sag=math.tan(theta)*R*(1-math.cos(math.pi/12))
    ring_len=2*math.pi*HUB
    area=T.area_mesh(LAYOUTS[name])
    return {'single_long_panel_necessarily_bent_at_flat_to_cone':name=='single_piece_radial_13',
      'flat_single_panel_radial_chord_error_at_r2_m':round(at_transition,5) if name=='single_piece_radial_13' else None,
      'conical_pane_flat_facet_approximation_edge_error_at_r3p5_m':round(edge_sag,5),
      'central_ring_circumference_m':round(ring_len,4),
      'central_ring_arc_per_radial_panel_m':round(ring_len/12,4),
      'exterior_rim_arc_per_radial_panel_m':round(2*math.pi*R/12,4),
      'radial_span_central_to_rim_m':R-HUB if name=='single_piece_radial_13' else None,
      'tile_area':area}

def main():
    reference=json.loads((ROOT/'command/l1_replaceable_outer_tiles_results.json').read_text())
    ray_cache={st:T.rays_from_seat(j) for j,st in enumerate(T.D.IDS)}
    scores={}
    geometry={}
    for name,layout in LAYOUTS.items():
        geometry[name]=pane_geometry(name)
        stations={}
        for st,(r,phi,denom,base) in ray_cache.items():
            _,sep=T.polar_id_gaps(r,phi,layout)
            sweeps={}
            for mm in T.SEAMS_MM:
                blocked=int((sep<mm/2000).sum())
                sweeps[str(mm)]={'blocked_visible_rays':blocked,
                    'still_visible':base-blocked,
                    'forward_visible_fraction':round((base-blocked)/denom,6),
                    'lost_forward_percentage_points':round(blocked/denom*100,4)}
            stations[st]={'sample_count':denom,
                'baseline_visible_rays':base,'base_fraction':round(base/denom,6),
                'seam_width_mm':sweeps}
        scores[name]=stations
        g=geometry[name]['tile_area']
        print(name,'count',g['panel_count'],'m2',g['total_surface_area_m2'],
              'min',g['smallest_panel_area_m2'],'max',g['largest_panel_area_m2'],
              'maxkg',g['largest_panel_armor_mass_kg'],'seam10',g['width_sensitivity']['10']['seam_band_area_m2'],
              'Pilot 10mm',stations['PILOT']['seam_width_mm']['10']['forward_visible_fraction'],flush=True)
    old=reference['tile_areas_and_seams']['staggered_trapezoids_compact_12']
    assert geometry['held_reference_staggered_37']['tile_area']==old,'Reference geometry changed'
    # A separate 13-panel layout can not be described as a single flat piece
    # while retaining the current flat centre to 50deg cone surface.
    assert geometry['single_piece_radial_13']['flat_single_panel_radial_chord_error_at_r2_m']>.5
    for nm,g in geometry.items():
        a=g['tile_area']
        assert a['panel_count']=={'single_piece_radial_13':13,'split_at_facet_25':25,
              'held_reference_staggered_37':37}[nm]
        assert abs(a['total_surface_area_m2']-52.888)<.04
        assert abs(a['largest_panel_armor_mass_kg']-270*a['largest_panel_area_m2'])<.1
        for st, v in scores[nm].items():
            s=[v['seam_width_mm'][str(i)]['forward_visible_fraction'] for i in (5,10,20)]
            assert v['base_fraction']>=s[0]>=s[1]>=s[2]
    output={'classification':'RESEARCH NON-CANON NOT QUALIFIED',
        'source_pr432_sha':'3485830a56dfead79b2ef8bba031a595b536fbb5',
        'reference_holds_37':True,
        'design_intent':'central 0.75m clear circular protective tile + 12 radial outer segments; split those 12 at 2.0m flat/facet transition for 25-piece option',
        'original_pressure_hull_and_seats_unchanged':True,
        'projected_seam_width_mm_tested':T.SEAMS_MM,
        'layouts':LAYOUTS,
        'tile_area_results':{name:row['tile_area'] for name,row in geometry.items()},
        'special_geometry':{name:{k:v for k,v in row.items() if k!='tile_area'} for name,row in geometry.items()},
        'sightline_results':scores,
        'critical_limits':[
         'Single radial 13-piece exterior panel crosses a real flat-to-50deg-slope break and must be bent/molded or change the ship profile; it is NOT a large flat trapezoid.',
         'Even split radial 25-piece sectors on a smooth cone are slightly curved: a true planar facet changes existing shell shape.',
         'Outer protective panel mass equals assumed existing 270kg/m2 opaque armour equivalent, not demonstrated nanoengineering/HVI performance.',
         'Each outer panel can in principle be separately removed outward if retainers disengage independently; no mounts, seal, panel removal sweep, space manipulator or crack-failure mechanics assessed.',
         'Structural central anchor is a perimeter support RING, not the centre transparent pane; ring and attachments are not sized.',
         'Seams modeled as 5/10/20mm fully opaque projected widths and are not proven MMOD-protective or mechanically structural.',
         'Ray scores are straight-line geometric, do not include refraction in thick actual glazing.',
         'Inner pressure glazing stays in place unchanged in both geometry and mass, and its actual pressurised structural implementation remains unqualified.',
         'Current 37-tile reference remains intact and preferred unless observable benefit justifies a new design.'
        ]}
    (ROOT/'command/l1_radial_13_vs_25_vs_37_results.json').write_text(json.dumps(output,indent=2))
if __name__=='__main__':main()
