"""Wayfarer v1 shuttle at 1:100: what prints (Claude, 14 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
Source: the shuttle_v1 nodes inside the canon stowed/closed exterior GLB (the shuttle itself is NON-CANON v1 research).
PROPOSAL (F4): survey + one decision. Print LOD only."""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Rectangle
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import glb_read
RAW = [(n, T) for n, T in glb_read.load(os.path.join(HERE, '..', '..', 'render', 'out', 'wayfarer_exterior_detail_88ce19fc_stowed_closed.glb')) if 'shuttle' in n]
# GLB stores ship coordinates as [X, Z, -Y]; convert back to ship X, Y, Z
parts = [(n, np.stack([T[..., 0], -T[..., 2], T[..., 1]], -1)) for n, T in RAW]
INTERNAL = ('pod_', 'water_tank', 'torch_reactor', 'kit_reactor', 'kit_exchanger'); THIN = ('rotor_blade',)
def cat(n):
    k = n.split('/')[-1]
    return 'int' if any(k.startswith(t) for t in INTERNAL) else 'thin' if any(k.startswith(t) for t in THIN) else 'ok'
INK, MUT = '#1d2228', '#6b737c'; C = {'ok': '#7f97a8', 'thin': '#d9773a'}
fig = plt.figure(figsize=(13, 10.5), dpi=110); fig.patch.set_facecolor('#f6f5f2')
fig.text(0.04, 0.955, 'Wayfarer shuttle at 1:100: what prints (NON-CANON v1 shuttle, print only)', fontsize=17, weight='bold', color=INK)
fig.text(0.04, 0.93, '128 x 38 mm. Blue: prints as modelled (1 mm+). Orange: too thin, needs a decision. Inside the hull (pod, wheels, tank, reactors): hidden, not printed.', fontsize=10.5, color=MUT)
for rect, ij, title in (([0.04, 0.57, 0.92, 0.32], (0, 1), 'Seen from above, through the open bay doors: nose left; spine + blades to starboard (top), heat shield to port (bottom)'),
                        ([0.04, 0.23, 0.92, 0.32], (0, 2), 'Side view: gullwing crew door on top, facing the bay doors (blades shown through the hull)')):
    ax = fig.add_axes(rect); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, loc='left', fontsize=11.5, weight='bold', color=INK)
    for want in ('ok', 'thin'):
        polys = [P for n, T in parts if cat(n) == want for P in T[:, :, list(ij)] * 10]
        ax.add_collection(PolyCollection(polys, facecolors=C[want], edgecolors='none', alpha=0.55 if want == 'ok' else 1.0))
    ax.set_xlim(185, 320); ax.set_ylim(-26, 26)
    ax.plot([188, 316], [-23, -23], color=INK, lw=1); ax.text(252, -25.8, '128 mm', ha='center', fontsize=9, color=INK)
ax = fig.add_axes([0.04, 0.02, 0.36, 0.19]); ax.set_aspect('equal'); ax.axis('off'); ax.set_title('In the bay (section)', loc='left', fontsize=11, weight='bold', color=INK)
ax.add_patch(Circle((0, 0), 45, fc='#dfe2e0', ec=INK)); ax.add_patch(Circle((0, 0), 24, fc='#f6f5f2', ec=INK))
ax.add_patch(Rectangle((-24, 0), 48, 46, fc='#f6f5f2', ec='none')); ax.add_patch(Circle((0, 0), 19, fc='#7f97a8', ec=INK))
ax.text(50, -20, 'bay bore 48 mm\nshuttle 38 mm, on its side:\ncrew door up, spine\nstarboard, heat shield\nport; lifts out through\nthe open doors', fontsize=9, color=INK); ax.set_xlim(-50, 95); ax.set_ylim(-48, 50)
ax = fig.add_axes([0.42, 0.02, 0.56, 0.19]); ax.axis('off')
ax.text(0, 0.97, 'Decision: the 4 stowed rotor blades (56 mm long, 0.1-0.4 mm thick)\n'
        '  (a) engrave as outlines in the spine groove\n  (b) thicken to 0.5 mm raised strips\n  (c) leave the groove empty\n'
        'Claude: (a). They lie flat in a recessed groove, so outlines read\nright and nothing thin sticks up.\n'
        'Also: seams and gullwing door edges (0.17-0.4 mm) become 0.5 mm grooves.', fontsize=10, va='top', color=INK, linespacing=1.45)
fig.savefig(os.path.join(HERE, 'shuttle_1to100_survey.png'), facecolor=fig.get_facecolor())
