"""Narrow radial-tambour shutter stowage test for Wayfarer Rev 7.
Non-governing. Uses actual pressure profile and Rev7 ring-0 node location.
Tests NECESSARY geometry only; a PASS here would NOT be engineering closure.
"""
import json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT),str(ROOT/'command')]
import l1_design_search as S

GEOM=json.loads((ROOT/'out/wayfarer_v05_geometry.json').read_text())
NODES=[f for f in GEOM['features'] if f.get('kind')=='node_face' and f.get('ring')==0]
SHUTTER_AREAL_KG_M2=270.0
EFFECTIVE_DENSITY_KG_M3=1375.0
T=SHUTTER_AREAL_KG_M2/EFFECTIVE_DENSITY_KG_M3
RO=4.5
RP=4.3
MAX_DIAMETER_M=9.0

def pressure_x(r):
    if r>RP: return None
    return 2.35-2.15*math.sqrt(max(0,1-(r/RP)**2))

def geom(shape,crown):
    extension,face,a=shape
    angle=math.radians(a)
    sec=1/math.cos(angle)
    exposed=S.exterior_aperture_area_m2(shape,crown,'radial')
    storage=math.pi*(RO**2-crown**2)*sec
    covered_meridian=min(face,crown)+max(0,crown-face)*sec
    stow_meridian=(RO-crown)*sec
    min_layers=math.ceil(covered_meridian/stow_meridian-1e-12)
    radii=np.linspace(crown,RO,1301)
    clearance_per_layer=[]
    layers_that_fit=[]
    for n in (1,2,3,4):
        depths=[]
        for r in radii:
            # Normal directed inward: (+cos a, -sin a) in (x,r).
            r_in=float(r-n*T*math.sin(angle))
            x_in=float(S.facet_x(r,*shape)+n*T*math.cos(angle))
            px=pressure_x(r_in)
            if px is not None:
                depths.append(px-x_in)
        min_clearance=min(depths) if depths else float('inf')
        clearance_per_layer.append(round(min_clearance,4))
        layers_that_fit.append(min_clearance>0)
    return dict(shape=shape,crown_r_m=crown,
        exterior_coverage_m2=exposed,
        exterior_annulus_m2=round(storage,2),
        exterior_annulus_area_margin_m2=round(storage-exposed,2),
        exterior_annulus_area_ratio=round(storage/exposed,3),
        shutter_meridian_m=round(covered_meridian,3),
        stow_meridian_m=round(stow_meridian,3),
        minimum_radial_stow_layers=min_layers,
        layer_equivalent_thickness_m=round(T,4),
        shutter_material_t=round(exposed*SHUTTER_AREAL_KG_M2/1000,2),
        shutter_material_m3=round(exposed*T,2),
        minimum_pressure_clearance_m_by_layers=clearance_per_layer,
        inward_stow_min_layers_clear_pressure=layers_that_fit[min(min_layers,4)-1],
        nominal_outward_extra_diameter_m=round(2*T*math.sin(angle),3),
        node_ring_0_count=len(NODES),
        node_ring_0_x_m=round(NODES[0]['pos'][0],3),
        node_ring_0_radial_m=round(math.hypot(*NODES[0]['pos'][1:]),3),
        no_swept_volume_proof=True)

def draw_svg(g,path):
    # x increases right (aft); radial z increases up. Mathematically metrically scaled.
    W,H=1100,720
    scale=132; origin_x=300; origin_y=650
    X=lambda x:origin_x+scale*x
    Z=lambda r:origin_y-scale*r
    xlim=(-1.15,2.9)
    exterior=g['shape'];face=exterior[1];crown=g['crown_r_m']
    def poly(points,color,width=3,dash=''):
        p=' '.join(f'{X(x):.2f},{Z(r):.2f}' for x,r in points)
        return f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}" {("stroke-dasharray="+chr(34)+dash+chr(34)) if dash else ""}/>'
    def txt(x,y,t,size=15,color='#dbeafe'):
        return f'<text x="{x}" y="{y}" fill="{color}" font-family="system-ui" font-size="{size}">{t}</text>'
    p=[(pressure_x(float(r)),float(r)) for r in np.linspace(0,RP,180)]
    ext=[(float(S.facet_x(float(r),*exterior)),float(r)) for r in np.linspace(0,RO,180)]
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<rect width="100%" height="100%" fill="#0a1322"/>',
       txt(28,36,'WAYFARER: radial shutter stowage test',23,'#fff'),
       txt(28,61,f'+{exterior[0]:.1f} m  /  {exterior[2]:.0f}° facet  /  {crown:.1f} m crown  ·  Non-governing, metric-scale section',16,'#a9bed8'),
       poly([(2.35,0),(2.35,4.5)],'#9ca3af',1,'7,7'),
       poly(p,'#60b5f9',4),poly(ext,'#e1a456',4),
       poly([(float(S.facet_x(float(r),*exterior)),float(r)) for r in np.linspace(crown,RO,50)],'#35d3bd',8),
       txt(560,99,'Blue: pressure head',14,'#60b5f9'),
       txt(560,122,'Orange: new exterior',14,'#e1a456'),
       txt(560,145,'Green: candidate stow annulus',14,'#35d3bd')]
    # Draw prospective maximum necessary-layer interior stack surface
    a=math.radians(exterior[2]);n=g['minimum_radial_stow_layers']
    q=[(float(S.facet_x(float(r),*exterior)+n*T*math.cos(a)),float(r-n*T*math.sin(a))) for r in np.linspace(crown,RO,100)]
    o.append(poly(q,'#ff6464',3,'6,5'))
    o.append(txt(560,168,f'Red dashed: {n} stacked armour-equivalent layers',14,'#ff7777'))
    o.append(txt(28,690,'x increases aft (right); radius increases up. Axes measured in metres.',14,'#d5e1f3'))
    for rr in range(6):
        y=Z(rr)
        if y<70:continue
        o.append(poly([(-1.1,rr),(2.6,rr)],'#21324b',1))
        o.append(txt(25,y-6,f'r={rr} m',12,'#9aaec7'))
    for x in [-1,0,1,2]:
        o.append(poly([(x,0),(x,4.5)],'#21324b',1))
        o.append(txt(X(x)+4,662,f'x={x} m',12,'#9aaec7'))
    for node in NODES:
        x,y,z=node['pos']
        r=math.hypot(y,z)
        o.append(f'<circle cx="{X(x):.2f}" cy="{Z(r):.2f}" r="{.175*scale:.2f}" fill="#a78bfa" fill-opacity=".22" stroke="#a78bfa" stroke-width="1.4"/>')
    o.append(txt(560,191,'Purple: 16 forward Metric-node faces (angularly superimposed)',14,'#bcafff'))
    o.append(txt(560,235,f'Shutter area: {g["exterior_coverage_m2"]:.2f} m²',17))
    o.append(txt(560,262,f'Annular area: {g["exterior_annulus_m2"]:.2f} m²',17))
    o.append(txt(560,289,f'Area margin: {g["exterior_annulus_area_margin_m2"]:+.2f} m²',17))
    o.append(txt(560,316,f'Minimum longitudinal layers: {n}',17))
    o.append(txt(560,343,f'Inward clearance at required layers:',17))
    o.append(txt(560,369,f'{g["minimum_pressure_clearance_m_by_layers"][n-1]:+.3f} m (negative = intersects pressure head)',16,'#ff8b8b'))
    o.append(txt(560,413,'Necessary tests only: not an actuator, seal, track,',14,'#a9bed8'))
    o.append(txt(560,434,'or ballistic survival qualification.',14,'#a9bed8'))
    o.append('</svg>')
    path.write_text('\n'.join(o))

def main():
    cases=[((.8,1.2,35),c) for c in (3.0,3.2,3.5)]
    cases += [((1.2,2,50),c) for c in (3.2,3.5)]
    result={'status':'NON-GOVERNING, NECESSARY STOWAGE CHECK ONLY',
            'source_sha':'3485830a56dfead79b2ef8bba031a595b536fbb5',
            'assumptions':{'areal_kg_m2':SHUTTER_AREAL_KG_M2,
                           'effective_density_kg_m3':EFFECTIVE_DENSITY_KG_M3,
                           'outer_r_m':RO,'pressure_r_m':RP},
            'models':[geom(shape,c) for shape,c in cases],
            'limitations':['Areal and meridional capacity are only necessary constraints',
                           'Stacking test assumes armour equivalent density and sliding normal to 35/50 degree facets',
                           'Original nodes are treated as exclusion-risk evidence, not full body solids',
                           'No shutter kinematics, actuator, seal, track, spall containment, or ballistic qualification']}
    target=next(q for q in result['models'] if q['shape']==(.8,1.2,35) and q['crown_r_m']==3.2)
    (ROOT/'command/l1_shutter_stowage_results.json').write_text(json.dumps(result,indent=2))
    draw_svg(target,ROOT/'render/out/nose_shutter_stowage_section.svg')
    print('LAYER THICKNESS',round(T,4),'m')
    for q in result['models']:
        print('CASE',q['shape'],q['crown_r_m'],
              'cover',q['exterior_coverage_m2'],'annulus',q['exterior_annulus_m2'],
              'margin',q['exterior_annulus_area_margin_m2'],
              'min layers',q['minimum_radial_stow_layers'],
              'internal pressures',q['minimum_pressure_clearance_m_by_layers'],
              'outer diameter addition',q['nominal_outward_extra_diameter_m'])
    print('RING0 nodes',len(NODES),'r',result['models'][0]['node_ring_0_radial_m'])
if __name__=='__main__':main()
