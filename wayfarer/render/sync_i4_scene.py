"""Refresh the already-scored integrated I4 command scene from current geometry and config.
The historical l1_study.py assumes the pre-I4 flight_deck key and is not the I4 exporter.
"""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
G=R/'results/out/wayfarer_v05_geometry.json'
H=hashlib.sha256(G.read_bytes()).hexdigest()
I=json.loads((R/'config/wayfarer_v05_inputs.json').read_text())
p=R/'render/out/l1_scene.json';s=json.loads(p.read_text())
C=I['habitat']['decks'][0]['command_layout']
s['geometry_sha256']=H
s['navigator_platform']={k:C['i4_lock']['platforms']['navigator_platform'][k] for k in ('x_m','y_m','z_m')}
s['command_terrace']={k:C['i4_lock']['platforms']['command_terrace'][k] for k in ('x_m','y_m','z_m')}
s['carryover']=I['i4_carryover']['items']
s['l1_l2_hatches']=[
 {'id':'l1_l2_hatch_'+str(i),'y':q['y'],'z':q['z'],'size_m':q['size'],
  'state':'OPEN/PARKED normally; physically CLOSABLE to isolate L1/L2 upon depressurisation',
  'closed_state':'0.92m sealed leaf covers 0.8m ladder opening; full-differential seal proof is HOLD',
  'pressure_isolating_intent':True,'mass_t':.15,
  'mass_basis':'0.15t per hatch DRAWN from Option C engineering reserve, includes frame, leaf, latch, seal and hinge; NOT existing no-mass outfitting'}
 for i,q in enumerate(s['ladders'])]
s['operating_phases']=[
  'coast+standing collaboration',
  'approach+six specialist stations',
  '4g+six occupied seats; standing stations inactive']
s['status']='kT integrated I4; 37 [1,12,12,12] with original rings and stagger; NAV platform and parked L1/L2 hatch leaves; 4g seated doctrine, twin dome and AOI optical research, source '+H
assert len(s['l1_l2_hatches'])==2 and len(s['carryover'])==16
p.write_text(json.dumps(s,indent=1)+'\n')
print('SCENE_SYNC',H,'NAV',s['navigator_platform'],'HATCHES',len(s['l1_l2_hatches']))
