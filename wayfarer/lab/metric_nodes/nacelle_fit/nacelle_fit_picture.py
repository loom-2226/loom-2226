"""Side elevation of the nacelle fit problem and fix. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
import nacelle_fit as F
HERE = os.path.dirname(os.path.abspath(__file__))
P = F.parts(F.GLB)
INK, MUTE, BG, GREY = '#0b0b0b', '#52514e', '#fcfcfb', '#c9cdd2'
BLUE, GREEN, RED, AMBER = '#2a78d6', '#1baf7a', '#c8432f', '#d99a1e'
def prof(k, xs):
    v = P[k]; r = np.hypot(v[:, 1], v[:, 2]); out = []
    for a, b in zip(xs[:-1], xs[1:]):
        m = (v[:, 0] >= a) & (v[:, 0] < b); out.append(r[m].max() if m.any() else np.nan)
    return np.array(out)
fig, axs = plt.subplots(1, 2, figsize=(12, 5.2), dpi=150, sharey=True); fig.patch.set_facecolor(BG)
fig.text(.03, .94, 'Fitting the nacelles: two clashes and a plume, and the fix', fontsize=14, weight='bold', color=INK)
fig.text(.03, .895, 'Side view along one nacelle line. NON-CANON check against the installed ship geometry. Dotted: fin parts 40° round, which only the full ring can reach.', fontsize=9.5, color=MUTE)
xs = np.linspace(33.5, 56, 226); xm = (xs[:-1] + xs[1:]) / 2
for ax, (title, rt, x1, hx, hR, cant, ok) in zip(axs, [('As sketched', 3.7, 53.5, 52.6, 4.4, 10, False), ('Fixed', 4.05, 54.3, 53.9, 4.6, 25, True)]):
    ax.set_facecolor(BG)
    for k, c, al in (('dry:nozzle', '#8f8a80', 1), ('dry:reactor', '#8f8a80', 1), ('dry:shield', '#8f8a80', 1), ('dry:thrust_cone', '#a7a39b', 1), ('dry:manifold', '#a7a39b', 1)):
        r = prof(k, xs); m = ~np.isnan(r); ax.fill_between(xm[m], 0, r[m], color=c, alpha=al, lw=0)
    ax.add_patch(Rectangle((39.3, 3.0), 14.0, 1.75, fc='none', ec='#9aa0a6', lw=.8, ls=':')); ax.text(53.1, 3.1, 'fin root\n(40° round)', fontsize=7, color=MUTE, ha='right')
    ax.add_patch(Rectangle((34.3, 4.76), 19.0, 2.0, fc='none', ec='#9aa0a6', lw=.8, ls=':')); ax.text(53.1, 6.45, 'folded fin pack (40° round)', fontsize=7, color=MUTE, ha='right')
    ax.add_patch(Rectangle((34.0, 4.37), .59, .59, color='#555', lw=0)); ax.text(34.3, 5.15, 'aft RCS', fontsize=7.5, ha='center')
    apex = np.array([34.59, 4.66]); a0 = np.radians(cant)
    for s in (-1, 1):
        a = a0 + s * np.radians(15); ax.plot([apex[0], apex[0] + 22], [apex[1], apex[1] + 22 * np.tan(a)], color=AMBER, lw=1, ls='--')
    ax.add_patch(Polygon([apex, [apex[0] + 22, apex[1] + 22 * np.tan(a0 - np.radians(15))], [apex[0] + 22, apex[1] + 22 * np.tan(a0 + np.radians(15))]], color=AMBER, alpha=.12, lw=0))
    ax.text(36.3, apex[1] + 1.6 * np.tan(a0 + np.radians(15)) + .55, f'aft thruster plume (cant {cant}°)', fontsize=8, color='#9a6a0c')
    ax.add_patch(Rectangle((39.5, rt - .6), x1 - 39.5, 1.2, fc=BLUE, alpha=.85, lw=0)); ax.text(41.5, rt, 'tucked', color='white', fontsize=8, va='center')
    ax.add_patch(Rectangle((39.5, 4.0), x1 - 39.5, 1.2, fc='none', ec=BLUE, lw=1.2, ls=(0, (3, 2)))); ax.text(41.5, 4.95, 'deployed', color=BLUE, fontsize=8)
    ax.add_patch(Circle((hx, hR), .35, fc=GREEN, ec='none')); ax.text(hx + .5, hR + .45, 'ring', color=GREEN, fontsize=8.5, weight='bold')
    if not ok:
        ax.annotate('touches the nozzle lip\n(0.01 m)', xy=(53.2, 3.15), xytext=(48.2, 1.0), fontsize=8.5, color=RED, arrowprops=dict(arrowstyle='->', color=RED))
        ax.annotate('ring cuts through\nthe hot-fin roots', xy=(52.6, 4.6), xytext=(54.0, 7.3), fontsize=8.5, color=RED, arrowprops=dict(arrowstyle='->', color=RED))
        ax.text(47.3, 8.1, 'nacelles sit in the\nthruster plume', fontsize=8.5, color=RED)
    else:
        ax.text(39.6, 1.05, 'tucked 0.23 m off the nozzle\nring 1.3 m aft: 0.25 m clear of fin roots\nplume canted 25°: clears everything', fontsize=8.5, color='#127a55')
    ax.set_title(title, fontsize=11.5, color=INK, loc='left', weight='bold'); ax.set_xlim(33.5, 56.5); ax.set_ylim(0, 9.4)
    ax.set_xlabel('x from the bow, m', color=MUTE, fontsize=9)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'): ax.spines[sp].set_color(MUTE)
    ax.tick_params(colors=MUTE, labelsize=8)
axs[0].set_ylabel('radius from the ship axis, m', color=MUTE, fontsize=9)
plt.subplots_adjust(left=.06, right=.98, top=.84, bottom=.11, wspace=.08)
fig.savefig(os.path.join(HERE, 'nacelle_fit.png'), facecolor=BG)
