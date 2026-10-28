"""Adapt the existing offline 16-leaf cam viewer to the tested flush lap seam.

Source reference viewer remains unchanged. This renders the two main planar
blades and provides an explanatory closed seam section; a full 3D rabbet
under-cut is NOT displayed as manufactured CAD.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
F=json.loads((ROOT/'command/l1_iris_flush_scarf_results.json').read_text())
B=json.loads((ROOT/'command/l1_iris_two_tier_cam_results.json').read_text())
old=next(q for q in B['results'] if q['iris_radius_m']==1.76)
frames=[]
for f in F['stage_frames']:
    frames.append({
     'angle_deg':f['opening_angle_deg'],
     'upper_front_x_m':f['upper_x_front_m'],
     'lower_front_x_m':f['lower_x_front_m'],
     'min_pressure_gap_m':f['minimum_pressure_gap_m'],
     'min_fixed_armour_gap_m':None if f['stage']!='joint_cam' else .026,
     'fixed_armour_contacts':f['outer_fixed_armour_contacts'],
     'same_tier_collision':f['same_tier_collision'],
     'min_intertier_gap_m':f['full_tier_separation_x_m'],
     'lap_gap_m':f['seam_lip_separation_x_m'],
     'stage':f['stage'],
     'stage_fraction':f['fraction'],
    })
model={'R':1.76,'frames':frames,'path_clear':F['path_sampled_geometry_clear'],
       'visibility':old['visibility'],'end_margin':old['end_available_x_interval_m']}
data={'options':[model],'T':old['thickness_each_m'],
      'gap':old['intertier_axial_gap_m'],
      'source':'PR432 source 3485830a56df, research angular 50deg; ideal 2deg flush scarf lap'}
html=(ROOT/'render/out/nose_two_tier_cam_viewer.html').read_text()
html,n=re.subn(r'const D=.*?,el=id=>',lambda m:'const D='+json.dumps(data,separators=(',',':'))+',el=id=>',html,count=1,flags=re.S)
assert n==1
html=html.replace('WAYFARER · INTERLEAVED IRIS CAM','WAYFARER · FLUSH LAP IRIS EXPERIMENT')
html=html.replace('16 thick leaves · two x-levels','16 thick leaves · flush when closed, staggered for motion')
html=html.replace("el('model').value='1';","el('model').value='0';")
html=html.replace('max="92" step="1" value="92"', 'max="122" step="1" value="122"')
html=html.replace('<h3>Mechanism assumptions</h3>', '''<h3>Ideal closed scarf-lap section</h3>
<svg viewBox="0 0 300 130" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Section through the closed lap. Front upper lip and rear lower lip each take half the full armor depth, with no empty layer.">
<rect x="6" y="6" width="288" height="118" fill="#0b1625" rx="6"/>
<text x="15" y="22" fill="#bed2e5" font-size="10">OUTSIDE → (x goes aft / inward)</text>
<text x="13" y="43" fill="#ebbd76" font-size="11">Upper lap</text>
<text x="13" y="84" fill="#68cfbf" font-size="11">Lower lap</text>
<rect x="105" y="30" width="77" height="30" fill="#ebbd76"/>
<rect x="182" y="60" width="77" height="30" fill="#68cfbf"/>
<line x1="182" y1="27" x2="182" y2="96" stroke="#ffffff" opacity=".6" stroke-width="1"/>
<text x="119" y="55" font-size="12" fill="#132033">98 mm</text>
<text x="193" y="82" font-size="12" fill="#132033">98 mm</text>
<text x="103" y="113" font-size="10" fill="#b0c5db">Nominal 196 mm combined, zero tolerance</text>
</svg>
<h3>Mechanism assumptions</h3>''')
html=html.replace('<p class="muted">Upper eight leaves <b style="color:#edbd77">gold</b>; lower eight <b style="color:#5dccbc">teal</b>. Each leaf is 0.1963 m thick, with 20 mm between levels. The leaves move aft first while inside the central aperture, then rotate together while an axial cam guides them beneath the fixed 20 cm-normal hypothetical shoulder armour.</p>',
'''<p class="muted">At <b>0% CLOSED</b>, gold and teal main blade faces are coplanar. Their 2° seams have a front 98 mm upper lip and mating rear 98 mm lower lip, preserving the 196 mm ideal material depth. <b>Then the lower eight retreat 216 mm</b>, both sets withdraw aft, and the 16 blades rotate on their previously tested cam. Physical hinges, seals and edge tolerances are NOT included.</p>''')
html=html.replace('<p class="muted"><b>Not a qualified mechanism:</b> no real rim throat, bearings, drives, finite lap seal, structural load path or ballistic closure. When shut, the two tiers still have a 216 mm surface step. The rendering shows thin face skins; collision study used through-thickness intervals.</p>',
'''<p class="muted"><b>Not a qualified mechanism:</b> no real rim throat, bearings, drives, finite lap seal, structural load path or ballistic closure. The closed <i>ideal</i> front plane has no step, but 4.19 mm lap width at the central boss and exactly zero tolerance makes this an unproven physical armour seam. The rendering shows main sheet faces only; lap rebates are explained in the cross-section.</p>''')
html=html.replace('<p class="muted">Drag to orbit, scroll to zoom. The 1.80 m design fails the two-tier pressure/shell allowance; 1.76 m and 1.75 m pass the selected necessary geometry checks. These do not imply mechanical certification or recovered panoramic side views.</p>',
'''<p class="muted">Drag to orbit, scroll to zoom. Selected 1.76 m design passes the tested geometric path. It is not a manufactured or impact-qualified shutter; broad forward-hemisphere visibility remains substantially below Rev 7.</p>''')
html=html.replace("'#ebbd76':'#5dccbc'","'#ebbd76':'#5dccbc'")
# In the lower-retreat phase, the full slabs don't overlap in azimuth,
# so negative "main-tier x separation" is not a material collision.
html=html.replace("'Minimum distance between tier faces <b>'+s.min_intertier_gap_m.toFixed(3)+' m</b>'", "'Main-tier axial separation (lap handles peel) <b>'+s.min_intertier_gap_m.toFixed(3)+' m</b>'")
html=html.replace("'Sampled frame status <b class='+", "'Sampled frame status <b class='+")
html=html.replace("const pass=!s.fixed_armour_contacts&&!s.same_tier_collision&&s.min_pressure_gap_m>=.025;", "const pass=!s.fixed_armour_contacts&&!s.same_tier_collision&&s.min_pressure_gap_m>=.025;")
html=html.replace("'<div class=\"stat\">Minimum distance between tier faces <b>'+s.min_intertier_gap_m.toFixed(3)+' m</b></div>'+",
"""'<div class="stat">Main-tier x separation <b>'+s.min_intertier_gap_m.toFixed(3)+' m</b> (before peel, overlap exists only in mating half-depth lips)</div>'+
 '<div class="stat">Mating-lip axial separation <b>'+s.lap_gap_m.toFixed(3)+' m</b></div>'+""")
out=ROOT/'render/out/nose_iris_flush_scarf_viewer.html'
out.write_text(html)
print('FLUSH SCARF VIEWER',out,'bytes',out.stat().st_size,'frames',len(frames))
