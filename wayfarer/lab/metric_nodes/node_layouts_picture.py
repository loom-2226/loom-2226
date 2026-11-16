"""Picture for node_optimize.py results. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(os.path.join(HERE, 'node_layouts_even.json')))
NB = json.load(open(os.path.join(HERE, 'nodes_before_after.json')))['before']
INK, MUTE, BG, BLU, RED, GRN = '#0b0b0b', '#52514e', '#fcfcfb', '#2a78d6', '#e34948', '#1baf7a'
fig = plt.figure(figsize=(11, 13), dpi=110); fig.patch.set_facecolor(BG)
fig.text(0.03, 0.972, 'Even node layouts that fit around everything (design search, not canon)', fontsize=15, weight='bold')
fig.text(0.03, 0.952, 'Hull unrolled, bow left. Shaded = no-go zones (bay doors, stowed strakes, longerons, hardware). Ring 0 at the bow is fixed by your 13 Nov decision.', fontsize=9.3, color=MUTE)
def panel(ax, nodes, title, cols):
    ax.set_facecolor(BG)
    for (a, b, n) in ((0, 2.35, 'bow'), (2.35, 14, 'habitat'), (14, 34.3, 'bay, tanks, strakes'), (34.3, 39.3, 'cone'), (39.3, 46.3, 'reactor'), (46.3, 53.3, 'nozzle')):
        ax.add_patch(Rectangle((a, 0), b - a, 360, fc='#f3f2ee' if n in ('bow', 'bay, tanks, strakes', 'reactor') else BG, ec='none', zorder=0))
        ax.text((a + b) / 2, 352, n, ha='center', fontsize=7.5, color=MUTE, zorder=5)
    ax.add_patch(Rectangle((18.0, 55), 14.3, 70, fc='#f6c9d7', ec='none', zorder=1))
    for s in (40, 140, 220, 320):
        ax.add_patch(Rectangle((14, s - 12.7), 18.3, 25.4, fc='#f3c6b0', ec='none', alpha=.8, zorder=1))
        ax.add_patch(Rectangle((34.3, s - 4), 19, 8, fc='#d9d6cf', ec='none', zorder=1))
    for l in (43.4, 136.6, 223.4, 316.6): ax.plot([14, 34.3], [l, l], color='#b9b6ae', lw=3, zorder=1)
    x = [n[0] for n in nodes]; a = [n[1] for n in nodes]
    ax.scatter(x, a, s=20, c=cols, edgecolor=BG, linewidth=.5, zorder=4)
    ax.set_xlim(-0.5, 53.8); ax.set_ylim(0, 360); ax.invert_yaxis(); ax.set_yticks([0, 90, 180, 270, 360])
    for s_ in ('top', 'right'): ax.spines[s_].set_visible(False)
    ax.tick_params(colors=MUTE, length=0, labelsize=8); ax.set_title(title, loc='left', fontsize=11, weight='bold')
bad = {'torch', 'strake', 'door', 'hw'}
a1 = fig.add_axes([0.06, 0.66, 0.9, 0.25])
panel(a1, [[n['x'], n['a']] for n in NB], 'Today (PR #184 baseline): 13 even rings, 120 nodes on something they should not be on', [RED if n['c'] in bad else BLU for n in NB])
L = R['layouts']['cone_fins']['nodes']
def zone(n):
    if abs(n[0] - 2.05) < .05: return '#6250d6'
    if n[0] > 39.3: return GRN
    if n[0] > 34.3: return '#eda100'
    return BLU
a2 = fig.add_axes([0.06, 0.34, 0.9, 0.25])
panel(a2, L, 'Best fit found: 208 nodes, none on a no-go zone, spaced by what each one has to cover', [zone(n) for n in L])
a2.set_xlabel('x from bow (m)', color=MUTE, fontsize=9)
for i, (c, t) in enumerate(((BLU, '133 on the hull skin'), ('#eda100', '20 on the thrust-cone skin'), (GRN, '39 on the hot-fin root trusses'), ('#6250d6', '16 ring 0, fixed'))):
    fig.text(0.06 + i * 0.235, 0.305, '●', color=c, fontsize=13, va='center'); fig.text(0.08 + i * 0.235, 0.305, t, fontsize=9.3, va='center')
# metrics
B, M = R['baseline_A0'], R['layouts']
rows = [('Nodes on a no-go zone', '120', '0', '0', '0'),
        ('Network in one piece', 'no (2)', 'yes', 'yes', 'yes'),
        ('Worst gap to the nearest node', f"{B['max_gap_m']:.1f} m", f"{M['hull_only']['metrics']['max_gap_m']:.1f} m", f"{M['cone']['metrics']['max_gap_m']:.1f} m", f"{M['cone_fins']['metrics']['max_gap_m']:.1f} m"),
        ('Typical gap (95% of skin within)', f"{B['p95_gap_m']:.1f} m", f"{M['hull_only']['metrics']['p95_gap_m']:.1f} m", f"{M['cone']['metrics']['p95_gap_m']:.1f} m", f"{M['cone_fins']['metrics']['p95_gap_m']:.1f} m"),
        ('Evenness (spread of load per node, lower is better)', f"{B['load_cv']:.2f}", f"{M['hull_only']['metrics']['load_cv']:.2f}", f"{M['cone']['metrics']['load_cv']:.2f}", f"{M['cone_fins']['metrics']['load_cv']:.2f}"),
        ('Skin within 2.1 m of a node', f"{B['reach_cover'] * 100:.0f}%", f"{M['hull_only']['metrics']['reach_cover'] * 100:.0f}%", f"{M['cone']['metrics']['reach_cover'] * 100:.0f}%", f"{M['cone_fins']['metrics']['reach_cover'] * 100:.0f}%")]
ax = fig.add_axes([0.03, 0.03, 0.94, 0.25]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
hdr = ['', 'Today', 'Hull only', '+ cone skin', '+ cone + fin roots']
xs = [0, .5, .62, .74, .88]
for x, h in zip(xs, hdr): ax.text(x, .95, h, fontsize=9.5, weight='bold', ha='left' if x == 0 else 'center', color=GRN if h.startswith('+ cone +') else INK)
for i, r in enumerate(rows):
    y = .82 - i * .125
    for x, v in zip(xs, r): ax.text(x, y, v, fontsize=9.3, ha='left' if x == 0 else 'center', color=INK if x == 0 else MUTE, weight='bold' if x == .88 else None)
ax.add_patch(Rectangle((.815, 0.08), .14, .92, fc=GRN, alpha=.08, ec='none'))
ax.text(0, .02, 'Hull-only and cone-only layouts leave the reactor and nozzle 12-20 m from any node. The fin-root nodes still need the heat-soak answer Sol flagged (1,750 K vs 20 K).', fontsize=8.8, color=MUTE)
fig.savefig(os.path.join(HERE, 'node_layouts_even.png'), facecolor=BG)
