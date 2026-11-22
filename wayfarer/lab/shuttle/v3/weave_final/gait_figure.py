"""Gait test figure: where she goes for a given hull configuration loop. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import gait_test as G
H = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(H, 'gait_test.json')))
INK = '#1f2933'; MUT = '#6b7280'; SH = '#2563eb'; WARN = '#d97706'; OK = '#16a34a'; PUR = '#7c3aed'
plt.rcParams.update({'font.size': 9.5, 'axes.edgecolor': MUT, 'axes.spines.top': False, 'axes.spines.right': False, 'xtick.color': MUT, 'ytick.color': MUT})
def trace(A, segs, dt=2e-3):
    X = np.zeros(2); th = 0.0; P = [X.copy()]; TH = [0.0]
    for q, qd, T in segs:
        for i in range(max(1, int(T / dt))):
            t = i * dt; Ax, Ay, Ath = A(q(t)); qv = qd(t); Vb = np.array([Ax @ qv, Ay @ qv]); c, s = math.cos(th), math.sin(th)
            X = X + dt * np.array([c * Vb[0] - s * Vb[1], s * Vb[0] + c * Vb[1]]); th += dt * (Ath @ qv); P.append(X.copy()); TH.append(th)
    return np.array(P), np.array(TH)
f = plt.figure(figsize=(13, 9.4)); f.suptitle('Gait test: the Weave as a swimmer (one hypothesis: field set by how fast the hull configuration changes)', x=0.02, ha='left', y=0.985, color=INK, fontsize=12.5)
f.text(0.02, 0.948, 'Lane field and motion law unchanged. Flat connection = joystick on a leash; curved connection = gaits. Every case ends with no lasting speed.', color=MUT, fontsize=9.5)
a = f.add_axes([0.05, 0.55, 0.2, 0.32]); sq = np.array(G.SQUARE); a.plot(sq[:, 0], sq[:, 1], color=INK, lw=2); a.annotate('', xy=(0.6, 0), xytext=(0.3, 0), arrowprops=dict(arrowstyle='->', color=INK))
a.set_xlim(-0.3, 1.3); a.set_ylim(-0.3, 1.3); a.set_aspect('equal'); a.set_xlabel('hull mode q1'); a.set_ylabel('hull mode q2'); a.set_title('one gait: a loop of hull configuration', loc='left', fontsize=9.5)
b = f.add_axes([0.32, 0.55, 0.3, 0.32])
for A, col, lab in ((G.A_flat(15), MUT, 'flat: back where she started, every time'), (G.A_curved_trans(15, 7.5), SH, 'curved: +7.5 m per loop, ratchets on')):
    P, _ = trace(A, G.path(G.SQUARE, 1.0) * 4); b.plot(P[:, 0], P[:, 1], color=col, lw=1.4, label=lab)
b.plot(0, 0, 'ko', ms=4); b.set_aspect('equal'); b.set_xlabel('x (m)'); b.set_ylabel('y (m)'); b.legend(frameon=False, fontsize=8.5, loc='upper left'); b.set_title('four loops', loc='left', fontsize=9.5)
c = f.add_axes([0.68, 0.55, 0.3, 0.32])
for pts, col, lab in (([(0, 0), (1, 0), (1, 1)], SH, 'mode 1 then mode 2'), ([(0, 0), (0, 1), (1, 1)], WARN, 'mode 2 then mode 1')):
    P, _ = trace(G.A_curved_trans(15, 7.5), G.path(pts, 1.0)); c.plot(P[:, 0], P[:, 1], color=col, lw=1.8, label=f'{lab}: ends x {P[-1, 0]:.2f} m')
c.set_aspect('equal'); c.set_xlabel('x (m)'); c.set_ylabel('y (m)'); c.legend(frameon=False, fontsize=8.5, loc='upper left'); c.set_title('same final configuration, different place (route memory)', loc='left', fontsize=9.5)
d = f.add_axes([0.05, 0.08, 0.42, 0.36]); both = G.A_both(15, 7.5, math.radians(30)); lq = [(0, 0), (-1, 0), (-1, -1), (0, -1), (0, 0)]
for segs, col, lab in ((G.path(G.SQUARE, 1.0) + G.path(lq, 1.0), SH, 'translation gait, then attitude gait'), (G.path(lq, 1.0) + G.path(G.SQUARE, 1.0), PUR, 'attitude gait, then translation gait')):
    P, TH = trace(both, segs); d.plot(P[:, 0], P[:, 1], color=col, lw=1.6, label=lab)
    for j in range(0, len(P), max(1, len(P) // 7)): d.annotate('', xy=(P[j, 0] + 2.2 * math.cos(TH[j]), P[j, 1] + 2.2 * math.sin(TH[j])), xytext=(P[j, 0], P[j, 1]), arrowprops=dict(arrowstyle='->', color=col, lw=0.8))
d.set_aspect('equal'); d.set_xlabel('x (m)'); d.set_ylabel('y (m)'); d.legend(frameon=False, fontsize=8.5, loc='upper left'); d.set_title('order matters (arrows: her nose); both turn her 60 deg and stop', loc='left', fontsize=9.5)
t = f.add_axes([0.53, 0.06, 0.45, 0.4]); t.axis('off'); import textwrap
lines = ['• Flat connection: a joystick on a leash. Bounded hull configuration, bounded reach.', '• Curved connection: displacement = curvature × loop area; reversed loop goes back; 10× slower gives the same 7.5 m (only the path counts).',
         '• Route memory: two routes to the same configuration end 7.5 m apart.', '• Attitude: a curved attitude connection turns her 30° per loop and leaves her not spinning: the falling cat. No conserved quantity changes.',
         '• Translation by gait still shifts the boost charge: an external partner is still needed (R4).', '• Never lasting speed: orbit and velocity matching are not gaits.',
         '', 'STRUCTURAL RESULT: with a bounded hull configuration, unbounded travel REQUIRES a curved connection.', '', 'NOT DETERMINED: whether the Builder connection is curved, how strongly, and how it depends on the environment. The field model does not constrain it: that is the single quantity to grant or refuse.']
y = 0.98
for ln in lines:
    for w in textwrap.wrap(ln, 78) or ['']: t.text(0, y, w, fontsize=9, color=INK if not ln.startswith(('STRUCT', 'NOT')) else (OK if ln.startswith('STRUCT') else WARN), weight='bold' if ln.startswith(('STRUCT', 'NOT')) else 'normal', transform=t.transAxes); y -= 0.058
f.savefig(os.path.join(H, 'weave_gait_test.png'), dpi=150, facecolor='white')
