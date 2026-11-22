"""Scale privilege figure. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math, sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): import dash_scaling as S
INK, MUTED, BG, PANEL, SPEC = '#1d2328', '#5b6670', '#eef0ef', '#f8f8f6', '#b8392f'; COL = ['#d9611b', '#7a5cff', '#1f77b4', '#2a9d5c']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.edgecolor': '#9aa3aa', 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.labelcolor': INK})
fig, (a, b) = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw=dict(width_ratios=[1.25, 1])); fig.patch.set_facecolor(BG)
fig.suptitle('Same physics, different craft: why a small domain is privileged in silent (zero-expansion) mode   [NON-CANON]', x=.012, ha='left', fontsize=13.5, weight='bold', color=INK)
Rs = np.linspace(3, 25, 23)
for k, (kind, lab) in enumerate((('alcubierre', 'snowplough mode (Alcubierre-type): ~ v² R² / δ'), ('natario', 'silent mode (zero-expansion): ~ v² R^3.2 / δ^2.8 (-> R⁴/δ³ thin wall)'))):
    E = [S.demand(kind, R, 2.0, 100, 0)['E_v_J'] for R in Rs]; a.plot(Rs, E, color=COL[k], lw=2.4, label=lab)
for name, R, mk in (('shuttle', math.sqrt(284 / (4 * math.pi)), 'o'), ('Wayfarer', math.sqrt(1900 / (4 * math.pi)), 's')):
    for k, kind in enumerate(('alcubierre', 'natario')):
        a.plot(R, S.demand(kind, R, 2.0, 100, 0)['E_v_J'], mk, color=COL[k], ms=9, mec=INK)
    a.axvline(R, color=MUTED, lw=.8, ls=':'); a.text(R + .3, 2.5e33, name, color=INK, fontsize=9.5, weight='bold')
a.set_yscale('log'); a.set_xlabel('area-equivalent domain radius R (m), wall δ = 2 m'); a.set_ylabel('geometric field demand at 100 m/s, |ρ_E| integrated (J)')
a.legend(frameon=False, fontsize=8.8, loc='upper left'); a.grid(color='#dde1e3', lw=.6); a.set_facecolor(PANEL)
a.set_title('Field demand is independent of payload mass; it depends on size and wall', fontsize=10, loc='left', color=INK)
a.text(.02, .03, 'DERIVED from the geometry (Hamiltonian constraint). How actuator energy maps to this demand: UNDETERMINED (no M2 law).', transform=a.transAxes, fontsize=7.8, color=SPEC)
cases = [('HW1: capacity ∝ area\n(L² plant, same node density)', 1.0, 20.0 / 6.7), ('HW2: same hardware\non both craft', 6.7, 20.0), ('HW3: prototype,\nk× capacity per area', None, None)]
x = np.arange(3); w = .36
b.bar(x[:2] - w / 2, [c_[1] for c_ in cases[:2]], w, color=COL[0], label='snowplough mode')
b.bar(x[:2] + w / 2, [c_[2] for c_ in cases[:2]], w, color=COL[1], label='silent mode')
for xi, c_ in zip(x[:2], cases[:2]):
    b.text(xi - w / 2, c_[1] * 1.08, f'{c_[1]:.1f}×', ha='center', fontsize=9); b.text(xi + w / 2, c_[2] * 1.08, f'{c_[2]:.1f}×', ha='center', fontsize=9)
b.text(2, 6, 'k × (any of the above)\nk is engineering,\nnot derived', ha='center', fontsize=9, color=COL[2])
b.set_xticks(x); b.set_xticklabels([c_[0] for c_ in cases], fontsize=8.5); b.set_ylabel('shuttle advantage in v² (or a) per unit capacity, vs Wayfarer')
b.set_ylim(0, 24); b.legend(frameon=False, fontsize=8.8); b.grid(color='#dde1e3', lw=.6, axis='y'); b.set_facecolor(PANEL)
b.set_title('What the shuttle gains, under three hardware hypotheses', fontsize=10, loc='left', color=INK)
b.text(0, -.25, 'Plus: momentum/centre-of-energy exchange per unit area is 2.9× lower for the shuttle (215 vs 615 kg/m²).\nSpheres stand in for real hulls: shape factor UNDETERMINED.', transform=b.transAxes, fontsize=8, color=MUTED)
fig.tight_layout(rect=(0, .04, 1, .94)); fig.savefig(os.path.join(H, 'scale_privilege.png'), dpi=110, facecolor=BG); print('ok')
