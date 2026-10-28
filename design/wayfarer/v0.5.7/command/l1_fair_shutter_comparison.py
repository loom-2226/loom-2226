"""Matched necessary constraints for original Rev7 brow and angular-nose shoulder stowage.

This does not certify either mechanism. A brow-ring geometry is conditionally
interpreted as 1.0 m RADIAL width and 0.22 m AXIAL depth. The input does not
provide manufactured gore, track or swept volumes.
"""
import json, math
from pathlib import Path
import numpy as np
import l1_design_search as S

ROOT = Path(__file__).resolve().parent.parent
I = json.loads((ROOT/'inputs/wayfarer_v05_inputs.json').read_text())
G = json.loads((ROOT/'out/wayfarer_v05_geometry.json').read_text())
CD = I['habitat']['decks'][0]['command_layout']['crown_dome']
ARM = next(p for p in G['parts'] if p['id']=='armor')
R_OUT=I['hull']['outer_r_m']
R_P=I['hull']['pressure_r_m']
DENSITY=ARM['mass_t']/ARM['volume_m3']*1000 # kg/m3
AREAL=CD['gores']['closed_restores_g_cm2']*10 # kg/m2
T=AREAL/DENSITY

def base_x(r):
    return 2.35*(1-math.sqrt(max(0,1-(r/R_OUT)**2)))
def base_dx(r):
    return 2.35*r/(R_OUT*R_OUT*math.sqrt(max(1e-12,1-(r/R_OUT)**2)))
def press_x(r):
    if r>R_P: return None
    return 2.35-2.15*math.sqrt(max(0,1-(r/R_P)**2))
def area_meridian(a,b,profile):
    r=np.linspace(a,b,5001)
    if profile is None:
        deriv=np.array([base_dx(float(k)) for k in r])
    else:
        face=profile[1];angle=math.radians(profile[2])
        deriv=np.where(r<=face,0.0,math.tan(angle))
    arc=np.sqrt(1+deriv*deriv)
    return float(np.trapz(2*math.pi*r*arc,r)),float(np.trapz(arc,r))
def necessary_case(name,profile,crown,outer_stow):
    aperture,travel=area_meridian(0,crown,profile)
    stow_area,stow_meridian=area_meridian(crown,outer_stow,profile)
    min_layers=math.ceil(travel/stow_meridian-1e-12)
    r=np.linspace(crown,outer_stow,2401)
    vals=[]
    for n in range(1,min_layers+1):
        gaps=[]
        for rad in r:
            rad=float(rad)
            if profile is None:
                x=base_x(rad);slope=base_dx(rad)
            else:
                x=float(S.facet_x(rad,*profile))
                slope=0 if rad<=profile[1] else math.tan(math.radians(profile[2]))
            nx=1/math.sqrt(1+slope*slope)
            nr=-slope*nx
            rr=rad+n*T*nr
            px=press_x(rr)
            if px is not None:gaps.append(px-(x+n*T*nx))
        vals.append(min(gaps) if gaps else None)
    node=next(f for f in G['features'] if f.get('kind')=='node_face')
    return {
        'name':name,'crown_r_m':crown,'stow_radial_range_m':[crown,outer_stow],
        'opening_outer_area_m2':round(aperture,3),
        'outer_stow_surface_area_m2':round(stow_area,3),
        'ideal_surface_area_margin_m2':round(stow_area-aperture,3),
        'cover_meridian_length_m':round(travel,3),
        'stow_meridian_length_m':round(stow_meridian,3),
        'minimum_lengthwise_layer_count':min_layers,
        'closed_g_cm2':CD['gores']['closed_restores_g_cm2'],
        'armour_equivalent_material_t':round(aperture*AREAL/1000,3),
        'effective_volume_m3':round(aperture*T,3),
        'equivalent_layer_thickness_m':round(T,4),
        'pressure_clearance_x_m_by_nested_layers':[None if v is None else round(v,3) for v in vals],
        'press_head_intersection_at_required_layers':vals[-1]<0,
        'exterior_node_ring_0_r_m':round(math.hypot(*node['pos'][1:]),3),
        'measured_swept_volume':'UNAVAILABLE',
    }

def main():
    baseline_outer=CD['r_m']+CD['brow_ring']['width_m'] # conditional radial interpretation
    rows=[
        necessary_case('Rev7 original 2.8 m dome + declared brow',None,CD['r_m'],baseline_outer),
        necessary_case('Angular compact +0.8m /35deg / crown3.2',(.8,1.2,35),3.2,4.5),
        necessary_case('Angular panoramic +1.2m /50deg / crown3.5',(1.2,2.0,50),3.5,4.5),
    ]
    brow_gross=math.pi*(baseline_outer**2-CD['r_m']**2)*CD['brow_ring']['height_m']
    out={
      'status':'RESEARCH / non-governing / necessary-geometry comparison only',
      'sources':'PR #432 Rev7 plus independent nose research branch',
      'assumptions':{
        'same_areal_protection_kg_m2':AREAL,
        'effective_density_kg_m3_from_geometry_armor_part':round(DENSITY,1),
        'equivalent_layer_thickness_m':round(T,4),
        'rev7_brow_height_m':CD['brow_ring']['height_m'],
        'rev7_brow_width_m':CD['brow_ring']['width_m'],
        'conditional_brow_gross_annular_volume_m3':round(brow_gross,3),
        'brow_radial_width_interpretation':'HYPOTHETICAL (not manufactured geometry)',
      },'cases':rows,
      'limitations':[
        'Same necessary area, path length and pressure envelope checks; no actual track solids or folded slat geometry',
        'Brow height and width are declared in input but radial and axial orientation is not defined by built mesh',
        'Rev7 gores only have declared brow stowage, not explicit manufactured shutter paths',
        'Equivalent density inferred from whole armour part is an effective accounting density, not proven materials constitutive law',
        'Radial stacking is one mechanism, not a proof of impossibility for hinged or translated shutters',
        'Sensor assembly clearance and Metric-node field of regard are not certified',
        'Negative axial x clearance in this model is not normal penetration depth',
      ]}
    (ROOT/'command/l1_fair_shutter_comparison.json').write_text(json.dumps(out,indent=2))
    print('density',DENSITY,'kg/m3; thickness',T,'m; brow gross',brow_gross,'m3')
    for c in rows:
        print(c['name'])
        print(' area',c['opening_outer_area_m2'],'stow',c['outer_stow_surface_area_m2'],
              'margin',c['ideal_surface_area_margin_m2'],
              'armour',c['armour_equivalent_material_t'],'t',c['effective_volume_m3'],'m3')
        print('travel',c['cover_meridian_length_m'],'stow',c['stow_meridian_length_m'],
              'layers',c['minimum_lengthwise_layer_count'],'clearances',c['pressure_clearance_x_m_by_nested_layers'])
if __name__=='__main__':main()
