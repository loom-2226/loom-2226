"""Views of B2/B3/B4, wings stowed and deployed; writes per-variant GLBs. ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import build_v2b as B, variants as VA
HERE = os.path.dirname(os.path.abspath(__file__))
COL = {k: np.array(v[0][:3]) for k, v in B.MAT.items()}; COL['glazing'] = np.array([0.25, 0.45, 0.65])
SUB = ('hull', 'belly_tps', 'glazing', 'kit_pod', 'fin_stbd', 'fin_port', 'body_flap')
def view(ax, P, az, el, title, lim=(7.6, 3.4)):
    T, C = [], []
    for k, (V, F) in P.items():
        t = V[F]
        if k in SUB or k.startswith('wing'):
            for _ in range(2):
                a, b, c = t[:, 0], t[:, 1], t[:, 2]; ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
                t = np.concatenate([np.stack(q, 1) for q in ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))])
        T.append(t); C.append(np.repeat(COL[k][None], len(t), 0))
    T = np.vstack(T) - [6.4, 0, 0.3]; C = np.vstack(C)
    a_, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a_), -np.sin(a_), 0], [np.sin(a_), np.cos(a_), 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    V = T @ (Rx @ Rz).T; n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    Lt = np.array([-0.35, -0.75, 0.55]); Lt /= np.linalg.norm(Lt); sh = np.clip(0.35 + 0.75 * np.abs(n @ Lt), 0, 1.1)
    o = np.argsort(-V[:, :, 1].mean(1)); o = o[(n[:, 1] < 0)[o]]
    cols = np.clip(C[o] * sh[o][:, None], 0, 1)
    ax.add_collection(PolyCollection(V[o][:, :, [0, 2]], facecolors=cols, edgecolors=cols, linewidths=0.7, antialiaseds=False))
    ax.set_xlim(-lim[0], lim[0]); ax.set_ylim(-lim[1], lim[1]); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, loc='left', fontsize=10, weight='bold')
R = json.load(open(os.path.join(HERE, 'aero_results.json')))
fig, ax = plt.subplots(3, 2, figsize=(11, 10.5), dpi=110); fig.patch.set_facecolor('#f4f3ef')
names = {'B2': 'B2 angular', 'B3': 'B3 fold wing', 'B4': 'B4 double fold'}
for i, v in enumerate(('B2', 'B3', 'B4')):
    A, s = VA.wing_geom(v); l = R['landing']['Venus'][names[v]]
    view(ax[i, 0], VA.model(v, False), 35, 28, f'{names[v]} - stowed (entry / bay)')
    view(ax[i, 1], VA.model(v, True), 25, 48, f'deployed: span {s:.1f} m, +{A:.0f} m2, glide L/D {l["LDmax"]:.1f}', lim=(8.2, 4.4))
    for st, P in (('stowed', VA.model(v, False)), ('deployed', VA.model(v, True))):
        if v == 'B2' and st == 'stowed': continue
        B.write_glb(P, os.path.join(HERE, 'viewer', 'glb', f'_tmp_{v}_{st}.glb'))
fig.suptitle('Shuttle v2 fold-out iterations - wings are the flank skin, hinged on the chine (NON-CANON)', x=0.03, ha='left', fontsize=13, weight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(HERE, 'variants_views.png'), facecolor=fig.get_facecolor())
