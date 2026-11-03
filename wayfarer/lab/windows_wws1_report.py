#!/usr/bin/env python3
"""Regenerate WWS-1 window inventory from exact current geometry. DRAFT."""
import json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
I=json.loads((ROOT/'config/wayfarer_v05_inputs.json').read_text())
Gpath=ROOT/'results/out/wayfarer_v05_geometry.json'
G=json.loads(Gpath.read_text());W=I['windows_wws1']
wind=[f for f in G['features'] if f['kind']=='window']
nodes=[f for f in G['features'] if f['kind']=='node_face']
assert len(wind)==20 and len(nodes)==208
sha=hashlib.sha256(Gpath.read_bytes()).hexdigest()
L=[]
def line(s=''):L.append(s)
line('# Wayfarer WWS-1 window plan, cost, node conflicts (DRAFT)')
line()
line('ALL bodies. ALL sponsors. 2026–2226.')
line()
line('**Basis:** stacked on PR #460, Wayfarer geometry '+sha+'. NON-CANON / NON-QUALIFICATION.')
line()
line('## Ordered plan')
line()
line('1. Upgrade the original 22 viewports and the existing L2 band to WWS-1, except close both L4 storm-shelter openings: 20 round windows remain.')
line('2. Preserve **one per berth** (10). Upper tier shifts from x6.45 to x6.70 to clear an existing Metric face, no node moved.')
line('3. Enlarge galley and exercise windows as **full-height (1.6m) segments of the existing L2 panoramic band**, retaining the 1.6m observation section and 0.6m wardroom section. Galley/exercise already had the narrow band; no gratuitous second holes.')
line('4. Enlarge the two medical ports to **0.75m** and move to x9.10m clear of the x10 principal frame and provisional x10.25 node ring. L4 shelter windows are **zero**.')
line()
line('## Every round port (20 total)')
line()
line('| Room / berth | x m | azimuth ° | diameter m | glass m² | WWS mass t¹ | reserve uplift t | nearest axial frame edge m |')
line('|---|---:|---:|---:|---:|---:|---:|---:|')
for f,p in zip(wind,W['port_list']):
    assert f['room']==p['room']
    x=f['pos'][0]
    theta=math.degrees(math.atan2(f['pos'][2],f['pos'][1]))%360
    frame=min(abs(x-2*j) for j in range(8))-f['d_m']/2
    suffix=(' / '+f['tier']) if f.get('tier') else ''
    line('| %s%s | %.2f | %.1f | %.2f | %.4f | %.4f | %.4f | %.3f |' % (
         f['room'],suffix,x,theta,f['d_m'],p['area_m2'],
         p['baseline_t']+p['incremental_t'],p['incremental_t'],frame))
line()
line('¹ WWS bare stack net of local replaced armour/hull plus retained existing window mounting/frame allowance; only uplift above existing booked legacy hardware draws released structural allocation. Local frame loads, large pane pressure and shutter proof OPEN. The two removed storm-shelter frames total 0.16t and are reused as shell restoration: no free credit.')
line()
line('## L2 WWS band')
line()
line('| Area | X range m | angles ° | glazed m² |')
line('|---|---|---|---:|')
r=I['hull']['pressure_r_m']
for seg in I['habitat']['crew_systems']['viewport_band']['segments']:
    x0,x1=seg['x_m'];a0,a1=seg['theta_deg']
    area=(x1-x0)*r*math.radians(a1-a0)
    name=('Galley' if a0>=300 or a1==30 else 'Wardroom' if a0==30 else 'Observation' if a0==150 else 'Exercise')
    line('| %s | %.2f–%.2f | %.1f–%.1f | %.4f |'%(name,x0,x1,a0,a1,area))
B=W['band']
line()
line('Original band area %.3f m²; new %.6f m². New complete net-stack + retained/scaled frame model %.6f t; previously booked band %.3f t; additional draw %.6f t.'%(
     B['original_area_m2'],B['new_area_m2'],B['new_net_assembly_t'],B['prior_mass_t'],B['incremental_t']))
line('L2 band crosses original x4m hull frame; G5 existing Osteon load-path is retained and recalculated, while real local cutout/transom fatigue remains OPEN.')
line()
line('## Budget (tonnes)')
line()
line('| Ledger | Before | Draw | After |')
line('|---|---:|---:|---:|')
line('| Engineering reserve | %.6f | 0.000000 | %.6f |'%(W['initial_engineering_t'],W['engineering_after_t']))
line('| Released structural allocation, zero radiation credit | %.6f | %.6f | %.6f |'%(
    W['initial_released_t'],W['window_budget_draw_t'],W['released_after_t']))
line('| **Combined uncommitted** | **%.6f** | **%.6f** | **%.6f** |'%(
    W['uncommitted_before_t'],W['window_budget_draw_t'],W['uncommitted_after_t']))
line()
line('Window retrofit draw: %.6f t L2 band + %.6f t round ports = **%.6f t**, versus **12.0 t** released draw limit and **13.7 t** total ceiling.'%(
   B['incremental_t'],sum(p['incremental_t'] for p in W['port_list']),W['window_budget_draw_t']))
line('Engineering reserve **%.6f >= 5.0 t** and combined uncommitted **%.6f >= 15.0 t**. Retired old ledger.venus_kit_t=1.7t was an unbooked annotation, giving **ZERO reclaimed mass**. v1 Venus kit remains 50t payload.'%(
     W['engineering_after_t'],W['uncommitted_after_t']))
line()
line('## Metric node and hull frame conflicts')
line()
conf=[n for n in nodes if 'overlaps_window' in n['flags']]
line('**Window overlaps after plan: %s**. PR #184 remains a face-placement HOLD. Existing 208 nodes unchanged.'%len(conf))
for n in conf:line('- CONFLICT: node ring %s theta %.1f, flags %s'%(n['ring'],n['theta_deg'],n['flags']))
line('The original PR #460 geometry had one window collision: node ring 1, theta 225°, against an upper berth window at x6.45. The *window* moved 0.25m to x6.70, not the node.')
for flag in sorted(set(f for n in nodes for f in n['flags'])-{'overlaps_window'}):
    cnt=sum(flag in n['flags'] for n in nodes)
    line('- Unchanged node-face hold (not a window conflict): %s, %d faces'%(flag,cnt))
line('Round port axial-frame clearances are shown individually above; expanded L2 intentionally bridges x4m frame plane. No window cutout moves a fixed Metric face.')
line()
line('## Shuttle-specific minimal viewports')
line()
line('No shuttle hull windows, cameras only. Three closed-cover pod ports per-seat Ø0.15–0.20m; 92bar external-pressure DESIGN target only. Mass 0.09–0.24t total assumed within existing pod fittings/seals range, not extra core mass; design/buckling/thermal seals still OPEN. See shuttle_wws1_port_inputs.json.')
line()
line('## G1–G12 and render results')
line()
report=ROOT/'results/out/certification_report.json'
if report.exists():
    q=json.loads(report.read_text())
    if q.get('geometry_sha256')==sha:
        line('Current report geometry matches source SHA. Verdicts listed below are numerical/declaration-qualified, never hardware qualification.')
        line('| Gate | Current verdict | Failed checks |')
        line('|---|---|---|')
        for g in q['gates']:
            fails=[c['name'] for c in g.get('checks',[]) if not c.get('pass')]
            line('| %s | %s | %s |'%(g['gate'],g['verdict'],', '.join(fails) if fails else 'None observed'))
    else:
        line('**NOT RECERTIFIED:** latest certificate geometry hash does not match new source. Hold all G1–G12 assertions until full execution.')
else:line('**NOT RECERTIFIED:** no new certificate.')
line()
line('Renders: wayfarer/render/wws1/before_ext_hab_viewports.png versus after_ext_hab_viewports.png, likewise ext_closed and ext_skin. After images count only if generated by current geometry. WWS-1 OPEN glazing and CLOSED armour states required.')
line('**Physical holds:** direct G6 particle/dose and shutter seam transport, AOI independent fracture response, actual per-cutout G5 frame reinforcement, G4 window thermal/dust survival, pod 92bar thick ports. No G1–G12 criteria relaxed.')
(ROOT/'docs/WINDOW_PLAN_WWS1.md').write_text('\n'.join(L)+'\n')
print('Report lines',len(L),'new hash',sha,'window-node conflicts',len(conf))
