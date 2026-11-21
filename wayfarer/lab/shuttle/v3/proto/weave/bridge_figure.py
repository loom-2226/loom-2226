"""Bridge figure. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); S = json.load(open(os.path.join(H, 'weave_bridge_series.json'))); R = json.load(open(os.path.join(H, 'weave_bridge.json')))
INK, MUTED, BG, PANEL, SPEC = '#1d2328', '#5b6670', '#eef0ef', '#f8f8f6', '#b8392f'; COL = ['#7a5cff', '#d9611b', '#2a9d5c']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.edgecolor': '#9aa3aa', 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.labelcolor': INK})
fig, (a, b) = plt.subplots(1, 2, figsize=(15, 5.8)); fig.patch.set_facecolor(BG)
fig.suptitle('Bridge test: the shuttle moves because spacetime moves; a relational mode keeps the books (NON-CANON)', x=.012, ha='left', fontsize=13.5, weight='bold', color=INK)
t = np.array(S['t'])
for ax in (a, b): ax.set_facecolor(PANEL); ax.grid(color='#dde1e3', lw=.6); [ax.spines[s].set_visible(False) for s in ('top', 'right')]
a.semilogy(t, np.maximum(S['con_felt'], 1e-4), color=COL[1], lw=2.4, label='ordinary force on the hull (4b0afba situation)')
a.semilogy(t, np.maximum(S['geo_felt'], 1e-4), color=COL[0], lw=2.4, label='carried by the moving shift geometry (Weave)')
a.set_ylim(1e-4, 50); a.set_xlabel('time (s)'); a.set_ylabel('acceleration felt by the crew (g, log)'); a.legend(frameon=False, fontsize=8.8, loc='center right')
a.set_title(f"Same 200 m, 125 m/s trajectory: crew feel {R['contact']['max_felt_crew_g']:.1f} g vs {R['geometric']['max_felt_crew_g']:.3f} g", fontsize=10, loc='left', color=INK)
a.text(.02, .05, 'Residual ~0.01 g = wall-profile gradient across the 10 m domain (derived, shrinks with a flatter plateau)', transform=a.transAxes, fontsize=8, color=INK)
b.plot(t, np.array(S['geoX']), color=COL[0], lw=2.2, label='shuttle position (m)')
b2 = b.twinx(); b2.plot(t, np.array(S['P']) / 1e6, color=COL[2], lw=2, ls='--', label='payload momentum (MN·s)'); b2.set_ylabel('payload momentum (MN·s)', color=COL[2]); b2.spines['top'].set_visible(False)
b.set_xlabel('time (s)'); b.set_ylabel('shuttle position (m)')
b.set_title('Momentum the relational mode must take; it ends shifted by %.0e m' % R['exchange']['relational_mode_residual_m'], fontsize=10, loc='left', color=INK)
b.text(.02, .9, 'DERIVED: geodesic transport (felt g ~ 0)\nASSUMED: the wall hands the payload momentum to the relational mode\n(the one link still needing a field model)', transform=b.transAxes, fontsize=8.3, color=SPEC, va='top')
fig.tight_layout(rect=(0, 0, 1, .93)); fig.savefig(os.path.join(H, 'weave_bridge.png'), dpi=110, facecolor=BG); print('ok')
