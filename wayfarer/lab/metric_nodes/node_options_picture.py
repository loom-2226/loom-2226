"""Sketch sheet for node_options.py. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Arc, FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__)); O = json.load(open(os.path.join(HERE, 'node_options.json')))['options']
E = json.load(open(os.path.join(HERE, 'node_layouts_even.json')))
INK, MUTE, BG, HULL = '#0b0b0b', '#52514e', '#fcfcfb', '#dfe3e8'
ZC = {'hull': '#2a78d6', 'cone': '#eda100', 'nozzle': '#1baf7a', 'mount': '#6250d6', 'shuttle': '#e87ba4', 'bow': '#8e8c86', 'fin': '#e34948'}
def profile(reactor=(39.3, 46.3), nozzle=(46.3, 53.3), collar=None):
    top = [(-0.3, 0), (0.2, 2.6), (1.2, 3.8), (3, 4.5), (34.3, 4.5), (39.3, 2.95), (39.3, 2.125), (reactor[1], 2.125)]
    if nozzle: top += [(nozzle[0], 2.125), (nozzle[1], 3.0)]
    else: top += [(reactor[1], 0.6)]
    return top + [(x, -y) for x, y in reversed(top)]
def zone_of(n, opt):
    x, a, r = n
    if abs(x - 2.05) < .06: return 'bow'
    if x <= 34.2: return 'shuttle' if (opt == 3 and 18.2 <= x <= 32.1 and 56 <= a <= 124) else 'hull'
    if x <= 39.3: return 'cone'
    if opt in (1, 3) and x < 40.1: return 'mount'
    if opt == 0: return 'fin'
    return 'nozzle'
def draw(ax, title, sub, nodes, opt, prof, metrics, extra=None):
    ax.set_facecolor(BG); ax.add_patch(Polygon(prof, closed=True, fc=HULL, ec=MUTE, lw=1))
    if extra: extra(ax)
    for n in nodes:
        x, a, r = n
        if math.cos(math.radians(a)) < -0.05: continue
        ax.plot(x, r * math.sin(math.radians(a)), 'o', ms=3.6, color=ZC[zone_of(n, opt)], mec=BG, mew=.3, zorder=4)
    ax.set_xlim(-1, 56); ax.set_ylim(-5.8, 8.0); ax.set_aspect('equal'); ax.axis('off')
    ax.text(-1, 7.9, title, fontsize=11.5, weight='bold', va='top'); ax.text(-1, 6.55, sub, fontsize=8.3, color=MUTE, va='top')
    if metrics:
        m = metrics; s = f"{'one network' if m['web_pieces'] == 1 else 'network splits'}  ·  worst gap {m['max_gap_m']:.1f} m  ·  evenness {m['load_cv']:.2f}  ·  skin in reach {m['reach_cover'] * 100:.0f}%  ·  ship {m.get('ship_x_max_m', 53.3):.1f} m"
        ax.text(-1, -5.75, s, fontsize=8.6, color=INK, weight='bold')
fig = plt.figure(figsize=(11, 17), dpi=110); fig.patch.set_facecolor(BG)
fig.text(0.03, 0.982, 'Creative ways to give Wayfarer an even node field (sketches, not canon)', fontsize=15, weight='bold')
fig.text(0.03, 0.968, 'Side view, near-side nodes only. Every layout below puts 208 nodes on allowed mounts only, ring 0 fixed. Evenness: lower is better (today 0.29).', fontsize=9, color=MUTE)
H = 0.152; Y = [0.80, 0.645, 0.49, 0.335, 0.18, 0.025]
ax = fig.add_axes([0.03, Y[0], 0.94, H]); cf = E['layouts']['cone_fins']
draw(ax, 'Reference: last search (hull + cone + hot-fin roots)', 'Works, but 39 nodes sit in the 1,750 K fin roots.', cf['nodes'], 0, profile(), dict(cf['metrics'], ship_x_max_m=53.3))
o = O['1_compact_torch_coil_ring']; ax = fig.add_axes([0.03, Y[1], 0.94, H])
draw(ax, '1  Compact torch + nozzle-coil node ring', 'Reactor 7 -> 4 m (denser), burn point 6 -> 4 m aft. Rear nodes ride the magnetic nozzle\'s coil frame, which is already superconducting and cold.',
     o['nodes'], 1, profile((39.3, 43.3), (43.3, 48.3)), o['metrics'])
o = O['2_telescoping_nozzle']; ax = fig.add_axes([0.03, Y[2], 0.94, H])
def ghost(ax):
    g = profile(); ax.add_patch(Polygon(g, closed=True, fc='none', ec='#b9b6ae', lw=1, ls='--'))
    ax.annotate('', xy=(42.3, -3.6), xytext=(50, -3.6), arrowprops=dict(arrowstyle='->', color='#1baf7a', lw=1.6)); ax.text(50.4, -3.75, 'coils slide forward', fontsize=7.5, color='#1baf7a')
draw(ax, '2  Telescoping nozzle', 'Full length when burning (dashed). For a jump the nozzle coil rings slide forward on rails and park as a collar round the reactor: the ship is 7 m shorter.',
     o['nodes'], 2, profile((39.3, 46.3), None) + [], o['metrics'], ghost)
o = O['3_shuttle_completes_hull']; ax = fig.add_axes([0.03, Y[3], 0.94, H])
def shut(ax): ax.add_patch(Rectangle((18.25, 3.85), 13.8, 0.65, fc='#f6c9d7', ec='#e87ba4', lw=1, zorder=2)); ax.text(25.1, 5.0, "shuttle's back = the hull here", ha='center', fontsize=7.5, color='#b44b77')
draw(ax, '3  The shuttle completes the hull (+ option 1)', 'No bay doors: the docked shuttle\'s flat back is the hull in that sector and carries 12 nodes that plug in when docked. Wayfarer cannot jump without its shuttle home (or a blank plate).',
     o['nodes'], 3, profile((39.3, 43.3), (43.3, 48.3)), o['metrics'], shut)
ax = fig.add_axes([0.03, Y[4], 0.94, H]); o = O['4_end_cap_lens']
def lens(ax):
    t = np.linspace(-1.2, 1.2, 100); ax.plot(34.3 + 22 * np.cos(t) * 0.9, 6.0 * np.sin(t), color='#eda100', lw=1.6, ls=(0, (5, 3)))
    ax.text(48, 4.6, 'wall thrown past the torch', fontsize=7.5, color='#b07900')
draw(ax, '4  End-cap lens (wildest)', 'No hardware aft of the cone at all. The aft rings phase together like an end-fire antenna and throw a closed bubble round the torch, the way Metric already shapes a long forward lobe.',
     o['nodes'], 4, profile(), o['metrics'], lens)
ax = fig.add_axes([0.03, Y[5], 0.94, 0.135]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
notes = [('My pick: 3 on top of 1.', 'Most even layout found (0.25), one network, no hot mounts, no doors. And it gives the flat Ranger-style shuttle a job: its back is a piece of the hull.'),
         ('Runner-up: 2.', 'Keeps today\'s torch when burning; costs a 30 t nozzle on rails. A great visual: the ship visibly "folds its tail" before a jump.'),
         ('4 is pure fiction.', 'Geometrically it fails (torch 15 m from any node); it only works if we rule that phased nodes can project the wall. Fun, but it hides the problem.'),
         ('Costs for 1 and 3.', 'Shorter torch: ~25% more dose behind the shield, shorter hot fins (less radiator), trim re-check. Torch card and dv unchanged; your 25 Oct burn-point decision would change.')]
for i, (h, t) in enumerate(notes):
    ax.text(0, .95 - i * .25, h, fontsize=9.6, weight='bold', va='top'); ax.text(.2, .95 - i * .25, t, fontsize=9, color=MUTE, va='top', wrap=True)
for i, (k, lab) in enumerate((('hull', 'hull'), ('cone', 'thrust cone'), ('mount', 'reactor mount ring'), ('nozzle', 'nozzle coils / collar'), ('shuttle', 'shuttle back'), ('fin', 'fin roots'), ('bow', 'ring 0'))):
    fig.text(0.03 + i * 0.135, 0.958, '●', color=ZC[k], fontsize=11, va='center'); fig.text(0.045 + i * 0.135, 0.958, lab, fontsize=8.3, va='center')
fig.savefig(os.path.join(HERE, 'node_options.png'), facecolor=BG)
