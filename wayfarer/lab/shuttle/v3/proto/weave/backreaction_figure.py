"""Relational back-reaction figure. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, sys, io, contextlib, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
with contextlib.redirect_stdout(io.StringIO()): import relational_backreaction as RB
R = json.load(open(os.path.join(H, 'relational_backreaction.json')))
INK, MUTED, BG, PANEL, SPEC = '#1d2328', '#5b6670', '#eef0ef', '#f8f8f6', '#b8392f'; COL = ['#2a9d5c', '#d9611b', '#7a5cff', '#1f77b4']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.3, 'axes.edgecolor': '#9aa3aa', 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.labelcolor': INK})
fig = plt.figure(figsize=(16, 10)); fig.patch.set_facecolor(BG)
fig.text(.012, .972, 'Relational back-reaction toy: the shuttle moves by trading momentum with the relational medium (NON-CANON)', fontsize=14.5, weight='bold', color=INK)
fig.text(.012, .948, 'Shuttle = its real 61 t. Medium = inertia μ, rest velocity u relative to the local body frame, share w. Translation-invariant coupling => momentum and centre of mass conserved exactly (checked).', fontsize=9.3, color=MUTED)
def clean(ax): ax.set_facecolor(PANEL); ax.grid(color='#dde1e3', lw=.6); [ax.spines[s].set_visible(False) for s in ('top', 'right')]
# (a) dash: shuttle path and actuator energy, local vs Sun-like medium
a = fig.add_axes([.05, .55, .42, .33]); clean(a)
o_loc = RB.run(RB.M_SH, RB.dash, RB.t, RB.SCEN['local medium (u=0)']); o_sun = RB.run(RB.M_SH, RB.dash, RB.t, RB.SCEN['Sun-like medium (u=29.8 km/s)'])
a.plot(RB.t, o_loc['_E'] / 1e9, color=COL[0], lw=2.4, label='energy into shuttle+field, local medium (GJ)')
a.plot(RB.t, np.abs(o_sun['_E']) / 1e9 / 100, color=COL[1], lw=2.2, ls='--', label='|same| with Sun-like medium, ÷100 (GJ)')
a2 = a.twinx(); a2.plot(RB.t, o_loc['_X'], color=MUTED, lw=1.2); a2.set_ylabel('shuttle position (m)', color=MUTED); a2.spines['top'].set_visible(False)
a.set_xlabel('time (s)'); a.set_ylabel('cumulative actuator energy (GJ)'); a.legend(frameon=False, fontsize=8.2, loc='upper left')
a.set_title('200 m start-dash-stop: ends at rest, net energy 0; the transient is what differs', fontsize=10, loc='left', color=INK)
a.text(.02, .08, 'local: peak 0.48 GJ (= ½mV², V=125 m/s) flows in and back out\nSun-like: ±227 GJ swings (233 GW peak), net still ~0', transform=a.transAxes, fontsize=8, color=INK)
# (b) hover / cycle harvesting vs medium velocity
b = fig.add_axes([.56, .55, .4, .33]); clean(b)
u = np.logspace(0, 6, 200); Pw = RB.M_SH * 9.81 * u
b.loglog(u, Pw, color=COL[1], lw=2.4, label='hover harvest power = m g u (vertical component)')
b.axhline(RB.M_SH * 9.81 * 1000 / 20, color=COL[0], lw=1.2, ls='--'); b.text(1.3, RB.M_SH * 9.81 * 1000 / 20 * 1.4, 'lift power for 1 km in 20 s (30 MW)', fontsize=8, color=COL[0])
for uu, lab in ((50, 'u_eff limit\n50 m/s'), (465, 'Earth rotation\n465 m/s (horizontal:\nno effect on hover)'), (29.8e3, 'Sun-like\n18 GW'), (370e3, 'cosmic\n221 GW')):
    b.axvline(uu, color=MUTED, lw=.8, ls=':'); b.text(uu * 1.1, 2e5, lab, fontsize=7.6, color=INK)
b.set_xlabel('medium rest-frame velocity relative to the local body, u (m/s)'); b.set_ylabel('energy harvested while hovering (W)'); b.set_ylim(1e5, 1e12)
b.set_title('Holding or lifting against a MOVING medium is an energy source', fontsize=10, loc='left', color=INK); b.legend(frameon=False, fontsize=8.2, loc='upper left')
# (c) inertia sweep
cax = fig.add_axes([.05, .1, .27, .32]); clean(cax)
mu = np.array([r['mu_kg'] for r in R['mu_sweep']]); disp = np.abs([r['medium_residual_m'] for r in R['mu_sweep']]); pk = np.array([r['peak_transient_J'] for r in R['mu_sweep']])
cax.loglog(mu, disp, 'o-', color=COL[2], lw=2, label='medium residual shift (m)')
cax2 = cax.twinx(); cax2.semilogx(mu, pk / 1e9, 's--', color=COL[3], lw=1.6, label='peak transient (GJ)'); cax2.set_ylabel('peak transient energy (GJ)', color=COL[3]); cax2.spines['top'].set_visible(False)
cax.axvline(61e3, color=MUTED, lw=.8, ls=':'); cax.text(7e4, 1e-14, 'shuttle\nmass', fontsize=8, color=MUTED)
cax.set_xlabel('medium inertia μ (kg)'); cax.set_ylabel('medium residual shift after the dash (m)')
cax.set_title('Medium inertia: large μ = invisible recoil', fontsize=10, loc='left', color=INK)
# (d) verdicts
d = fig.add_axes([.42, .04, .56, .4]); d.axis('off')
rows = [['Question (Sol test + Claude refinements)', 'Result'], ['Shuttle ends at rest 200 m away', 'YES (toy)'], ['Momentum and centre of mass conserved', 'YES, exact by symmetry (checked numerically)'],
        ['Reset without reversing the dash', 'YES: medium keeps a real shift −mΔx/μ (2e-18 m at Earth-scale μ)'], ['Net energy of a symmetric dash', '0 for any medium; transient ½mV² must be stored'],
        ['Hover / lift with a medium moving at u', 'harvests m·g·u: Sun-like 18 GW, cosmic 221 GW'], ['Requirement on the response kernel', 'non-local share < ~1e-3 (Sun), < ~1e-4 (cosmic)'],
        ['Wayfarer, same law', '200 m dash: 9.1 GJ transient; 0.268c: 4e21 J held by relational sector'],
        ['Does this DERIVE the mechanism?', 'NO: it shows what G_R must do (huge μ, locally anchored)'], ['Status', 'conservative toy mechanism: VIABLE, CONDITIONAL']]
tb = d.table(cellText=rows, loc='upper center', cellLoc='left', colWidths=[.4, .6]); tb.auto_set_font_size(False); tb.set_fontsize(8.5); tb.scale(1, 1.8)
for (r_, c_), cell in tb.get_celld().items():
    cell.set_edgecolor('#cfd5d8'); cell.set_facecolor('#e4e8ea' if r_ == 0 else 'white')
fig.savefig(os.path.join(H, 'relational_backreaction.png'), dpi=110, facecolor=BG); print('ok')
