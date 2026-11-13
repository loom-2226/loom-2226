"""Wayfarer 1:100 deployable hot fin + strake mechanism diagram (Claude, 13 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
PROPOSAL (F4): sketch + numbers. Canon facts: SPEC.md layout table; finish table rows 14-17; geometry parts strake_*/hotfin_*."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch, Polygon
INK, MUT, ACC, HOT, GRN = '#1d2228', '#6b737c', '#2f6f8f', '#d9773a', '#3f8f5a'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig = plt.figure(figsize=(13, 15), dpi=110); fig.patch.set_facecolor('#f6f5f2')
fig.text(0.04, 0.975, 'Wayfarer 1:100: deployable hot fins and strakes', fontsize=19, weight='bold', color=INK)
fig.text(0.04, 0.957, 'PROPOSAL, sketch + numbers. 1 mm on the model = 100 mm real. Printer: Bambu A2L, bed 330 x 320 mm.', fontsize=11, color=MUT)

# ---- A: end view, why this is hard ----
ax = fig.add_axes([0.04, 0.60, 0.44, 0.33]); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('A  End view at 1:100 (looking forward from the nozzle)', loc='left', fontsize=12, weight='bold', color=INK)
ax.add_patch(Circle((0, 0), 45, fc='#dfe2e0', ec=INK, lw=1.2)); ax.text(0, 0, 'hull\n90 mm', ha='center', va='center', color=MUT, fontsize=9)
for a in (40, 140, 220, 320):
    t = np.radians(a); u = np.array([np.cos(t), np.sin(t)])
    p0 = u * 47.5; p1 = u * (47.5 + 280)
    ax.plot(*zip(p0, p1), color=HOT, lw=2.4, solid_capstyle='butt')
    q0 = u * 47.5; q1 = u * (47.5 + 6)
    ax.plot(*zip(q0, q1), color=INK, lw=6, solid_capstyle='butt')
ax.add_patch(Rectangle((-165, -160), 330, 320, fill=False, ec=ACC, lw=1.2, ls='--'))
ax.text(-163, 152, 'printer bed 330 x 320', color=ACC, fontsize=9)
ax.set_xlim(-340, 340); ax.set_ylim(-300, 300)
ax.text(0, -285, 'Deployed span 655 mm tip to tip; ship is 540 mm long.\nFolded stack at true scale: 6 mm.  One pleat at true scale: 0.43 mm thick (too thin to print).',
        ha='center', fontsize=9.5, color=INK)
ax.text(190, 200, 'deployed fin\n280 mm', color=HOT, fontsize=10, weight='bold'); ax.text(60, 22, 'folded 6 mm', color=INK, fontsize=9)

# ---- B: accordion fold sequence ----
ax = fig.add_axes([0.53, 0.60, 0.44, 0.33]); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('B  How a fin unfolds (section across the fin, 14 pleats)', loc='left', fontsize=12, weight='bold', color=INK)
def zig(ax, x0, y0, n, w, ang, col):
    pts = [(x0, y0)]
    for k in range(n):
        s = 1 if k % 2 == 0 else -1; th = np.radians(90 - ang) * s
        x, y = pts[-1]; pts.append((x + w * np.cos(np.radians(ang)) , y + s * w * np.sin(np.radians(ang))))
    pts = np.array(pts); ax.plot(pts[:, 0], pts[:, 1], color=col, lw=2.2)
    ax.plot(pts[1:-1, 0], pts[1:-1, 1], 'o', ms=3.2, mfc='white', mec=INK, mew=0.9)
    return pts
for i, (ang, lab) in enumerate(((88, 'Folded (stowed, Metric)'), (45, 'Unfolding'), (0, 'Deployed: torch burn, 280 mm'))):
    y = 140 - i * 110
    ax.add_patch(Rectangle((-10, y - 12), 10, 24, fc='#cfd3d1', ec=INK)); ax.text(-12, y, 'root', ha='right', va='center', fontsize=8.5, color=MUT)
    zig(ax, 0, y, 14, 20, ang, HOT if ang == 0 else INK)
    ax.text(0, y + 26, lab, fontsize=10, color=INK, weight='bold')
ax.set_xlim(-40, 300); ax.set_ylim(-160, 190)
ax.text(0, -150, 'Each pleat 20 mm wide x 190 mm long.\n13 hinge lines run the full fin length\n(along the ship), alternating edge to edge\nlike a paper fan.', fontsize=9.5, color=INK)

# ---- C: hinge detail ----
ax = fig.add_axes([0.04, 0.30, 0.44, 0.26]); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('C  Hinge detail, recommended (enlarged 10x)', loc='left', fontsize=12, weight='bold', color=INK)
ax.add_patch(Rectangle((-30, -0.6), 28.8, 1.2, fc='#3b3f43', ec=INK)); ax.add_patch(Rectangle((1.2, -0.6), 28.8, 1.2, fc='#3b3f43', ec=INK))
ax.add_patch(Circle((0, 0), 1.2, fc='#8a8f94', ec=INK, lw=1)); ax.add_patch(Circle((0, 0), 0.65, fc='white', ec=INK, lw=0.6)); ax.add_patch(Circle((0, 0), 0.5, fc='#5b6066', ec='none'))
ax.annotate('1.0 mm steel pin (piano wire),\nruns the full 190 mm fin length', xy=(0.3, 0.3), xytext=(6, 6), fontsize=9.5, arrowprops=dict(arrowstyle='->', color=INK))
ax.annotate('knuckle 2.4 mm OD,\n0.15 mm clearance = friction hold', xy=(-1.0, -0.9), xytext=(-29, -7), fontsize=9.5, arrowprops=dict(arrowstyle='->', color=INK))
ax.annotate('pleat 1.2 mm thick', xy=(18, 0.6), xytext=(12, 4), fontsize=9.5, arrowprops=dict(arrowstyle='->', color=INK))
ax.annotate('180 deg hard stop: pleat ends butt\nwhen flat, so fins cannot over-bend', xy=(1.25, 0), xytext=(4, -7), fontsize=9.5, color=GRN, arrowprops=dict(arrowstyle='->', color=GRN))
ax.set_xlim(-32, 32); ax.set_ylim(-11, 10)

# ---- D: strakes ----
ax = fig.add_axes([0.53, 0.30, 0.44, 0.26]); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('D  Strakes: same hinge, 4 pleats, three set positions', loc='left', fontsize=12, weight='bold', color=INK)
for i, (phi, lab) in enumerate(((88, 'Loom 0 m: folded in its bay'), (60, 'Metric 2 m = 20 mm'), (0, 'Torch 4 m = 40 mm'))):
    x = i * 70
    ax.add_patch(Rectangle((x - 8, 0), 16, 5, fc='#dfe2e0', ec=INK)); ax.text(x, -6, 'hull', ha='center', fontsize=8.5, color=MUT)
    pts = [(x, 5)]
    for k in range(4):
        sg = 1 if k % 2 == 0 else -1; xx, yy = pts[-1]
        pts.append((xx + sg * 10 * np.sin(np.radians(phi)), yy + max(10 * np.cos(np.radians(phi)), 0.9)))
    pts = np.array(pts); ax.plot(pts[:, 0], pts[:, 1], color='#b5552a' if phi == 0 else INK, lw=2.2); ax.plot(pts[1:-1, 0], pts[1:-1, 1], 'o', ms=3, mfc='white', mec=INK)
    ax.text(x, 50, lab, ha='center', fontsize=9.5, weight='bold', color=INK)
ax.set_xlim(-25, 165); ax.set_ylim(-14, 60)
ax.text(-20, -13, 'Pleats 10 mm x 183 mm. Friction holds the 2 m (20 mm) position.', fontsize=9.5, color=INK)

# ---- E: the decisions ----
ax = fig.add_axes([0.04, 0.03, 0.92, 0.24]); ax.axis('off')
ax.set_title('E  What kT decides', loc='left', fontsize=12, weight='bold', color=INK)
rows = [('1  Pleat count', '14 pleats (true to canon)\nfolded stack 17.5 mm (3x scale)', '7 double pleats\nfolded stack 9 mm, pleats 40 mm wide', 'Claude: 14. The count is the\ncanon look; the thicker stack is a\ndeclared print exaggeration.'),
        ('2  How fins hold position', 'Friction pins + 180 deg stop\n(nothing to buy)', 'Plus 2 x 1 mm magnets in the\npleat edges (crisp click to flat)', 'Claude: friction first; add magnets\nonly if the test hinge sags.'),
        ('3  Pins', '1.0 mm steel piano wire\n(buy one rod)', '1.75 mm filament offcuts\n(free; stack grows to ~25 mm)', 'Claude: steel. Thinner, and it\nnever wears loose.')]
xs = [0.0, 0.22, 0.47, 0.72]
for j, h in enumerate(('', 'Option A', 'Option B', 'Recommendation')): ax.text(xs[j], 0.97, h, fontsize=10.5, weight='bold', color=ACC, va='top')
for i, r in enumerate(rows):
    y = 0.80 - i * 0.29
    for j, c in enumerate(r): ax.text(xs[j], y, c, fontsize=10, va='top', color=INK, weight='bold' if j == 0 else 'normal')
fig.savefig('fin_mechanism_1to100.png', facecolor=fig.get_facecolor()); print('ok')
