#!/usr/bin/env python3
"""Emit the small R2 evidence report from source input, geometry, cert and FQ."""
import json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
I=json.loads((ROOT/'config/wayfarer_v05_inputs.json').read_text())
Gpath=ROOT/'results/out/wayfarer_v05_geometry.json'
G=json.loads(Gpath.read_text());SHA=hashlib.sha256(Gpath.read_bytes()).hexdigest()
W=I['windows_wws1'];R=I['windows_wws1_round2'];port=[f for f in G['features'] if f['kind']=='window']
n=[f for f in G['features'] if f['kind']=='node_face']
assert len(port)==len(W['port_list'])==21 and len(n)==208
L=[]
def line(s=''): L.append(s)
line('# WWS-1 round 2: Window plan, numerical certification, occupant views')
line()
line('ALL bodies. ALL sponsors. 2026–2226.')
line()
line('**DRAFT / NON-CANON / NOT FOR MERGE.** kT approved 2026-11-03; same branch/PR #465 based on PR #460.')
line('Round-one baseline source SHA: '+R['base_geometry_sha256'])
line('Round-two source SHA: '+SHA)
line()
line('## Corrected budget authority')
line()
line('The **12.0 t cap is the TOTAL NEW DRAW from structure_split.released_to_reserve**, not a cap on nominal installed window material. kT retired the erroneous 13.7 t installed-mass ceiling. Do not use it as a criterion.')
line('The 1.7t historic Venus-kit annotation was never physically in the dry ledger and never creates reserve credit. The shuttle kit stays payload.')
line()
line('| Allocation (tonnes) | Round 1 | Round 2 additional | Round 2 final |')
line('|---|---:|---:|---:|')
line('| **New structural allocation committed** | %.6f | %.6f | **%.6f / 12.0** |'%(
    R['prior_new_draw_t'],R['round2_added_draw_t'],R['total_new_draw_t']))
line('| Remaining NEW draw headroom | %.6f | −%.6f | **%.6f** |'%(
    R['available_after_round1_t'],R['round2_added_draw_t'],R['unused_new_draw_t']))
line('| Released-to-reserve still uncommitted | %.6f | −%.6f | **%.6f** |'%(
    R['released_before_t'],R['round2_added_draw_t'],R['released_after_t']))
line('| Engineering reserve (unchanged) | %.6f | 0 | **%.6f >= 5.0** |'%(
    R['engineering_after_t'],R['engineering_after_t']))
line('| **Combined uncommitted** | %.6f | −%.6f | **%.6f >= 16.8** |'%(
    R['combined_before_t'],R['round2_added_draw_t'],R['combined_after_t']))
line()
line('Round-two increment: round ports **%.6f t** + L2 band **%.6f t** = **%.6f t**. Round-one includes **0.060 t** G5 longeron material; no new second-stage longeron appropriation is counted until a demonstrated G5 overrun.'%(
 R['round2_increment_ports_t'],R['round2_increment_band_t'],R['round2_added_draw_t']))
line('Full nominal installed WWS window assemblies: **%.6f t → %.6f t** (booked WWS material-plus-frames and older physically retained frame allocations), but there is explicitly **NO installed-mass cap**.'%(R['round1_installed_windows_t'],R['round2_installed_windows_t']))
line()
line('## Every round port: room, old/new size, area, mass and local axial frame clearance')
line()
line('| Room / tier | x m | θ ° | Old Ø m | New Ø m | Old total t | New total t | Delta t | Area m² | Frame edge m |')
line('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
round_delta=0
for f,p in zip(port,W['port_list']):
    assert f['room']==p['room'] and abs(f['d_m']-p['diameter_m'])<1e-7
    x,y,z=f['pos'];theta=(math.degrees(math.atan2(z,y))+360)%360
    d=p['diameter_m'];old=p['round1_full_assembly_t'];new=p['baseline_t']+p['incremental_t']
    diff=new-old;round_delta+=diff
    clearance=min(abs(x-2*j) for j in range(8))-d/2
    tier=' / '+f['tier'] if f.get('tier') else ''
    extra=' [NEW]' if p.get('new_port_round2') else ''
    line('| %s%s%s | %.2f | %.1f | %.2f | %.2f | %.4f | %.4f | %+.4f | %.4f | %.3f |'%(
        f['room'],tier,extra,x,theta,p['round1_diameter_m'],d,old,new,diff,p['area_m2'],clearance))
assert abs(round_delta-R['round2_increment_ports_t'])<5e-7,(round_delta,R['round2_increment_ports_t'])
line()
line('The 10 berth windows enlarge **0.50 → 0.80m**. Upper-tier ports shift 4° in the direction that clears the fixed Metric faces and retain at least 0.10m between paired pressure cutouts. At 0.80m, the opening nearly fills the declared 0.82m tier height: the pressure-retaining rim must mount outward / within structural shell. **That physical clearance and pressure-seal durability remain OPEN.**')
line('Medical: two existing 0.75m ports replaced with 1.55m ports and a **third 1.55m port added** at θ180/210/240 and x9.10. All round apertures must pass G5 principal frames / 0.10m hull-web separation and G9 crawler clearances.')
line()
line('## L2 galley and exercise glass, no other room intrusions')
line()
line('| Sector | Old x-range m | New x-range m | θ ° | New area m² |')
line('|---|---|---|---|---:|')
for old,seg in zip(R['round1_band_segments'],I['habitat']['crew_systems']['viewport_band']['segments']):
    a0,a1=seg['theta_deg'];x0,x1=seg['x_m'];area=(x1-x0)*I['hull']['pressure_r_m']*math.radians(a1-a0)
    kind='Galley' if a0>=300 or a1<=30 else 'Wardroom' if a0==30 else 'Observation' if a0==150 else 'Exercise'
    line('| %s | %.2f–%.2f | %.2f–%.2f | %.0f–%.0f | %.3f |'%(kind,*old['x_m'],x0,x1,a0,a1,area))
line()
line('Total L2 glazing **%.6f → %.6f m²**; extended galley/exercise segments to x3.35–5.55, maintaining 0.05m room-end allowance. Other sectors and opaque washroom unchanged. Added local partial edge rings **%.6f t** and two transoms **%.6f t** to the existing frame model, plus scaled mullions and shutters. This is declared design mass, not local FEA pressure/vibration qualification.'%(
 R['round1_band_area_m2'],R['l2_new_area_m2'],R['l2_local_edge_return_t'],R['l2_extra_transoms_t']))
line()
line('## Window/node/external-equipment clearances')
line()
hit=[(x['ring'],x['theta_deg']) for x in n if 'overlaps_window' in x['flags']]
line('- 208 existing Metric faces, placement authority **PR #184 HOLD**. New window/node overlaps: **%d**. No node-face coordinates moved.'%len(hit))
line('- Storm shelter L4 **ZERO** windows. Camera-only shuttle hull and three separately covered 92-bar-unqualified pod ports are unchanged.')
line('- Source certifier G5 checks every round port against 2m-pitch axial frames, all round-port pair hull-web separation >=0.10m, and enlarged L2 sectors against room limits and node faces. G9 checks all external gear incl. crawler point #6. A geometric pass is not an independently proved pressure seal, FEM load path or particle transport model.')
line()
line('## G1–G12 exact-geometry certification')
line()
report=ROOT/'results/out/certification_report.json'
if report.exists():
    j=json.loads(report.read_text())
    if j['geometry_sha256']==SHA:
        line('| Gate | Result | Failed source checks |')
        line('|---|---|---|')
        for gate in j['gates']:
            failed=[c['name'] for c in gate['checks'] if not c['pass']]
            line('| %s | %s | %s |'%(gate['gate'],gate['verdict'],', '.join(failed) if failed else 'None'))
        if all(g['verdict'].startswith('PASS') for g in j['gates']):
            line('**G1–G12 PASS/PASS-DECLARED; no criteria relaxed.** PASS-DECLARED is a design screen, not hardware qualification.')
    else:line('**PENDING: certificate hash does not match round-two geometry.** Never use stale pass evidence.')
else:line('**PENDING: no new certification report.**')
line()
fq=ROOT/'lab/flight_qual/fq_house_power_20261101/FQ1_FQ4_CURRENT_SUMMARY.json'
if fq.exists():
    q=json.loads(fq.read_text())
    if q.get('geometry_sha256')==SHA:
        line('**FQ1–FQ4 current-geometry matrix:** '+str(q.get('status',q.get('summary','check JSON')))+'. Check the source case counts in the linked FQ file.')
    else:line('**FQ1–FQ4 PENDING:** source summary not current geometry hash.')
for name in ('RCS_40S_CURRENT_TRACE.json','RCS_60S_DEGRADED_TRACE.json'):
    f=ROOT/'lab/flight_qual/fq_house_power_20261101'/name
    if f.exists():
        v=json.loads(f.read_text())
        line('- %s: %s'% (name,'hash MATCH' if v.get('geometry_sha256')==SHA else 'STALE / HOLD'))
line()
line('## Five occupant viewpoints')
line()
line('Each uses the same camera both rounds, source 3D geometry, shutters OPEN, and source-hashed render manifest.')
line()
line('| Occupant view | Round 1 BEFORE | Round 2 AFTER |')
line('|---|---|---|')
for name in ('berth','lounge','galley','exercise','medical'):
    a=f'../render/wws1_round2/before_pov_{name}.png'
    b=f'../render/wws1_round2/after_pov_{name}.png'
    line('| %s | %s | %s |'%(name,'[Rendered]('+a+')' if (ROOT/f'render/wws1_round2/before_pov_{name}.png').exists() else 'MISSING',
       '[Rendered]('+b+')' if (ROOT/f'render/wws1_round2/after_pov_{name}.png').exists() else 'PENDING'))
line()
line('### What remains unqualified')
line()
line('Large 2226 ceramic primary/backup pane independent failure, AOI shock coupling and optical/heat attenuation, per-cutout fatigue and pressure-seal FEM, movable Strata shutter/edge radiation transport, and emergency closing actuation. Every shutter CLOSED restores nominal local armour areal mass but no actual dose-transport qualification has been established. PR #184 node placement remains HOLD.')
(ROOT/'docs/WINDOW_PLAN_WWS1_ROUND2.md').write_text('\n'.join(L)+'\n')
print('R2_REPORT',len(L),'lines hash',SHA,'nodes/window hits',len(hit))
