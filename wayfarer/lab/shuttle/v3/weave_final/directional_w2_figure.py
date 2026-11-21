"""Directional-W2 ascent: waste heat sets the ascent time. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(H, 'directional_w2_ascent.json')))
INK = '#1f2933'; MUT = '#6b7280'; C9 = '#d97706'; C12 = '#dc2626'; SH = '#2563eb'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': MUT, 'axes.spines.top': False, 'axes.spines.right': False, 'xtick.color': MUT, 'ytick.color': MUT})
W = D['fast_0p4g']['field_work_TJ'] * 1e12; tf = D['fast_0p4g']['t_s'] / 3600
eta = np.linspace(0.3, 0.999, 300)
f, a = plt.subplots(figsize=(11, 6.4)); f.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.12)
for T, c in ((900, C9), (1200, C12)):
    rad = 0.85 * 5.67e-8 * T ** 4 * 152.6; th = np.maximum(W * (1 / eta - 1) / rad / 3600, tf)
    a.plot(eta, th, color=c, lw=2.2); a.text(0.31, th[0] * 1.08, f'hull radiating at {T} K ({rad / 1e6:.0f} MW)', color=c, fontsize=9.5)
a.axhline(tf, color=SH, lw=1.2, ls='--'); a.text(0.31, tf * 0.78, f'fastest at the 0.4 g cap: {tf * 60:.0f} min', color=SH, fontsize=9.5)
a.axvline(0.48, color=MUT, lw=1, ls=':'); a.text(0.485, 300, 'lane cushion\nη 0.6 × conversion 0.8', color=MUT, fontsize=8.8)
a.set_yscale('log'); a.set_xlim(0.3, 1.0); a.set_ylim(0.4, 400)
a.set_xlabel('combined efficiency: field × source-to-field conversion'); a.set_ylabel('shortest ascent the hull can cool (hours)')
f.suptitle('Torchless Tic Tac: surface to Wayfarer on experimental directional W2 — waste heat sets the pace', x=0.02, ha='left', y=0.97, color=INK, fontsize=13)
f.text(0.02, 0.88, f"Energy, velocity match ({D['fast_0p4g']['v_rel_to_circular_ms']:.2f} m/s) and partner bookkeeping close. Field work {W / 1e12:.2f} TJ; peak {D['fast_0p4g']['P_field_peak_GW']:.1f} GW (reactor 7.7 GW: not limiting). "
       "The hull is the only radiator. A fast ascent would need ~640 t of water boiled at lane efficiency.", color=MUT, fontsize=9.2, wrap=True)
f.savefig(os.path.join(H, 'weave_directional_w2_ascent.png'), dpi=150, facecolor='white')
