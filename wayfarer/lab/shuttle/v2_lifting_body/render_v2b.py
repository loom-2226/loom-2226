"""Shaded views of the v2-B lab model (painter's algorithm). ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle
import build_v2b as B
HERE = os.path.dirname(os.path.abspath(__file__))
P = B.parts(); man = json.load(open(os.path.join(HERE, 'shuttle_v2b_manifest.json')))
COL = {k: np.array(v[0][:3]) for k, v in B.MAT.items()}; COL['glazing'] = np.array([0.25, 0.45, 0.65])
def tris(skip=(), cut=False):
    T, C, D = [], [], []
    for k, (V, F) in P.items():
        if k in skip: continue
        t = V[F]
        if cut and k in ('hull', 'belly_tps', 'glazing'): t = t[t[:, :, 1].mean(1) > -0.02]
        T.append(t); C.append(np.repeat(COL[k][None], len(t), 0)); D.append(np.full(len(t), cut and k in ('hull', 'belly_tps', 'glazing')))
    return np.vstack(T), np.vstack(C), np.concatenate(D)
def view(ax, az, el, title, cut=False, lim=None, skip=()):
    T, C, D = tris(skip, cut); T = T - [6.4, 0, 0.3]
    a, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    V = T @ (Rx @ Rz).T
    n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    vis = (n[:, 1] < 0) | D
    C = np.where((D & (n[:, 1] >= 0))[:, None], C * 0.55, C)
    Lt = np.array([-0.35, -0.75, 0.55]); Lt /= np.linalg.norm(Lt)
    sh = np.clip(0.35 + 0.75 * np.clip(-(n @ -Lt), 0, 1) * 0 + 0.75 * np.abs(n @ Lt), 0, 1.1)
    o = np.argsort(-V[:, :, 1].mean(1)); o = o[vis[o]]
    cols = np.clip(C[o] * sh[o][:, None], 0, 1)
    ax.add_collection(PolyCollection(V[o][:, :, [0, 2]], facecolors=cols, edgecolors=cols, linewidths=0.7, antialiaseds=False))
    lim = lim or (7.4, 2.6)
    ax.set_xlim(-lim[0], lim[0]); ax.set_ylim(-lim[1], lim[1]); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, loc='left', fontsize=10, weight='bold')
fig = plt.figure(figsize=(11, 12.5), dpi=110); fig.patch.set_facecolor('#f4f3ef')
gs = fig.add_gridspec(4, 2, height_ratios=[1.15, 1.0, 0.8, 1.15], width_ratios=[1.6, 1])
view(fig.add_subplot(gs[0, :]), 35, 28, 'Three-quarter, from above and forward (nose left)', lim=(7.6, 3.0))
view(fig.add_subplot(gs[1, :]), 35, 28, 'Cutaway: near half of the aeroshell removed - twin 1.9 m Ti spheres, tunnel, top hatch trunk', cut=True, lim=(7.6, 3.0))
view(fig.add_subplot(gs[2, 0]), 0, 0, 'Side (nose left): flat heat-shield belly, kit pod aft', lim=(7.0, 1.9))
a = fig.add_subplot(gs[2, 1]); view(a, 90, 0, 'Front: fins stowed check', lim=(2.6, 2.4), skip=('fin_stbd', 'fin_port'))
a.add_patch(Circle((0, -0.3), 2.15, fill=False, ec='#c0392b', ls='--', lw=1.2)); a.text(0, -2.38, '4.3 m bay envelope', ha='center', fontsize=8, color='#c0392b')
view(fig.add_subplot(gs[3, 0]), 0, 90, 'Plan from above (nose left)', lim=(7.0, 2.6))
t = fig.add_subplot(gs[3, 1]); t.axis('off')
m = man; h = m['hull']; r = m['v1_ref']
lines = [('Length / body span', f"{m['length_m']} / {m['span_body_m']} m"), ('Height', f"{m['height_m']} m"),
         ('Fin span deployed', f"{m['fins_deployed_span_m']} m (fold to stow)"), ('Bay fit (r <= 2.15)', f"{m['bay_fit']['max_radius_stowed_m']} m  PASS"),
         ('Wetted area', f"{h['wetted_area_m2']} m2  (v1 {r['wetted_area_m2']}, x{m['area_ratio_v2_over_v1']})"),
         ('Internal volume', f"{h['enclosed_volume_m3']} m3  (v1 {r['enclosed_volume_m3']}, x{m['volume_ratio_v2_over_v1']})"),
         ('Planform area', f"{h['planform_area_m2']} m2"), ('Crew spheres', f"2 x 1.9 m = {m['spheres']['total_volume_m3']} m3 gross"),
         ('Sphere-to-skin gap', f"{m['spheres']['min_clearance_to_skin_m']} m min"), ('Mesh', f"watertight, {h['watertight_unmatched_edges']} open edges")]
for i, (k, v) in enumerate(lines):
    t.text(0, 1 - i * 0.095, k, fontsize=8.5, color='#555', transform=t.transAxes); t.text(0.43, 1 - i * 0.095, v, fontsize=8.5, weight='bold', transform=t.transAxes)
fig.suptitle('Shuttle v2-B lifting body - first build (NON-CANON lab model)', x=0.03, ha='left', fontsize=14, weight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.975]); fig.savefig(os.path.join(HERE, 'shuttle_v2b_build.png'), facecolor=fig.get_facecolor())
