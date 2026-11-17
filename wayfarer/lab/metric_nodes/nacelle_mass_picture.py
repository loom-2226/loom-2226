"""Picture for nacelle_mass_screen.json (14 m vs 10 m nacelles). NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'nacelle_mass_screen.json')))
INK, MUTE, BG, RED, GREEN = '#0b0b0b', '#52514e', '#fcfcfb', '#c8432f', '#1baf7a'
free = d['basis']['free_above_floor_t']
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
fig.text(.03, .935, 'Four nacelles + aft ring: 14 m vs 10 m nacelles', fontsize=14, weight='bold', color=INK)
fig.text(.03, .885, 'NON-CANON screen. No credits counted until a booked part is shown to shrink. 16.8 t floor not lowered.', fontsize=9.5, color=MUTE)
rows = [('nacelle_14m', '14 m (chosen)', 2), ('nacelle_10m', '10 m', 1)]
for key, lab, y in rows:
    v = d['variants'][key]; n = v['need_t']; c = v['coverage']
    ax.barh(y, n['mid'], height=.46, color='#2a78d6' if y == 2 else '#76abe8', edgecolor=BG)
    ax.plot([n['p5'], n['p95']], [y, y], color=INK, lw=1.2); [ax.plot([q, q], [y - .07, y + .07], color=INK, lw=1.2) for q in (n['p5'], n['p95'])]
    ok = c['web_pieces'] == 1
    ax.text(n['p95'] + .15, y + .1, f"needs {n['mid']:.1f} t   short {v['gap_vs_free_t']['mid']:.1f} t", va='center', fontsize=9.5, color=INK, weight='bold')
    ax.text(n['p95'] + .15, y - .14, f"worst gap {c['max_gap_m']:.1f} m · evenness {c['load_cv']:.2f} · " + ('network joined' if ok else 'network SPLITS in 2'),
            va='center', fontsize=8.8, color=GREEN if ok else RED)
ax.barh(0, free, height=.46, color='#7fd3b1', edgecolor=BG)
ax.text(free + .15, 0, f'free reserve above the floor: {free:.2f} t', va='center', fontsize=9.5, color=INK)
ax.axvline(free, color=MUTE, lw=.8, ls=(0, (3, 3)))
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([r[1] for r in rows] + ['available'], fontsize=10)
ax.text(0, -.72, 'Today (no nacelles): worst gap 5.0 m, evenness 0.29. Lower evenness = more even.', fontsize=8.5, color=MUTE)
ax.set_xlim(0, 13); ax.set_ylim(-.9, 2.5); ax.set_xlabel('tonnes', color=MUTE, fontsize=9)
for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(MUTE); ax.tick_params(colors=MUTE, length=0)
plt.subplots_adjust(left=.14, right=.97, top=.84, bottom=.12)
fig.savefig(os.path.join(HERE, 'nacelle_mass_screen.png'), facecolor=BG)
