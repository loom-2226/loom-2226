"""3D sketch sheet: two nacelles vs four nacelles + aft ring. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(os.path.join(HERE, 'node_ring.json')))
BG, INK, MUTE = '#fcfcfb', '#0b0b0b', '#52514e'
COL = dict(hull=(.86, .87, .88), torch=(.62, .60, .57), fin=(.89, .45, .40), finst=(.70, .70, .70), nac=(.17, .47, .84), hoop=(.17, .47, .84), node=(.11, .69, .48))
def rev(prof, n=48):
    th = np.linspace(0, 2 * np.pi, n + 1); T = []
    for (x0, r0), (x1, r1) in zip(prof[:-1], prof[1:]):
        for a, b in zip(th[:-1], th[1:]):
            p = lambda x, r, t: (x, r * np.cos(t), r * np.sin(t))
            T += [[p(x0, r0, a), p(x1, r1, a), p(x1, r1, b)], [p(x0, r0, a), p(x1, r1, b), p(x0, r0, b)]]
    return np.array(T)
def cylinder(x0, x1, cy, cz, r, n=20):
    th = np.linspace(0, 2 * np.pi, n + 1); T = []
    for a, b in zip(th[:-1], th[1:]):
        A = lambda x, t: (x, cy + r * np.cos(t), cz + r * np.sin(t))
        T += [[A(x0, a), A(x1, a), A(x1, b)], [A(x0, a), A(x1, b), A(x0, b)], [(x0, cy, cz), A(x0, b), A(x0, a)], [(x1, cy, cz), A(x1, a), A(x1, b)]]
    return np.array(T)
def torus(x, Rr, r, n=72, m=10):
    u = np.linspace(0, 2 * np.pi, n + 1); v = np.linspace(0, 2 * np.pi, m + 1); T = []
    P = lambda a, b: (x + r * np.sin(b), (Rr + r * np.cos(b)) * np.cos(a), (Rr + r * np.cos(b)) * np.sin(a))
    for a0, a1 in zip(u[:-1], u[1:]):
        for b0, b1 in zip(v[:-1], v[1:]): T += [[P(a0, b0), P(a1, b0), P(a1, b1)], [P(a0, b0), P(a1, b1), P(a0, b1)]]
    return np.array(T)
def panel(az, x0, x1, r0, r1, t=0.12):
    a = math.radians(az); d = np.array([0, math.cos(a), math.sin(a)]); n = np.array([0, -math.sin(a), math.cos(a)]) * t / 2
    c = [np.array([x0, 0, 0]) + r0 * d, np.array([x1, 0, 0]) + r0 * d, np.array([x1, 0, 0]) + r1 * d, np.array([x0, 0, 0]) + r1 * d]
    q1 = [p + n for p in c]; q2 = [p - n for p in c]
    return np.array([[q1[0], q1[1], q1[2]], [q1[0], q1[2], q1[3]], [q2[0], q2[2], q2[1]], [q2[0], q2[3], q2[2]]])
def octa(p, s=.34):
    p = np.array(p); e = [np.array(v) * s for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
    F = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    return np.array([[p + e[i], p + e[j], p + e[k]] for i, j, k in F])
HULLP = [(-0.3, 0.01), (0.2, 2.6), (1.2, 3.8), (3, 4.5), (34.3, 4.5), (39.3, 2.95)]
TORCH = [(39.3, 2.95), (39.3, 2.125), (46.3, 2.125), (53.3, 3.0), (53.31, 0.01)]
def scene(n_nac, hoop, deployed, nodes):
    parts = [(rev(HULLP), 'hull'), (rev(TORCH), 'torch')]
    for s in (40, 140, 220, 320):
        parts.append((panel(s, 34.3, 53.3, 4.75, 6.75) if not deployed else panel(s, 34.3, 53.3, 4.75, 5.05), 'fin' if not deployed else 'finst'))
    r = 4.6 if deployed else 3.4
    for az in ([0, 180] if n_nac == 2 else [0, 90, 180, 270]):
        a = math.radians(az); parts.append((cylinder(39.5, 53.5, r * math.cos(a), r * math.sin(a), .6), 'nac'))
    if hoop and deployed: parts.append((torus(52.6, 4.4, .35), 'hoop'))
    if deployed:
        for p in nodes:
            if p[0] > 34.3: parts.append((octa(p), 'node'))
    return parts
def render(ax, parts, az=-38, el=24, title=''):
    T = np.concatenate([p for p, _ in parts]); C = np.concatenate([[COL[k]] * len(p) for p, k in parts])
    T = T - [41, 0, 0]; a, e = math.radians(az), math.radians(el)
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
    V = T @ (Rx @ Rz).T; n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); nn = np.linalg.norm(n, axis=1)[:, None] + 1e-12; n = n / nn
    Lt = np.array([-.3, -.6, .75]); Lt /= np.linalg.norm(Lt); sh = np.clip(.38 + .7 * np.abs(n @ Lt), 0, 1.08)
    o = np.argsort(-V[:, :, 1].mean(1)); cols = np.clip(C[o] * sh[o][:, None], 0, 1)
    ax.add_collection(PolyCollection(V[o][:, :, [0, 2]], facecolors=cols, edgecolors=cols, linewidths=.4))
    ax.set_xlim(-17, 17); ax.set_ylim(-10, 10); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, loc='left', fontsize=11, weight='bold')
fig = plt.figure(figsize=(11, 12.5), dpi=110); fig.patch.set_facecolor(BG)
fig.text(.03, .975, 'Two nacelles, or four that lock into a ring (sketches, not canon)', fontsize=15, weight='bold')
fig.text(.03, .955, 'Rear three-quarter view of the aft half. Left: burning the torch (nacelles folded in, hot fins out). Right: Metric or Loom (torch cold, fins stowed, nacelles out, nodes green).', fontsize=9.2, color=MUTE)
cases = [('two_nacelles', 2, False, 'A  Two nacelles'), ('four_nacelles_ring', 4, True, 'B  Four nacelles that lock into an aft ring')]
for i, (k, nn_, hp, lab) in enumerate(cases):
    nodes = R['options'][k]['nodes']
    for j, dep in enumerate((False, True)):
        ax = fig.add_axes([.02 + j * .49, .58 - i * .37, .47, .33]); ax.set_facecolor(BG)
        render(ax, scene(nn_, hp, dep, nodes), title=f"{lab}: {'jumping' if dep else 'burning'}")
# metrics
ax = fig.add_axes([.03, .03, .94, .2]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
A, B = R['options']['two_nacelles']['metrics'], R['options']['four_nacelles_ring']['metrics']
rows = [('', 'A  Two nacelles', 'B  Four + ring'),
        ('Worst gap to a node', f"{A['max_gap_m']:.1f} m", f"{B['max_gap_m']:.1f} m"),
        ('Typical gap (95% of skin within)', f"{A['p95_gap_m']:.1f} m", f"{B['p95_gap_m']:.1f} m"),
        ('Evenness (lower is better; today 0.29)', f"{A['load_cv']:.2f}", f"{B['load_cv']:.2f}"),
        ('Rear nodes per quarter (stbd, top, port, bottom)', ' / '.join(map(str, A['aft_quadrant_counts'])), ' / '.join(map(str, B['aft_quadrant_counts']))),
        ('Extra structure (rough)', '3-6 t', '8-14 t')]
for r_, row in enumerate(rows):
    y = .95 - r_ * .16
    for x, v in zip((0, .55, .8), row): ax.text(x, y, v, fontsize=9.6, va='top', ha='left' if x == 0 else 'center', weight='bold' if r_ == 0 else None, color=INK if (r_ == 0 or x == 0) else MUTE)
fig.savefig(os.path.join(HERE, 'node_ring.png'), facecolor=BG)
