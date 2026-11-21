"""Concept visuals for the Builder prototype lane. ALL bodies. ALL sponsors. 2026-2226.
Hull from the explorer engine (#2643 params); everything labelled CONCEPT / PROTOTYPE is unverified packaging."""
import sys, os, json, math, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon, Circle, Rectangle, Ellipse, FancyBboxPatch
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'explorer'))
import engine as E
D = json.load(open(os.path.join(H, '..', 'explorer', 'explorer_results.json'))); by = {r['id']: r for r in D['results']}
P = dict(by[2643]['params'], span=17.0, chord=1.8, wildcard='osteon_cautious+programmable')
V, F, K, base_ids, st = E.loft(P); T0 = V[F]
INK, HULL, BELLY, GLASS, WING, FAN, ACC, WATER, FIELD = '#1d2328', (.86, .87, .85), (.17, .17, .19), (.22, .40, .58), (.78, .80, .79), (.25, .27, .30), '#d9611b', '#2f6e9c', '#7a5cff'
def hull_parts(state):
    cz = T0[:, :, 2].mean(1); cx = T0[:, :, 0].mean(1); ny = np.cross(T0[:, 1] - T0[:, 0], T0[:, 2] - T0[:, 0])[:, 2]
    cols = [BELLY if (z < -0.2) else (GLASS if (2.6 < x < 4.6 and z > 0.5) else HULL) for z, x in zip(cz, cx)]
    parts = [(T0, np.array(cols, float))]
    if state in ('flight', 'hover'):
        half = P['span'] / 2; ch = P['chord']
        for s in (1, -1):
            q = np.array([(6.2, s * 2.05, 0.15), (6.2 + ch * 1.5, s * 2.05, 0.15), (7.4 + ch * 1.2, s * half, 0.45), (7.0 + 0.3, s * half, 0.45)])
            for dz in (0, .1):
                qq = q + [0, 0, dz]; parts.append((np.array([qq[[0, 1, 2]], qq[[0, 2, 3]]]), np.tile(WING, (2, 1))))
            for k, (fx, fy) in enumerate(((7.0, 3.3), (7.5, 5.0))):     # fans set in the inner wing (2 x 2 per side, schematic)
                th = np.linspace(0, 2 * np.pi, 25); r = 0.78
                ring = np.c_[fx + r * np.cos(th), s * fy + r * np.sin(th), np.full_like(th, 0.58)]
                c = np.array([fx, s * fy, 0.58]); parts.append((np.array([[c, ring[i], ring[i + 1]] for i in range(24)]), np.tile(FAN, (24, 1))))
    nz = np.array([[(12.8, -0.6, -0.2), (13.7, -0.9, -0.5), (13.7, 0.9, -0.5)], [(12.8, -0.6, -0.2), (13.7, 0.9, -0.5), (12.8, 0.6, -0.2)]]); parts.append((nz, np.tile((.45, .45, .48), (2, 1))))
    return parts
def proj(pts, az, el):
    a, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return pts @ (Rx @ Rz).T
def draw3d(ax, parts, az, el, off=(0, 0, 0), scale=1.0, z0=0.0, light=(-.35, -.75, .55)):
    T = np.vstack([p[0] for p in parts]) - [6.4, 0, 0]; C = np.vstack([p[1] for p in parts])
    Vv = proj(T * scale, az, el) + np.array(off); n = np.cross(Vv[:, 1] - Vv[:, 0], Vv[:, 2] - Vv[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    L = np.array(light) / np.linalg.norm(light); sh = np.clip(.45 + .65 * np.abs(n @ L), 0, 1.1); o = np.argsort(-Vv[:, :, 1].mean(1))
    cols = np.clip(C[o] * sh[o][:, None], 0, 1)
    ax.add_collection(PolyCollection(Vv[o][:, :, [0, 2]], facecolors=cols, edgecolors=cols, linewidths=.4, zorder=3))
def tag(ax, x, y, text, color, fs=8.5, ha='left'):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va='top', transform=ax.transAxes, bbox=dict(boxstyle='round,pad=.3', fc='white', ec=color, lw=1, alpha=.92), zorder=10)
fig = plt.figure(figsize=(18, 12.5)); fig.patch.set_facecolor('#eef0ef')
# ---------------------------------------------------------------- A. stowed in Wayfarer (2-D schematic from the geometry record)
a = fig.add_axes([0.01, 0.53, 0.37, 0.41]); a.set_facecolor('#f7f7f5')
a.add_patch(Rectangle((11.0, -4.5), 23.3, 9.0, fc='#e3e6e6', ec=INK, lw=1))
a.add_patch(Rectangle((14, -2), 3, 4, fc='#b9a7d9', ec=INK, lw=.6)); a.text(15.5, 0, 'relational\nplant fore', ha='center', va='center', fontsize=7)
a.add_patch(Rectangle((32.3, -2), 2.0, 4, fc='#b9a7d9', ec=INK, lw=.6)); a.text(33.3, 0, 'plant\naft', ha='center', va='center', fontsize=7)
a.add_patch(Rectangle((32.3, 2), 2.0, 2.48, fc='#d6b38a', ec=INK, lw=.6)); a.add_patch(Rectangle((32.3, -4.48), 2.0, 2.48, fc='#d6b38a', ec=INK, lw=.6)); a.text(33.3, 3.2, 'torch\nmanifold', ha='center', fontsize=6.5)
for z0, z1 in ((2.45, 4.28), (-4.28, -2.45)): a.add_patch(Rectangle((18, z0), 13.5, z1 - z0, fc='#9cc3e6', ec=INK, lw=.5))
a.text(24.7, 3.35, 'remass tank (annulus round the bay)', ha='center', fontsize=7.5)
a.add_patch(Rectangle((17, 2), 1, 2.3, fc='#f4d03f', ec=INK, lw=.5)); a.add_patch(Rectangle((17, -4.3), 1, 2.3, fc='#f4d03f', ec=INK, lw=.5)); a.text(17.5, -4.45, 'x17-18\nband', ha='center', va='top', fontsize=6.5)
a.add_patch(Rectangle((14, 2), 3, 2.3, fc='none', ec='#2f8a4e', ls='--', lw=1.2)); a.text(15.5, 4.55, 'free 87 m³ (record):\nband moves here', ha='center', fontsize=6.5, color='#2f8a4e')
a.add_patch(Rectangle((11.0, -4.5), 2.7, 9.0, fc='#d5dbe0', ec=INK, lw=.6)); a.text(12.3, 0, 'habitat\nL5', ha='center', va='center', fontsize=7)
a.add_patch(Rectangle((18.25, -2.4), 13.8, 4.8, fc='none', ec=INK, lw=1.4)); a.add_patch(Rectangle((17.0, -2.4), 15.3, 4.8, fc='none', ec='#2f8a4e', lw=1.4, ls='--'))
xs = np.linspace(0, 12.8, 30); top = [np.interp(x, K[:, 0], K[:, 1]) for x in xs]; bot = [E.section(K, x, P['keel'])[4][1] for x in xs]
for x0, col, lab in ((18.75, INK, '12.8 m today'), ):
    a.fill_between(x0 + xs, np.array(bot) - 0.1, np.array(top) - 0.1, color='#8a939b', alpha=.9, zorder=4)
a.text(25.1, -2.15, 'shuttle (rolled 90° when stowed; drawn unrolled)', ha='center', fontsize=7, color='w', zorder=5)
a.text(18.3, 2.55, 'bay 12.8 m', fontsize=7.5); a.text(19.0, -2.9, '14.3 m option bore x 17.0-32.3 (no remass lost)', fontsize=7, color='#2f8a4e')
a.set_xlim(10.8, 35); a.set_ylim(-5.2, 5.6); a.set_aspect('equal'); a.axis('off')
a.set_title('A  Stowed in Wayfarer (side schematic from the geometry record)', loc='left', fontsize=12, weight='bold')
tag(a, .01, .085, 'VERIFIED: bay, tank, plant and band positions (geometry record)\nNOT VERIFIED: morphing wing, fans, floats stowed in the bay; 14.3 m relocation; trim', '#b8392f', 8)
s = fig.add_axes([0.385, 0.56, 0.11, 0.32]); s.set_facecolor('#f7f7f5')
s.add_patch(Circle((0, 0), 4.48, fc='#e3e6e6', ec=INK)); th = np.linspace(0, 2 * np.pi, 400)
s.add_patch(Circle((0, 0), 4.28, fc='#9cc3e6', ec=INK, lw=.5)); s.add_patch(Circle((0, 0), 2.45, fc='#f7f7f5', ec=INK, lw=.5)); s.add_patch(Rectangle((-2.4, 0), 4.8, 4.6, fc='#f7f7f5', ec='none'))
sec = E.section(K, 9.0, P['keel']); rot = np.c_[sec[:, 1], sec[:, 0]]                    # rolled 90 deg: span axis vertical
s.add_patch(Polygon(rot + [-0.2, 0.1], fc='#8a939b', ec=INK))
s.add_patch(Rectangle((-0.2 + 1.35, -1.9), 0.18, 3.9, fc='#7a8b99', ec=INK, lw=.4)); s.add_patch(Rectangle((-0.2 - 1.55, -1.9), 0.18, 3.9, fc='#7a8b99', ec=INK, lw=.4))
s.text(0, -4.95, 'x 25 section: hull rolled 90°,\nwing panels folded flat (concept)', ha='center', va='top', fontsize=6.5)
s.set_xlim(-4.8, 4.8); s.set_ylim(-6.2, 4.8); s.set_aspect('equal'); s.axis('off')
# ---------------------------------------------------------------- B. deployed for atmospheric flight
b = fig.add_axes([0.50, 0.53, 0.49, 0.41]); b.set_facecolor('#dfe9f1')
draw3d(b, hull_parts('flight'), 32, 24)
b.set_xlim(-11, 11); b.set_ylim(-6.5, 5.5); b.set_aspect('equal'); b.axis('off')
b.set_title('B  Deployed for atmospheric flight: morphing wing out to 17 m, lift fans in the wing', loc='left', fontsize=12, weight='bold')
tag(b, .01, .99, 'PROTOTYPE LANE (non-canon): programmable structure (W1) + Osteon cautious\nmodel: dry 38.4 t, glide L/D 7.0, hot-extraction touchdown 44.3 m/s (limit 50), all five missions pass', ACC, 8.5)
tag(b, .01, .14, 'hull: explorer #2643 geometry (rough model)\nwing, fan and float placement: schematic, not packaged', '#5d6872', 7.5)
# ---------------------------------------------------------------- C. metric-assisted hot extraction storyboard
frames = [('1  Hover 8 m over the water inside the metric envelope', 0.02), ('2  Rise to 2 km on the field: no exhaust over people', 0.345), ('3  Torch lights at 2 km, climbs to orbit', 0.67)]
for i, (title, x0) in enumerate(frames):
    c = fig.add_axes([x0, 0.06, 0.315, 0.40]); c.set_facecolor('#cfe0ee' if i < 2 else '#bcd3ea')
    if i == 0:
        c.add_patch(Rectangle((-12, -8), 24, 3.0, fc='#4f7fa6', ec='none', zorder=1))
        for k in range(14): c.plot([-12 + k * 1.8, -11.1 + k * 1.8, -10.2 + k * 1.8], [-5.0, -4.75, -5.0], color='w', lw=.8, zorder=2)
        for px in (-7.5, -6.2, -5.0): c.add_patch(Ellipse((px, -4.6), 0.9, 0.5, fc='#f39c12', ec=INK, lw=.5, zorder=2)); c.plot([px, px], [-4.4, -3.6], color=INK, lw=1.5, zorder=2); c.add_patch(Circle((px, -3.4), .18, fc=INK, zorder=2))
        c.text(-6.3, -6.3, 'evacuees in floats', ha='center', fontsize=7.5, color='w', zorder=3)
        draw3d(c, hull_parts('hover'), 28, 12, off=(1.5, 0, 0.0))
        c.add_patch(Ellipse((1.5, 0.0), 19.5, 8.0, fc=FIELD, ec=FIELD, alpha=.13, lw=2, zorder=5)); c.text(1.5, 3.7, 'metric envelope (wall ≥ 1.5 m off the hull; must not touch the water)', ha='center', fontsize=7, color=FIELD, zorder=6)
        c.annotate('', xy=(-4.6, -3.2), xytext=(-2.4, -2.0), arrowprops=dict(arrowstyle='->', color=INK), zorder=6); c.text(-3.0, -1.6, 'ramp', fontsize=7, zorder=6)
    elif i == 1:
        draw3d(c, hull_parts('hover'), 28, 12, off=(0, 0, 1.0), scale=.75)
        c.add_patch(Ellipse((0, 1.0), 14.8, 6.2, fc=FIELD, ec=FIELD, alpha=.14, lw=2, zorder=5))
        c.add_patch(Rectangle((-12, -8), 24, 1.2, fc='#4f7fa6', ec='none'))
        for y in (-2.5, -4.0, -5.5): c.plot([-0.4, 0.4], [y, y], color=FIELD, lw=1, alpha=.6)
        c.annotate('', xy=(0, 4.8), xytext=(0, 3.9), arrowprops=dict(arrowstyle='-|>', color=FIELD, lw=2))
        c.text(-11.5, 4.9, '~20 s to 2 km, ~240 m/s\ncabin rides in free fall (no g)\n~3 GJ from a ~1 t flywheel at ~150 MW', fontsize=7.5, va='top', zorder=6)
    else:
        az3, el3, sc3, off3 = 152, 18, .7, np.array((1.5, 0, 0.5))
        draw3d(c, hull_parts('flight'), az3, el3, off=tuple(off3), scale=sc3)
        tail = proj(np.array([[13.6 - 6.4, 0, -0.35], [13.6 + 9 - 6.4, 0, -1.2]]) * sc3, az3, el3) + off3
        tx, tz = tail[0, 0], tail[0, 2]; ex, ez = tail[1, 0], tail[1, 2]; nx, nz_ = -(ez - tz), (ex - tx); nn = math.hypot(nx, nz_)
        c.add_patch(Polygon([(tx, tz), (ex + 0.9 * nx / nn, ez + 0.9 * nz_ / nn), (ex - 0.9 * nx / nn, ez - 0.9 * nz_ / nn)], fc='#ffd27a', ec='#ff9f1c', alpha=.9, zorder=2))
        c.text(-11.5, 4.9, 'torch at T/W 1.4, ~20 km/s exhaust\nhot-extraction water 21.3 of 23.1 t\n(8 t metric module case)', fontsize=7.5, va='top', zorder=6)
    c.set_xlim(-12, 12); c.set_ylim(-8, 5.2); c.set_aspect('equal'); c.axis('off'); c.set_title(title, loc='left', fontsize=10.5, weight='bold')
fig.text(0.02, 0.475, 'C  Metric-assisted hot extraction (W2 "cushion", PROTOTYPE LANE, non-canon). Needs a NEW effect: a powered metric that puts onboard energy into the ship\'s ordinary state (canon ENERGY-B forbids gaining height for free)\n'
         'and a shuttle relational module of ≤ 8-12 t (L² candidate scaling gives ~14 t). Numbers are REQUIRED values for the hypothesis, not results.', fontsize=9.5, color=FIELD)
fig.suptitle('Shuttle hero concept: Builder prototype lane (CONCEPT RENDERS: hull from the rough model; stowage, wing, fans, envelope and storyboard unverified)', fontsize=13.5, y=.995)
fig.savefig(os.path.join(H, 'hero_concepts.png'), dpi=105, facecolor=fig.get_facecolor())
