"""Finite Weave dash physics figure. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'dash_ambient.json'))); C = json.load(open(os.path.join(H, 'dash_charges.json')))
INK, MUTED, BG, PANEL, SPEC = '#1d2328', '#5b6670', '#eef0ef', '#f8f8f6', '#b8392f'
COL = ['#d9611b', '#1f77b4', '#2a9d5c', '#7a5cff']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': '#9aa3aa', 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.labelcolor': INK})
fig = plt.figure(figsize=(16, 10.5)); fig.patch.set_facecolor(BG)
fig.text(.012, .972, 'Finite Weave dash: what the physics decides (NON-CANON, SOL handoff e17fd62)', fontsize=15, weight='bold', color=INK)
fig.text(.012, .948, '61 t shuttle, 10 m domain, 2 m wall, 100 m/s, 1 s up / 1 s cruise / 1 s down (200 m). Air follows the shift exactly (unit lapse => Eulerian geodesics): the domain design decides the disturbance.', fontsize=9.3, color=MUTED)
for k, (kind, title) in enumerate((('alcubierre', 'Alcubierre-type (SOL test geometry): snowplough'), ('natario', 'Natário-type (zero expansion): air flows around'))):
    ax = fig.add_axes([.05 + k * .49, .55, .4, .34]); ax.set_facecolor(PANEL)
    g = A['grids'][kind]; nx, ny = g['nx'], g['ny']; ext = [-40, 261, -30, 30]
    if kind == 'alcubierre':
        val = np.log10(np.clip(np.array(g['r']), 1e-3, 1e3)).reshape(ny, nx); img = np.vstack([val[::-1], val]); sc = ax.imshow(img, extent=ext, aspect='auto', cmap='RdBu_r', vmin=-2, vmax=2, origin='upper')
        cb = fig.colorbar(sc, ax=ax, fraction=.04, pad=.015); cb.set_label('final density / ambient (log10)', fontsize=8)
        r = A['results'][kind]; note = f"Colour = final density of the air parcel that started there. Pile-up x{r['max_density_ratio']:.0f}, channel to {r['min_density_ratio']:.3f};\ncompression energy ~{r['residual_exergy_after_stop_GJ']:.0f} GJ (dust limit: a blast and a thunderclap in real air)"
    else:
        val = np.array(g['dx']).reshape(ny, nx); img = np.vstack([val[::-1], val]); sc = ax.imshow(img, extent=ext, aspect='auto', cmap='viridis', vmin=0, vmax=200, origin='upper')
        cb = fig.colorbar(sc, ax=ax, fraction=.04, pad=.015); cb.set_label('air displacement (m)', fontsize=8)
        r = A['results'][kind]; note = f"Colour = how far the air parcel that started there moved. No compression anywhere (x1.00);\nthe domain carries its own interior air; axis air drifts forward; ambient KE {r['ambient_KE_at_cruise_MJ']:.0f} MJ, returned at stop"
    for X in (0, 200): ax.add_patch(Circle((X, 0), 10, fill=False, ec=INK, lw=1, ls='--'))
    ax.text(0, 13, 'start', ha='center', fontsize=8); ax.text(200, 13, 'stop', ha='center', fontsize=8)
    ax.set_xlim(-40, 262); ax.set_ylim(-30, 30); ax.set_aspect('auto'); ax.set_xlabel('initial position along dash (m)'); ax.set_ylabel('distance from axis (m)')
    ax.set_title(title, fontsize=10.5, loc='left', color=INK); ax.text(0, -.24, note, transform=ax.transAxes, fontsize=8.3, color=INK)
b = fig.add_axes([.2, .12, .27, .3]); b.set_facecolor(PANEL)
cl = C['ledger']['closures']
items = [('R1 radiate the impulse away', float(cl['R1 radiation to infinity']['min_energy_J'])), ('R2 local partner (exterior field)', float(cl['R2 exterior Weave field reaching environment matter (local partner)']['transient_energy_J'].split()[0])),
         ('R3 Sun partner (canon §7.1b)', float(cl['R3 nonlocal exchange to a distant partner (canon §7.1b type)']['sun_frame_transient_J'].split()[0].strip('+/-'))), ('R4 remnant scar: ±m c² left behind', 61e3 * 2.998e8 ** 2)]
yy = np.arange(len(items))[::-1]
b.barh(yy, [v for _, v in items], color=[SPEC, COL[2], COL[0], COL[3]], height=.55); b.set_xscale('log'); b.set_xlim(1e7, 1e23)
for y, (lab, v) in zip(yy, items): b.text(v * 1.6, y, f'{v:.1e} J', va='center', fontsize=8.5)
b.set_yticks(yy); b.set_yticklabels([s for s, _ in items], fontsize=8.6); b.set_xlabel('energy the closure requires for one 200 m dash (J, log)')
b.set_title('Where the centre-of-energy charge goes\n(an isolated dash is INCONSISTENT)', fontsize=10, loc='left', color=INK)
b.text(-.62, -.22, 'R5: a Loom-type sector change (M1) discharges it without flux: that is option 2 / Weave seams, not Metric.', transform=b.transAxes, fontsize=8.3, color=INK)
t = fig.add_axes([.53, .03, .45, .42]); t.axis('off')
rows = [['Question', 'Verdict'], ['Target geometry, crew inertial', 'DERIVED (SOL)'], ['Ordinary-GR source', 'INCONSISTENT (negative energy)'], ['M2 sources the exotic stress', 'ASSUMED (permission, no law)'],
        ['Isolated displacement, field relaxed', 'INCONSISTENT (boost charge)'], ['Velocity change via partner', 'DERIVED structure; cost in partner frame'], ['Who the partner is', 'UNDETERMINED (range of S_R)'],
        ['Closed-cycle gain, local partner', 'none (DERIVED)'], ['Closed-cycle gain, Sun partner', '0.6 GJ/km harvest (DERIVED)'], ['Air: zero-expansion domain', 'no compression (DERIVED, ideal fluid)'],
        ['Air: Alcubierre-type', 'snowplough / blast (DERIVED, dust)'], ['Water, ground, gravity, solids', 'UNDETERMINED']]
tb = t.table(cellText=rows, loc='upper center', cellLoc='left', colWidths=[.55, .45]); tb.auto_set_font_size(False); tb.set_fontsize(8.8); tb.scale(1, 1.75)
for (r_, c_), cell in tb.get_celld().items():
    cell.set_edgecolor('#cfd5d8'); cell.set_facecolor('#e4e8ea' if r_ == 0 else 'white')
    if r_ and c_ == 1:
        s = rows[r_][1]; cell.get_text().set_color(SPEC if s.startswith('INCONS') else (COL[2] if s.startswith('DERIVED') or s.startswith('none') or s.startswith('no ') else (COL[0] if 'UNDET' in s or 'ASSUMED' in s else INK)))
fig.savefig(os.path.join(H, 'dash_physics.png'), dpi=110, facecolor=BG); print('ok')
