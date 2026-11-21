"""Experiment 2 figures. ALL bodies. ALL sponsors. 2026-2226. NON-CANON prototype lane.
exp2_departure.png: four departure scenarios (W2). exp2_w1_w3.png: W1 bay fit and decomposition, W3 boundary cases."""
import os, sys, json, math
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, FancyBboxPatch
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..', 'explorer'))
import engine as E
W1, W2, W3 = (json.load(open(os.path.join(H, f))) for f in ('exp2_w1.json', 'exp2_w2.json', 'exp2_w3.json'))
G = 9.81; INK, MUTED, BG, PANEL, SPEC = '#1d2328', '#5b6670', '#eef0ef', '#f8f8f6', '#b8392f'
COL = ['#d9611b', '#1f77b4', '#2a9d5c', '#7a5cff']    # validated categorical (dataviz validator: all checks pass)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': '#9aa3aa', 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED})
def tag(ax, x, y, s, c=SPEC, fs=7.5): ax.text(x, y, s, transform=ax.transAxes, fontsize=fs, color=c, va='top', bbox=dict(fc='white', ec=c, lw=.8, boxstyle='round,pad=.3'))
def clean(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.grid(color='#dde1e3', lw=.6); ax.set_axisbelow(True)

# ================================================================ departure figure
S = W2['scenarios']; t = np.linspace(0, 32, 641)
def hist(i):
    if i in (0, 1): a = 1.5 * G; return [(t, 0.5 * a * t * t, True)]
    af = 0.5 * G; hh = 200 if i == 2 else 2000; tf = math.sqrt(2 * hh / af); vf = af * tf; at = (1.0 if i == 2 else 0.4) * G
    t1 = t[t <= tf]; t2 = t[t >= tf]
    return [(t1, 0.5 * af * t1 * t1, False), (t2, hh + vf * (t2 - tf) + 0.5 * at * (t2 - tf) ** 2, True)]
def crew(i):
    if i == 0: return [(0, 32, 2.5)]
    if i == 1: return [(0, 15, 2.0), (15, 32, 2.5)]
    tf = math.sqrt(2 * (200 if i == 2 else 2000) / (0.5 * G)); return [(0, tf, 0.0), (tf, 32, 2.0 if i == 2 else 1.4)]
fig = plt.figure(figsize=(16, 10.2)); fig.patch.set_facecolor(BG)
fig.text(.012, .975, 'Experiment 2 · W2 metric assistance: four departures from a hot-extraction landing zone', fontsize=15, weight='bold', color=INK)
fig.text(.012, .952, 'Reference: W1 + Osteon cautious (#2643, 17 m, 18 t tank + 5 t sprint), lift-off ~61 t.  Field mechanism M1 (planet-referenced lift).  '
         'Solid = torch burning (exhaust); dashed = field only (no exhaust).', fontsize=9.5, color=MUTED)
a = fig.add_axes([.05, .53, .42, .38]); a.set_facecolor(PANEL); clean(a)
names = ['S0 conventional', 'S1 15 s partial pulse', 'S2 field to 200 m', 'S3 field to 2 km']
for i in range(4):
    for tt, hh, torch in hist(i):
        a.plot(tt, hh / 1e3, color=COL[i], lw=(6 if i == 0 else 2.2) if torch else 2.0, ls='-' if torch else (0, (4, 2)), zorder=2 if i == 0 else 3)
a.text(16.6, 1.55, 'S0 conventional  and\nS1 15 s partial pulse\n(same path)', color=INK, fontsize=8.5, weight='bold', ha='left')
a.plot([16.4, 15.9], [1.62, 1.75], color=MUTED, lw=.8)
a.text(25.3, 1.3, names[2], color=COL[2], fontsize=9, weight='bold'); a.text(26.0, 0.95, names[3], color=COL[3], fontsize=9, weight='bold')
for y, s in ((0.2, '200 m: small-arms / crowd clearance'), (2.0, '2 km: plume no longer reaches the ground')):
    a.axhline(y, color=MUTED, lw=.8, ls=':'); a.text(0.4 if y > 1 else 31.6, y + .04, s, fontsize=7.5, color=MUTED, ha='left' if y > 1 else 'right')
a.set_xlim(0, 32); a.set_ylim(0, 3.2); a.set_xlabel('time from lift-off (s)'); a.set_ylabel('altitude (km)')
a.set_title('Altitude: the field climb is SLOWER off the ground than the torch, but exhaust-free', fontsize=10, loc='left', color=INK)
tag(a, .02, .97, 'MODEL: vertical kinematics; drag ignored\nfield net 0.5 g (1.5 x weight) [ASSUMPTION]')
b = fig.add_axes([.54, .53, .42, .38]); b.set_facecolor(PANEL); clean(b)
for i in range(4):
    for k, (t0, t1, gg) in enumerate(crew(i)):
        b.plot([t0, t1], [gg + 0.04 * (i - 1.5)] * 2, color=COL[i], lw=2.6, ls='-' if gg > 0 or i < 2 else (0, (4, 2)))
        if k: b.plot([t0, t0], [crew(i)[k - 1][2] + 0.04 * (i - 1.5), gg + 0.04 * (i - 1.5)], color=COL[i], lw=1.2)
for i, (x, y) in enumerate(((1, 2.62), (1, 1.83), (1.0, 0.16), (13, 0.16))):
    b.text(x, y, names[i], color=COL[i], fontsize=8.5, weight='bold')
b.text(9.3, 2.12, 'S2 torch hand-over: 0 g to 2 g', fontsize=7.5, color=COL[2]); b.text(28.9, 1.5, 'S3: 0 to 1.4 g', fontsize=7.5, color=COL[3], ha='right')
b.set_xlim(0, 32); b.set_ylim(-0.1, 3.0); b.set_xlabel('time from lift-off (s)'); b.set_ylabel('crew acceleration felt (g)')
b.set_title('Crew load: a uniform field climb is weightless; the torch hand-over is the load event', fontsize=10, loc='left', color=INK)
tag(b, .45, .97, 'M1 acting on ALL mass (uniform). If it acts on the structure\ninstead, crew feel 1.5 g during the field climb.', MUTED)
# table
c = fig.add_axes([.03, .2, .94, .27]); c.axis('off')
ce = W2['module_ceiling_t']; hv = W2['heavy_14p3_8c']
def fmt(v, d=1): return '-' if v is None else (f'{v:.{d}f}' if isinstance(v, float) else str(v))
rows = [['', 'to 200 m', 'to 2 km', 'exhaust at\nthe surface', 'energy to\nshuttle', 'field source\n(central)', 'peak\npower', 'storage\n(2226 decl.)', 'module ceiling\ncentral / pess.', 'hot water\nneed / 23 t', '14.3 m 8-couch\nhot closes?', 'new operational choice']]
verdict = ['baseline: plume into the LZ (MW/m² near the axis)', 'none: same plume; ~0 water; does not fix 8-couch thrust', 'exhaust-free pickup; lands vertically on LAND with fans', 'exhaust-free to 2 km; 7 t water spare']
for i, s in enumerate(S):
    k = ['S0', 'S1', 'S2', 'S3'][i]; cl = ce.get(k, {})
    rows.append([names[i], f"{s['t_to_200m_s']} s", f"{s['t_to_2km_s']} s", 'YES' if i < 2 else 'no', f"{s['energy_to_shuttle_GJ']} GJ", f"{s['field_source_GJ']} GJ",
                 f"{s['peak_power_MW']} MW", f"{s['storage_t']} t", '-' if i == 0 else f"{fmt(cl.get('central'))} / {fmt(cl.get('pessimistic'))} t",
                 f"{s['hot_water_t']} t", ('no (thrust-short)' if hv[i]['thrust_short'] else ('only if device ~0 t' if cl.get('heavy_14p3_8c') == 0.0 else 'yes, device ≤ %s t' % fmt(cl.get('heavy_14p3_8c')))), verdict[i]])
tb = c.table(cellText=rows, loc='upper center', cellLoc='center', colWidths=[.1, .05, .05, .06, .06, .07, .055, .065, .08, .07, .1, .2])
tb.auto_set_font_size(False); tb.set_fontsize(8.2); tb.scale(1, 2.15)
for (r_, c_), cell in tb.get_celld().items():
    cell.set_edgecolor('#cfd5d8'); cell.set_facecolor('white' if r_ else '#e4e8ea')
    if r_ and c_ == 0: cell.get_text().set_color(COL[r_ - 1]); cell.get_text().set_weight('bold')
    if r_ and c_ == 11: cell.get_text().set_ha('left'); cell._loc = 'left'
c.text(0, .02, 'Energy: central = coupling efficiency 0.6, 0.05 GJ establishment, 0.5 MW upkeep; pessimistic = 0.3, 0.3 GJ, 5 MW [ASSUMPTIONS]. The 29 MWe fan reactor feeds the field during the climb. '
       'Storage uses kT\'s DECLARED 2226 flywheel (1 kWh/kg, 150 kW/kg).\nWith ordinary 2026 storage (0.1 kWh/kg, 10 kW/kg) no field scenario closes: S3 alone would need ~20 t for its 218 MW peak. '
       'Module ceiling = largest field device that keeps hot extraction closing (water, thrust, 52.5 t). It is an INTEGRATION LIMIT, not a prediction of device mass.',
       transform=c.transAxes, fontsize=7.8, color=MUTED, va='top')
d = fig.add_axes([.03, .012, .94, .125]); d.axis('off')
mech = [('M1 reduced effective gravitational loading', 'NEW CONSTITUTIVE RELATION: a switchable coupling with the\nreaction on the planet. Hover ideally ~free (a static force does\nno work). Tension with the equivalence principle only if framed as\nchanging matter. The narrowest useful effect.', COL[2]),
        ('M2 modified inertial response', 'TENSION WITH AN INVARIANT: equivalence principle;\nmomentum or energy must be paid on switch-off.\nNo lift: weight is unchanged. Dropped for departure.', SPEC),
        ('M3 engineered local spacetime geometry', 'CANON-FAMILY PHYSICS (inside the M2 miracle), BEYOND\nCANON TECHNOLOGY. The wall may not cut water or people,\nso it cannot start from a floating shuttle unless the\nboundary may cross matter.', COL[3])]
for k, (h_, s_, cc) in enumerate(mech):
    x0 = k / 3
    d.add_patch(FancyBboxPatch((x0 + .004, .05), 1 / 3 - .012, .9, boxstyle='round,pad=.004', fc='white', ec=cc, lw=1.4, transform=d.transAxes))
    d.text(x0 + .012, .9, h_, transform=d.transAxes, fontsize=8.8, weight='bold', color=cc, va='top')
    d.text(x0 + .012, .66, s_, transform=d.transAxes, fontsize=7.6, color=INK, va='top')
fig.text(.012, .145, 'Three mechanisms, kept apart (none established):', fontsize=9, weight='bold', color=INK)
fig.savefig(os.path.join(H, 'exp2_departure.png'), dpi=110, facecolor=BG); plt.close(fig)

# ================================================================ W1 + W3 figure
fig = plt.figure(figsize=(16, 9.6)); fig.patch.set_facecolor(BG)
fig.text(.012, .972, 'Experiment 2 · W1 programmable structure vs conventional mechanisms · W3 a 50-100 m metric step', fontsize=15, weight='bold', color=INK)
# (a) bay section
a = fig.add_axes([.02, .47, .27, .45]); a.set_facecolor(PANEL); a.set_aspect('equal')
ref = dict({r['id']: r for r in json.load(open(os.path.join(H, '..', '..', 'explorer', 'explorer_results.json')))['results']}[2643]['params'], span=17.0, chord=1.8)
K = E.keys(ref); sec = E.section(K, 9.0, ref['keel']); zc = W1['bay_fold']['centre_z_m']
a.add_patch(Circle((0, zc), 2.4, fc='#e3e6e6', ec=INK, lw=1.2)); a.add_patch(Circle((0, zc), E.R_ENV, fc='none', ec=MUTED, lw=1, ls='--'))
a.add_patch(Polygon(sec, fc='#8a939b', ec=INK, lw=1))
top = 1.51; tp = W1['bay_fold']['panel_thickness_m']
for k in range(2): a.add_patch(Rectangle((-0.9, top + 0.05 + k * (tp + 0.03)), 1.8, tp, fc=COL[1], ec=INK, lw=.6, alpha=.85))
a.annotate('two outer panels\n6.37 m × 1.8 m × 0.22 m\nfolded over the spine', (0.9, top + 0.3), (1.2, 2.75), fontsize=7.5, color=COL[1], arrowprops=dict(arrowstyle='-', color=COL[1], lw=.8))
a.text(0, 0.0, 'hull section\nx = 9 m', ha='center', va='center', fontsize=8, color='white')
a.set_xlim(-2.9, 2.9); a.set_ylim(-2.75, 3.1); a.axis('off')
a.set_title('Bay fit: a CONVENTIONAL 17 m fold fits\n(band 0.74 m clear, stack needs 0.53 m)', fontsize=10, loc='left', color=INK)
tag(a, .0, .06, 'GEOMETRY from the loft. Bore r 2.4 m, envelope r 2.15 m (dashed).\nNOT CHECKED: fans, pop-out floats and cradle sharing the\nband; chine hinge fittings', SPEC, 6.8)
# (b) W1 variants
b = fig.add_axes([.35, .53, .3, .38]); b.set_facecolor(PANEL); clean(b)
lab = {'A': 'A telescoping 13.7 m', 'B': 'B fold 17 m', 'C': 'C 2-stage telescope 17 m', 'D': 'D programmable stow only', 'E': 'E fold + adaptive camber',
       'F': 'F full W1 (lane ref.)', 'G': 'G telescoping + adaptive camber'}
off = {'A': (.12, .3), 'B': (.12, .3), 'C': (-.08, .3), 'D': (.12, -.6), 'E': (.12, -.55), 'F': (.12, .25), 'G': (.12, .3)}
for k, v in W1['variants'].items():
    L_ = k[0]; prog = L_ in 'DEFG'; c_ = COL[3] if prog else COL[1]
    b.scatter(v['dry_t'], v['hot_td'], s=90 if L_ == 'E' else 55, color=c_, edgecolor=INK if L_ == 'E' else 'white', lw=1.2, zorder=3, marker='o' if prog else 's')
    b.text(v['dry_t'] + off[L_][0], v['hot_td'] + off[L_][1], lab[L_], fontsize=7.6, color=INK, ha='right' if L_ == 'C' else 'left')
b.axhline(50, color=SPEC, lw=1, ls='--'); b.text(35.7, 50.15, 'heavy-landing limit 50 m/s', fontsize=7.5, color=SPEC)
b.set_xlim(35.5, 39.6); b.set_ylim(42.5, 51); b.set_xlabel('dry mass (t)'); b.set_ylabel('hot-extraction water touchdown (m/s)')
b.set_title('The margin comes from ADAPTIVE CAMBER, not shape-changing stowage', fontsize=10, loc='left', color=INK)
tag(b, .5, .66, 'MODEL: explorer ROM.\n■ conventional  ● programmable feature\nCamber credit (CL cap 5) is a\nSENSITIVITY, not established.\nAll seven pass all five missions.', MUTED, 7)
# (c) lock shear
c = fig.add_axes([.71, .53, .27, .38]); c.set_facecolor(PANEL); clean(c)
req = W1['stiffness']['REQUIRED_lock_shear_MPa']; known = W1['stiffness']['known_reversible_locks_MPa']
items = [('vacuum jamming', known['vacuum_jamming_MPa'], MUTED), ('electro-adhesion', known['electroadhesion_MPa'], MUTED), ('structural adhesive\n(not reversible)', known['structural_adhesive_MPa'], MUTED),
         ('Ti pin / tooth\ninterlock', known['titanium_pin_or_tooth_MPa'], COL[2])] + [('REQUIRED, ' + k.replace(' lock lands', ' lands'), v, SPEC) for k, v in req.items()]
y = np.arange(len(items))[::-1]
c.barh(y, [v for _, v, _ in items], color=[cc for _, _, cc in items], height=.6); c.set_xscale('log'); c.set_xlim(0.01, 3000)
c.set_yticks(y); c.set_yticklabels([s for s, _, _ in items], fontsize=7.5)
for yy, (_, v, _) in zip(y, items): c.text(v * 1.25, yy, f'{v:g}', va='center', fontsize=7.5, color=INK)
c.set_xlabel('shear strength (MPa, log)'); c.set_title('A flat-stowed wing must lock like a\nmechanism, not like a jammed laminate', fontsize=10, loc='left', color=INK)
tag(c, .3, .985, 'REQUIRED at 8 g limit × 1.5, 59 t, wing root.\nAn unlocked web = open section, ~1% torsional\nstiffness: lock integrity is flight-critical', SPEC, 6.8)
# (d) W3
d = fig.add_axes([.06, .07, .5, .32]); d.set_facecolor(PANEL); clean(d)
ts = np.logspace(-1.3, 0.4, 100)
for A_, cd, ls_, nm in ((10, .5, '-', 'H1 region sweeps the air, nose-on'), (60, 1.2, '--', 'H1 broadside')):
    d.plot(ts, [0.5 * 1.225 * (100 / tt) ** 2 * cd * A_ * 100 / 1e6 for tt in ts], color=COL[0], ls=ls_, lw=2, label=nm)
for k, v in W3['H2_boundary_bound'].items():
    d.axhline(v['bound_MJ'], color=COL[3], lw=1.6, ls=':'); d.text(1.95, v['bound_MJ'] * 1.12, f"H2 boundary bang, {k}: ≤{v['bound_MJ']:.0f} MJ (~{v['tnt_kg_equiv']:.0f} kg TNT)", fontsize=7.4, color=COL[3], ha='right')
d.text(1.95, 0.13, 'H2 with content SWAP → toward 0 (near-silent) · H3 vacuum only: environment term 0', fontsize=7.6, color=COL[2], ha='right')
d.axvspan(0.05, 0.5, color=COL[2], alpha=.08); d.text(0.06, 2.3e3, 'defeats a 30 g interceptor endgame\n(step done inside the last 0.5 s)', fontsize=7.5, color=COL[2])
d.axvline(2.26, color=MUTED, lw=1); d.text(2.2, 4e3, 'conventional 100 m\nsidestep at 8 g: 2.26 s', fontsize=7.4, color=MUTED, ha='right', va='top')
d.set_xscale('log'); d.set_yscale('log'); d.set_xlim(0.05, 2.5); d.set_ylim(0.1, 8e3)
d.set_xlabel('time to complete a 100 m step (s)'); d.set_ylabel('energy into the air (MJ)')
d.set_title('W3: the air bill depends entirely on what the boundary does to matter', fontsize=10, loc='left', color=INK)
d.legend(loc='lower left', fontsize=7.5, frameon=False)
tag(d, .3, .97, 'SPECULATIVE: no mechanism established. Ordinary aerodynamics used for H1 ONLY.', SPEC, 7.2)
e = fig.add_axes([.6, .05, .38, .35]); e.axis('off')
txt = [('W1 smallest credible capability', 'Adaptive camber / trailing structure that holds shape at 8 g\n(+ re-armable crash and slam absorbers). Conventional fold\nfor stowage. 37.3 t dry, hot touchdown 43.3 m/s.', COL[1]),
       ('W2 smallest effect that changes hot extraction', '~1.5 × weight for ~9 s to 200 m (~0.35 GJ, ~70 MW), plus\n~0.65 × weight to hover with the fans: exhaust-free pickup and\nvertical landing on land. Device ceiling ~3.5 t.', COL[2]),
       ('W3 decisive unknown', 'What the field boundary does to matter in a transition:\ncarry/swap it, push it aside, or fail. Same unknown decides\nwhether W2 can start from a floating shuttle.', COL[3])]
for k, (h_, s_, cc) in enumerate(txt):
    y0 = 1 - k * .34
    e.add_patch(FancyBboxPatch((0, y0 - .31), 1, .29, boxstyle='round,pad=.005', fc='white', ec=cc, lw=1.4, transform=e.transAxes))
    e.text(.02, y0 - .045, h_, transform=e.transAxes, fontsize=9.2, weight='bold', color=cc, va='top')
    e.text(.02, y0 - .12, s_, transform=e.transAxes, fontsize=7.9, color=INK, va='top')
fig.savefig(os.path.join(H, 'exp2_w1_w3.png'), dpi=110, facecolor=BG); plt.close(fig)
print('ok')
