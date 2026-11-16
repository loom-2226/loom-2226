"""Picture for nacelle_mass_screen.json. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'nacelle_mass_screen.json')))
INK, MUTE, BG = '#0b0b0b', '#52514e', '#fcfcfb'
BLUE, GREEN, AMBER, RED = '#2a78d6', '#1baf7a', '#d99a1e', '#c8432f'
hw = d['hardware_mid_t']; need = d['need_t']; free = d['basis']['free_above_floor_t']; cred = d['credit_t']['mid']
labels = {'shell': 'shells', 'frames_rails_trunk_tray': 'frames + rails', 'thermal_shroud': 'heat shroud',
          'parallel_links_actuators': 'links + drives', 'tail_arms': 'tail arms', 'arm_hinges_latches': 'hinges + latches', 'hard_points': 'hard points'}
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=150); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
fig.text(.03, .93, 'Four nacelles + aft ring: does the mass fit?', fontsize=14, weight='bold', color=INK)
fig.text(.03, .875, 'NON-CANON screen. Dry mass is fixed at 868.192 t, so new hardware must come out of the reserve.', fontsize=9.5, color=MUTE)
# row 1: what it needs (median breakdown, scaled to the median need incl. growth)
scale = need['mid'] / sum(hw.values()); x = 0
shades = ['#1f5fa8', '#2a78d6', '#4f93e0', '#76abe8', '#9cc3ef', '#bdd6f4', '#d9e7f8']
for (k, v), c in zip(hw.items(), shades):
    w = v * scale; ax.barh(1, w, left=x, height=.5, color=c, edgecolor=BG, lw=2)
    if w > .55: ax.text(x + w / 2, 1, labels[k], ha='center', va='center', fontsize=7.5, color='white' if c in shades[:3] else INK, rotation=0 if w > 1.1 else 90)
    x += w
ax.plot([need['p5'], need['p95']], [1.36, 1.36], color=INK, lw=1.2); ax.plot([need['p5']] * 2, [1.31, 1.41], color=INK, lw=1.2); ax.plot([need['p95']] * 2, [1.31, 1.41], color=INK, lw=1.2)
ax.text(need['p95'] + .1, 1.36, f"needs {need['p5']:.1f}–{need['p95']:.1f} t (middle {need['mid']:.1f})", va='center', fontsize=9, color=INK)
# row 2: what is available without lowering the floor
ax.barh(0, cred, height=.5, color=GREEN, edgecolor=BG, lw=2); ax.barh(0, free, left=cred, height=.5, color='#7fd3b1', edgecolor=BG, lw=2)
ax.text(cred + free + .12, 0, f"available {cred + free:.1f} t: hull-mount credit {cred:.1f} + free reserve {free:.2f}", va='center', fontsize=9, color=INK)
gap = d['gap_vs_free_t']
ax.annotate('', xy=(need['mid'], -.42), xytext=(cred + free, -.42), arrowprops=dict(arrowstyle='<->', color=RED, lw=1.4))
ax.text((need['mid'] + cred + free) / 2, -.62, f"short by about {gap['mid']:.1f} t  (range {gap['p5']:.1f}–{gap['p95']:.1f})", ha='center', fontsize=9.5, color=RED, weight='bold')
ax.set_yticks([1, 0]); ax.set_yticklabels(['needs', 'has'], fontsize=10)
ax.set_xlim(0, 11.5); ax.set_ylim(-.85, 1.65); ax.set_xlabel('tonnes', color=MUTE, fontsize=9)
for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(MUTE); ax.tick_params(colors=MUTE, length=0)
plt.subplots_adjust(left=.09, right=.97, top=.82, bottom=.13)
fig.savefig(os.path.join(HERE, 'nacelle_mass_screen.png'), facecolor=BG)
