"""Picture for manifold_bottom_up.json. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'manifold_bottom_up.json')))
INK, MUTE, BG = '#0b0b0b', '#52514e', '#fcfcfb'
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
fig.text(.03, .935, 'Radiator manifold, built up from its parts', fontsize=14, weight='bold', color=INK)
fig.text(.03, .885, f"NON-CANON. Sized for the worst real load, {d['duty_mw']['design']:.0f} MW (torch burn), with one strake loop lost. Nothing booked.", fontsize=9.5, color=MUTE)
P = d['parts_mid_t']; scale = d['transport_t']['mid'] / sum(P.values())
lab = {'pipes': 'pipes', 'lithium': 'lithium', 'insulation': 'insul.', 'pumps': 'pumps', 'exchangers': 'exchangers',
       'strake_root_interfaces': 'roots', 'valves_crossties': 'valves', 'accumulators_thaw': 'thaw', 'load_transfer_structure': 'structure'}
blues = ['#1f5fa8', '#2a78d6', '#4f93e0', '#76abe8', '#9cc3ef', '#5b86c0', '#3f6fb0', '#8fb4e3', '#2f5f9e']
x = 0
for (k, v), c in zip(P.items(), blues):
    w = v * scale; ax.barh(1, w, left=x, height=.5, color=c, edgecolor=BG, lw=1.5)
    if w > 6: ax.text(x + w / 2, 1, lab[k], ha='center', va='center', fontsize=7.5, color='white')
    x += w
c = d['torch_cryocooler']['t']
ax.barh(1, c['mid'], left=x, height=.5, color='#d99a1e', edgecolor=BG, lw=1.5)
ax.text(x + c['mid'] / 2, 1, 'torch magnet cryocooler\n(owner unresolved)', ha='center', va='center', fontsize=8, color=INK)
tot = d['case_A_cooler_inside_manifold']['total_t']
ax.plot([tot['p5'], tot['p95']], [1.38, 1.38], color=INK, lw=1.2); [ax.plot([q, q], [1.33, 1.43], color=INK, lw=1.2) for q in (tot['p5'], tot['p95'])]
ax.text(tot['p95'] + 1, 1.38, f"{tot['mid']:.0f} t ({tot['p5']:.0f}–{tot['p95']:.0f})", va='center', fontsize=9.5, weight='bold')
ax.barh(0, d['seed_manifold_t'], height=.5, color='#b8bdc4', edgecolor=BG); ax.text(d['seed_manifold_t'] + 1, 0, f"{d['seed_manifold_t']:.0f} t booked today (never sized)", va='center', fontsize=9.5)
ax.text(d['transport_t']['mid'] / 2, .62, f"heat transport {d['transport_t']['mid']:.0f} t", ha='center', fontsize=8.5, color=MUTE)
s = d['case_A_cooler_inside_manifold']['saving_t']
ax.text(0, -.62, f"If the cryocooler belongs in the 90 t: saving {s['p5']:.0f}–{s['p95']:.0f} t (middle {s['mid']:.0f}). "
        f"If not, its owner is still unknown.", fontsize=9, color=INK)
ax.set_yticks([1, 0]); ax.set_yticklabels(['bottom-up', 'seed'], fontsize=10); ax.set_xlim(0, 115); ax.set_ylim(-.8, 1.65)
ax.set_xlabel('tonnes', color=MUTE, fontsize=9)
for sp in ('top', 'right', 'left'): ax.spines[sp].set_visible(False)
ax.spines['bottom'].set_color(MUTE); ax.tick_params(colors=MUTE, length=0)
plt.subplots_adjust(left=.1, right=.97, top=.83, bottom=.13)
fig.savefig(os.path.join(HERE, 'manifold_bottom_up.png'), facecolor=BG)
