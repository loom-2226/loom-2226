"""Picture for manifold_resize_screen.json. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'manifold_resize_screen.json')))
INK, MUTE, BG = '#0b0b0b', '#52514e', '#fcfcfb'
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.6), dpi=150, gridspec_kw=dict(width_ratios=[1, 1.35]))
fig.patch.set_facecolor(BG)
fig.text(.03, .935, 'Torch chain: the radiator manifold carries far less heat than it did', fontsize=14, weight='bold', color=INK)
fig.text(.03, .885, 'NON-CANON screen. Jet power, fins, strakes, reactor, nozzle and shield unchanged. Nothing booked.', fontsize=9.5, color=MUTE)
for a in (a1, a2):
    a.set_facecolor(BG); [a.spines[s].set_visible(False) for s in ('top', 'right')]; a.spines['left'].set_color(MUTE); a.spines['bottom'].set_color(MUTE); a.tick_params(colors=MUTE)
q0, qn = d['duty_on_record_mw'], d['duty_now_mw']
a1.bar([0, 1], [q0, qn['torch']], color=['#b8bdc4', '#2a78d6'], width=.6, edgecolor=BG)
a1.errorbar([1], [qn['torch']], yerr=[[0], [qn['design_range'][1] - qn['torch']]], color=INK, capsize=5, lw=1.2)
a1.set_xticks([0, 1]); a1.set_xticklabels(['before torch-heat\npackage (v0.5.1)', 'now (v0.5.2)\n+35% margin'], fontsize=9)
a1.set_ylabel('heat through the manifold, MW', color=MUTE, fontsize=9)
a1.text(0, q0 + 8, f'{q0:.0f}', ha='center', fontsize=10, weight='bold'); a1.text(1, qn['design_range'][1] + 8, f"{qn['torch']:.0f}–{qn['design_range'][1]:.0f}", ha='center', fontsize=10, weight='bold')
a1.text(.5, -.3, 'The 1.4 GW of hot heat now goes straight\nto the 1,750 K fins on their own loops.', transform=a1.transAxes, ha='center', fontsize=8.5, color=MUTE)
a1.set_ylim(0, 440)
m = d['manifold_after_t']; s = d['conservative_saving_t']; gap = d['nacelle_gap_t']
a2.barh(2, d['manifold_seed_t'], color='#b8bdc4', height=.55, edgecolor=BG); a2.text(d['manifold_seed_t'] + 1, 2, f"{d['manifold_seed_t']:.0f} t today", va='center', fontsize=9.5)
a2.barh(1, m['mid'], color='#2a78d6', height=.55, edgecolor=BG); a2.plot([m['p5'], m['p95']], [1, 1], color=INK, lw=1.2)
[a2.plot([v, v], [.93, 1.07], color=INK, lw=1.2) for v in (m['p5'], m['p95'])]
a2.text(m['p95'] + 1, 1, f"{m['mid']:.0f} t resized ({m['p5']:.0f}–{m['p95']:.0f})", va='center', fontsize=9.5)
a2.barh(0, gap, color='#c8432f', height=.55, edgecolor=BG); a2.barh(0, s - gap, left=gap, color='#1baf7a', height=.55, edgecolor=BG)
a2.text(s + 1, 0, f"freed, counted low: {s:.0f} t\n{gap:.1f} t to nacelles, {s - gap:.0f} t back to reserve", va='center', fontsize=9)
a2.set_yticks([2, 1, 0]); a2.set_yticklabels(['manifold', 'manifold', 'freed'], fontsize=9.5); a2.set_xlim(0, 125); a2.set_xlabel('tonnes', color=MUTE, fontsize=9)
plt.subplots_adjust(left=.08, right=.98, top=.82, bottom=.22, wspace=.42)
fig.savefig(os.path.join(HERE, 'manifold_resize_screen.png'), facecolor=BG)
