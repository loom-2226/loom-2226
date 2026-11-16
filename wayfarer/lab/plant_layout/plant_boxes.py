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
    ax.text(x0 + L / 2, 3.75, title, ha='center', fontsize=11, weight='bold'); ax.text(x0 + L / 2, -3.85, cap, ha='center', fontsize=8.5, color=MUTE)
    ax.set_xlim(x0 - .6, x0 + L + .6); ax.set_ylim(-3.9, 3.9); ax.set_aspect('equal'); ax.axis('off')
DENS = dict(tiles=1.5, bank=1.0, cryo=1.0, heat=1.5, ctrl=0.6, struct=3.0)   # t/m3, assumed
FM = dict(tiles=3, bank=10, cryo=9, heat=3, ctrl=5, struct=3); AM_BOX = dict(tiles=3, bank=10, cryo=9, struct=3); AM_RING = dict(heat=3, ctrl=3)
vol = lambda m: sum(v / DENS[k] for k, v in m.items())
VF, VA, VR = vol(FM), vol(AM_BOX), vol(AM_RING); VFB, VAB = 3.14159 * 4 * 3, 3.14159 * 4 * 2
FORECAP = f'side cut, bow left; {VF:.0f} of {VFB:.1f} m3 ({VF / VFB * 100:.0f}% full)'
AFTCAP = f'{VA:.0f} of {VAB:.1f} m3 ({VA / VAB * 100:.0f}%); {VR:.0f} m3 moves into the manifold ring'
ax1 = fig.add_axes([0.03, 0.62, 0.52, 0.3]); ax2 = fig.add_axes([0.58, 0.62, 0.39, 0.3])
fore = [('tiles', 14.9, 16.1, 0, .55, '50 tiles'), ('bank', 14.9, 16.1, .6, 1.95, 'bank'), ('cryo', 16.15, 16.95, 0, 1.95, 'cryo'),
        ('heat', 14.05, 14.85, 1.2, 1.95, '900K'), ('ctrl', 14.05, 14.85, 0, 1.15, 'drivers'), ('struct', 14.0, 17.0, 1.95, 2.0, '')]
aft = [('tiles', 32.35, 33.3, 0, .55, '50'), ('bank', 32.35, 33.3, .6, 1.95, 'bank'), ('cryo', 33.35, 34.25, 0, 1.95, 'cryo'),
       ('struct', 32.3, 34.3, 1.95, 2.0, ''), ('heat', 32.35, 34.25, 2.1, 2.9, 'into ring'), ('ctrl', 32.35, 34.25, 2.95, 3.6, 'into ring')]
box(ax1, 14, 3, 'Fore box  x 14-17 m', fore, FORECAP)
box(ax2, 32.3, 2, 'Aft box  x 32.3-34.3 m', aft, AFTCAP)
# legend row
for i, k in enumerate(C):
    x = 0.03 + (i % 3) * 0.32; y = 0.595 - (i // 3) * 0.022
    fig.text(x, y, '■', color=C[k], fontsize=14, va='center'); fig.text(x + 0.022, y, NAME[k], fontsize=9.5, va='center')
# mass table
rows = [('Mc tile cassettes (100 x 100 g Mc, host lattice, cryostat)', 3.0, 3.0, 'tiles'),
        ('Field bank, 2 GJ (superconducting toroid at 20 K, ~100 kJ/kg)', 10.0, 10.0, 'bank'),
        ('Cryoplant (turbo-Brayton trains; 20 K cold, rejects at 900 K)', 9.0, 9.0, 'cryo'),
        ('900 K heat exchangers to the strakes (aft set in the manifold ring)', 3.0, 3.0, 'heat'),
        ('Node drivers, phase control (aft set in the manifold ring)', 5.0, 3.0, 'ctrl'),
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
ax.text(.03, y, 'Plant core (boxes + aft ring set)', fontsize=9.5, weight='bold', va='center')
for xx, v in ((.66, tf), (.76, ta), (.88, tf + ta)): ax.text(xx, y, f'{v:.1f}', ha='right', va='center', fontsize=9.5, weight='bold')
y -= .085
for lab, v in (('208 node modules, ~60 kg each, out on the hull ring frames', 12.5), ('Distribution trunk: 20 K cryo lines, power feeds, control fibre', 4.0), ('Margin (the plant\'s spread reserve)', 7.5)):
    ax.text(.03, y, lab, fontsize=9.5, va='center'); ax.text(.88, y, f'{v:.1f}', ha='right', va='center', fontsize=9.5); y -= .075
ax.plot([0, .9], [y + .035, y + .035], color='#e4e3df', lw=1)
ax.text(.03, y, 'Plant total (canon, unchanged)', fontsize=10, weight='bold', va='center'); ax.text(.88, y, '88.0', ha='right', va='center', fontsize=10, weight='bold')
notes = ['APPROVED by kT 16 Nov: 16.5 t (nodes and trunk) moves out of the boxes onto the hull. Total stays 88 t; centre of mass moves only about 1 cm aft.',
         'APPROVED by kT 16 Nov: the aft 900 K hot end goes into the ring around the aft box. That ring is the radiator manifold (pumps and heat exchangers, 101 m3 booked, unsized), so the hot end belongs there.',
         'CORRECTION: the aft box was ~16% over volume, not 9%. Moving only the hot end leaves it ~8% over; moving the aft node drivers into the ring too brings it to ' + f'{VA / VAB * 100:.0f}% (needs your OK).',
         'Each box keeps half the tiles, half the bank and its own cryo train, so losing one box is a degraded drive, not a dead one. Densities are assumptions, shown in the script.']
for i, n in enumerate(notes): fig.text(0.03, 0.17 - i * 0.04, ('• ' + n), fontsize=9.3, color=INK, wrap=True)
import os; fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plant_boxes_proposal.png'), facecolor=BG)
