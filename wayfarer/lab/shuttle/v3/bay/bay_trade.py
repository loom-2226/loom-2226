"""Wayfarer-side cost of longer/wider shuttle bays (read-only study; no Wayfarer change).
ALL bodies. ALL sponsors. 2026-2226. Sources: wayfarer_v05_geometry.json parts, CANON II v2.5 §13/§14, occupancy.json."""
import json, math, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OCC = json.load(open(os.path.join(HERE, 'occupancy.json')))
WET_S1, REMASS, VE_ECON = 1167.532686975091, 245.39043171108221, 3000.0      # CANON II v2.5 §13, §14
DRY_S1 = WET_S1 - REMASS
def econ_dv(remass_removed):
    return VE_ECON * math.log((WET_S1 - remass_removed) / DRY_S1)
DV0 = econ_dv(0)
def slot_annulus_area(r0, r1, hw=2.4, n=400):
    """area of the tank annulus r0..r1 outside the bay slot (|y| < hw, z > 0) - the C-slot rule of the geometry record"""
    rs = np.linspace(r0, r1, n); A = 0.0; dr = (r1 - r0) / (n - 1)
    for r in rs:
        th = np.linspace(0, 2 * math.pi, 1441)[:-1]; y, z = r * np.cos(th), r * np.sin(th)
        keep = ~((np.abs(y) < hw) & (z > 0)); A += keep.mean() * 2 * math.pi * r * dr
    return A
opts = {}
# A: today
opts['A 12.8 m (today)'] = dict(bore_x=[18.25, 32.05], shuttle_max_m=12.8, remass_removed_t=0.0, structure_t=0.0,
    moves='none', conflicts=[], notes='bay bore x 18.25-32.05 sits between the relational plant blocks (fore r<2 ends x 17, aft starts x 32.3)')
# B: 14.3 m - bore x 17.0-32.3, relocate the x17-18 band into the free fore annulus
band = OCC['x17-18 r0-4.3']; fore = OCC['x14-17 r2-4.3 (fore annulus)']
moved_m3 = round(band['occupants'].get('electrical_fwd', 0) + band['occupants'].get('house_energy_battery', 0) + band['occupants'].get('house_reactor_B', 0) + band['occupants'].get('c_lite_dry', 0), 1)
opts['B 14.3 m'] = dict(bore_x=[17.0, 32.3], shuttle_max_m=14.3, remass_removed_t=0.0,
    structure_t=round(4.231 * 2.05 / 13.8 + 2 * 1.058 * 2.05 / 13.8, 2),
    moves=f'electrical_fwd (23.3 t), house battery, house reactor B, C-lite (~{moved_m3} m3) from x 17-18 into the fore annulus x 14-17 (geometry record shows {fore["free_m3"]} m3 free there); crew-transfer tunnel_1 rerouted',
    conflicts=['G3 trim: ~26 t moved ~1.5 m forward shifts the ship CG ~3 cm; worst trim today 0.356 deg of 0.5 deg (re-check)',
               'canon launch-bay reservation is "approximately x 16-28 m"; already exceeded today; not frozen'],
    notes='no remass change; bay liner and doors 2.05 m longer')
# C: 16.8 m - bore x 14.5-32.3, plant_fore off the axis
slot_cut = round(4.8 * (4.3 - 2.4) * (17.0 - 14.5), 1)
need = round(37.7 + moved_m3 + 3.5, 1)          # plant_fore cylinder volume + x17-18 band + tunnels/collar share
free_after = round(fore['free_m3'] - slot_cut, 1)
into_tank = round(max(0.0, need - free_after), 1)
opts['C 16.8 m'] = dict(bore_x=[14.5, 32.3], shuttle_max_m=16.8, remass_removed_t=into_tank,
    structure_t=round(4.231 * 4.55 / 13.8 + 2 * 1.058 * 4.55 / 13.8 + 1.0, 2),
    moves=f'relational plant fore block (37.8 t, r<2, x 14-17) moved off the axis; x 17-18 band as in B; slot cut through x 14.5-17 removes ~{slot_cut} m3 of the fore annulus; ~{need} m3 to rehouse, ~{free_after} m3 free -> ~{into_tank} m3 into the remass annulus',
    conflicts=['relational plant layout (kt relational_plant_layout_2026_11_16) and node topology change -> Loom commit configuration and certification redone (CANON II §12.1)',
               'normal remass 245.39 t is CANON (CCR-2026-0004): any reduction needs a canon change request',
               'plant block in a C-annulus is asymmetric (slot side): CG, inertia and field geometry unknown',
               'docking collar and crew-transfer tunnels in x 14-17 rerouted'],
    notes='displaced remass is lost capacity; it is not a dry-mass saving')
# D: 18 m - bore 19 m
opts['D 18 m'] = dict(bore_x=[13.3, 32.3], shuttle_max_m=18.0, remass_removed_t=None, structure_t=None,
    moves='bore would have to start at x 13.3 (habitat aft bulkhead x 13.4-13.7, L5 rooms x 11.1-13.4) or end past x 32.3 (torch manifold 55 t + relational plant aft block x 32.3-34.3, ~94% occupied)',
    conflicts=['habitat L5 / aft bulkhead or torch manifold / aft plant block: redesigning the ship, not trading remass'], notes='STOP: conflicts with Wayfarer invariants')
# W: wider bore (r 2.4 -> 2.7), envelope r 2.15 -> 2.45
A = slot_annulus_area(2.47, 2.77); vol = A * 13.5
opts['W wider bore r 2.7 m'] = dict(bore_x=[18.25, 32.05], shuttle_max_m=12.8, shuttle_radius_m=2.45, remass_removed_t=round(vol, 1), structure_t=None,
    moves=f'tank inner wall moved out 0.3 m over x 18-31.5: {round(vol,1)} m3 of tank volume lost',
    conflicts=['the four canonical D-He3 CSlot fuel lobes (CANON II §13.3) share the tank annulus: re-packing them is a canon change',
               'normal remass 245.39 t is CANON (CCR-2026-0004)'], notes='width is expensive: every 0.1 m of bore radius costs ~%d t of remass' % round(vol / 3))
for k, o in opts.items():
    x = o['remass_removed_t']
    if x is not None:
        o['econ_dv_kms'] = round(econ_dv(x), 1); o['econ_dv_lost_kms'] = round(DV0 - econ_dv(x), 1); o['econ_dv_lost_pct'] = round(100 * (1 - econ_dv(x) / DV0), 1)
json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', econ_dv_full_kms=round(DV0, 2), basis='CANON II v2.5 §13-14; geometry record v0.5; read-only', options=opts),
          open(os.path.join(HERE, 'bay_trade.json'), 'w'), indent=1)
for k, o in opts.items(): print(k, o.get('shuttle_max_m'), o.get('remass_removed_t'), o.get('econ_dv_lost_kms'), o.get('econ_dv_lost_pct'), o.get('structure_t'))
