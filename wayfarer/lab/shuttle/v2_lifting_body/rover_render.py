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
T = {'flight': 'In the bay / entry: rover is the crew cabin, wings folded, wheels stowed above the belly panel',
     'landed': 'Landed: rover wheels are the main gear (4 x 0.9 m); shuttle sits on its own rover',
     'out': 'Rover out: four jack legs lift the shuttle 2.15 m, the rover drives out aft with its belly-panel floor'}
for i, st in enumerate(('flight', 'landed', 'out')):
    P = VA.model_rover('B3', st)
    Pv = P if st == 'out' else {k: v for k, v in P.items() if k.startswith(('hull', 'belly', 'glazing', 'kit', 'fin', 'body', 'torch', 'wing')) or (st == 'landed' and k.startswith(('wheel', 'strut')))}
    view(ax[i], Pv, 32, 18, T[st], lim=(12.4 if st == 'out' else 8.2, 4.3 if st == 'out' else 3.0))
    if st == 'out': ax[i].plot([-12, 14], [VA.GROUND_Z - 0.3 - 0.2, VA.GROUND_Z - 0.3 - 0.2], alpha=0)
    for v in ('B2', 'B3', 'B4'):
        if st == 'flight': continue
        B.write_glb(VA.model_rover(v, st), os.path.join(HERE, 'viewer', 'glb', f'_t.glb'))
        json.dump({'b64': base64.b64encode(open(os.path.join(HERE, 'viewer', 'glb', '_t.glb'), 'rb').read()).decode()},
                  open(os.path.join(HERE, 'viewer', 'glb', f'{v}_{st}.json'), 'w'))
os.remove(os.path.join(HERE, 'viewer', 'glb', '_t.glb'))
fig.suptitle('Shuttle v2-B3 with the twin-sphere belly rover (NON-CANON lab model)', x=0.03, ha='left', fontsize=13, weight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(HERE, 'rover_states.png'), facecolor=fig.get_facecolor())
# manifest
P = VA.model_rover('B3', 'flight'); skip = ('sphere_stbd', 'sphere_port', 'tunnel', 'hatch_trunk')
allv = np.vstack([P[k][0] for k in P if k not in skip])
gap = min(float(np.min(np.linalg.norm(P[k][0] - [B.SPH_X, s * B.SPH_Y, B.SPH_Z], axis=1)) - B.SPH_R) for k in P if k.startswith('wheel') for s in (1, -1))
man = dict(status='NON-CANON lab model (kT "Sure", 2026-11-14)', concept='twin-sphere belly rover = crew cabin; option C of rover_trade 2026-11-03 rebuilt for v2',
           rover=dict(length_m=4.4, width_m=3.4, track_m=round(2 * (VA.WHEEL_Y + 0.07 + VA.WHEEL_W / 2 + 0.02), 2), wheelbase_m=round(VA.WHEEL_X[1] - VA.WHEEL_X[0], 2),
                      wheels=f'4 x {2 * VA.WHEEL_R} m dia x {VA.WHEEL_W} m', ground_clearance_m=round(-0.965 - VA.GROUND_Z, 2), height_m=round(1.05 - VA.GROUND_Z, 2)),
           bay_fit_stowed_max_radius_m=round(float(np.max(np.hypot(allv[:, 1], allv[:, 2]))), 3), wheel_to_sphere_min_gap_m=round(gap, 3),
           jack_lift_m=2.15, jack_legs=4, volume_taken_by_wheels_m3=round(4 * np.pi * VA.WHEEL_R ** 2 * VA.WHEEL_W, 2),
           mass_basis='rover_trade C vs A, 3 crew: ~+0.7 t core dry at midpoint; taller jack legs than the trade assumed (OPEN)',
           open=['TPS seam around the 4.4 x 3.7 m belly panel through the entry heat shield', 'jack-leg mass for 2.15 m lift',
                 'internal access to torch/kit while the rover is out', 'ascent re-dock alignment', 'Venus-hot wheel/tyre material'])
json.dump(man, open(os.path.join(HERE, 'rover_manifest.json'), 'w'), indent=1); print(json.dumps(man, indent=1))
