"""v2 'catamaran' belly rover concept sketch: the twin-sphere crew module is the rover.
NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, matplotlib, os
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, FancyBboxPatch
import build_v2b as B
HERE = os.path.dirname(os.path.abspath(__file__))
INK, RED, GREY, TPS, BLUE = '#1d2733', '#c0392b', '#dfe6ee', '#2b2b2b', '#2a78d6'
fig, ax = plt.subplots(2, 2, figsize=(11, 8.6), dpi=110, gridspec_kw=dict(width_ratios=[1, 1.5]))
fig.patch.set_facecolor('#f6f5f2')
def section(a, x, rover_down=0.0, title=''):
    P = np.array(B.section(x)); a.add_patch(Polygon(P, closed=True, fc=GREY, ec=INK, lw=1.4))
    a.plot([-1.85, 1.85], [-0.95, -0.95], color=TPS, lw=5)
    a.add_patch(Circle((0, 0), 2.15, fill=False, ec='#999', ls='--', lw=1))
    d = rover_down
    if d:  # belly panel lowered with the rover; opening left in the hull
        a.plot([-1.85, 1.85], [-0.95, -0.95], color='#f6f5f2', lw=6); a.plot([-1.85, 1.85], [-0.95, -0.95], color=INK, lw=1, ls=':')
    for s in (1, -1): a.add_patch(Circle((s * 1.0, 0.1 - d), 0.95, fc='#e8c7b8', ec=RED, lw=1.6))
    a.add_patch(Rectangle((-0.35, 0.1 - d - 0.33), 0.7, 0.66, fc='#e8c7b8', ec=RED, lw=1))
    a.add_patch(Rectangle((-1.85, -0.93 - d), 3.7, 0.08, fc=TPS, ec=TPS))            # rover floor = belly TPS panel
    for s in (1, -1):
        wy = s * 1.55
        if d: a.add_patch(Rectangle((wy - 0.18, -1.95 - d + 0.0), 0.36, 0.9, fc='#555', ec=INK)); a.plot([wy, wy], [-1.05 - d, -0.9 - d], color=INK, lw=3)
    if d: a.plot([-4, 4], [-1.95 - d, -1.95 - d], color='#8a7f6a', lw=2); a.text(0, -2.2 - d, 'Venus surface', ha='center', fontsize=8, color='#8a7f6a')
    a.set_xlim(-3.2, 3.2); a.set_ylim(-3.6 if d else -2.4, 2.3); a.set_aspect('equal'); a.axis('off'); a.set_title(title, loc='left', fontsize=10, weight='bold')
section(ax[0, 0], 7.8, 0, 'Section, stowed: rover is the crew cabin')
section(ax[1, 0], 7.8, 0.6, 'Section, landed: shuttle kneels, rover lowers out')
def plan(a, title, out=False):
    xs = np.linspace(0, 12.8, 200); hw = [max(abs(p[0]) for p in B.section(x)) for x in xs]
    a.fill_between(xs, -np.array(hw), hw, color=GREY, ec=INK, lw=1.2)
    dx = 0 if not out else 0
    a.add_patch(Rectangle((5.6, -1.85), 4.4, 3.7, fill=False, ec=TPS, lw=2.2, ls='--'))
    for s in (1, -1): a.add_patch(Circle((7.8, s * 1.0), 0.95, fc='#e8c7b8', ec=RED, lw=1.6))
    a.add_patch(Rectangle((7.45, -0.3), 0.7, 0.6, fc='#e8c7b8', ec=RED))
    for x in (6.0, 9.6):
        for s in (1, -1): a.add_patch(FancyBboxPatch((x - 0.45, s * 1.55 - 0.18), 0.9, 0.36, boxstyle='round,pad=0,rounding_size=0.15', fc='#555', ec=INK))
    for s in (1, -1): a.add_patch(Rectangle((5.6, s * 1.55 - 0.06), 4.4, 0.12, fc=BLUE, ec=BLUE))
    a.text(7.8, -2.45, 'rover 4.4 m long x 3.7 m wide (3.1 m track); belly panel = its floor', ha='center', fontsize=8)
    a.set_xlim(-0.3, 13.1); a.set_ylim(-2.8, 2.6); a.set_aspect('equal'); a.axis('off'); a.set_title(title, loc='left', fontsize=10, weight='bold')
plan(ax[0, 1], 'Plan, nose left: twin-sphere "catamaran" rover in the belly bay')
t = ax[1, 1]; t.axis('off')
rows = [('What it is', 'Option C from the 11-03 rover trade, rebuilt for v2: the\ntwin spheres + tunnel sit on a two-rail chassis. The belly\npanel under them is the rover floor and drops out with it.'),
        ('Wheels', '4 x 0.9 m, ahead of and behind the spheres; wheelbase\n3.6 m, track 3.1 m. They are also the main landing gear.'),
        ('Why it suits v2', 'Flat belly = natural rover bay. Wide track and low\nspheres = very stable on rough ground. Two spheres =\ntwo separable cabins (one can rescue the other).'),
        ('Cost (11-03 trade)', 'C vs A, 3 crew: ~+0.7 t core dry at midpoint. Adds\nwheel doors, a big TPS seam and rover landing loads.'),
        ('Open', 'TPS seam through the entry heat shield; hatch path to\nthe torch/kit while the rover is out; ascent re-dock.')]
for i, (k, v) in enumerate(rows):
    t.text(0, 1 - i * 0.205, k, fontsize=9, weight='bold', transform=t.transAxes, va='top')
    t.text(0.28, 1 - i * 0.205, v, fontsize=8.5, transform=t.transAxes, va='top')
fig.suptitle('Shuttle v2 - the rover comes back: twin-sphere belly rover (NON-CANON sketch)', x=0.03, ha='left', fontsize=13, weight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.96]); fig.savefig(os.path.join(HERE, 'rover_concept.png'), facecolor=fig.get_facecolor())
