"""Tic Tac build-out v1 (kT 2026-11-22: 'Tic tac. It is'). NON-CANON lab design. ALL bodies. ALL sponsors. 2026-2226.

Sol's checks are the build-out list: afloat stability, waterborne cargo/rover access, realistic field-off recovery,
exact-fit bay exit, Titan lake buoyancy. Same module, tank, torch and mass rules as tictac_vs_shuttle.py.

Geometry: capsule, length 12.8 m, hemispherical ends, diameter D (3.8 = F10 exit limit exactly; 3.7 = 0.05 m extra each side).
Axis at y = z = 0, nose tip x = 0 (docking hatch on the axis, F7). Inner surface = outer - 0.12 m.
Layout (fore to aft): nose dome (docking vestibule + passage, avionics, parachutes, water) | cabin (6 couches 3x2) |
cargo well (floodable, side door in the lower flank, W4) | module bay | growth bay (unallocated) | aft dome (torch, reactor, RCS).
One continuous deck at z_f; water in bilge cells under the deck and in the dome remainders.
Hydrostatics: every section is a circle centred on the axis, so buoyancy always acts through the axis: roll GM = -z_CG
(exact), less the free-surface correction of the slack tanks / flooded well.
Every assumption is labelled ASSUMPTION."""
import os, sys, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import closure_screen as CS
E = CS.E
TV = json.load(open(os.path.join(H, 'tictac_vs_shuttle.json')))
L, WALL, TANK, PAY = 12.8, 0.12, 23.1, 1.1
G = 9.81; RHO_SW = 1.025
DECK = -0.85                                  # ASSUMPTION: deck height; leaves a ~0.9 m bilge for water cells (low CG)
COUCH = dict(w=0.65, l=1.85, h=0.95, gap=0.05)
ZONES_LEN = dict(cabin=3.95, well=1.30, module=1.60)   # ASSUMPTION: cabin = 2 couch rows + aisle; well sized for a 6 m3 rigid box
CHUTE_FRAC = 0.035                            # ASSUMPTION: parachute system ~3.5% of the landing mass (Apollo ~4.5%)
POWER_UNIT_T = 1.0                            # ASSUMPTION: cooling / flywheel recharge power unit (no lift fans)
SURVIVE = dict(water=10.0, land=6.0)          # ASSUMPTION (as the shuttle card): survivable vertical impact, m/s

def r_out(x, R):
    if x < R: return math.sqrt(max(R * R - (R - x) ** 2, 0.0))
    if x > L - R: return math.sqrt(max(R * R - (x - (L - R)) ** 2, 0.0))
    return R
def r_in(x, R):
    ri = R - WALL
    if x < R: return math.sqrt(max(ri * ri - (R - x) ** 2, 0.0))
    if x > L - R: return math.sqrt(max(ri * ri - (x - (L - R)) ** 2, 0.0))
    return ri
def seg_below(r, z):                          # area of a circle of radius r (centre 0) below height z
    if r <= 0: return 0.0
    if z <= -r: return 0.0
    if z >= r: return math.pi * r * r
    return r * r * math.acos(-z / r) + z * math.sqrt(r * r - z * z)
def seg_cz_below(r, z):                       # centroid height of that segment
    A = seg_below(r, z)
    if A <= 0: return 0.0
    if z >= r: return 0.0
    return -(2.0 / 3.0) * (r * r - z * z) ** 1.5 / A
XS = np.linspace(0.0, L, 2561); DX = XS[1] - XS[0]
def zone(x0, x1, R, zlo=None, zhi=None):
    """volume and centroid (x, z) of the inner hull between x0, x1 and heights zlo..zhi"""
    V = Mx = Mz = 0.0
    for x in XS[(XS >= x0) & (XS < x1)]:
        r = r_in(x, R); lo = -r if zlo is None else max(zlo, -r); hi = r if zhi is None else min(zhi, r)
        if hi <= lo: continue
        A = seg_below(r, hi) - seg_below(r, lo)
        if A <= 0: continue
        zc = (seg_below(r, hi) * seg_cz_below(r, hi) - seg_below(r, lo) * seg_cz_below(r, lo)) / A
        V += A * DX; Mx += A * DX * x; Mz += A * DX * zc
    return (V, Mx / V if V else 0.0, Mz / V if V else 0.0)
def box_in(R, x0, x1, y0, y1, z0, z1):
    for x in np.linspace(x0, x1, 7):
        r = r_in(x, R)
        for y in (y0, y1):
            for z in (z0, z1):
                if y * y + z * z > r * r: return False
    return True

def build(D):
    R = D / 2; out = dict(D=D, R=R)
    # ------------------------------------------------ mass ledger (tictac_vs_shuttle rules, scaled to D)
    base = TV['tictac']; mi = dict(base['mass_items'])
    sw = 2 * math.pi * R * (L - 2 * R) + 4 * math.pi * R * R; pl = 2 * R * (L - 2 * R) + math.pi * R * R
    mi['hull_structure'] *= sw / base['swet_m2']; mi['entry_tps'] *= pl / base['planform_m2']; mi['fans_reactor'] = POWER_UNIT_T
    mi['floats'] = 0.0
    host = sum(mi.values()); fly = 0.0
    for _ in range(40):
        lift = host + CS.MODULE['installed_t'] + fly + PAY + TANK; Es, P, fn = CS.cushion_energy(lift)
        chutes = CHUTE_FRAC * (host + CS.MODULE['installed_t'] + fn + PAY + TANK)      # sized for a full-tank landing
        if abs(fn - fly) < 1e-8: break
        fly = fn
    dry = host + CS.MODULE['installed_t'] + fly + chutes
    out['mass'] = dict(items={k: round(v, 3) for k, v in mi.items()}, host_t=round(host, 2), module_t=CS.MODULE['installed_t'], flywheel_t=round(fly, 3),
                       chutes_t=round(chutes, 2), dry_t=round(dry, 2), margin_t=round(52.5 - dry, 2), cushion_GJ=round(Es / 1e9, 2), cushion_MW=round(P / 1e6))
    dv_h = CS.climb_dv(2e3)[0]; legs = [(200, .1, 1), (round(3000 - dv_h), 1.4, 9.81), (6400, .8, 9.81), (400, .1, 1)]
    w, sh = E.water_chk(dry, PAY, legs); out['water'] = dict(earth_cushion_t=w, tank_t=TANK, ok=w <= TANK and not sh,
        earth_torch_only_t=E.water_chk(dry, PAY, E.S2.MISSIONS['R1 Earth: sea to orbit, 6 pax + 2 t']['legs'])[0])
    # ------------------------------------------------ layout
    xa = R; xb = xa + ZONES_LEN['cabin']; xc = xb + ZONES_LEN['well']; xd = xc + ZONES_LEN['module']; xe = L - R
    Z = {}
    Z['nose_dome'] = zone(0, xa, R); Z['aft_dome'] = zone(xe, L, R)
    Z['cabin'] = zone(xa, xb, R, DECK); Z['well'] = zone(xb, xc, R, DECK); Z['module_bay'] = zone(xc, xd, R, DECK); Z['growth_bay'] = zone(xd, xe, R, DECK)
    Z['bilge'] = zone(xa, xe, R, None, DECK)
    inner_total = zone(0, L, R)[0]
    need = dict(cabin=21.0, water=1.05 * TANK, well=6.0, aft=7.0 + 0.04 * 6.0, avionics=3.0, chutes=1.0 + 0.0 * chutes, passage=math.pi * 0.16 * R,
                module=2.0, flywheel=fly / 2.0, install=0.3)
    # items placed in the domes; dome remainders below the axis hold water
    nose_items = need['avionics'] + need['chutes'] + need['passage']; aft_items = need['aft']
    dome_water = (Z['nose_dome'][0] - nose_items) + (Z['aft_dome'][0] - aft_items)
    mod_items = need['module'] + need['flywheel'] + need['install']
    water_vol = Z['bilge'][0] + dome_water
    rows = [(xb - COUCH['gap'] - COUCH['l'], xb - COUCH['gap']), (xb - 2 * (COUCH['gap'] + COUCH['l']), xb - 2 * COUCH['gap'] - COUCH['l'])]
    ys = [(-1.5 * COUCH['w'] - COUCH['gap'], -0.5 * COUCH['w'] - COUCH['gap']), (-0.5 * COUCH['w'], 0.5 * COUCH['w']), (0.5 * COUCH['w'] + COUCH['gap'], 1.5 * COUCH['w'] + COUCH['gap'])]
    couches_ok = all(box_in(R, x0, x1, y0, y1, DECK + 0.02, DECK + 0.02 + COUCH['h']) for x0, x1 in rows for y0, y1 in ys) and rows[1][0] >= xa
    wb = None
    for hw in np.arange(1.6, 0.6, -0.02):
        for ht in np.arange(2.4, 1.0, -0.02):
            ln = need['well'] / (2 * hw * ht)
            if ln <= ZONES_LEN['well'] - 0.1 and box_in(R, xb + 0.05, xb + 0.05 + ln, -hw, hw, DECK + 0.02, DECK + 0.02 + ht):
                wb = dict(volume_m3=round(2 * hw * ht * ln, 2), length=round(ln, 2), width=round(2 * hw, 2), height=round(ht, 2)); break
        if wb: break
    core = need['module'] ** (1 / 3); fdh = need['flywheel'] / (math.pi * 0.25)
    module_ok = box_in(R, xc + 0.05, xc + 0.05 + core, -core - 0.05, -0.05, DECK + 0.02, DECK + 0.02 + core) and box_in(R, xc + 0.05, xc + 1.05, 0.05, 1.05, DECK + 0.02, DECK + 0.02 + fdh)
    headroom = (R - WALL) - DECK
    spare = inner_total - (need['cabin'] + need['well'] + mod_items + nose_items + aft_items + need['water'])
    out['layout'] = dict(x=dict(nose_dome=(0, xa), cabin=(xa, xb), well=(xb, xc), module_bay=(xc, xd), growth_bay=(xd, xe), aft_dome=(xe, L)), deck_z=DECK,
                         zones_m3={k: round(v[0], 2) for k, v in Z.items()}, inner_total_m3=round(inner_total, 1), need_m3={k: round(v, 2) for k, v in need.items()},
                         water_cells_m3=round(water_vol, 2), water_ok=water_vol >= need['water'], cabin_ok=Z['cabin'][0] >= need['cabin'] and couches_ok,
                         couches_ok=couches_ok, rows=rows, ys=ys, headroom_m=round(headroom, 2), well_box=wb, well_ok=wb is not None and Z['well'][0] >= need['well'],
                         module_ok=module_ok, core_edge_m=round(core, 3), flywheel_drum=dict(d=1.0, h=round(fdh, 3)),
                         unallocated_m3=round(spare, 1), passage_at_nose='0.8 m passage fits from the nose tip: the hemispherical nose solves the B4-S-family nose-port gap')
    # ------------------------------------------------ mass properties (x, z); y = 0 by symmetry
    cab = Z['cabin']; bil = Z['bilge']
    items = [('shell: hull, cabin wall, gear, mounts', mi['hull_structure'] + mi['cabin_wall'] + mi['gear_door'] + mi['crash_mounts'], L / 2, 0.0),
             ('entry TPS (windward = belly)', mi['entry_tps'], L / 2, -0.85 * R),
             ('torch, belly RCS, power distribution', mi['torch'] + mi['belly_rcs'] + mi['power_dist'], L - 0.75, 0.0),
             ('power unit', mi['fans_reactor'], L - 1.3, -0.6),
             ('cabin outfit, custody, payload', mi['cabin'] + mi['custody'] + PAY, cab[1], DECK + 0.6),
             ('avionics', mi['avionics'], 0.9, 0.3), ('parachutes (upper nose)', chutes, 0.9, 0.9),
             ('relational module', CS.MODULE['installed_t'], xc + 0.05 + core / 2, DECK + 0.02 + core / 2),
             ('flywheel', fly, xc + 0.55, DECK + 0.02 + fdh / 2), ('water tank cells (structure)', mi['water_tank'], bil[1], bil[2])]
    water_cells = [(bil[0], bil[1], bil[2]), (Z['nose_dome'][0] - nose_items, *zone(0, xa, R, None, 0.0)[1:]), (Z['aft_dome'][0] - aft_items, *zone(xe, L, R, None, 0.0)[1:])]
    def props(water_t):                                   # water fills the bilge first, then the dome cells
        its = list(items); left = water_t
        for v, x, z in water_cells:
            take = min(left, v / 1.05 * 1.0); its.append(('water', take, x, z if take >= v / 1.05 - 1e-9 else z - 0.15)); left -= take
        m = sum(i[1] for i in its); return m, sum(i[1] * i[2] for i in its) / m, sum(i[1] * i[3] for i in its) / m
    # ------------------------------------------------ hydrostatics (outer hull, circular sections)
    def disp(zw):
        return sum(seg_below(r_out(x, R), zw) for x in XS) * DX
    def waterline(m_t):
        lo, hi = -R, R
        for _ in range(60):
            mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if disp(mid) * RHO_SW < m_t else (lo, mid)
        return 0.5 * (lo + hi)
    Vh = disp(R + 1)
    # free-surface correction: baffled bilge cells (ASSUMPTION: 4 longitudinal x 2 transverse cells), flooded well (one free surface)
    bw = 2 * math.sqrt((R - WALL) ** 2 - DECK ** 2); bl = xe - xa
    I_bilge = 8 * ((bl / 4) * (bw / 2) ** 3 / 12)
    cases = {}
    def case(water_t, flood):
        m, xg, zg = props(water_t); zw = waterline(m)
        fs = (I_bilge * 1.0 / RHO_SW) / (m / RHO_SW) if 0 < water_t < TANK else (I_bilge * 0.25 / RHO_SW) / (m / RHO_SW)
        if flood:
            for _ in range(3):
                fv = max(0.0, zone(xb, xc, R, DECK, zw)[0]); m2 = m + fv * RHO_SW; zw = waterline(m2)
            zg = (m * zg + fv * RHO_SW * zone(xb, xc, R, DECK, zw)[2]) / m2 if fv > 0 else zg
            fs += (ZONES_LEN['well'] * (2 * math.sqrt(max((R - WALL) ** 2 - zw ** 2, 0))) ** 3 / 12) / (m2 / RHO_SW); m = m2
        return -zg - fs
    ballast = next((w for w in np.arange(2.0, TANK + 0.01, 0.5) if case(w, True) >= 0.3), None)
    out['afloat_rule'] = dict(min_water_ballast_t_for_GM_0p3_well_flooded=ballast, GM_at_that=round(case(ballast, True), 3) if ballast else None,
                              note='operational rule: keep at least this much water in the bilge cells while afloat with the well door open (or pump sea ballast into empty cells)')
    for name, water_t, flood in (('full tank', TANK, False), ('light (2 t water)', 2.0, False), ('full tank, well flooded', TANK, True), ('light, well flooded', 2.0, True)):
        m, xg, zg = props(water_t); zw = waterline(m)
        fs = (I_bilge * 1.0 / RHO_SW) / (m / RHO_SW) if 0 < water_t < TANK else (I_bilge * 0.25 / RHO_SW) / (m / RHO_SW)   # full cells: small residual ullage
        if flood:                                         # sea floods the well up to the waterline: lost buoyancy = flooded volume (approx as added mass)
            fv = zone(xb, xc, R, DECK, None)[0] if zw > DECK else 0.0
            fv = max(0.0, zone(xb, xc, R, DECK, zw)[0]); m2 = m + fv * RHO_SW
            zw = waterline(m2); fv = max(0.0, zone(xb, xc, R, DECK, zw)[0]); m2 = m + fv * RHO_SW; zw = waterline(m2)
            zg = (m * zg + fv * RHO_SW * zone(xb, xc, R, DECK, zw)[2]) / m2 if fv > 0 else zg
            fs += (ZONES_LEN['well'] * (2 * math.sqrt(max((R - WALL) ** 2 - zw ** 2, 0))) ** 3 / 12) / (m2 / RHO_SW); m = m2
        gm = -zg - fs
        cases[name] = dict(mass_t=round(m, 2), cg_x=round(xg, 2), cg_z=round(zg, 3), waterline_z=round(zw, 3), freeboard_axis_m=round(-zw, 3),
                           draft_m=round(zw + R, 2), GM_roll_m=round(gm, 3), stable=gm > 0.05, free_surface_m=round(fs, 3),
                           well_deck_vs_waterline_m=round(DECK - zw, 2), reserve_buoyancy=round(Vh * RHO_SW / m - 1, 2))
    out['hydrostatics'] = dict(hull_m3=round(Vh, 1), cases=cases, note='roll GM exact for circular sections (buoyancy through the axis); pitch stability large (length 12.8 m)')
    # W3 torch exit: on the axis at the aft dome
    zw_full = cases['full tank']['waterline_z']
    out['torch_exit'] = dict(z=0.0, waterline_full=zw_full, clear_of_waterline_plus_1m=0.0 >= zw_full + 1.0,
                             note='axis torch is horizontal; a field-off torch take-off from water would need the thrust pointed down. Not available: see fallback.')
    # ------------------------------------------------ field-off fallback (hover, from rest)
    m_full = props(TANK)[0]
    def chute_fall(h0, m_t, CdA, t_deploy=1.0, t_inflate=2.5, rho=1.225, dt=0.002):
        z, v, t = h0, 0.0, 0.0
        while z > 0:
            f = 0.0 if t < t_deploy else min(1.0, (t - t_deploy) / t_inflate)
            a = G - 0.5 * rho * v * v * CdA * f / (m_t * 1e3); v += a * dt; z -= v * dt; t += dt
        return v
    CdA = 2 * m_full * 1e3 * G / (1.225 * 8.0 ** 2)                # ASSUMPTION: cluster sized for 8 m/s at full-tank mass
    def hmin(t_inf):
        return next(h for h in np.arange(2, 600, 1.0) if chute_fall(h, m_full, CdA, t_inflate=t_inf) <= SURVIVE['water'] and all(chute_fall(hh, m_full, CdA, t_inflate=t_inf) <= SURVIVE['water'] for hh in np.arange(h, h + 60, 5)))
    sens = {f'inflate_{t:g}s': float(hmin(t)) for t in (2.5, 4.0, 6.0)}
    h_min_water = next(h for h in np.arange(2, 400, 1.0) if chute_fall(h, m_full, CdA) <= SURVIVE['water'] and all(chute_fall(hh, m_full, CdA) <= SURVIVE['water'] for hh in np.arange(h, h + 60, 5)))
    out['fallback'] = dict(drop_survivable_water_m=round(SURVIVE['water'] ** 2 / (2 * G), 1), drop_survivable_land_m=round(SURVIVE['land'] ** 2 / (2 * G), 1),
                           chute_CdA_m2=round(CdA), chute_min_hover_alt_water_m=float(h_min_water), chute_terminal_ms=8.0, chute_min_alt_sensitivity_m=sens,
                           chute_assumptions='mortar deploy 1.0 s, linear inflation 2.5 s, cluster CdA for 8 m/s at full-tank mass; survivable 10 m/s water / 6 m/s land',
                           torch='axis torch is horizontal: arresting a fall needs a 90 deg pitch-up first (time not credited); torch remains the ascent engine',
                           afloat_field_off='floats stably; cannot torch off the water (thrust horizontal); waits for field restart or Wayfarer recovery',
                           shuttle_for_comparison=dict(no_recovery_band_m=[5.1, 46.8], above='torch (1-3 s start)', airspeed='wings take over >= ~50 m/s'))
    # ------------------------------------------------ bay exit (F8, F10) and docking
    out['bay'] = dict(F8_radius_m=R, F8_limit=2.15, F8_ok=R <= 2.15, F10_width_m=D, F10_limit=3.8, F10_extra_margin_each_side_m=round((3.8 - D) / 2, 3),
                      F10_ok=D <= 3.8 + 1e-9, roll='any (round)', F9_length_m=L, F9_ok=L <= 12.8 + 1e-9, collar='not needed', note='protrusions (hinges, RCS, antennas) must stay inside D')
    # ------------------------------------------------ Titan lakes
    tw = E.water_chk(dry, PAY, E.S2.MISSIONS['R3 Titan']['legs'])[0]
    m_t = dry + PAY + tw
    out['titan'] = {f'{name} ({rho} kg/m3)': dict(rho=rho, landed_t=round(m_t, 1), max_supported_t=round(Vh * rho / 1e3, 1), reserve=round(Vh * rho / 1e3 / m_t - 1, 2),
                    full_tank_reserve=round(Vh * rho / 1e3 / (dry + PAY + TANK) - 1, 2), float_kit_m3_for_50pct=round(max(0.0, 1.5 * m_t * 1e3 / rho - Vh), 1))
                    for name, rho in (('Ligeia-like', 551), ('near-pure methane', 447))}
    out['titan_water_t'] = tw
    # ------------------------------------------------ rover option (fits the growth bay?)
    rov_t = 0.973 + 0.258 + 0.6
    out['rover_option'] = dict(mass_t=round(rov_t, 2), source='b4s_mass.json standard_A2 rover chassis + light cabin shell + outfit', capsule_m='1.9 x 3.0 (B4-S rover/capsule)',
                               growth_bay_m3=round(Z['growth_bay'][0], 1), growth_bay_len_m=round(xe - xd, 2), margin_after_t=round(52.5 - dry - rov_t, 2),
                               fits_length=(xe - xd) >= 3.0, well_plus_growth_len_m=round(xe - xb, 2), fits_if_well_and_growth_merged=(xe - xb) >= 3.2, note='kT decision 6 (option D, 2026-11-20) wanted the rover deployed/recovered from water; the Weave host dropped it for volume')
    return out

if __name__ == '__main__':
    OUT = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, options={})
    for D in (3.8, 3.7):
        o = build(D); OUT['options'][f'D{D}'] = o
        print(D, o['mass'], o['water'], json.dumps(o['layout']['zones_m3']), 'water', o['layout']['water_cells_m3'], 'spare', o['layout']['unallocated_m3'],
              'couch', o['layout']['couches_ok'], 'box', o['layout']['well_box'], 'mod', o['layout']['module_ok'])
        for k, v in o['hydrostatics']['cases'].items(): print('  ', k, v)
        print('  fallback', {k: o['fallback'][k] for k in ('chute_min_hover_alt_water_m', 'chute_CdA_m2')}, 'titan', o['titan'], 'rover', o['rover_option'])
    json.dump(OUT, open(os.path.join(H, 'tictac_v1.json'), 'w'), indent=1, default=float)
