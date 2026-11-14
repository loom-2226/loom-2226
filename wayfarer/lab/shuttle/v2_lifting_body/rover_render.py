"""Rover states for v2 (flight / landed / rover out): views, GLBs, manifest. ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, os, json, base64, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import build_v2b as B, variants as VA
from variants_render import view
HERE = os.path.dirname(os.path.abspath(__file__))
for k in list(B.MAT): pass
import variants_render as VR
VR.COL.update({k: np.array(v[0][:3]) for k, v in B.MAT.items() if k not in VR.COL})
fig, ax = plt.subplots(3, 1, figsize=(10, 11.5), dpi=110); fig.patch.set_facecolor('#f4f3ef')
T = {'flight': 'In the bay / entry: rover is the crew cabin, wings folded flush on the flanks',
     'landed': 'Landed on its own four short legs, belly 0.6 m up, doors shut',
     'out': 'Side door open (nose right): lower flank = ramp, wing swings up = awning; rover crab-steers out'}
for i, st in enumerate(('flight', 'landed', 'out')):
    P = VA.model_rover('B3', st)
    Pv = P if st == 'out' else {k: v for k, v in P.items() if k.startswith(('hull', 'belly', 'glazing', 'kit', 'fin', 'body', 'torch', 'wing')) or (st == 'landed' and k.startswith(('leg', 'pad')))}
    view(ax[i], Pv, 32 if st != 'out' else 148, 18 if st != 'out' else 26, T[st], lim=(9.0 if st == 'out' else 8.2, 4.6 if st == 'out' else 3.0))
    if st == 'out': ax[i].plot([-12, 14], [VA.GROUND_Z - 0.3 - 0.2, VA.GROUND_Z - 0.3 - 0.2], alpha=0)
    for v in ('B2', 'B3', 'B4'):
        if st == 'flight': continue
        B.write_glb(VA.model_rover(v, st), os.path.join(HERE, 'viewer', 'glb', f'_t.glb'))
        json.dump({'b64': base64.b64encode(open(os.path.join(HERE, 'viewer', 'glb', '_t.glb'), 'rb').read()).decode()},
                  open(os.path.join(HERE, 'viewer', 'glb', f'{v}_{st}.json'), 'w'))
os.remove(os.path.join(HERE, 'viewer', 'glb', '_t.glb'))
fig.suptitle('Shuttle v2-B3 with the twin-sphere rover - side door egress (NON-CANON lab model)', x=0.03, ha='left', fontsize=13, weight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(HERE, 'rover_states.png'), facecolor=fig.get_facecolor())
# manifest
P = VA.model_rover('B3', 'flight'); skip = ('sphere_stbd', 'sphere_port', 'tunnel', 'hatch_trunk')
allv = np.vstack([P[k][0] for k in P if k not in skip])
gap = min(float(np.min(np.linalg.norm(P[k][0] - [B.SPH_X, s * B.SPH_Y, B.SPH_Z], axis=1)) - B.SPH_R) for k in P if k.startswith('wheel') for s in (1, -1))
import variants as VA2
Po = VA.model_rover('B3', 'out'); up = Po['wing_in_stbd'][0]; rr = np.vstack([Po[k][0] for k in VA.ROVER_PARTS])
man = dict(status='NON-CANON lab model (kT "Rather go out the side", 2026-11-15)',
           concept='twin-sphere rover = crew cabin, exits through a starboard side door (option A of rover_trade 2026-11-03, rebuilt for v2)',
           door=dict(lower='lower flank panel hinged on the belly corner, folds down as a ramp', ramp_length_m=round(VA.LOW_L, 2),
                     ramp_angle_deg=round(float(np.degrees(np.arcsin((VA.BC_Z - VA.GROUND_Z) / VA.LOW_L))), 1),
                     upper='upper flank panel (the wing on B3/B4) hinged on the shoulder, swings up to horizontal as an awning',
                     opening_x_m=list(VA.DOOR_LOW_X), opening_z_m=[VA.BC_Z, VA.SH_Z], awning_underside_z_m=round(float(up[:, 2].min()), 2)),
           rover=dict(length_m=4.1, width_m_stowed=3.24, width_m_wheels_out=round(float(np.ptp(rr[:, 1])), 2), wheelbase_m=round(VA.WHEEL_X[1] - VA.WHEEL_X[0], 2),
                      wheels=f'4 x {2 * VA.WHEEL_R} m dia, crab-steer 90 deg', stowed_z_band_m=[-0.9, 1.05], ground_clearance_m=round(-0.90 - (-0.86) + VA.WHEEL_R, 2)),
           shuttle_legs=dict(count=4, belly_height_m=round(VA.BC_Z - VA.GROUND_Z, 2)),
           bay_fit_stowed_max_radius_m=round(float(np.max(np.hypot(allv[:, 1], allv[:, 2]))), 3), wheel_to_sphere_min_gap_m=round(gap, 3),
           wings_with_shoulder_hinge={v: dict(span_m=round(VA.wing_geom(v)[1], 2), added_area_m2=round(VA.wing_geom(v)[0], 1)) for v in ('B2', 'B3', 'B4')},
           mass_basis='rover_trade option A (inside, side door + ramp + own gear) is the v1 baseline: no rover-integration delta vs v1; v2 deltas are twin spheres +0.4 t and wings',
           open=['hatch trunk to the dorsal hatch must retract upward before the rover slides out', 'longerons above and below the 4.2 m side opening (shoulder and belly corner) carry hull bending',
                 'door seals through the entry heat shield on the lower flank', 'wing hinge on the shoulder must also be the door hinge (ground loads)', 'Venus-hot wheel/tyre material'])
json.dump(man, open(os.path.join(HERE, 'rover_manifest.json'), 'w'), indent=1); print(json.dumps(man, indent=1))
