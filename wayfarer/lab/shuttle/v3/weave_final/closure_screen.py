"""Weave shuttle finalization, steps 1-2: configuration and closure screen (SOL GO after bc0eeb5). NON-CANON until the CCR.
ALL bodies. ALL sponsors. 2026-2226.

Selected configuration (kT 2026-11-22): host = explorer #2643 + Osteon cautious + W1 programmable wing (17 m span, 1.8 m chord,
folds flat for the bay), fans 8 m2 (upper-surface blowing), floats 30 m3, 23.1 t tank, 6 couches; ~8 t onboard relational module
(W2 cushion + Weave shift) + flywheel; Weave field R 15 m / wall 2 m.
Screens (rough, as Sol asked): mass and module accounting; buoyancy; interior volume; bay stowage and exit (F8-F11 envelope);
field clearance of the actual host in its operating configurations; conventional fallback recovery envelope. G3 trim deferred.
Every assumption is labelled ASSUMPTION; values read from repo records are labelled with their source."""
import sys, os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); V3 = os.path.join(H, '..')
sys.path.insert(0, os.path.join(V3, 'explorer')); sys.path.insert(0, V3)
import engine as E
G = 9.81; C_SW = 1.025
D = json.load(open(os.path.join(V3, 'explorer', 'explorer_results.json'))); by = {r['id']: r for r in D['results']}
CFG = dict(by[2643]['params'], wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=23.1)
# ---------------------------------------------------------------- module accounting
MODULE = dict(core_t=8.0,                      # kT 2026-11-22 approved design assumption
              mounts_t=0.3,                    # ASSUMPTION: crash-rated (16-20 g) mounts per shuttle_v3_limit_load_8g
              cooling_t=0.4,                   # ASSUMPTION: cryo/thermal allowance (Wayfarer plant cryo 3.5 MW NORMAL at 88 t scales to ~0.3 MW)
              power_cond_t=0.3)                # ASSUMPTION: power conditioning and cabling to the fan reactor / flywheel
MODULE['installed_t'] = round(sum(v for k, v in MODULE.items()), 2)
PLANT_FORE = dict(mass_t=35.75, x_m=(14, 17), r_m=2.0)     # wayfarer_v05_inputs.json service.plant_fore (kT 2026-11-16)
RHO_PLANT = PLANT_FORE['mass_t'] / (math.pi * PLANT_FORE['r_m'] ** 2 * (PLANT_FORE['x_m'][1] - PLANT_FORE['x_m'][0]))
def climb_dv(h=10e3, tw=1.4):                    # copied from proto/metric_wildcards.py (torch dv spent, speed at h, time)
    a = (tw - 1) * G; t = math.sqrt(2 * h / a); return tw * G * t, a * t, t
def cushion_energy(m_t, h=2e3, eta=0.6, t_assist=20.0):
    """proto/metric_wildcards.cushion: lift to h with eta, over t_assist; flywheel 1 kWh/kg or 150 kW/kg, whichever larger"""
    _, v_h, _ = climb_dv(h)
    E_src = m_t * 1e3 * (G * h + 0.5 * v_h ** 2) / eta; P = E_src / t_assist
    return E_src, P, max(E_src / 3.6e6 / 1e3, P / 150e3 / 1e3)
def mass_close():
    r = E.evaluate(dict(CFG)); pay = 0.5 + 0.1 * CFG['seats']
    host = r['dry_t']; fly = 0.0
    for _ in range(20):                          # flywheel depends on lift-off mass: iterate (counted ONCE, in dry)
        m_lift = host + MODULE['installed_t'] + fly + pay + CFG['water_t']; Es, P, fly_new = cushion_energy(m_lift)
        if abs(fly_new - fly) < 1e-6: break
        fly = fly_new
    dry = host + MODULE['installed_t'] + fly
    lane = host + MODULE['core_t'] + cushion_energy(host + MODULE['core_t'] + 1.08 + pay + CFG['water_t'])[2]
    return r, dict(host_dry_t=host, module=MODULE, flywheel_t=round(fly, 3), dry_t=round(dry, 2), ceiling_t=52.5, margin_t=round(52.5 - dry, 2),
                   payload_t=pay, liftoff_t=round(dry + pay + CFG['water_t'], 2), cushion_source_GJ=round(Es / 1e9, 2), cushion_power_MW=round(P / 1e6),
                   lane_estimate_check_t=round(lane, 2), flywheel_counted='once (in dry); lane cushion() also counted it once')
def gates(r, M):
    pay = M['payload_t']; dry = M['dry_t']; tank = CFG['water_t']; out = {}
    earth = E.S2.MISSIONS['R1 Earth: sea to orbit, 6 pax + 2 t']['legs']; w, sh = E.water_chk(dry, pay, earth)
    out['earth_water_t'] = dict(value=w, limit=tank, thrust_short=sh, ok=(w <= tank and not sh))
    hard = [(200, .1, 1), (300, 1.3, 9.81), (3000, 2.5, 9.81), (6400, .8, 9.81), (400, .1, 1)]; w2, sh2 = E.water_chk(dry, pay, hard)
    out['hot_egress_torch_only_t'] = dict(value=w2, limit=tank + 5.0, thrust_short=sh2, ok=(w2 <= tank + 5 and not sh2), note='no cushion assist; +5 t sprint kit')
    dv_h = climb_dv(2e3)[0]; cush_legs = [(200, .1, 1), (round(3000 - dv_h), 1.4, 9.81), (6400, .8, 9.81), (400, .1, 1)]; w3, sh3 = E.water_chk(dry, pay, cush_legs)
    out['earth_and_hot_egress_with_cushion_t'] = dict(value=w3, limit=tank, thrust_short=sh3, ok=(w3 <= tank and not sh3),
        note='lane W2 legs (proto/metric_wildcards.cushion): cushion lifts to 2 km (replaces water take-off and the 2.5 g hot climb), torch from 1.4 g')
    out['earth_water_t']['note'] = 'torch-only Earth profile (field unavailable): fallback information, not the Weave operating profile' 
    m_float = dry + pay + tank; disp = m_float / C_SW; Vh = r['hull_m3']
    out['buoyancy_total_m3'] = dict(value=round(Vh + CFG['floats_m3'], 1), limit=round(1.5 * disp, 1), ok=Vh + CFG['floats_m3'] >= 1.5 * disp)
    out['buoyancy_hull_m3'] = dict(value=Vh, limit=round(disp, 1), ok=Vh >= disp)
    mod_m3 = MODULE['core_t'] / RHO_PLANT; fly_m3 = M['flywheel_t'] / 2.0; cool_m3 = 0.5      # ASSUMPTIONS: plant density basis; flywheel+housing 2 t/m3; cooling 0.5 m3
    need = r['interior_need_m3'] + mod_m3 + fly_m3 + cool_m3
    out['interior_m3'] = dict(value=r['inner_m3'], need=round(need, 1), host_need=r['interior_need_m3'], module_m3=round(mod_m3, 1), flywheel_m3=round(fly_m3, 2), cooling_m3=cool_m3,
                              margin=round(r['inner_m3'] - need, 1), ok=r['inner_m3'] >= need, rho_basis_t_m3=round(RHO_PLANT, 3),
                              note='module volume at Wayfarer fore relational-plant block density (35.75 t in r 2 m x 3 m)')
    S, clmax, stat = r['land']['S'], r['land']['clmax'], r['land']['static_kN']
    vtd = lambda mm: math.sqrt(2 * max(mm * 1e3 * G - stat * 1e3, 1.0) / (1.225 * S * clmax))
    out['fallback_touchdown_heavy_ms'] = dict(value=round(vtd(dry + pay + w), 1), limit=50.0, ok=vtd(dry + pay + w) <= 50.0, note='field off, climb water aboard, ~1 m waves (kT rule)')
    out['fallback_touchdown_light_ms'] = dict(value=round(vtd(dry + pay + 2.0), 1), limit=40.0, ok=vtd(dry + pay + 2.0) <= 40.0, note='field off, light, 2 m waves')
    out['torch_max_thrust_MN'] = 2 * 7.7e9 / 10e3 / 1e6
    return out
# ---------------------------------------------------------------- bay stowage and exit (F8-F11)
R_ENV, SLOT_HALF = 2.15, 1.9                        # F8: r 2.15 incl. 0.25 m; F10: <= 3.8 m across the slot incl. 0.5 m each side
def stowage():
    K = E.keys(CFG); xs = np.linspace(0.05, float(K[-1, 0]), 129); secs = [E.section(K, x, CFG['keel']) for x in xs]
    pts = np.vstack(secs); zs = np.linspace(pts[:, 1].min(), pts[:, 1].max(), 241)
    zc = zs[int(np.argmin([np.hypot(pts[:, 0], pts[:, 1] - z).max() for z in zs]))]
    fit_r = float(np.hypot(pts[:, 0], pts[:, 1] - zc).max())
    best = None
    for th in np.radians(np.arange(0, 180, 1.0)):                     # roll about the long axis
        c, s = math.cos(th), math.sin(th); yy = pts[:, 0] * c - (pts[:, 1] - zc) * s
        hw = float(np.abs(yy).max())
        if best is None or hw < best[1]: best = (th, hw)
    th, hw = best; c, s = math.cos(th), math.sin(th)
    phis = np.radians(np.arange(0, 360, 1.0)); dphi = np.radians(1.0); dx = xs[1] - xs[0]
    def ray_hull(S):                                                   # distance from bay axis to hull boundary along each ray (rolled frame)
        Q = np.c_[S[:, 0] * c - (S[:, 1] - zc) * s, S[:, 0] * s + (S[:, 1] - zc) * c]
        out = np.zeros(len(phis))
        for i, p in enumerate(phis):
            d = np.array([math.cos(p), math.sin(p)]); best_t = 0.0
            for j in range(len(Q)):
                a, b = Q[j], Q[(j + 1) % len(Q)]; e = b - a; M = np.array([[d[0], -e[0]], [d[1], -e[1]]])
                if abs(np.linalg.det(M)) < 1e-12: continue
                t, u = np.linalg.solve(M, a)
                if t > 0 and -1e-9 <= u <= 1 + 1e-9: best_t = max(best_t, t)
            out[i] = best_t
        return out
    def ray_allowed():
        cp, sp = np.cos(phis), np.sin(phis); band = np.where(np.abs(cp) > 1e-9, SLOT_HALF / np.maximum(np.abs(cp), 1e-9), 99.0)
        return np.minimum(R_ENV, band)
    RA = ray_allowed(); gaps = np.array([RA - ray_hull(S) for S in secs])          # (x, phi) outward gap
    rh = RA[None, :] - gaps
    sheet_area = {t: float(np.sum((gaps >= t) * rh) * dphi * dx) for t in (0.05, 0.08, 0.15, 0.3, 0.5)}
    vol = {t: float(np.sum(np.where(gaps >= t, 0.5 * (RA[None, :] ** 2 - rh ** 2), 0.0)) * dphi * dx) for t in (0.0, 0.08, 0.5)}
    # largest contiguous patch with gap >= 0.5 m (for a 1.6 m fan): extent along x and along the perimeter
    patch = gaps >= 0.5; best_patch = (0.0, 0.0)
    for j in range(patch.shape[1]):
        col = patch[:, j]; run = 0; mx = 0
        for v in col: run = run + 1 if v else 0; mx = max(mx, run)
        best_patch = max(best_patch, (mx * dx, 0.0))
    perim_run = 0.0
    for i in range(patch.shape[0]):
        row = np.r_[patch[i], patch[i]]; run = 0; mx = 0
        for k, v in enumerate(row):
            run = run + 1 if v else 0; mx = max(mx, run)
        perim_run = max(perim_run, min(mx, 360) * dphi * float(np.median(rh[i][patch[i]])) if patch[i].any() else 0.0)
    hull_len = float(K[-1, 0])
    return dict(fit_r_m=round(fit_r, 3), r_env_m=R_ENV, exit_roll_deg=round(math.degrees(th), 1), slot_half_width_m=round(hw, 3), slot_half_limit_m=SLOT_HALF,
                hull_exit_ok=hw <= SLOT_HALF, hull_length_m=hull_len, length_limit_m=12.8, length_ok=hull_len <= 12.8 + 1e-9,
                sheet_area_m2_by_gap=sheet_area, free_volume_m3_by_gap=vol, gap_ge_0p5_max_run_x_m=round(best_patch[0], 2), gap_ge_0p5_max_run_perimeter_m=round(perim_run, 2),
                gaps=gaps, xs=xs, phis=phis, RA=RA, zc=zc, th=th)
# ---------------------------------------------------------------- field clearance (actual host, operating configurations)
R_F, D_F = 15.0, 2.0
def F(r): return 0.5 * (np.tanh((r + R_F) / D_F) - np.tanh((r - R_F) / D_F))
def Fp(r): return 0.5 / D_F * (1 / np.cosh((r + R_F) / D_F) ** 2 - 1 / np.cosh((r - R_F) / D_F) ** 2)
def vehicle_points(conf):
    V, Fc, K, _, _ = E.loft(CFG); P = [V]
    xw0, xw1, zw = 5.5, 7.3, 0.2                                       # ASSUMPTION: wing root station and height (chine)
    if conf in ('flight', 'afloat'):
        for sgn in (-1, 1):
            for x in np.linspace(xw0, xw1, 5):
                for y in np.linspace(2.13, CFG['span'] / 2, 12): P.append(np.array([[x, sgn * y, zw]]))
        for y in (2.9, 3.9):                                           # ASSUMPTION: 4 fans of 1.6 m at the roots (USB)
            for sgn in (-1, 1):
                ang = np.linspace(0, 2 * np.pi, 16); P.append(np.c_[np.full(16, xw0 - 0.2), sgn * y + 0.8 * np.cos(ang), zw + 0.4 + 0.3 * np.sin(ang)])
    if conf == 'afloat':
        rf = math.sqrt(CFG['floats_m3'] / 2 / (math.pi * 8.0))       # ASSUMPTION: two 8 m sponsons
        for sgn in (-1, 1):
            ang = np.linspace(0, 2 * np.pi, 16)
            for x in np.linspace(2.0, 10.0, 9): P.append(np.c_[np.full(16, x), sgn * (2.13 + rf) + rf * np.cos(ang), -0.6 + rf * np.sin(ang)])
    return np.vstack(P)
def clearance():
    out = {}
    for conf in ('stowed', 'flight', 'afloat'):
        P = vehicle_points(conf); best = None
        for cx in np.linspace(4, 9, 26):
            for cz in np.linspace(-1, 1, 11):
                r = np.sqrt((P[:, 0] - cx) ** 2 + P[:, 1] ** 2 + (P[:, 2] - cz) ** 2).max()
                if best is None or r < best[0]: best = (r, cx, cz)
        r, cx, cz = best; Q = P - np.array([cx, 0, cz]); rr = np.linalg.norm(Q, axis=1) + 1e-12
        # carriage fraction along the motion axis for motion along x (axial) and along y (transverse): b_par = F + rho^2 F'/(2r)
        res = {}
        for ax, name in ((0, 'axial'), (1, 'transverse')):
            rho2 = rr ** 2 - Q[:, ax] ** 2; bpar = F(rr) + rho2 * Fp(rr) / (2 * rr)
            res[name] = dict(min_carriage=float(bpar.min()), differential=float(1 - bpar.min()))
        out[conf] = dict(max_radius_m=round(float(r), 2), field_centre_x_m=round(cx, 2), field_centre_z_m=round(cz, 2), guideline_m=R_F - 2.5 * D_F,
                         F_at_max=float(F(r)), ok=float(r) <= R_F - 2.5 * D_F, **res,
                         differential_g_at_71g=round(71.0 * max(res['axial']['differential'], res['transverse']['differential']), 3))
    return out
# ---------------------------------------------------------------- fallback recovery envelope (estimates)
def fallback(M, gt):
    m = M['liftoff_t'] * 1e3; T = gt['torch_max_thrust_MN'] * 1e6; a_net = T / m - G
    v_min = gt['fallback_touchdown_heavy_ms']['value']
    rows = dict(water_drop_survivable_m=round(10.0 ** 2 / (2 * G), 1), land_drop_survivable_m=round(6.0 ** 2 / (2 * G), 1),
                torch_net_accel_g=round(a_net / G, 2))
    for ts in (1.0, 2.0, 3.0):
        v = G * ts; rows[f'torch_recovery_min_alt_m_start_{ts:g}s'] = round(0.5 * G * ts ** 2 + v ** 2 / (2 * a_net) + 10.0, 1)
    rows['aero_recovery_from_hover_min_alt_m'] = round(v_min ** 2 / (2 * G) * 1.3 + v_min ** 2 / (G * 1.5), 0)
    rows['aero_immediate_if_airspeed_ge_ms'] = v_min
    rows['assumptions'] = ('ASSUMPTIONS: survivable vertical impact 10 m/s on water (floats, crash-rated seats), 6 m/s on land (gear); torch emergency start '
                           '1-3 s at full 7.7 GW with the 10 km/s exhaust floor (max thrust 1.54 MN); aero recovery = dive to the heavy minimum flying speed '
                           '(fallback touchdown speed) with 30% loss allowance plus a 2.5 g pull-out; no field assistance; no miraculous failsafe')
    return rows
if __name__ == '__main__':
    r, M = mass_close(); gt = gates(r, M); S = stowage(); Cl = clearance(); FB = fallback(M, gt)
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, config=CFG, host_record=dict(fit_r=r['fit_r_m'], hull_m3=r['hull_m3'], inner_m3=r['inner_m3'],
               mass_items_t=r['mass_t'], osteon=r['osteon'], interior_need_host_m3=r['interior_need_m3']), mass=M, gates=gt,
               stowage={k: v for k, v in S.items() if k not in ('gaps', 'xs', 'phis', 'RA', 'zc', 'th')}, field_clearance=Cl, fallback=FB)
    json.dump(out, open(os.path.join(H, 'closure_screen.json'), 'w'), indent=1, default=float)
    np.savez_compressed(os.path.join(H, 'closure_stowage.npz'), gaps=S['gaps'], xs=S['xs'], phis=S['phis'], RA=S['RA'], zc=S['zc'], th=S['th'])
    print(json.dumps({k: out[k] for k in ('mass', 'gates', 'stowage', 'field_clearance', 'fallback')}, indent=1, default=float))
