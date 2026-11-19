"""Option B (big 1-bar cabin + Venus pod in the kit): how the pod becomes the Venus rover. Sketch, roughly to scale.
NON-CANON. ALL bodies. ALL sponsors. 2026-2226. Uses the B4 side-door egress (kT 'Rather go out the side', 2026-11-15)."""
import os, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch, Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTE, BG, TI, CAB, KIT, SKIN, GND = '#0b0b0b', '#52514e', '#fcfcfb', '#8f8a80', '#2a78d6', '#d99a1e', '#eef0f3', '#c9a27a'
fig = plt.figure(figsize=(9, 15), dpi=140); fig.patch.set_facecolor(BG)
fig.text(.04, .975, 'Option B: how the Venus pod becomes the rover', fontsize=15, weight='bold')
fig.text(.04, .962, 'Sketch, roughly to scale. NON-CANON. Starboard side door from B4; pod and chassis come in the Venus/Titan kit.', fontsize=9, color=MUTE)

# 1. side view: where the pod rides
ax = fig.add_axes([.04, .80, .92, .15]); ax.set_facecolor(BG)
body = [(0, .55), (.6, 1.25), (2.2, 2.2), (4, 2.45), (11.5, 2.4), (12.8, 1.9), (12.8, .2), (10, 0), (2, 0), (.4, .25)]
ax.add_patch(Polygon(body, fc=SKIN, ec=MUTE, lw=1.1))
ax.add_patch(FancyBboxPatch((2.9, .25), 5.9, 1.95, boxstyle='round,pad=0,rounding_size=.25', fc=CAB, ec=INK, lw=1, alpha=.85))
ax.text(5.85, 1.22, '1-bar cabin', ha='center', va='center', color='white', fontsize=10, weight='bold')
ax.add_patch(Rectangle((8.8, .25), 2.3, 1.95, fc='none', ec=CAB, lw=1, ls=(0, (3, 2))))
ax.add_patch(Circle((10.0, 1.2), 1.05, fc=TI, ec=INK, lw=1)); ax.text(10.0, 1.2, 'pod', ha='center', va='center', color='white', fontsize=9, weight='bold')
ax.add_patch(Rectangle((8.75, 1.0), .2, .4, fc=INK)); ax.annotate('hatch: crew walk\nfrom cabin to pod', xy=(8.85, 1.4), xytext=(5.6, 2.75), fontsize=8.5, arrowprops=dict(arrowstyle='->', color=INK))
ax.text(11.25, 2.75, 'dashed: cabin space on\nnon-Venus flights', fontsize=8, color=CAB)
ax.set_xlim(-.3, 14.5); ax.set_ylim(-.3, 3.4); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('1  On Venus trips the pod rides at the back, docked to the cabin', loc='left', fontsize=11.5, weight='bold')

# end-view section at the pod station (looking forward, starboard to the right)
def section(st):
    h, g = 0.6, -0.6                          # belly 0.6 m above ground on legs
    P = dict(bp=(-1.5, 0), bs=(1.5, 0), cs=(2.125, .7), ss=(1.6, 2.0), ts=(.9, 2.45), tp=(-.9, 2.45), sp=(-1.6, 2.0), cp=(-2.125, .7))
    return P, g
steps = [('2  Landed. Crew already in the pod', 'closed'), ('3  Side door opens: lower flank drops as a ramp, wing lifts as an awning', 'open'),
         ('4  Wheels unfold; the pod rolls out on its rails', 'rolling'), ('5  Down the ramp: a four-wheel crab-steer rover', 'out')]
for i, (title, st) in enumerate(steps):
    ax = fig.add_axes([.04, .60 - i * .185, .92, .165]); ax.set_facecolor(BG)
    P, g = section(st)
    ax.add_patch(Rectangle((-6, -1.2), 16, .6, fc=GND, ec='none')); ax.plot([-6, 10], [g, g], color='#8b6a48', lw=1)
    for sx in (-1.2, 1.2): ax.plot([sx, sx * 1.35], [0, g], color=INK, lw=2.5)          # legs
    sec = [P['bp'], P['bs'], P['cs'], P['ss'], P['ts'], P['tp'], P['sp'], P['cp']]
    ax.add_patch(Polygon(sec, fc=SKIN, ec='none', closed=True, alpha=1 if st == 'closed' else .55))
    edge = sec + [P['bp']] if st == 'closed' else [P['bs'], P['bp'], P['cp'], P['sp'], P['tp'], P['ts']]
    ax.plot(*zip(*edge), color=MUTE, lw=1.2)
    if st != 'closed':
        L = .6 / np.sin(np.radians(30)); ramp = [(1.5, 0), (1.5 + L * np.cos(np.radians(30)), g)]
        ax.plot(*zip(*ramp), color=INK, lw=4, solid_capstyle='round'); ax.text(ramp[1][0] + .1, g + .15, 'ramp 30°', fontsize=8)
        aw = [(.9, 2.45), (.9 + 2.0 * np.cos(np.radians(20)), 2.45 + 2.0 * np.sin(np.radians(20)))]
        ax.plot(*zip(*aw), color=INK, lw=4, solid_capstyle='round'); ax.text(aw[1][0] - .3, aw[1][1] + .15, 'wing as awning', fontsize=8)
    cx, cz, wheels = {'closed': (0, 1.2, 'folded'), 'open': (0, 1.2, 'folded'), 'rolling': (1.2, 1.25, 'half'), 'out': (5.2, g + 1.55, 'down')}[st]
    ax.add_patch(Circle((cx, cz), 1.05, fc=TI, ec=INK, lw=1.1, zorder=3))
    ax.add_patch(Circle((cx + .45, cz + .35), .18, fc='#bfe3f2', ec=INK, lw=.8, zorder=4))   # viewport
    if wheels == 'folded':
        ax.add_patch(Rectangle((cx - 1.0, .02), 2.0, .12, fc=INK, zorder=3))
        for s in (-1, 1): ax.add_patch(Circle((cx + s * 1.25, cz - .2), .45, fc='#3d3d3d', ec=INK, zorder=2))
    else:
        base = cz - 1.25 if wheels == 'down' else .08
        for s in (-1, 1):
            wx, wz = cx + s * 1.3, (g + .45) if wheels == 'down' else .45
            ax.plot([cx + s * .7, wx], [cz - .6, wz], color=INK, lw=3, zorder=2)
            ax.add_patch(Circle((wx, wz), .45, fc='#3d3d3d', ec=INK, zorder=3))
    if st == 'out':
        ax.add_patch(Rectangle((cx - .5, cz + 1.0), 1.0, .12, fc=KIT, zorder=4)); ax.text(cx + .6, cz + 1.25, 'Venus cooler + hot loop (kit)', fontsize=8, color='#9a6a0c')
        ax.annotate('', xy=(cx + 2.4, g + .3), xytext=(cx + 1.6, g + .3), arrowprops=dict(arrowstyle='->', lw=2, color=INK))
    if st == 'closed': ax.text(2.6, 1.0, 'starboard', fontsize=8, color=MUTE)
    ax.set_xlim(-3.2, 9.5); ax.set_ylim(-1.2, 3.6); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, loc='left', fontsize=11.5, weight='bold')
for i, n in enumerate(['End view through the pod, looking forward. Pod 2.1 m Ti sphere, 92 bar outside / 1 bar inside, 3 crew for the surface stint.',
                       'Coming home: drive back up the ramp, wheels fold, door closes, crew move back to the cabin after launch.',
                       'Off Venus, the pod and chassis stay in Wayfarer\'s hold and the back of the cabin is living space again.']):
    fig.text(.04, .035 - i * .013, '• ' + n, fontsize=8.6)
fig.savefig(os.path.join(HERE, 'b4_split_rover.png'), facecolor=BG)
