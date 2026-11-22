"""First experimental flight: what the ocean did. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(H, 'first_flight.json'))); S = np.load(os.path.join(H, 'first_flight_snaps.npz'))
INK = '#1f2933'; MUT = '#6b7280'; SH = '#2563eb'; SEA = '#0e7490'; WARN = '#d97706'
plt.rcParams.update({'font.size': 9.5, 'axes.edgecolor': MUT, 'axes.spines.top': False, 'axes.spines.right': False, 'xtick.color': MUT, 'ytick.color': MUT})
s = D['series']; t = np.array(s['t']); Z = np.array(s['Z']); u = np.array(s['under']); eq = np.array(s['eq']); wE = np.array(s['wave_E'])
f = plt.figure(figsize=(13, 9.8)); f.suptitle("Tic Tac first flight: 30 m sidestep, then down to 10 m over calm sea and back (NON-CANON)", x=0.02, ha='left', y=0.985, color=INK, fontsize=13)
ss = D['sidestep']; w = D['water']
f.text(0.02, 0.948, f"Sidestep at 24 m: {ss['peak_accel_g']} g, {ss['peak_speed_ms']} m/s peak; crew feel {ss['crew_peak_g']} g; field edge Mach {ss['field_edge_mach']}; no water response.  "
       f"Bowl appears below ~{w['bowl_first_appears_at_Z_m']:.0f} m; {w['max_depth_during_hold_m']} m deep at 10 m; {w['wave_energy_left_MJ']} MJ of waves left behind.", color=MUT, fontsize=9.3)
a = f.add_axes([0.06, 0.6, 0.88, 0.3])
for a0, b0, lab in D['profile']:
    a.axvspan(a0, b0, color='#f1f5f9' if lab in ('hover',) else '#e0f2fe', alpha=0.6, lw=0)
    if b0 - a0 > 4: a.text((a0 + b0) / 2, 25.5, lab, ha='center', fontsize=8.5, color=MUT)
a.annotate('30 m sidestep, 0.5 s', xy=(5.25, 24), xytext=(7, 21.5), fontsize=8.5, color=INK, arrowprops=dict(arrowstyle='->', color=INK, lw=0.8))
a.plot(t, Z, color=SH, lw=2, label='field centre height Z (m)'); a.axhline(19, color=MUT, ls=':', lw=1); a.text(74.5, 19.4, '~19 m', ha='right', fontsize=8, color=MUT)
a.plot(t, -u, color=SEA, lw=2, label='bowl depth under her (m), dynamic'); a.plot(t, -eq, color=SEA, lw=1, ls='--', label='bowl depth if the sea kept up (static)')
a2 = a.twinx(); a2.plot(t, wE / 1e6, color=WARN, lw=1.4, label='sea energy away from rest (MJ): released as waves'); a2.set_ylabel('MJ', color=WARN); a2.tick_params(colors=WARN); a2.spines['top'].set_visible(False)
a.set_xlim(0, 75); a.set_ylim(0, 27); a.set_xlabel('time (s)'); a.set_ylabel('m')
h1, l1 = a.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels(); a.legend(h1 + h2, l1 + l2, loc='center right', frameon=False, fontsize=8.5)
keys = ['20', '29', '36', '44', '50', '62']; titles = {'20': 'descending, Z 16.3 m', '29': 'arriving at 10 m', '36': 'holding at 10 m', '44': 'start of climb', '50': 'climbing, Z 16 m', '62': '4 s after she is back at 24 m'}
for i, k in enumerate(keys):
    ax = f.add_axes([0.04 + i * 0.16, 0.08, 0.145, 0.38]); e = S[k]
    ax.imshow(e.T, origin='lower', cmap='RdBu_r', vmin=-6, vmax=6, extent=[-90, 130, -110, 110]); ax.set_xlim(-40, 80); ax.set_ylim(-60, 60)
    ax.set_title(f't = {k} s\n{titles[k]}', fontsize=8.5, color=INK, loc='left'); ax.set_xticks([]); ax.set_yticks([])
    ax.text(-38, -57, f'min {e.min():.1f} m', fontsize=7.5, color=INK)
f.text(0.04, 0.03, 'Sea surface from above (blue = below calm level, red = above), 120 m x 120 m window. Linear deep-water model: no breaking, spray or foam; rim slopes reach ~31 deg, where real water would likely whiten.', fontsize=8.6, color=MUT)
f.savefig(os.path.join(H, 'weave_first_flight.png'), dpi=150, facecolor='white')
