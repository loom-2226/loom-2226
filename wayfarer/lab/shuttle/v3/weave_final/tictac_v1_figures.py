"""Tic Tac build-out v1 figures. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, sys, json, math
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, Polygon
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import tictac_v1 as T
O = json.load(open(os.path.join(H, 'tictac_v1.json')))['options']['D3.8']; R = O['R']; Lx = O['layout']['x']; DECK = O['layout']['deck_z']
INK = '#1f2933'; MUT = '#6b7280'; SH = '#2563eb'; WARN = '#d97706'; OK = '#16a34a'; BAD = '#dc2626'; SEA = '#93c5fd'
C_WAT, C_CAB, C_MOD, C_WEL, C_AFT, C_AVI, C_GRO = '#bfdbfe', '#99f6e4', '#ddd6fe', '#fde68a', '#d1d5db', '#cbd5e1', '#f1f5f9'
plt.rcParams.update({'font.size': 9.5, 'axes.edgecolor': MUT, 'axes.labelcolor': INK, 'xtick.color': MUT, 'ytick.color': MUT, 'axes.spines.top': False, 'axes.spines.right': False})
xs = np.linspace(0, T.L, 600); ro = np.array([T.r_out(x, R) for x in xs]); ri = np.array([T.r_in(x, R) for x in xs])

# ======================================================== figure 1: the vehicle
f = plt.figure(figsize=(13, 9.6))
f.suptitle("Weave shuttle 'Tic Tac' — build-out v1 (NON-CANON)", x=0.02, ha='left', y=0.985, color=INK, fontsize=13)
m = O['mass']; f.text(0.02, 0.948, f"12.8 m x 3.8 m capsule · {m['dry_t']:.1f} t dry ({m['margin_t']:.1f} t under the 52.5 t ceiling) · same 8 t module, 23.1 t tank, torch · "
                      f"no wings, no fans · parachutes {m['chutes_t']:.1f} t", color=MUT, fontsize=9.5)
a = f.add_axes([0.04, 0.53, 0.92, 0.34])
def band(x0, x1, lo, hi, col, lab=None):
    mm = (xs >= x0) & (xs <= x1); top = np.minimum(ri[mm], hi) if hi is not None else ri[mm]; bot = np.maximum(-ri[mm], lo) if lo is not None else -ri[mm]
    a.fill_between(xs[mm], bot, np.maximum(top, bot), color=col, lw=0, label=lab)
band(*Lx['nose_dome'], None, None, C_AVI, 'nose: docking hatch, avionics, parachutes')
band(*Lx['nose_dome'], None, 0.0, C_WAT)
band(*Lx['cabin'], DECK, None, C_CAB, 'cabin'); band(*Lx['well'], DECK, None, C_WEL, 'cargo well (floodable)')
band(*Lx['module_bay'], DECK, None, C_GRO); band(*Lx['growth_bay'], DECK, None, C_GRO, 'unallocated (growth)')
band(Lx['nose_dome'][1], Lx['aft_dome'][0], None, DECK, C_WAT, 'water cells')
band(*Lx['aft_dome'], None, None, C_AFT, 'aft: torch, power unit, RCS'); band(*Lx['aft_dome'], None, -0.9, C_WAT)
a.plot(xs, ro, color=INK, lw=1.4); a.plot(xs, -ro, color=INK, lw=1.4)
for x0, x1 in O['layout']['rows']: a.add_patch(Rectangle((x0, DECK + 0.02), x1 - x0, 0.95, fc='white', ec='#0f766e'))
a.text(np.mean(Lx['cabin']), DECK + 1.25, '6 couches (3 abreast x 2 rows)', ha='center', fontsize=8.5, color='#0f766e')
wb = O['layout']['well_box']; a.add_patch(Rectangle((Lx['well'][0] + 0.05, DECK + 0.02), wb['length'], wb['height'], fc='none', ec=WARN, lw=1.3))
a.text(np.mean(Lx['well']), DECK + wb['height'] + 0.15, f"6 m³ box\n{wb['width']:.1f} m wide", ha='center', fontsize=8, color=WARN)
ce = O['layout']['core_edge_m']; a.add_patch(Rectangle((Lx['module_bay'][0] + 0.05, DECK + 0.02), ce, ce, fc=C_MOD, ec='#6d28d9', lw=1.2, label='relational module'))
a.text(Lx['module_bay'][0] + 0.05 + ce / 2, DECK + ce + 0.15, 'module +\nflywheel', ha='center', fontsize=8, color='#6d28d9')
a.plot([0, 1.2], [0, 0], color=INK, ls='--', lw=0.9); a.text(0.15, 0.12, 'hatch + passage', fontsize=8)
cg = O['hydrostatics']['cases']['full tank']; a.plot(cg['cg_x'], cg['cg_z'], 'o', ms=9, mfc='white', mec=INK, mew=2); a.plot(cg['cg_x'], cg['cg_z'], '+', ms=9, color=INK, mew=1.6)
a.text(cg['cg_x'] + 0.2, cg['cg_z'] - 0.25, f"mass centre, full tank (z {cg['cg_z']:+.2f} m)", fontsize=8)
a.set_xlim(-0.3, 13.1); a.set_ylim(-2.2, 2.4); a.set_aspect('equal'); a.set_xlabel('x from the nose tip (m)'); a.set_ylabel('z (m)')
a.legend(loc='upper center', ncol=4, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 1.13))
# section
s = f.add_axes([0.04, 0.07, 0.22, 0.38]); s.add_patch(Circle((0, 0), R, fc='none', ec=INK, lw=1.4)); rr = R - T.WALL
th = np.linspace(0, 2 * np.pi, 200); P = np.c_[rr * np.cos(th), rr * np.sin(th)]
s.add_patch(Polygon(P[P[:, 1] >= DECK], fc=C_CAB, ec='none')); s.add_patch(Polygon(P[P[:, 1] <= DECK], fc=C_WAT, ec='none'))
for y0, y1 in O['layout']['ys']: s.add_patch(Rectangle((y0, DECK + 0.02), y1 - y0, 0.95, fc='white', ec='#0f766e'))
s.text(0, 1.2, f"headroom {O['layout']['headroom_m']:.2f} m", ha='center', fontsize=8.5); s.text(0, -1.35, 'water cells', ha='center', fontsize=8.5, color=SH)
s.set_xlim(-2.2, 2.2); s.set_ylim(-2.2, 2.2); s.set_aspect('equal'); s.set_title('section through the cabin', loc='left', fontsize=9.5, color=INK); s.set_yticks([])
# volume table
t = f.add_axes([0.30, 0.07, 0.27, 0.38]); t.axis('off'); t.set_title('Volume (m³)', loc='left', fontsize=9.5, color=INK)
z = O['layout']['zones_m3']; nd = O['layout']['need_m3']
rows = [('cabin (need 21)', z['cabin']), ('cargo well (need 6; rigid 6 m³ box fits)', z['well']), ('water cells (need 24.3)', O['layout']['water_cells_m3']),
        ('module bay', z['module_bay']), ('growth bay', z['growth_bay']), ('inner hull total', O['layout']['inner_total_m3']), ('unallocated after all needs', O['layout']['unallocated_m3'])]
for k, (n, v) in enumerate(rows):
    y = 0.88 - k * 0.12; t.text(0, y, n, fontsize=9, color=INK, transform=t.transAxes); t.text(0.98, y, f'{v:.1f}', ha='right', fontsize=9.5, color=OK if k == 6 else INK, weight='bold' if k == 6 else 'normal', transform=t.transAxes)
# mass bars
b = f.add_axes([0.77, 0.1, 0.2, 0.33]); it = m['items']
grp = [('hull + TPS + wall', it['hull_structure'] + it['entry_tps'] + it['cabin_wall']), ('module + flywheel', m['module_t'] + m['flywheel_t']), ('torch + RCS + power', it['torch'] + it['belly_rcs'] + it['power_dist'] + it['fans_reactor']),
       ('cabin, avionics, custody', it['cabin'] + it['avionics'] + it['custody']), ('tank, gear, mounts', it['water_tank'] + it['gear_door'] + it['crash_mounts']), ('parachutes', m['chutes_t'])]
yy = np.arange(len(grp))[::-1]; b.barh(yy, [g[1] for g in grp], color=SH, height=0.6)
for y_, g in zip(yy, grp): b.text(g[1] + 0.2, y_, f'{g[1]:.1f}', va='center', fontsize=8.5)
b.set_yticks(yy); b.set_yticklabels([g[0] for g in grp], fontsize=8.5); b.set_xlabel('t'); b.set_title(f"Dry mass {m['dry_t']:.1f} t", loc='left', fontsize=9.5, color=INK)
f.savefig(os.path.join(H, 'weave_tictac_v1_vehicle.png'), dpi=150, facecolor='white'); plt.close(f)

# ======================================================== figure 2: Sol's checks
f = plt.figure(figsize=(13, 10.6))
f.suptitle("Tic Tac build-out v1: Sol's checks", x=0.02, ha='left', y=0.985, color=INK, fontsize=13)
f.text(0.02, 0.948, 'Afloat stability · waterborne cargo access · field-off recovery · bay exit · Titan lakes', color=MUT, fontsize=9.5)
hc = O['hydrostatics']['cases']
for k, (name, c) in enumerate(hc.items()):
    ax = f.add_axes([0.03 + k * 0.245, 0.56, 0.22, 0.32]); zw = c['waterline_z']
    ax.add_patch(Rectangle((-2.6, -2.6), 5.2, zw + 2.6, fc=SEA, alpha=0.45, ec='none'))
    ax.add_patch(Circle((0, 0), R, fc='#f8fafc', ec=INK, lw=1.4)); ax.plot([-2.6, 2.6], [zw, zw], color=SH, lw=1.0, ls='--'); ax.plot([-R + T.WALL, R - T.WALL], [DECK, DECK], color=INK, lw=0.8)
    if 'flooded' in name:
        rr = R - T.WALL; zz = np.linspace(DECK, min(zw, rr), 50); yv = np.sqrt(np.maximum(rr ** 2 - zz ** 2, 0))
        ax.add_patch(Polygon(np.r_[np.c_[-yv, zz], np.c_[yv[::-1], zz[::-1]]], fc=SEA, ec='none', alpha=0.8))
    ax.plot(0, c['cg_z'], 'o', ms=7, mfc='white', mec=INK, mew=1.8); ax.plot(0, 0, 'x', color=SH, ms=7, mew=1.6)
    ok = c['GM_roll_m'] >= 0.3; col = OK if ok else (WARN if c['GM_roll_m'] > 0.05 else BAD)
    ax.set_title(name, loc='left', fontsize=9.5, color=INK)
    ax.text(0, -2.45, f"GM {c['GM_roll_m']:.2f} m · draft {c['draft_m']:.2f} m", ha='center', fontsize=9, color=col, weight='bold')
    ax.set_xlim(-2.6, 2.6); ax.set_ylim(-2.6, 2.6); ax.set_aspect('equal'); ax.axis('off')
f.text(0.03, 0.525, f"× = hull axis (centre of buoyancy always on the vertical through it)   ○ = mass centre.   Deck is {abs(hc['full tank']['well_deck_vs_waterline_m']):.1f} m below the waterline at full tank: "
       f"the side-door well floods by design (W4).\nLight and flooded: neutral. Rule: when afloat light, flood the empty water cells with sea ballast "
       f"(≥ {O['afloat_rule']['min_water_ballast_t_for_GM_0p3_well_flooded']:.1f} t gives GM 0.3 m with the well open).", fontsize=8.8, color=MUT)
# fallback ladder
a = f.add_axes([0.05, 0.07, 0.3, 0.36]); fb = O['fallback']; sens = fb['chute_min_alt_sensitivity_m']
for xc, lab, segs in ((0.25, 'selected shuttle\n(wings, torch)', [(0, 5.1, OK), (5.1, 46.8, BAD), (46.8, 110, '#e5e7eb')]),
                      (0.75, 'Tic Tac\n(parachutes)', [(0, fb['drop_survivable_water_m'], OK), (fb['drop_survivable_water_m'], fb['chute_min_hover_alt_water_m'], BAD), (fb['chute_min_hover_alt_water_m'], sens['inflate_6s'], WARN), (sens['inflate_6s'], 110, '#e5e7eb')])):
    for lo, hi, colr in segs: a.add_patch(Rectangle((xc - 0.18, lo), 0.36, hi - lo, fc=colr, ec='white'))
    a.text(xc, -14, lab, ha='center', fontsize=8.5, color=INK)
a.text(0.96, 20, f"no recovery\n5–{fb['chute_min_hover_alt_water_m']:.0f} m", fontsize=8, color=BAD, ha='left', transform=a.transData)
a.text(0.96, 50, f"chutes if they\ninflate in 4–6 s\n({sens['inflate_4s']:.0f}–{sens['inflate_6s']:.0f} m)", fontsize=8, color=WARN, ha='left')
a.set_xlim(0, 1.25); a.set_ylim(0, 110); a.set_xticks([]); a.set_ylabel('hover height over water when the field fails (m)')
a.set_title('Field-off recovery from a slow hover', loc='left', fontsize=9.5, color=INK); a.spines['bottom'].set_visible(False)
# Titan
tt = f.add_axes([0.45, 0.1, 0.22, 0.3]); TI = O['titan']; names = list(TI)
vals = [TI[n]['reserve'] * 100 for n in names]; full = [TI[n]['full_tank_reserve'] * 100 for n in names]
xx = np.arange(2); tt.bar(xx - 0.18, vals, 0.34, color=SH, label=f"landed, ascent water only ({TI[names[0]]['landed_t']:.0f} t)"); tt.bar(xx + 0.18, full, 0.34, color='#93c5fd', label='landed with a full tank')
tt.axhline(50, color=MUT, ls='--', lw=0.9); tt.text(1.45, 52, '50% reserve', fontsize=8, ha='right', color=MUT); tt.axhline(0, color=INK, lw=0.8)
tt.set_xticks(xx); tt.set_xticklabels(['Ligeia-like\n551 kg/m³', 'pure methane\n447 kg/m³'], fontsize=8.5); tt.set_ylabel('reserve buoyancy (%)')
tt.set_title('Titan lakes (shared gap)', loc='left', fontsize=9.5, color=INK); tt.legend(frameon=False, fontsize=7.8, loc='upper right')
# bay + summary
sm = f.add_axes([0.70, 0.04, 0.29, 0.4]); sm.axis('off'); bay = O['bay']; ro_ = O['rover_option']
lines = [('Bay exit', f"3.8 m = F10 limit exactly; round, so any roll; F8 r 1.9 ≤ 2.15; 12.8 m, no collar", OK),
         ('', 'Rule: nothing may protrude beyond the 3.8 m diameter', WARN),
         ('Docking', '0.8 m hatch on the nose axis: fixes the B4-S nose-passage gap', OK),
         ('Water from orbit', f"Earth with cushion {O['water']['earth_cushion_t']:.1f} t of 23.1", OK),
         ('Afloat, field off', 'stable and survivable; cannot torch off the water (thrust axis horizontal): waits for field restart or recovery', WARN),
         ('Rover option', f"+{ro_['mass_t']:.1f} t; fits if well + growth bay merge ({ro_['well_plus_growth_len_m']:.1f} m); margin then {ro_['margin_after_t']:.1f} t", SH),
         ('Titan', f"float kit for 50%: {TI[names[0]]['float_kit_m3_for_50pct']:.0f} m³ (Ligeia) / {TI[names[1]]['float_kit_m3_for_50pct']:.0f} m³ (methane); never land a full tank", WARN)]
y = 0.97
for h_, txt, colr in lines:
    if h_: sm.text(0, y, h_, fontsize=9, color=INK, weight='bold', transform=sm.transAxes); y -= 0.056
    import textwrap
    for ln in textwrap.wrap(txt, 58): sm.text(0.02, y, ln, fontsize=8.3, color=colr, transform=sm.transAxes); y -= 0.052
    y -= 0.012
f.savefig(os.path.join(H, 'weave_tictac_v1_checks.png'), dpi=150, facecolor='white'); plt.close(f)
