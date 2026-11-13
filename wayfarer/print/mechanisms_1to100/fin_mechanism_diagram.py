"""Wayfarer 1:100 plug-in hot fins + strakes (Claude, 13 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
kT 2026-11-13: no hinges; swappable plug-in fin sets. Canon facts: SPEC.md layout table; finish rows 14-17; geometry parts."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
INK, MUT, ACC, HOT, GRN = '#1d2228', '#6b737c', '#2f6f8f', '#d9773a', '#3f8f5a'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig = plt.figure(figsize=(13, 14), dpi=110); fig.patch.set_facecolor('#f6f5f2')
fig.text(0.04, 0.973, 'Wayfarer 1:100: plug-in hot fins and strakes (no hinges)', fontsize=19, weight='bold', color=INK)
fig.text(0.04, 0.955, 'kT 13 Nov: swap whole fin sets instead of folding them. 1 mm on the model = 100 mm real. Bambu A2L, bed 330 x 320 mm.', fontsize=11, color=MUT)

# A: the two fin sets, end view
ax = fig.add_axes([0.04, 0.56, 0.44, 0.36]); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('A  Two hot-fin sets, same sockets (end view)', loc='left', fontsize=12, weight='bold', color=INK)
for cx, dep, lab in ((-170, False, 'FOLDED set (stowed, Metric)\ndisplay default, 135 mm across'), (170, True, 'DEPLOYED set (torch burn)\n655 mm across')):
    ax.add_patch(Circle((cx, 0), 45 * 0.55, fc='#dfe2e0', ec=INK))
    for a in (40, 140, 220, 320):
        t = np.radians(a); u = np.array([np.cos(t), np.sin(t)]); v = np.array([-u[1], u[0]])
        r0 = 47.5 * 0.55; L = (280 if dep else 20) * 0.55; w = (1.6 if dep else 6) * 0.55
        p = np.array([cx, 0]) + u * r0
        poly = [p + v * w / 2, p + v * w / 2 + u * L, p - v * w / 2 + u * L, p - v * w / 2]
        ax.add_patch(plt.Polygon(poly, fc=HOT if dep else '#2b2d2f', ec='none'))
    ax.text(cx, -175, lab, ha='center', fontsize=10, weight='bold', color=INK)
ax.text(-170, 60, 'scale 0.55x', ha='center', fontsize=8, color=MUT)
ax.set_xlim(-330, 330); ax.set_ylim(-200, 175)

# B: the two parts
ax = fig.add_axes([0.53, 0.56, 0.44, 0.36]); ax.axis('off'); ax.set_aspect('equal')
ax.set_title('B  One fin, both versions (printed flat)', loc='left', fontsize=12, weight='bold', color=INK)
ax.add_patch(Rectangle((0, 120), 190, 20, fc='#2b2d2f', ec=INK))
for k in range(1, 14): ax.plot([0, 190], [120 + 20 * 0 + 0, 120], color='none')
ax.text(0, 145, 'FOLDED: solid stack 190 x 20 x 6 mm (true scale)\n14 pleat edges engraved on the side faces', fontsize=9.5, color=INK, va='bottom')
ax.add_patch(Rectangle((0, -170), 190, 280 * 0.9, fc='#3a3436', ec=INK))
for k in range(1, 14): ax.plot([0, 190], [-170 + k * 20 * 0.9] * 2, color='#8a7f7a', lw=0.8)
for x in np.arange(0, 190, 5): ax.plot([x, x], [-170, -170 + 280 * 0.9], color='#4d4547', lw=0.4)
ax.text(200, -60, 'DEPLOYED: panel 190 x 280 x 1.6 mm\npleat lines every 20 mm (13)\nheat-pipe channels every 5 mm\n(the approved 0.5 m channels)', fontsize=9.5, color=INK)
for y0 in (118, -172):
    ax.add_patch(Rectangle((10, y0 - 4), 170, 4, fc=ACC, ec='none'))
    for px in (40, 150): ax.add_patch(Rectangle((px - 0.9, y0 - 9), 1.8, 5, fc=GRN, ec='none'))
ax.text(200, 108, 'root bar + 2 pegs\n(same on both)', fontsize=9, color=ACC)
ax.set_xlim(-10, 330); ax.set_ylim(-190, 175)

# C: socket detail
ax = fig.add_axes([0.04, 0.29, 0.44, 0.24]); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('C  Socket detail (section across the root, enlarged 8x)', loc='left', fontsize=12, weight='bold', color=INK)
ax.add_patch(Rectangle((-2, -10), 4, 10, fc='#cfd3d1', ec=INK)); ax.text(-3, -6, 'fin root on ship\n(thickened 3 to 4 mm)', ha='right', fontsize=9, color=MUT)
ax.add_patch(Rectangle((-0.95, -6), 1.9, 6, fc='white', ec=INK, lw=0.6))
ax.add_patch(Rectangle((-0.875, -5.8), 1.75, 7, fc=GRN, ec='none')); ax.add_patch(Rectangle((-2, 1.2), 4, 3, fc=ACC, ec=INK))
ax.add_patch(Rectangle((-0.8, 4.2), 1.6, 10, fc='#3a3436', ec=INK))
ax.annotate('1.75 mm filament peg (cut offcut),\nfriction fit in a 1.9 mm hole', xy=(0.6, -3), xytext=(4, -8), fontsize=9.5, arrowprops=dict(arrowstyle='->', color=INK))
ax.annotate('root bar 4 x 3 mm on the fin', xy=(2, 2.7), xytext=(5, 2.5), fontsize=9.5, arrowprops=dict(arrowstyle='->', color=INK))
ax.annotate('fin (folded stack or\ndeployed panel)', xy=(0.8, 10), xytext=(5, 9), fontsize=9.5, arrowprops=dict(arrowstyle='->', color=INK))
ax.set_xlim(-20, 25); ax.set_ylim(-12, 15)

# D: strakes
ax = fig.add_axes([0.53, 0.29, 0.44, 0.24]); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('D  Strakes: three sets of four, same socket', loc='left', fontsize=12, weight='bold', color=INK)
for i, (h, lab) in enumerate(((2, 'Loom 0 m\nflush bay cover'), (20, 'Metric 2 m\n20 mm accordion block'), (40, 'Torch 4 m\n40 mm panel'))):
    x = i * 60; ax.add_patch(Rectangle((x - 10, 0), 20, 4, fc='#dfe2e0', ec=INK))
    ax.add_patch(Rectangle((x - 1.5, 4), 3, h, fc='#292d30', ec=INK)); ax.text(x, 52, lab, ha='center', fontsize=9.5, weight='bold', color=INK)
ax.text(-12, -8, 'Each strake 183 mm long. Pleat lines engraved on the 2 m block.', fontsize=9.5, color=INK)
ax.set_xlim(-20, 150); ax.set_ylim(-12, 66)

# E: parts + decision
ax = fig.add_axes([0.04, 0.03, 0.92, 0.23]); ax.axis('off')
ax.set_title('E  Parts list and the one choice left', loc='left', fontsize=12, weight='bold', color=INK)
txt = ('Parts:  4 folded fins + 4 deployed fins + 12 strakes (3 sets) = 20 plug-in parts. Pegs: 40 short filament offcuts (free).\n'
       'Each deployed fin prints flat (190 x 280 mm) on the 330 x 320 bed; everything else is small.\n'
       'Hot-fin glow, colours and heat-pipe channels follow the approved finish (rows 14-17) and 2/2/2.\n\n'
       'Choice:  pegs (friction, nothing to buy)  or  tiny 3 x 1 mm magnets (snap in, buy 40).\n'
       'Claude: pegs. Try them on the test print; switch to magnets only if a fin works loose.\n\n'
       'Declared print exaggerations: deployed panel 1.6 mm (true pleat 0.43 mm); root bar 4 mm (true root edge 3 mm).')
ax.text(0, 0.92, txt, fontsize=10.5, va='top', color=INK, linespacing=1.5)
fig.savefig('fin_mechanism_1to100.png', facecolor=fig.get_facecolor()); print('ok')
