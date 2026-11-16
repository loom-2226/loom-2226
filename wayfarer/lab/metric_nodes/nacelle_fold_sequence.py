import math, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle
BG, INK, MUTE, NAC, ARM, FIN, TOR = '#fcfcfb', '#0b0b0b', '#52514e', '#2a78d6', '#1baf7a', '#e34948', '#a8a49c'
fig = plt.figure(figsize=(11, 12.6), dpi=110); fig.patch.set_facecolor(BG)
fig.text(.03, .982, 'How the four nacelles and the ring fold (sketch, not canon)', fontsize=15, weight='bold')
fig.text(.03, .952, 'Seen from behind the ship. The trick: the ring is not one piece. Each nacelle carries two short tail arms (an eighth of the ring each) that swing out like gates and latch to the neighbour\'s arm.', fontsize=9, color=MUTE, wrap=True)
AZ = [0, 90, 180, 270]
def view(ax, r_nac, fins, arm_frac, title, note):
    ax.set_facecolor(BG); ax.set_aspect('equal'); ax.axis('off')
    ax.add_patch(Circle((0, 0), 4.5, fill=False, ec='#c9c7c0', ls='--', lw=1)); ax.add_patch(Circle((0, 0), 3.0, fc=TOR, ec=MUTE)); ax.add_patch(Circle((0, 0), 2.1, fc='#8f8b82', ec=MUTE))
    for s in (40, 140, 220, 320):
        a = math.radians(s); r0, r1 = (4.75, 6.75) if fins == 'out' else ((4.75, 5.0) if fins == 'stowed' else (4.75, 5.75))
        ax.plot([r0 * math.cos(a), r1 * math.cos(a)], [r0 * math.sin(a), r1 * math.sin(a)], color=FIN if fins == 'out' else '#b9b6ae', lw=5 if fins == 'out' else 3, solid_capstyle='butt')
    for az in AZ:
        a = math.radians(az); cx, cy = r_nac * math.cos(a), r_nac * math.sin(a)
        # arms: each spans 45 deg of the ring when fully out; folded they lie along the nacelle (shown as a short stub beside it)
        for side in (-1, 1):
            if arm_frac > 0:
                ang = np.linspace(az, az + side * 45 * arm_frac, 30); R = r_nac - 0.15
                ax.plot(R * np.cos(np.radians(ang)), R * np.sin(np.radians(ang)), color=ARM, lw=5, solid_capstyle='round')
            else:
                t = np.array([-math.sin(a), math.cos(a)]) * side * 0.72; ax.plot([cx + t[0]], [cy + t[1]], 's', ms=6, color=ARM)
        ax.add_patch(Circle((cx, cy), .6, fc=NAC, ec=BG, lw=1.2, zorder=5))
    ax.set_xlim(-7.4, 7.4); ax.set_ylim(-7.4, 7.4)
    ax.set_title(title, fontsize=10.5, weight='bold'); ax.text(0, -8.1, note, ha='center', va='top', fontsize=8.6, color=MUTE, wrap=True)
steps = [(3.7, 'out', 0, '1  Burning', 'Nacelles tucked in between the hot fins.\nTail arms folded flat along each nacelle.'),
         (3.7, 'stowed', 0, '2  Torch off, fins fold', 'Cool-down. Hot fins fold to the hull.\nNothing else moves yet.'),
         (4.6, 'stowed', 0, '3  Nacelles swing out', 'Parallel links push each nacelle\n0.9 m outward, keeping it level.'),
         (4.6, 'stowed', 0.6, '4  Tail arms swing out', 'Each nacelle opens two arms\nlike gates, toward its neighbours.'),
         (4.6, 'stowed', 1.0, '5  Ring locks', 'Arm tips latch in pairs: a closed\nhoop. Nodes go live; jump allowed.'),
         (None, None, None, '', '')]
for i, (r, f, af, t, n) in enumerate(steps):
    if r is None: continue
    ax = fig.add_axes([.03 + (i % 3) * .32, .52 - (i // 3) * .42, .3, .36]); view(ax, r, f, af, t, n)
# side detail
ax = fig.add_axes([.67, .1, .3, .3]); ax.set_facecolor(BG); ax.axis('off'); ax.set_xlim(37, 59); ax.set_ylim(-4, 4); ax.set_aspect('equal')
ax.add_patch(plt.Rectangle((39.5, -.6), 14, 1.2, fc=NAC, ec=BG)); ax.text(46.5, 0, 'nacelle (14 m)', ha='center', va='center', color='white', fontsize=8, weight='bold')
ax.add_patch(plt.Rectangle((49.9, .62), 3.45, .28, fc=ARM)); ax.add_patch(plt.Rectangle((49.9, -.9), 3.45, .28, fc=ARM)); ax.text(51.6, 1.25, 'folded: arms lie along the tail', ha='center', fontsize=7.5, color=ARM)
ax.plot([53.35, 53.35], [.6, 3.6], color=ARM, lw=4, alpha=.45); ax.plot([53.35, 53.35], [-.6, -3.6], color=ARM, lw=4, alpha=.45); ax.text(53.8, 2.9, 'out: swing 90° on\na hinge at the tail', fontsize=7.5, color=ARM)
ax.set_title('One nacelle from the side: the tail arms', fontsize=10, weight='bold')
fig.text(.03, .08, 'Numbers: each arm is about 3.5 m long (an eighth of a 4.4 m-radius ring) and bows only ~0.35 m, so folded it sits snug beside its nacelle.\n'
         'Every hinge and latch carries the node lines (20 K, power, timing); a latch that does not report closed blocks the jump.\n'
         'Tucked at r 3.7 m (not 3.4) so they clear the nozzle exit (r 3.0). This fits canon\'s configuration lock: the geometry is fixed before a commit, and moving any of it aborts the jump.', fontsize=9, color=INK, va='top')
import os; fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nacelle_fold_sequence.png'), facecolor=BG)
