"""Check views of the B4-S lab model (x-ray: hull hidden). NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import build_v2b as B, build_b4s as S, variants_render as VR
VR.COL.update({k: np.array(v[0][:3]) for k, v in B.MAT.items() if k not in VR.COL})
HERE = os.path.dirname(os.path.abspath(__file__))
SKIN = ('hull', 'belly_tps', 'glazing', 'wing_in_', 'wing_out_', 'door_ramp', 'kit_pod', 'body_flap')
fig, ax = plt.subplots(3, 1, figsize=(10, 12), dpi=110); fig.patch.set_facecolor('#f4f3ef')
cases = [('flight', 'Standard, x-ray: 6-seat cabin + light rover at the back', True, 32, 18, (7.6, 3.4)),
         ('venus', 'Venus kit, x-ray: Ti capsule on the same chassis', True, 32, 18, (7.6, 3.4)),
         ('rover_std', 'Standard rover out on the ramp side', False, 148, 24, (9.0, 4.6))]
for a, (st, t, xray, az, el, lim) in zip(ax, cases):
    P = S.shuttle(st)
    if xray: P = {k: v for k, v in P.items() if not k.startswith(SKIN)}
    VR.view(a, P, az, el, t, lim=lim)
fig.tight_layout(); fig.savefig(os.path.join(HERE, 'b4s_views.png'), facecolor=fig.get_facecolor())
