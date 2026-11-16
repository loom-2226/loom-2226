"""Inside the 88 t relational plant: a proposal layout (sketch + numbers). ALL bodies. ALL sponsors. 2026-2226."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
INK, MUTE, BG = '#0b0b0b', '#52514e', '#fcfcfb'
C = dict(tiles='#2a78d6', bank='#eb6834', cryo='#1baf7a', heat='#e34948', ctrl='#6250d6', struct='#8e8c86')
NAME = dict(tiles='Mc tile cryostat', bank='2 GJ field bank', cryo='Cryoplant 20 K', heat='900 K heat exchanger', ctrl='Node drivers + phase control', struct='Structure, shielding, mounts')
fig = plt.figure(figsize=(11, 14), dpi=110); fig.patch.set_facecolor(BG)
fig.text(0.03, 0.972, "Inside the drive boxes: a first layout (proposal, not canon)", fontsize=16, weight='bold')
fig.text(0.03, 0.953, 'Canon fixes only the totals: 88 t plant, 10 kg Mc in 100 tiles, 208 nodes, 2 GJ bank, 150 kW-class cryoplant at 20 K, 900 K heat reject.', fontsize=9.5, color=MUTE)
def box(ax, x0, L, title, parts, cap):
    ax.set_facecolor(BG); ax.add_patch(Rectangle((x0, -2), L, 4, fc='#eef0f3', ec=MUTE, lw=1.4))
    for (k, a, b, r0, r1, lab) in parts:
        for s in (1, -1):
            ax.add_patch(Rectangle((a, s * r0 if s > 0 else -r1), b - a, r1 - r0, fc=C[k], ec=BG, lw=1.2, alpha=.92))
        if lab: ax.text((a + b) / 2, (r0 + r1) / 2, lab, ha='center', va='center', fontsize=8, color='white', weight='bold')
    ax.plot([x0 - .3, x0 + L + .3], [0, 0], color=MUTE, lw=.6, ls=(0, (3, 3)))
    ax.text(x0 + L / 2, 2.35, title, ha='center', fontsize=11, weight='bold'); ax.text(x0 + L / 2, -2.7, cap, ha='center', fontsize=8.5, color=MUTE)
    ax.set_xlim(x0 - .6, x0 + L + .6); ax.set_ylim(-3.1, 2.8); ax.set_aspect('equal'); ax.axis('off')
ax1 = fig.add_axes([0.03, 0.62, 0.52, 0.3]); ax2 = fig.add_axes([0.58, 0.62, 0.39, 0.3])
fore = [('tiles', 14.9, 16.1, 0, .55, '50 tiles'), ('bank', 14.9, 16.1, .6, 1.95, 'bank'), ('cryo', 16.15, 16.95, 0, 1.95, 'cryo'),
        ('heat', 14.05, 14.85, 1.2, 1.95, '900K'), ('ctrl', 14.05, 14.85, 0, 1.15, 'drivers'), ('struct', 14.0, 17.0, 1.95, 2.0, '')]
aft = [('tiles', 32.35, 33.3, 0, .55, '50'), ('bank', 32.35, 33.3, .6, 1.95, 'bank'), ('cryo', 33.35, 34.25, 0, 1.4, 'cryo'),
       ('heat', 33.35, 34.25, 1.45, 1.95, '900K'), ('struct', 32.3, 34.3, 1.95, 2.0, '')]
box(ax1, 14, 3, 'Fore box  x 14-17 m  (44 t booked)', fore, 'side cut, bow left; 37.7 m3, layout fills ~91%')
box(ax2, 32.3, 2, 'Aft box  x 32.3-34.3 m', aft, '25.1 m3: ~9% OVER, see note')
# legend row
for i, k in enumerate(C):
    x = 0.03 + (i % 3) * 0.32; y = 0.595 - (i // 3) * 0.022
    fig.text(x, y, '■', color=C[k], fontsize=14, va='center'); fig.text(x + 0.022, y, NAME[k], fontsize=9.5, va='center')
# mass table
rows = [('Mc tile cassettes (100 x 100 g Mc, host lattice, cryostat)', 3.0, 3.0, 'tiles'),
        ('Field bank, 2 GJ (superconducting toroid at 20 K, ~100 kJ/kg)', 10.0, 10.0, 'bank'),
        ('Cryoplant (turbo-Brayton trains; 20 K cold, rejects at 900 K)', 9.0, 9.0, 'cryo'),
        ('900 K heat exchangers and pumps to the strake manifold', 3.0, 3.0, 'heat'),
        ('Node drivers, phase control, power conditioning', 5.0, 3.0, 'ctrl'),
        ('Structure, magnetic shielding, isolation mounts', 3.0, 3.0, 'struct')]
ax = fig.add_axes([0.03, 0.2, 0.94, 0.36]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.text(0, .98, 'Where the 88 t goes (proposal)', fontsize=12, weight='bold', va='top')
hdr = .9; ax.text(.66, hdr, 'fore', ha='right', fontsize=9.5, color=MUTE); ax.text(.76, hdr, 'aft', ha='right', fontsize=9.5, color=MUTE); ax.text(.88, hdr, 'total t', ha='right', fontsize=9.5, color=MUTE)
y = .83; tf = ta = 0
for lab, f, a, k in rows:
    ax.text(0, y, '■', color=C[k], fontsize=12, va='center'); ax.text(.03, y, lab, fontsize=9.5, va='center')
    for xx, v in ((.66, f), (.76, a), (.88, f + a)): ax.text(xx, y, f'{v:.1f}', ha='right', va='center', fontsize=9.5)
    tf += f; ta += a; y -= .075
ax.plot([0, .9], [y + .035, y + .035], color='#e4e3df', lw=1)
ax.text(.03, y, 'Inside the two boxes', fontsize=9.5, weight='bold', va='center')
for xx, v in ((.66, tf), (.76, ta), (.88, tf + ta)): ax.text(xx, y, f'{v:.1f}', ha='right', va='center', fontsize=9.5, weight='bold')
y -= .085
for lab, v in (('208 node modules, ~60 kg each, out on the hull ring frames', 12.5), ('Distribution trunk: 20 K cryo lines, power feeds, control fibre', 4.0), ('Margin (the plant\'s spread reserve)', 7.5)):
    ax.text(.03, y, lab, fontsize=9.5, va='center'); ax.text(.88, y, f'{v:.1f}', ha='right', va='center', fontsize=9.5); y -= .075
ax.plot([0, .9], [y + .035, y + .035], color='#e4e3df', lw=1)
ax.text(.03, y, 'Plant total (canon, unchanged)', fontsize=10, weight='bold', va='center'); ax.text(.88, y, '88.0', ha='right', va='center', fontsize=10, weight='bold')
notes = ['Total stays 88 t (mass-neutral). But 16.5 t of it (nodes and trunk) would move out of the boxes onto the hull: that shifts the centre of mass, so it is your call.',
         'Aft box is ~9% over volume. Easiest fix: put the aft cryo train\'s hot end in the free ring around the box (r 2-4.4 m) next to the strake manifold. Needs a clash check.',
         'Canon power check: HARD mode needs 23.9 MW of cryo electrical to lift 136 kW at 20 K (rejected at 900 K). That is about 25% of ideal: consistent, and it drives the cryoplant size.',
         'Each box carries half the tiles, half the bank and its own cryo train, so losing one box is a degraded drive, not a dead one.']
for i, n in enumerate(notes): fig.text(0.03, 0.17 - i * 0.04, ('• ' + n), fontsize=9.3, color=INK, wrap=True)
import os; fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plant_boxes_proposal.png'), facecolor=BG)
