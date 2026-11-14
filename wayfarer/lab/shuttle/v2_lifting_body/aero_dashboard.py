"""Charts for aero_results.json. ALL bodies. ALL sponsors. 2026-2226."""
import json, os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(os.path.join(HERE, 'aero_results.json')))
VEH = list(R['vehicles']); COL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']   # validated default categorical slots 1-4
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK})
fig, ax = plt.subplots(3, 2, figsize=(11, 12.5), dpi=110); fig.patch.set_facecolor(SURF)
def style(a, t, unit=''):
    a.set_facecolor(SURF); a.set_title(t, loc='left', fontsize=11, weight='bold'); a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
    for s in ('top', 'right', 'left'): a.spines[s].set_visible(False)
    a.tick_params(length=0); a.set_ylabel(unit)
def bars(a, worlds, key, src, fmt='{:.0f}', log=False):
    x = np.arange(len(worlds)); bw = 0.8 / len(VEH)
    for i, v in enumerate(VEH):
        vals = [src[w][v][key] for w in worlds]
        b = a.bar(x + (i - 1.5) * bw, vals, bw - 0.03, color=COL[i], label=v)
        if i in (0, 1):
            for xx, vv in zip(x + (i - 1.5) * bw, vals): a.text(xx, vv * (1.06 if log else 1) + (0 if log else max(vals) * 0.01), fmt.format(vv), ha='center', va='bottom', fontsize=7, color=INK2)
    a.set_xticks(x); a.set_xticklabels(worlds)
    if log: a.set_yscale('log')
a = ax[0, 0]; style(a, 'Hypersonic L/D vs angle of attack (Newtonian, on the meshes)', 'L/D')
for i, v in enumerate(VEH):
    p = R['hyper_polar'][v]; a.plot([q['alpha'] for q in p], [q['LD'] for q in p], color=COL[i], lw=2, label=v)
a.axvline(40, color=GRID, lw=1); a.text(40.5, 0.05, 'v2 entry\nalpha 40', fontsize=7, color=INK2); a.set_xlabel('alpha (deg)'); a.set_ylim(0, 1.8)
a.legend(frameon=False, fontsize=8, loc='upper right')
W4 = ['Venus', 'Earth', 'Mars', 'Titan']
bars(ax[0, 1], W4, 'crossrange_km', R['entry']); style(ax[0, 1], 'Entry cross-range (bank 60 deg, from low orbit)', 'km')
bars(ax[1, 0], W4, 'peak_g', R['entry'], '{:.1f}'); style(ax[1, 0], 'Peak entry deceleration', 'Earth g')
bars(ax[1, 1], W4, 'peak_q_Wcm2', R['entry']); style(ax[1, 1], 'Peak nose heating (Sutton-Graves)', 'W/cm2')
a = ax[2, 0]; style(a, 'Subsonic glide: max L/D, wings deployed', 'L/D max')
lv = [R['landing']['Venus'][v]['LDmax'] for v in VEH]
a.bar(range(4), lv, 0.6, color=COL)
for i, v in enumerate(lv): a.text(i, v + 0.05, f'{v:.1f}', ha='center', fontsize=8, color=INK2)
a.set_xticks(range(4)); a.set_xticklabels([v.replace(' ', '\n', 1) for v in VEH])
W6 = ['Venus', 'Titan', 'Earth', 'Mars', 'Triton', 'Pluto']
bars(ax[2, 1], W6, 'v_td', R['landing'], '{:.0f}', log=True); style(ax[2, 1], 'Unpowered touchdown speed at alpha 15 (log)', 'm/s')
ax[2, 1].axhline(100, color=INK2, lw=1, ls='--'); ax[2, 1].text(5.45, 112, 'Space Shuttle\n~100 m/s', fontsize=7, color=INK2, ha='right')
fig.suptitle('Shuttle aero test - v1 vs v2 angular family across solar-system atmospheres (ROM, NON-CANON)', x=0.03, ha='left', fontsize=13, weight='bold')
fig.text(0.03, 0.005, 'Entry masses 45 t (Venus/Titan, kit aboard) / 35 t (Earth/Mars) + variant deltas. Wings stowed for entry, deployed for glide. '
         'Venus VIRA; other atmospheres approximate tables. Methods in aero_test.py.', fontsize=7.5, color=INK2)
plt.tight_layout(rect=[0, 0.015, 1, 0.97]); fig.savefig(os.path.join(HERE, 'aero_dashboard.png'), facecolor=SURF)
