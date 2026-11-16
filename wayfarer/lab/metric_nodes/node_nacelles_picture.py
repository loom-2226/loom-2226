"""Sketch: retractable node nacelles. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch, Circle, Rectangle, Wedge
HERE = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(os.path.join(HERE, 'node_nacelles.json')))
O = json.load(open(os.path.join(HERE, 'node_options.json')))['options']; E = json.load(open(os.path.join(HERE, 'node_layouts_even.json')))
INK, MUTE, BG, HULL, NAC, NODE, FIN = '#0b0b0b', '#52514e', '#fcfcfb', '#dfe3e8', '#2a78d6', '#1baf7a', '#e34948'
top = [(-0.3, 0), (0.2, 2.6), (1.2, 3.8), (3, 4.5), (34.3, 4.5), (39.3, 2.95), (39.3, 2.125), (46.3, 2.125), (53.3, 3)]
prof = top + [(x, -y) for x, y in reversed(top)]
fig = plt.figure(figsize=(11, 13.5), dpi=110); fig.patch.set_facecolor(BG)
fig.text(0.03, 0.982, 'Retractable node nacelles (your idea, sketched; not canon)', fontsize=16, weight='bold')
fig.text(0.03, 0.952, 'Seen from above, bow left. Two nacelles flank the torch. The trick: torch burns and Metric/Loom never happen together (Canon II §14), so the nacelles only swing out when the torch is cold.', fontsize=9, color=MUTE, wrap=True)
def plan(ax, title, out):
    ax.set_facecolor(BG); ax.add_patch(Polygon(prof, closed=True, fc=HULL, ec=MUTE, lw=1.1))
    if not out:   # torch config: hot fins out (plan view shows the 40 and 320 / 140 and 220 pairs)
        for s in (1, -1):
            ax.add_patch(Rectangle((34.3, s * 4.75 * math.cos(math.radians(40))), 19, s * 2 * math.cos(math.radians(40)), fc='#f6b8b0', ec=FIN, lw=.8, alpha=.8))
        ax.text(44, 6.3, 'hot fins out, 1,750 K', fontsize=8, color=FIN, ha='center')
    r = 4.6 if out else 3.4
    for s in (1, -1):
        y = s * r; ax.add_patch(FancyBboxPatch((39.5, y - .6), 14.0, 1.2, boxstyle='round,pad=0,rounding_size=.6', fc=NAC if out else '#9cc0ea', ec=NAC, lw=1.2, zorder=4))
        ax.plot([41.0, 41.0], [s * 2.15, y - s * .55], color=MUTE, lw=2, zorder=3); ax.plot([46.0, 46.0], [s * 2.15, y - s * .55], color=MUTE, lw=2, zorder=3)
        if out:
            for x in np.arange(40.2, 53.2, 1.1): ax.plot(x, y + s * .62, 'o', ms=4, color=NODE, mec=BG, mew=.4, zorder=5)
    if out:
        t = np.linspace(0, 2 * math.pi, 300); ax.plot(27 + 29 * np.cos(t), 7.1 * np.sin(t), color=NODE, lw=1.3, ls=(0, (5, 3)))
        ax.text(48, 7.6, 'node wall wraps the torch evenly', fontsize=8, color=NODE)
        ax.annotate('', xy=(48.5, 4.0), xytext=(48.5, 3.0), arrowprops=dict(arrowstyle='->', color=NAC, lw=1.6))
    ax.set_xlim(-1.5, 58); ax.set_ylim(-8.2, 8.6); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, loc='left', fontsize=12, weight='bold')
plan(fig.add_axes([0.03, 0.67, 0.94, 0.26]), 'Burning the torch: nacelles folded in tight against the torch, inside the hull outline', False)
plan(fig.add_axes([0.03, 0.40, 0.94, 0.26]), 'Metric or Loom: torch cold, fins stowed, nacelles swing out 1.2 m on parallel links', True)
# end views
for i, out in enumerate((False, True)):
    e = fig.add_axes([0.05 + i * 0.25, 0.20, 0.2, 0.18]); e.set_aspect('equal'); e.axis('off'); e.set_facecolor(BG)
    e.add_patch(Circle((0, 0), 4.5, fc=HULL, ec=MUTE)); e.add_patch(Circle((0, 0), 2.125, fc='#c9c7c0', ec=MUTE))
    for s in (40, 140, 220, 320):
        a = math.radians(s); r0, r1 = (4.75, 6.75) if not out else (4.5, 4.75)
        e.plot([r0 * math.cos(a), r1 * math.cos(a)], [r0 * math.sin(a), r1 * math.sin(a)], color=FIN, lw=4 if not out else 2)
    r = 4.6 if out else 3.4
    for s in (0, 180): e.add_patch(Circle((r * math.cos(math.radians(s)), r * math.sin(math.radians(s))), .6, fc=NAC, ec=BG))
    e.set_xlim(-7.2, 7.2); e.set_ylim(-7.2, 7.2); e.set_title(('torch burning' if not out else 'Metric / Loom') + ' (from aft)', fontsize=9.5, weight='bold')
# table
ax = fig.add_axes([0.55, 0.19, 0.42, 0.2]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
rows = [('Layout', 'worst gap', 'evenness', 'skin in reach'),
        ('Today', '5.0 m', '0.29', '88%'),
        ('Fin roots', '4.3 m', '0.28', '89%'),
        ('Shuttle-as-hull + compact torch', '4.8 m', '0.25', '92%')]
for k, lab in (('two_nacelles', 'Two nacelles'), ('three_nacelles', 'Three (+ keel)')):
    m = R['options'][k]['metrics']; rows.append((lab, f"{m['max_gap_m']:.1f} m", f"{m['load_cv']:.2f}", f"{m['reach_cover'] * 100:.0f}%"))
for i, r in enumerate(rows):
    y = .95 - i * .15
    for x, v in zip((0, .58, .76, .93), r): ax.text(x, y, v, fontsize=9, ha='left' if x == 0 else 'center', va='top', weight='bold' if i == 0 or 'nacelle' in r[0].lower() else None, color=INK if i == 0 or x == 0 else MUTE)
notes = ['Why it works: nodes sit on cold nacelles beside the torch, never on the reactor, nozzle or fins, and the network stays in one piece. Torch length unchanged.',
         'Why tucked, not slid forward: sliding them into the hull would cut about 50 m3 out of the water tanks, whose packing is canon. Tucked against the torch they stay inside the 4.5 m outline (F1).',
         'Costs: two 14 m nacelles with parallel links, roughly 3-6 t of structure (nodes unchanged). Their inner faces shade the nodes from the reactor during burns, so a light heat shield on the inner side.',
         'Look: a proper ship-with-nacelles silhouette when it jumps, and a tidy torch when it burns. Combine with the shuttle-as-hull idea and the bay doors go too.']
for i, n in enumerate(notes): fig.text(0.03, 0.16 - i * 0.037, '• ' + n, fontsize=9, wrap=True)
fig.savefig(os.path.join(HERE, 'node_nacelles.png'), facecolor=BG)
