"""Weave shuttle finalization, step 5: geometry, docking collar, interior fit and G3 trim. NON-CANON lab demonstration.
ALL bodies. ALL sponsors. 2026-2226.

Scope (Sol, after PR #570 / CCR-2026-0005 PROPOSED): the 13.02 m shuttle, the retractable Wayfarer docking collar,
interior fit and G3 trim. Docked and absent configurations are DEMONSTRATED here; released Wayfarer geometry,
canon GLBs and canon_glb.json are NOT touched.

1. Length: 13.02 m (stretch 0.22) vs 13.12 m (0.32), kT range. Bay fit radius, roll, slot width, buoyancy, mass, water.
2. Collar: Wayfarer tunnel_2 (r 0.6 m, x 17.6-18.75, results/out/wayfarer_v05_geometry.json) ends in a telescoping
   section. DOCKED: collar out, face at the F7 port x 18.75. UNDOCK: collar retracts by the stretch, shuttle backs off
   the rest of 0.5 m (F11). ABSENT: collar retracted. Axial positions of every state are reported.
3. Interior: a concrete zone layout (nose avionics, cabin over water, module bay, cargo well over water, aft systems)
   on the actual inner hull (0.12 m inset), with box-containment checks for six couches, the module core, the flywheel
   and the cargo well. Water is the conformal remainder.
4. Shuttle mass properties from the layout, then Wayfarer G3: the B4-S part (36.48 t at its source centroid) is
   replaced by the Weave shuttle in docked states S1-S4, S7, with the collar added in all states; trim recomputed
   with the pinned torch-chain offset (y +0.03, z -0.26) exactly as build_v05.trim_deg. Perturbation, not a rebuild.
Every assumption is labelled ASSUMPTION."""
import os, sys, json, math
import numpy as np
from matplotlib.path import Path
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import closure_screen as CS, closure_v2 as V2
E = CS.E
WF = os.path.abspath(os.path.join(H, '..', '..', '..', '..'))
GEO = json.load(open(os.path.join(WF, 'results', 'out', 'wayfarer_v05_geometry.json')))
INP = json.load(open(os.path.join(WF, 'config', 'wayfarer_v05_inputs.json')))
RHO_MOD = 4.0                                   # kt_decisions shuttle_weave_interior_stretch_collar_2026_11_22 (prototype assumption)
INSET = 0.12                                    # engine.evaluate usable-interior inset

# ---------------------------------------------------------------- 1. length options
def length_case(L):
    v2 = V2.run(RHO_MOD, length=L)              # sets CS.CFG (floats 32, length L)
    r, M = CS.mass_close(); S = CS.stowage(); Cl = CS.clearance()
    return dict(cfg=dict(CS.CFG), r=r, M=M, v2=v2, stow={k: v for k, v in S.items() if k in ('fit_r_m', 'exit_roll_deg', 'slot_half_width_m', 'hull_length_m')},
                th=float(S['th']), zc=float(S['zc']), clearance=Cl)

# ---------------------------------------------------------------- 2. collar and axial states
BAY_X = INP['bay']['x_m']; PORT_X = INP['shuttle']['nose_port_x_m']; BACKOFF = 0.5
COLLAR = dict(radius_m=0.6, wall_mm=6, ti_t_m3=4.5,
              mass_t=0.08,                       # ASSUMPTION: Ti sleeve ~0.03 t + seal rings, 4 screw actuators, latches, cabling ~0.05 t
              note='telescoping end of tunnel_2; pressure seal only; berth loads stay on the four cradle latches (inputs shuttle.b4s_berth.load_route)')
def axial_states(L):
    stroke = round(L - 12.8, 3)
    fixed_face = PORT_X - stroke
    docked = dict(collar_face_x=PORT_X, nose_x=PORT_X, tail_x=PORT_X + L, aft_clearance_m=round(BAY_X[1] - (PORT_X + L), 3),
                  fore_note='nose on the collar face at x 18.75 (F7 unchanged in the docked state)')
    nose_b = fixed_face + BACKOFF
    undock = dict(collar_face_x=fixed_face, nose_x=nose_b, tail_x=nose_b + L, separation_m=round(nose_b - fixed_face, 3),
                  backoff_by_shuttle_m=round(nose_b - PORT_X, 3), aft_clearance_m=round(BAY_X[1] - (nose_b + L), 3))
    absent = dict(collar_face_x=fixed_face, note='collar retracted; bay empty')
    base = dict(nose_x=PORT_X, tail_x=PORT_X + 12.8, aft_clearance_m=round(BAY_X[1] - PORT_X - 12.8, 3),
                after_backoff_tail_x=PORT_X + BACKOFF + 12.8, after_backoff_aft_clearance_m=round(BAY_X[1] - PORT_X - BACKOFF - 12.8, 3))
    return dict(stroke_m=stroke, fixed_tunnel_face_x=round(fixed_face, 3), stub_fixed_m=round(fixed_face - BAY_X[0], 3), docked=docked, undock=undock,
                absent=absent, baseline_12p8=base, collar=COLLAR,
                checks=dict(F11_separation_ok=abs(undock['separation_m'] - BACKOFF) < 1e-9, undock_tail_inside_bay=undock['tail_x'] <= BAY_X[1] + 1e-9,
                            F7_docked_port_unchanged=docked['collar_face_x'] == PORT_X,
                            F9_docked_aft_clearance_m=docked['aft_clearance_m'], F9_criterion_m=0.5,
                            F9_status='below the 0.5 m criterion; kT accepted the reduced docked aft clearance with the collar (kt_decisions shuttle_weave_interior_stretch_collar_2026_11_22)',
                            retracted_collar_fits_stub=stroke <= (fixed_face - BAY_X[0]) + 1e-9))

# ---------------------------------------------------------------- 3. interior layout
def clip_above(S, z0, keep_above=True):
    out = []; n = len(S)
    for i in range(n):
        a, b = S[i], S[(i + 1) % n]; ina = (a[1] >= z0) == keep_above; inb = (b[1] >= z0) == keep_above
        if ina: out.append(a)
        if ina != inb:
            t = (z0 - a[1]) / (b[1] - a[1]); out.append(a + t * (b - a))
    return np.array(out) if len(out) >= 3 else np.zeros((0, 2))
def area(S): return E.poly_area(S) if len(S) >= 3 else 0.0
class Hull:
    def __init__(s, cfg):
        s.cfg = cfg; s.K = E.keys(cfg); s.L = float(s.K[-1, 0])
        s.xs = np.linspace(0.0, s.L, 652); s.dx = s.xs[1] - s.xs[0]
        s.secs = [E.inset(E.section(s.K, x, cfg['keel']), INSET) for x in s.xs]
        s.A = np.array([area(S) for S in s.secs])
        s.zg = np.round(np.arange(-1.30, 1.50, 0.01), 2)                  # floor-height grid: area above z, per slice, cumulative in x
        s.Aab = np.array([[area(clip_above(S, z)) for z in s.zg] for S in s.secs])
        s.cumA = np.r_[0.0, np.cumsum(s.A) * s.dx]; s.cumAb = np.vstack([np.zeros(len(s.zg)), np.cumsum(s.Aab, 0) * s.dx])
    def idx(s, x): return int(np.searchsorted(s.xs, x - 1e-12))
    def kz(s, z): return int(np.argmin(np.abs(s.zg - z)))
    def _cum(s, C, x):                                                  # cumulative volume to x, interpolated (slice i spans xs[i] +- dx/2)
        u = (x - s.xs[0]) / s.dx + 0.5; i = int(np.clip(np.floor(u), 0, len(s.xs) - 1)); fr = float(np.clip(u - i, 0, 1))
        return C[i] + fr * (C[i + 1] - C[i])
    def vol_fast(s, x0, x1, z=None, above=True):
        tot = s._cum(s.cumA, x1) - s._cum(s.cumA, x0)
        if z is None: return tot
        u = float(np.clip((z - s.zg[0]) / 0.01, 0, len(s.zg) - 1.001)); k = int(u); w = u - k     # linear in z between grid rows
        ab = [(s._cum(s.cumAb[:, j], x1) - s._cum(s.cumAb[:, j], x0)) for j in (k, k + 1)]; ab = (1 - w) * ab[0] + w * ab[1]
        return ab if above else tot - ab
    def floor_for(s, x0, x1, target):                                  # floor height giving exactly target volume above it
        lo, hi = float(s.zg[0]), float(s.zg[-1])
        if s.vol_fast(x0, x1, lo) < target: return None
        for _ in range(50):
            m = 0.5 * (lo + hi); lo, hi = (m, hi) if s.vol_fast(x0, x1, m) > target else (lo, m)
        return round(0.5 * (lo + hi), 4)
    def inner(s, x): return E.inset(E.section(s.K, x, s.cfg['keel']), INSET)
    def vol(s, x0, x1, f=None):
        m = (s.xs >= x0) & (s.xs < x1)
        return float(sum((f(S) if f else area(S)) for S, k in zip(s.secs, m) if k) * s.dx)
    def solve_x(s, x0, target, forward=True):
        """x at which the full-section volume measured from x0 (towards +x or -x) reaches target (bisection on vol_fast)"""
        lo, hi = (x0, s.L) if forward else (0.0, x0)
        f = (lambda x: s.vol_fast(x0, x) - target) if forward else (lambda x: s.vol_fast(x, x0) - target)
        if (f(hi) if forward else f(lo)) < 0: return None, None
        for _ in range(60):
            m = 0.5 * (lo + hi)
            if forward: lo, hi = (m, hi) if f(m) < 0 else (lo, m)
            else: lo, hi = (lo, m) if f(m) < 0 else (m, hi)
        return float(0.5 * (lo + hi)), target
    def box_ok(s, x0, x1, y0, y1, z0, z1, n=9):
        for x in np.linspace(x0, x1, n):
            P = Path(np.vstack([s.inner(x), s.inner(x)[:1]]))
            pts = np.array([(y, z) for y in (y0, y1) for z in (z0, z1)])
            if not P.contains_points(pts).all(): return False
        return True
    def headroom(s, x, zf):
        S = s.inner(x); return float(S[:, 1].max() - zf)
COUCH = dict(w=0.65, l=1.85, h=0.95, gap=0.05)  # ASSUMPTION: reclined crash couch with occupant (6 couches, 3 abreast x 2 rows)
HEADROOM_MIN = 1.6                               # ASSUMPTION: clear cabin height above the floor (sit-up / weightless cabin)
PASSAGE_R = 0.4                                  # ASSUMPTION: 0.8 m clear crew passage from the nose port to the cabin
def layout(hull, need):
    """Order fore to aft: nose avionics | forward water tank with the crew passage | cabin over water | cargo well over water |
    module bay (core cube + flywheel drum side by side, next to the reactor) | aft systems."""
    L = hull.L; above = lambda z: (lambda S: area(clip_above(S, z))); below = lambda z: (lambda S: area(clip_above(S, z, False)))
    a, _ = hull.solve_x(0.0, need['avionics']); d, _ = hull.solve_x(L, need['aft'], forward=False)
    core = need['module'] ** (1 / 3); fly_d = 1.0; fly_h = need['flywheel'] / (math.pi * 0.25 * fly_d ** 2)
    lm = max(core, fly_d) + 0.25                                      # ASSUMPTION: 0.25 m service/installation gap
    c = d - lm
    fm = None
    for zf in np.arange(-1.0, 0.0, 0.01):
        if hull.box_ok(c + 0.05, c + 0.05 + core, -core - 0.05, -0.05, zf, zf + core) and hull.box_ok(c + 0.05, c + 0.05 + fly_d, 0.05, 0.05 + fly_d, zf, zf + fly_h):
            fm = round(float(zf), 2); break
    ys = [(-1.5 * COUCH['w'] - COUCH['gap'], -0.5 * COUCH['w'] - COUCH['gap']), (-0.5 * COUCH['w'], 0.5 * COUCH['w']), (0.5 * COUCH['w'] + COUCH['gap'], 1.5 * COUCH['w'] + COUCH['gap'])]
    feas = []
    for fc in np.arange(-0.80, -0.20, 0.02):
        for b in np.arange(a + 4.0, c - 0.6, 0.04):
            rows = [(b - COUCH['gap'] - COUCH['l'], b - COUCH['gap']), (b - 2 * (COUCH['gap'] + COUCH['l']), b - 2 * COUCH['gap'] - COUCH['l'])]
            s0 = None                                                 # cabin runs forward from b until it holds its allocation (passage counted in)
            for x in hull.xs[(hull.xs >= a) & (hull.xs < b)][::-1]:
                if hull.vol_fast(x, b, fc) + math.pi * PASSAGE_R ** 2 * (x - a) >= need['cabin']: s0 = float(x); break
            if s0 is None or s0 > rows[1][0]: continue
            fw = hull.floor_for(b, c, need['well'])
            if fw is None: continue
            feas.append(dict(fc=round(float(fc), 2), b=round(float(b), 2), s=round(s0, 2), fw=fw, rows=rows))
    def well_box(b, fw):                                              # largest rigid rectangular cargo box inside the well (the 6 m3 is a gross allocation)
        bb = None
        for z0 in np.arange(fw + 0.02, fw + 0.5, 0.06):
            for hw in np.arange(1.9, 0.4, -0.05):
                for ht in np.arange(2.5, 0.5, -0.05):
                    if hull.box_ok(b + 0.05, c - 0.05, -hw, hw, z0, z0 + ht, n=5):
                        v = (c - b - 0.1) * 2 * hw * ht
                        if bb is None or v > bb['volume_m3']: bb = dict(volume_m3=round(v, 2), length=round(c - b - 0.1, 2), width=round(2 * hw, 2), height=round(ht, 2), z0=round(z0, 2))
                        break
        return bb
    best = None; seen = set()
    for f in feas:
        if hull.headroom(f['b'] - 1.0, f['fc']) < HEADROOM_MIN: continue
        if not all(hull.box_ok(x0, x1, y0, y1, f['fc'] + 0.02, f['fc'] + 0.02 + COUCH['h']) for (x0, x1) in f['rows'] for (y0, y1) in ys): continue
        key = (round(f['b'], 1), round(f['fw'], 1))
        if key in seen: continue
        seen.add(key); wb = well_box(f['b'], f['fw'])
        if wb and (best is None or wb['volume_m3'] > best['well_box']['volume_m3']): best = dict(f, well_box=wb)
    if best is None: return dict(ok=False, reason='no layout: couches and cargo well do not both fit', a=a, c=c, d=d, n_volume_feasible=len(feas))
    b, s, fc, fw = best['b'], best['s'], best['fc'], best['fw']
    vf = hull.vol_fast
    V = dict(avionics=vf(0, a), aft=vf(d, L),
             passage=math.pi * PASSAGE_R ** 2 * (s - a), fwd_tank_water=vf(a, s) - math.pi * PASSAGE_R ** 2 * (s - a),
             cabin=vf(s, b, fc) + math.pi * PASSAGE_R ** 2 * (s - a), under_cabin_water=vf(s, b, fc, False),
             well=vf(b, c, fw), under_well_water=vf(b, c, fw, False), module_bay=vf(c, d))
    V['module_items'] = need['module'] + need['flywheel'] + need['install']
    V['module_bay_water'] = V['module_bay'] - V['module_items']
    V['water_total'] = V['fwd_tank_water'] + V['under_cabin_water'] + V['under_well_water'] + V['module_bay_water']
    V['inner_total'] = hull.vol_fast(0, L)
    lay = dict(a=a, s=s, b=b, c=c, d=d, fc=fc, well_floor=fw, rows=best['rows'], ys=ys, well_box=best['well_box'], module_floor=fm,
               core_edge_m=round(core, 3), flywheel=dict(d=fly_d, h=round(fly_h, 3)), n_volume_feasible=len(feas),
               volumes_m3={k: round(v, 2) for k, v in V.items()}, fore_access_m=round(best['rows'][1][0] - s, 2),
               headroom_cabin_m=round(hull.headroom(b - 1.0, fc), 2), module_ok=fm is not None, well_ok=True, well_rigid_box_fraction=round(best['well_box']['volume_m3'] / need['well'], 2),
               water_ok=V['water_total'] >= need['water'] - 1e-6, water_margin_m3=round(V['water_total'] - need['water'], 2))
    lay['ok'] = lay['module_ok'] and lay['water_ok'] and a < s < b < c < d
    xp = None                                                         # where does the 0.8 m passage first fit (nose port interface)
    for x in hull.xs:
        S = hull.inner(x); zm = 0.5 * (S[:, 1].min() + S[:, 1].max())
        if Path(np.vstack([S, S[:1]])).contains_points([(PASSAGE_R * math.cos(t), zm + PASSAGE_R * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 24)]).all():
            xp = float(x); break
    lay['passage_08m_first_x'] = round(xp, 2) if xp else None
    return lay

# ---------------------------------------------------------------- 4. mass properties and Wayfarer G3
def shell_centroid(hull):
    w = [];
    for x, S0 in zip(hull.xs, [E.section(hull.K, x, hull.cfg['keel']) for x in hull.xs]):
        per = float(np.sum(np.linalg.norm(np.roll(S0, -1, 0) - S0, axis=1))); zc = float(np.mean(S0[:, 1])); w.append((per, x, zc))
    w = np.array(w); return float(np.average(w[:, 1], weights=w[:, 0])), float(np.average(w[:, 2], weights=w[:, 0]))
def zone_centroid(hull, x0, x1, f=lambda S: S):
    acc = np.zeros(3);
    for x, S in zip(hull.xs, hull.secs):
        if x0 <= x < x1:
            P = f(S)
            if len(P) < 3: continue
            A = area(P); acc += np.array([A * x, A * float(np.mean(P[:, 1])), A]) * hull.dx
    return acc[0] / acc[2], acc[1] / acc[2]
def mass_props(hull, lay, r, M, wet):
    mi = r['mass_t']; xs_, zs_ = shell_centroid(hull)
    a, s_, b, c, d, fc, fw = lay['a'], lay['s'], lay['b'], lay['c'], lay['d'], lay['fc'], lay['well_floor']
    cab = zone_centroid(hull, s_, b, lambda S: clip_above(S, fc)); aft = zone_centroid(hull, d, hull.L); nose = zone_centroid(hull, 0, a)
    wz = [(zone_centroid(hull, a, s_), 'fwd_tank_water'), (zone_centroid(hull, s_, b, lambda S: clip_above(S, fc, False)), 'under_cabin_water'),
          (zone_centroid(hull, b, c, lambda S: clip_above(S, fw, False)), 'under_well_water'), (zone_centroid(hull, c, d), 'module_bay_water')]
    vw = {k: lay['volumes_m3'][k] for _, k in wz}; Vt = sum(vw.values())
    wx = sum(p[0] * vw[k] for p, k in wz) / Vt; wzz = sum(p[1] * vw[k] for p, k in wz) / Vt
    mod = (c + 0.05 + lay['core_edge_m'] / 2, lay['module_floor'] + lay['core_edge_m'] / 2)
    items = [  # (name, t, x, z)  ASSUMPTION: item positions; lateral symmetry about y = 0
        ('shell: hull, TPS, cabin wall, gear, mounts, floats', mi['hull_structure'] + mi['entry_tps'] + mi['cabin_wall'] + mi['gear_door'] + mi['crash_mounts'] + mi['floats'], xs_, zs_),
        ('wings (folded, root 5.5-7.3 m)', mi['wings'], 6.4, 0.2),
        ('fans at the roots (half of fans+reactor)', 0.5 * mi['fans_reactor'], 5.3, 0.6),
        ('reactor (half of fans+reactor)', 0.5 * mi['fans_reactor'], *aft),
        ('torch, belly RCS, power distribution', mi['torch'] + mi['belly_rcs'] + mi['power_dist'], *aft),
        ('cabin outfit, custody', mi['cabin'] + mi['custody'], *cab),
        ('avionics', mi['avionics'], *nose),
        ('water tank (conformal)', mi['water_tank'], wx, wzz),
        ('relational module installed', M['module']['installed_t'], *mod),
        ('flywheel', M['flywheel_t'], c + 0.05 + lay['flywheel']['d'] / 2, lay['module_floor'] + lay['flywheel']['h'] / 2)]
    if wet:
        items += [('water 23.1 t (spread over the conformal tank cells by volume)', 23.1, wx, wzz)]
    m = sum(i[1] for i in items); x = sum(i[1] * i[2] for i in items) / m; z = sum(i[1] * i[3] for i in items) / m
    return dict(mass_t=round(m, 3), cg_x_m=round(x, 3), cg_z_m=round(z, 3), items=[(n, round(t, 3), round(px, 2), round(pz, 2)) for n, t, px, pz in items])
def g3(mp_dry, mp_wet, th, zc):
    TO = GEO['thrust_line_offset_m']; dy, dz = TO['y'], TO['z']; tx = INP['torch']['thrust_point_x_m']
    old = next(p for p in GEO['parts'] if p['id'] == 'shuttle'); m0 = old['mass_t']; c0 = np.array(old['centroid_m'])
    def to_wf(mp, sgn):
        zr = mp['cg_z_m'] - zc; ang = sgn * th
        return np.array([PORT_X + mp['cg_x_m'], -zr * math.sin(ang), zr * math.cos(ang)])
    def trim(cg): e = math.hypot(cg[1] - dy, cg[2] - dz); return math.degrees(math.atan2(e, tx - cg[0]))
    col = np.array([PORT_X - 0.11, 0.0, 0.0])
    out = {}
    for case, mp in (('dry', mp_dry), ('wet', mp_wet)):
        for sgn in (1, -1):
            rows = {}
            for s, st in GEO['states'].items():
                M0 = st['mass_t']; cg = np.array(st['cg_m']) * M0 + COLLAR['mass_t'] * col; Mn = M0 + COLLAR['mass_t']
                if INP['states'][s]['shuttle'] == 'docked':
                    cn = to_wf(mp, sgn); cg = cg - m0 * c0 + mp['mass_t'] * cn; Mn = Mn - m0 + mp['mass_t']
                cg = cg / Mn
                rows[s] = dict(mass_t=round(Mn, 2), cg_m=[round(v, 4) for v in cg], trim_deg=round(trim(cg), 4), released_trim_deg=round(st['trim_deg'], 4))
            out[f'{case}_roll{"+" if sgn > 0 else "-"}'] = dict(states=rows, worst_deg=max(v['trim_deg'] for v in rows.values()),
                                                                 worst_state=max(rows, key=lambda k: rows[k]['trim_deg']))
    lim = json.load(open(os.path.join(WF, 'config', 'cert_criteria.json')))['G3']['trim_max_deg']
    return dict(limit_deg=lim, design_target_deg=INP['torch']['thrust_line_offset']['design_target_deg'], torch_offset_yz=[dy, dz], cases=out,
                worst_deg=max(v['worst_deg'] for v in out.values()), released_worst_deg=round(max(s['trim_deg'] for s in GEO['states'].values()), 4),
                method='perturbation of results/out/wayfarer_v05_geometry.json states (B4-S part replaced, collar added); trim as build_v05.trim_deg')
def berth(mp_dry, mp_wet):
    B = INP['shuttle']['b4s_berth']; g = B['ultimate_g']
    need = {k: round(mp['mass_t'] * 1e3 * 9.81 * g / 4 / 1e6, 3) for k, mp in (('dry', mp_dry), ('wet', mp_wet))}
    return dict(latch_allow_MN_each=B['latch_allow_tension_mn_each'], need_MN_each=need, ultimate_g=g,
                dry_ok_with_current_latches=need['dry'] <= B['latch_allow_tension_mn_each'],
                note='M6 is a CANDIDATE: kT 2026-11-20 decision 3 sets the docked-dry ceiling ~52.5 t with the berth latch upgrade included')

if __name__ == '__main__':
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, rho_module_t_m3=RHO_MOD, lengths={})
    for L in (13.02, 13.12):
        C = length_case(L); r, M = C['r'], C['M']
        need = dict(avionics=3.0, aft=7.0 + 0.04 * r['fans']['MWe'], cabin=CS.E.CABIN_M3_PER_COUCH * C['cfg']['seats'], well=6.0, water=1.05 * C['cfg']['water_t'],
                    module=CS.MODULE['core_t'] / RHO_MOD, flywheel=M['flywheel_t'] / 2.0, install=0.3)
        hull = Hull(C['cfg']); lay = layout(hull, need)
        if not lay.get('ok'): print(L, 'LAYOUT FAIL', lay); out['lengths'][f'{L:.2f}'] = dict(layout=lay, need_m3=need); continue
        mpd = mass_props(hull, lay, r, M, False); mpw = mass_props(hull, lay, r, M, True)
        out['lengths'][f'{L:.2f}'] = dict(stretch_m=round(L - 12.8, 2), closure=C['v2'], stowage=C['stow'], roll_th_rad=C['th'], fit_centre_z=C['zc'],
            field_clearance={k: dict(max_radius_m=v['max_radius_m'], ok=v['ok']) for k, v in C['clearance'].items()},
            need_m3={k: round(v, 2) for k, v in need.items()}, layout={k: v for k, v in lay.items()}, mass_dry=mpd, mass_wet=mpw,
            axial=axial_states(L), g3=g3(mpd, mpw, C['th'], C['zc']), berth=berth(mpd, mpw))
        o = out['lengths'][f'{L:.2f}']
        print(L, 'layout', {k: lay[k] for k in ('a', 's', 'b', 'c', 'd', 'fc', 'well_floor', 'module_floor', 'well_box', 'headroom_cabin_m', 'fore_access_m', 'water_margin_m3', 'passage_08m_first_x')}, lay['volumes_m3'],
              'dry', mpd['mass_t'], mpd['cg_x_m'], mpd['cg_z_m'], 'G3 worst', o['g3']['worst_deg'], 'aft clr', o['axial']['docked']['aft_clearance_m'])
    json.dump(out, open(os.path.join(H, 'step5_geometry.json'), 'w'), indent=1, default=float)
