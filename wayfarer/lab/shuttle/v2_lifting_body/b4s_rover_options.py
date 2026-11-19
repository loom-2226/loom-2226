"""Venus rover shape options for B4-S (kT: 'I didn't think the rover was a sphere anymore'). Side views, to scale.
NON-CANON sketch. ALL bodies. ALL sponsors. 2026-2226. Shell mass ratios are thin-shell ROM ASSUMPTIONS vs the 2.1 m sphere."""
import os, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Polygon
HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTE, BG, TI, SH, GND, GOLD = '#0b0b0b', '#52514e', '#fcfcfb', '#a0694f', '#d8dde3', '#c9a27a', '#d9a21e'
fig, axs = plt.subplots(3, 1, figsize=(8.5, 11), dpi=140); fig.patch.set_facecolor(BG)
fig.text(.05, .965, 'What the Venus rover could look like', fontsize=15, weight='bold')
fig.text(.05, .947, 'Side views to scale. Inside, something must hold off 92 bar at 735 K. NON-CANON sketch.', fontsize=9.5, color=MUTE)
def wheels(ax, xs, r=.45):
    for x in xs: ax.add_patch(Circle((x, r), r, fc='#333', ec=INK, zorder=3)); ax.add_patch(Circle((x, r), .12, fc='#888', zorder=4))
def ground(ax): ax.add_patch(Rectangle((-1, -.3), 9, .3, fc=GND, ec='none'))
# 1 today: bare sphere
ax = axs[0]; ground(ax); wheels(ax, [1.6, 3.9]); ax.plot([1.6, 3.9], [.75, .75], color='#667', lw=3)
ax.add_patch(Circle((2.75, 1.85), 1.05, fc=TI, ec=INK, zorder=2)); ax.add_patch(Rectangle((2.3, 2.88), .9, .12, fc=GOLD, zorder=3))
ax.set_title('Today: the bare sphere on a chassis', loc='left', fontsize=12, weight='bold')
ax.text(5.2, 1.9, 'room 4.9 m³\npod shell ×1.0\nlooks like a ball on wheels', fontsize=9.5, va='center')
# 2 sphere inside a rover body
ax = axs[1]; ground(ax)
body = [(.6, .8), (4.9, .8), (5.1, 1.3), (4.9, 2.95), (1.4, 3.05), (.6, 2.3)]
ax.add_patch(Polygon(body, fc=SH, ec=INK, lw=1.2, zorder=2))
ax.add_patch(Circle((2.75, 1.9), 1.05, fc='none', ec=TI, lw=1.6, ls=(0, (4, 2)), zorder=3)); ax.text(2.75, 1.9, 'sphere\ninside', ha='center', va='center', fontsize=8.5, color='#7a4a35', zorder=4)
ax.add_patch(Polygon([(.75, 2.2), (1.45, 2.85), (1.75, 2.85), (1.75, 2.2)], fc='#9fd0e8', ec=INK, zorder=4))
ax.add_patch(Rectangle((3.9, 1.0), .85, 1.7, fc='#c5ccd4', ec=INK, lw=.8, zorder=3)); ax.text(4.32, 1.85, 'bays', rotation=90, ha='center', va='center', fontsize=8, zorder=4)
ax.add_patch(Rectangle((1.6, 3.05), 2.6, .12, fc=GOLD, zorder=3)); wheels(ax, [1.3, 4.3])
ax.set_title('B: same sphere, inside a boxy insulated rover body', loc='left', fontsize=12, weight='bold')
ax.text(5.5, 1.9, 'room 4.9 m³ (same)\npod shell ×1.0, + ~0.4 t body\nthe body is the heat shield it\nneeds anyway, plus bays for\nbatteries, samples, the cooler', fontsize=9.5, va='center')
# 3 short capsule
ax = axs[2]; ground(ax)
ax.add_patch(FancyBboxPatch((.7, .95), 4.2, 1.9, boxstyle='round,pad=0,rounding_size=.95', fc=TI, ec=INK, zorder=2))
for x in (1.9, 2.8, 3.7): ax.plot([x, x], [.97, 2.83], color='#6d4533', lw=1.2, zorder=3)
ax.add_patch(Circle((1.25, 2.15), .2, fc='#9fd0e8', ec=INK, zorder=4)); ax.add_patch(Rectangle((1.9, 2.85), 2.2, .12, fc=GOLD, zorder=3)); wheels(ax, [1.4, 4.2])
ax.set_title('C: a short Ti capsule (ring-stiffened tube)', loc='left', fontsize=12, weight='bold')
ax.text(5.5, 1.9, 'room ~7.3 m³ (+50%)\npod shell ×1.8–2.4 (+2–3 t)\nlooks most like a vehicle;\nlonger: the side door and\nshuttle layout must grow', fontsize=9.5, va='center')
for ax in axs: ax.set_xlim(-.5, 8.5); ax.set_ylim(-.35, 3.4); ax.set_aspect('equal'); ax.axis('off')
fig.text(.05, .025, 'All three keep the crew room at 1 bar. B keeps the mass of today\'s pod; C costs 2-3 t in the Venus kit (not the shuttle).', fontsize=9)
plt.subplots_adjust(top=.92, bottom=.06, hspace=.3)
fig.savefig(os.path.join(HERE, 'b4s_rover_options.png'), facecolor=BG)
