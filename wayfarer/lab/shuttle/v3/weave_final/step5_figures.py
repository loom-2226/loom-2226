"""Step 5 figures: docking collar states (docked / undocking / absent) and interior fit + G3. NON-CANON.
ALL bodies. ALL sponsors. 2026-2226."""
import os, sys, json, math
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import step5_geometry as S5
INK = '#1f2933'; MUT = '#6b7280'; SH = '#2563eb'; WARN = '#d97706'; OK = '#16a34a'; BAD = '#dc2626'
C_WAT, C_CAB, C_MOD, C_WEL, C_AFT, C_AVI = '#bfdbfe', '#99f6e4', '#ddd6fe', '#fde68a', '#d1d5db', '#cbd5e1'
plt.rcParams.update({'font.size': 9.5, 'axes.edgecolor': MUT, 'axes.labelcolor': INK, 'xtick.color': MUT, 'ytick.color': MUT,
                     'axes.spines.top': False, 'axes.spines.right': False})
R = json.load(open(os.path.join(H, 'step5_geometry.json'))); O = R['lengths']['13.02']; AX = O['axial']
cfg = dict(S5.CS.by[2643]['params'], wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=23.1, floats_m3=32.0, length=13.02)
hull = S5.Hull(cfg); K = hull.K
# planform half-width of the outer hull (rolled ~86 deg in the bay, so the side view of the bay shows the planform)
xs0 = np.linspace(0.0, hull.L, 200); hw = np.array([np.abs(S5.E.section(K, x, cfg['keel'])[:, 0]).max() for x in xs0]); xs = np.linspace(0.3, hull.L, 200)

# ======================================================== figure 1: collar states
f = plt.figure(figsize=(13, 10.0))
f.suptitle('Weave shuttle in the Wayfarer bay: retractable docking collar (NON-CANON lab demonstration)', x=0.02, ha='left', y=0.985, color=INK, fontsize=13)
f.text(0.02, 0.948, 'Side view of the bay, slot (+Z) up. Shuttle 13.02 m, rolled for stowage. Released Wayfarer geometry unchanged: the collar is a proposed modification.',
       color=MUT, fontsize=9.5)
states = [('DOCKED', AX['docked']['nose_x'], AX['docked']['collar_face_x'], True),
          ('UNDOCKING: collar in 0.22 m, shuttle backs 0.28 m, then rises', AX['undock']['nose_x'], AX['undock']['collar_face_x'], True),
          ('ABSENT (shuttle away)', None, AX['absent']['collar_face_x'], False)]
fixed = AX['fixed_tunnel_face_x']; bx0, bx1 = 18.25, 32.05
for i, (title, nose, face, present) in enumerate(states):
    y0 = 0.68 - i * 0.285
    a = f.add_axes([0.04, y0, 0.6, 0.22]); z = f.add_axes([0.69, y0, 0.29, 0.22])
    for ax, xl in ((a, (17.2, 32.6)), (z, (17.4, 19.7))):
        ax.add_patch(Rectangle((bx0, -2.4), bx1 - bx0, 4.8, fc='#f8fafc', ec=MUT, lw=1.0))
        ax.plot([bx0, bx0], [-2.4, 2.4], color=INK, lw=2.2); ax.plot([bx1, bx1], [-2.4, 2.4], color=INK, lw=2.2)
        ax.add_patch(Rectangle((17.2, -0.6), fixed - 17.2, 1.2, fc='#e5e7eb', ec=INK, lw=1.0))                     # tunnel_2, fixed part
        ax.add_patch(Rectangle((fixed - (0.22 if face < 18.7 else 0), -0.66), 0.22, 1.32, fc=WARN, ec=INK, lw=1.0, alpha=0.9))   # collar sleeve
        if present:
            ax.add_patch(Polygon(np.c_[np.r_[nose + xs0, (nose + xs0)[::-1]], np.r_[hw, -hw[::-1]]], fc='#e0f2fe', ec=SH, lw=1.3))
        ax.set_xlim(*xl); ax.set_ylim(-2.8, 2.8); ax.set_yticks([])
        if ax is a: ax.set_aspect('equal')
    a.set_title(title, loc='left', color=INK, fontsize=10.5)
    z.set_title('fore end, zoomed', loc='left', color=MUT, fontsize=9)
    if present:
        tail = nose + hull.L; clr = bx1 - tail
        a.annotate('', xy=(bx1, 1.9), xytext=(tail, 1.9), arrowprops=dict(arrowstyle='<->', color=BAD if clr < 0.5 - 1e-9 else OK, lw=1.2))
        a.text(tail - 0.15, 2.05, f'aft clearance {clr:.2f} m', ha='right', fontsize=8.5, color=INK)
        a.text(nose + 6.5, 0, 'Weave shuttle 13.02 m', ha='center', va='center', color=SH, fontsize=9)
        if nose > face + 1e-6:
            z.annotate('', xy=(nose, 1.0), xytext=(face, 1.0), arrowprops=dict(arrowstyle='<->', color=OK, lw=1.2))
            z.text(0.5 * (face + nose), 1.15, f'{nose - face:.2f} m (F11)', ha='center', fontsize=8.5, color=INK)
    z.text(19.65, -1.6, f'fixed tunnel face x {fixed:.2f}', fontsize=8.5, color=MUT, ha='right')
    z.text(19.65, -2.1, f'collar face x {face:.2f}' + ('  (= F7 port)' if abs(face - 18.75) < 1e-6 else '  (retracted)'), fontsize=8.5, color=WARN, ha='right')
    a.set_xlabel('Wayfarer x (m)' if i == 2 else ''); z.set_xlabel('Wayfarer x (m)' if i == 2 else '')
f.text(0.04, 0.012, "Docked aft clearance 0.28 m is below the 0.5 m F9 criterion (kT accepted this with the collar). After undocking the tail sits at the bay's aft wall,\n"
       f"exactly as the 12.8 m baseline does. Collar: 0.22 m stroke into the 0.28 m fixed stub, ~{AX['collar']['mass_t']:.2f} t (assumption), pressure seal only; berth loads stay on the cradle latches.",
       fontsize=8.8, color=MUT)
f.savefig(os.path.join(H, 'weave_step5_collar.png'), dpi=150, facecolor='white'); plt.close(f)

# ======================================================== figure 2: interior fit and G3
L = O['layout']; V = L['volumes_m3']; N = O['need_m3']
f = plt.figure(figsize=(13, 9.6))
f.suptitle('Weave shuttle 13.02 m: interior fit, mass centre and Wayfarer G3 trim (NON-CANON)', x=0.02, ha='left', y=0.985, color=INK, fontsize=13)
f.text(0.02, 0.948, 'Zones on the actual inner hull (0.12 m inset). Boxes are containment-checked. Water fills the conformal remainder.', color=MUT, fontsize=9.5)
a = f.add_axes([0.05, 0.56, 0.9, 0.34])
top = np.array([hull.inner(x)[:, 1].max() for x in xs]); bot = np.array([hull.inner(x)[:, 1].min() for x in xs])
def band(x0, x1, zlo, zhi, col, lab=None):
    m = (xs >= x0) & (xs <= x1)
    lo = np.maximum(bot[m], zlo) if zlo is not None else bot[m]; hi = np.minimum(top[m], zhi) if zhi is not None else top[m]
    a.fill_between(xs[m], lo, hi, color=col, lw=0, label=lab)
band(0, L['a'], None, None, C_AVI, 'avionics, sensors')
band(L['a'], L['s'], None, None, C_WAT, 'water (conformal cells)')
band(L['s'], L['b'], L['fc'], None, C_CAB, 'cabin'); band(L['s'], L['b'], None, L['fc'], C_WAT)
band(L['b'], L['c'], L['well_floor'], None, C_WEL, 'cargo well'); band(L['b'], L['c'], None, L['well_floor'], C_WAT)
band(L['c'], L['d'], None, None, C_WAT); band(L['d'], hull.L, None, None, C_AFT, 'aft: torch, reactor, RCS')
a.plot(xs, top, color=INK, lw=1.2); a.plot(xs, bot, color=INK, lw=1.2)
zm = lambda x: 0.5 * (hull.inner(x)[:, 1].min() + hull.inner(x)[:, 1].max())
px = np.linspace(L['passage_08m_first_x'], L['s'], 20); a.plot(px, [zm(x) + 0.4 for x in px], color=INK, ls='--', lw=0.9); a.plot(px, [zm(x) - 0.4 for x in px], color=INK, ls='--', lw=0.9)
a.text(L['a'] + 0.1, zm(L['a'] + 0.9) + 0.5, 'crew passage 0.8 m', fontsize=8, color=INK)
for (x0, x1) in L['rows']:
    a.add_patch(Rectangle((x0, L['fc'] + 0.02), x1 - x0, S5.COUCH['h'], fc='white', ec='#0f766e', lw=1.0))
a.text(0.5 * (L['rows'][0][0] + L['rows'][1][0]) + 0.9, L['fc'] + 1.15, '6 couches (3 abreast x 2 rows)', fontsize=8.5, color='#0f766e', ha='center')
wb = L['well_box']; a.add_patch(Rectangle((L['b'] + 0.05, wb['z0']), wb['length'], wb['height'], fc='none', ec=WARN, lw=1.3, ls='-'))
mf = L['module_floor']; ce = L['core_edge_m']
a.add_patch(Rectangle((L['c'] + 0.05, mf), ce, ce, fc=C_MOD, ec='#6d28d9', lw=1.2, label='relational module')); a.text(L['c'] + 0.05 + ce / 2, mf + ce / 2, 'module core\n+ flywheel\n(side by side)', ha='center', va='center', fontsize=8, color='#6d28d9')
for k, (mp, col, lab) in enumerate(((O['mass_dry'], INK, 'mass centre, dry'), (O['mass_wet'], SH, 'with 23.1 t water'))):
    a.plot(mp['cg_x_m'], mp['cg_z_m'], marker='o', ms=9, mfc='white', mec=col, mew=2); a.plot(mp['cg_x_m'], mp['cg_z_m'], marker='+', ms=9, color=col, mew=1.6)
    a.text(8.5, -0.78 - 0.2 * k, f"{'⊕ ' }{lab}: x {mp['cg_x_m']:.2f} m, z {mp['cg_z_m']:+.2f} m", ha='center', fontsize=8, color=col)
a.set_xlim(-0.2, 13.3); a.set_ylim(-1.5, 1.8); a.set_aspect('equal'); a.set_xlabel('shuttle x from the nose tip (m)'); a.set_ylabel('z (m)')
a.legend(loc='upper center', ncol=6, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 1.13))
# cross-section through the couches
s = f.add_axes([0.05, 0.08, 0.2, 0.36]); xc = 0.5 * (L['rows'][0][0] + L['rows'][0][1]); P = hull.inner(xc); Po = S5.E.section(K, xc, cfg['keel'])
s.add_patch(Polygon(Po, fc='none', ec=INK, lw=1.2)); s.add_patch(Polygon(P, fc=C_CAB, ec=MUT, lw=0.6))
s.add_patch(Polygon(S5.clip_above(P, L['fc'], False), fc=C_WAT, ec='none'))
s.add_patch(Polygon(P, fc='none', ec=MUT, lw=0.6))
for (y0, y1) in L['ys']: s.add_patch(Rectangle((y0, L['fc'] + 0.02), y1 - y0, S5.COUCH['h'], fc='white', ec='#0f766e'))
s.text(0, L['fc'] + S5.COUCH['h'] + 0.15, f"headroom {L['headroom_cabin_m']:.2f} m", ha='center', fontsize=8.5, color=INK)
s.set_xlim(-2.3, 2.3); s.set_ylim(-1.4, 1.7); s.set_aspect('equal'); s.set_title(f'section at x {xc:.1f} m (couches)', loc='left', fontsize=9.5, color=INK); s.set_yticks([])
# volume table
t = f.add_axes([0.29, 0.08, 0.3, 0.36]); t.axis('off'); t.set_title('Volume: allocated need vs layout (m³)', loc='left', fontsize=9.5, color=INK)
rows = [('cabin (6 x 3.5)', N['cabin'], V['cabin']), ('water 23.1 t + 5%', N['water'], V['water_total']), ('cargo well', N['well'], V['well']),
        ('aft systems + fan power', N['aft'], V['aft']), ('avionics', N['avionics'], V['avionics']), ('module + flywheel + install', N['module'] + N['flywheel'] + N['install'], V['module_items'])]
for k, (n, need, have) in enumerate(rows):
    yy = 0.86 - k * 0.12; t.text(0.0, yy, n, fontsize=9, color=INK, transform=t.transAxes)
    t.text(0.66, yy, f'{need:.2f}', fontsize=9, color=MUT, ha='right', transform=t.transAxes); t.text(0.86, yy, f'{have:.2f}', fontsize=9, color=INK, ha='right', transform=t.transAxes)
    t.text(0.98, yy, '✓' if have >= need - 0.03 else '✗', color=OK if have >= need - 0.03 else BAD, fontsize=10, transform=t.transAxes)
t.text(0.66, 0.97, 'need', ha='right', fontsize=8.5, color=MUT, transform=t.transAxes); t.text(0.86, 0.97, 'layout', ha='right', fontsize=8.5, color=MUT, transform=t.transAxes)
t.text(0.0, 0.08, f"Rigid cargo box in the well: {wb['volume_m3']:.1f} m³ ({wb['length']} x {wb['width']} x {wb['height']} m);\nthe rest of the 6 m³ is wedge space for soft or shaped cargo.",
       fontsize=8.5, color=WARN, transform=t.transAxes)
# G3
g = f.add_axes([0.66, 0.1, 0.31, 0.32]); G3 = O['g3']; st = list(G3['cases']['dry_roll+']['states'])
rel = [G3['cases']['dry_roll+']['states'][k]['released_trim_deg'] for k in st]
dry = [max(G3['cases'][c]['states'][k]['trim_deg'] for c in ('dry_roll+', 'dry_roll-')) for k in st]
wet = [max(G3['cases'][c]['states'][k]['trim_deg'] for c in ('wet_roll+', 'wet_roll-')) for k in st]
xx = np.arange(len(st)); g.bar(xx - 0.27, rel, 0.26, color='#cbd5e1', label='released (B4-S)'); g.bar(xx, dry, 0.26, color=SH, label='Weave docked dry'); g.bar(xx + 0.27, wet, 0.26, color='#93c5fd', label='Weave docked wet')
g.axhline(G3['limit_deg'], color=BAD, lw=1.2); g.text(len(st) - 0.5, G3['limit_deg'] + 0.01, 'limit 0.5°', ha='right', fontsize=8.5, color=BAD)
g.axhline(G3['design_target_deg'], color=MUT, lw=0.8, ls='--'); g.text(-0.5, G3['design_target_deg'] + 0.01, 'design target 0.35°', fontsize=8, color=MUT)
g.set_xticks(xx); g.set_xticklabels(st); g.set_ylim(0, 0.68); g.set_ylabel('thrust trim (deg)')
g.set_title(f"Wayfarer G3 trim: worst {G3['worst_deg']:.3f}° (S6, shuttle away: unchanged)", loc='left', fontsize=9.5, color=INK); g.legend(frameon=False, fontsize=8, loc='upper left', ncol=3, bbox_to_anchor=(0.0, 1.0))
f.text(0.05, 0.015, f"Dry {O['mass_dry']['mass_t']:.2f} t. Berth latches need {O['berth']['need_MN_each']['dry']:.2f} MN each at 7.5 g docked dry (now 0.75 MN: upgrade, inside kT's 52.5 t ceiling); "
       f"{O['berth']['need_MN_each']['wet']:.2f} MN if docked with full water.\nNose: the 0.8 m crew passage fits only from x {L['passage_08m_first_x']:.2f} m (open interface item, shared with B4-S).",
       fontsize=8.6, color=MUT)
f.savefig(os.path.join(H, 'weave_step5_interior.png'), dpi=150, facecolor='white'); plt.close(f)
