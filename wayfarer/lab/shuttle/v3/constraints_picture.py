"""Shuttle v3 fit envelope in Wayfarer's bay, read from source. ALL bodies. ALL sponsors. 2026-2226."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, '..', '..', '..')
I = json.load(open(os.path.join(W, 'config', 'wayfarer_v05_inputs.json'))); C = json.load(open(os.path.join(W, 'config', 'cert_criteria.json')))
BORE, SL, BX = I['bay']['bore_r_m'], I['bay']['slot_half_width_m'], I['bay']['x_m']
RC, PC, AC = C['G8']['radial_clearance_min_m'], C['G8']['path_clearance_min_m'], C['G8']['axial_clearance_min_m']
INK, MUTE, BG, HARD, CRIT, ENV = '#0b0b0b', '#52514e', '#fcfcfb', '#2b2b2b', '#d99a1e', '#1baf7a'
fig = plt.figure(figsize=(10, 9.5), dpi=150); fig.patch.set_facecolor(BG)
fig.text(.04, .965, 'Shuttle v3: the box it has to fit, read from Wayfarer', fontsize=15, weight='bold')
fig.text(.04, .945, 'Black = installed ship (hard). Amber = certification margin. Green = what the shuttle may occupy.', fontsize=9.5, color=MUTE)
ax = fig.add_axes([.04, .32, .5, .6]); ax.set_facecolor(BG)
ax.add_patch(Circle((0, 0), BORE, fc='#eef0f3', ec=HARD, lw=2))
for s in (-1, 1):
    ax.plot([s * SL, s * SL], [0, 4.6], color=HARD, lw=2.5); ax.plot([s * SL, s * SL], [4.6, 6.1], color=HARD, lw=1.2, ls=(0, (3, 2)))
for it in I['longerons']['items']:
    if it['kind'] == 'tube': ax.add_patch(Circle((it['y_m'], it['z_m']), it['d_m'] / 2, fc=HARD))
ax.add_patch(Circle((0, 0), BORE - RC, fc='none', ec=CRIT, lw=1.4, ls=(0, (4, 2))))
for s in (-1, 1): ax.plot([s * (SL - PC)] * 2, [-2.6, 6.0], color=CRIT, lw=1.4, ls=(0, (4, 2)))
import numpy as np
r = BORE - RC; w = SL - PC; th = np.linspace(-np.pi, np.pi, 400); y, z = r * np.cos(th), r * np.sin(th)
m = np.abs(y) <= w; ax.fill(np.clip(y, -w, w), z, color=ENV, alpha=.35, lw=0)
ax.text(0, 0, 'shuttle\nsection\nlives here', ha='center', va='center', fontsize=10, color='#0d6b48', weight='bold')
ax.annotate('bore r 2.4 (hard)', xy=(-1.7, -1.7), xytext=(-3.6, -3.2), fontsize=8.5, arrowprops=dict(arrowstyle='-', color=MUTE))
ax.annotate('r 2.15: 0.25 m margin', xy=(1.52, -1.52), xytext=(1.3, -3.2), fontsize=8.5, color='#9a6a0c', arrowprops=dict(arrowstyle='-', color=CRIT))
ax.text(0, 5.3, 'slot 4.8 m → exits +Z', ha='center', fontsize=9)
ax.text(0, 4.35, '≤ 3.8 m across the slot\n(0.5 m each side)', ha='center', fontsize=8.5, color='#9a6a0c')
ax.text(2.95, 2.95, 'longeron', fontsize=8); ax.text(-3.0, 6.25, 'doors open vertical', fontsize=8, color=MUTE)
ax.set_xlim(-4, 4); ax.set_ylim(-3.5, 6.6); ax.set_aspect('equal'); ax.axis('off'); ax.set_title('End view, looking forward', fontsize=11, weight='bold', loc='left')
ax2 = fig.add_axes([.58, .62, .38, .26]); ax2.set_facecolor(BG)
ax2.add_patch(Rectangle((BX[0], -BORE), BX[1] - BX[0], 2 * BORE, fc='#eef0f3', ec=HARD, lw=2))
ax2.add_patch(Rectangle((BX[0] + AC, -(BORE - RC)), BX[1] - BX[0] - 2 * AC, 2 * (BORE - RC), fc=ENV, alpha=.35, ec=CRIT, ls=(0, (4, 2))))
ax2.plot([BX[0] - 1.8, BX[0]], [0, 0], color=HARD, lw=4); ax2.text(BX[0] - 1.9, .45, 'transfer\ntunnel', fontsize=7.5, ha='left')
ax2.add_patch(Circle((BX[0] + AC, 0), .22, fc=HARD)); ax2.text(BX[0] + AC + .3, -.75, 'nose port\nx 18.75', fontsize=7.5)
ax2.text((BX[0] + BX[1]) / 2, 2.85, f'bay x {BX[0]}–{BX[1]} m · shuttle ≤ 12.8 m long', ha='center', fontsize=8.5)
ax2.set_xlim(15.8, 33.2); ax2.set_ylim(-3.2, 3.4); ax2.set_aspect('equal'); ax2.axis('off'); ax2.set_title('Side view', fontsize=11, weight='bold', loc='left')
t = fig.add_axes([.58, .32, .38, .28]); t.axis('off')
rows = [('Mass and loads', None), ('reserve left above floor', '31.96 t'), ('berth holds (latches as drawn)', '40.8 t at 7.5 g'),
        ('ship trim margin used', '0.36 of 0.5°'), ('each t of shuttle water', '−3.25 km/s Wayfarer reach'), ('hold space for kits + 50 t cargo', '56.1 m³'),
        ('37 t envelope', 'kT choice, not physics')]
y = .98
for k, v in rows:
    if v is None: t.text(0, y, k, fontsize=10.5, weight='bold'); y -= .14; continue
    t.text(0, y, k, fontsize=9, va='top'); t.text(1, y, v, fontsize=9, ha='right', va='top', weight='bold', color='#c8432f' if 'kT' in v else INK); y -= .13
fig.text(.04, .26, 'What this means for any design:', fontsize=11, weight='bold')
for i, s in enumerate(['Stowed: ≤ 12.8 m long, inside a 4.3 m circle, and ≤ 3.8 m wide across the slot (it may ride rolled).',
                       'Docks nose-first on its long axis. Wings or fins wider than 4.3 m must fold.',
                       'Mass is limited by the reserve, the berth latches and ship trim, not by a fixed 37 t.',
                       'Propellant is expensive for Wayfarer: refilling from oceans, ice or ports matters.']):
    fig.text(.05, .225 - i * .03, '• ' + s, fontsize=9.5)
fig.savefig(os.path.join(HERE, 'shuttle_v3_constraints.png'), facecolor=BG)
