"""Tic Tac build-out v1 (kT 2026-11-22: 'Tic tac. It is'; rulings after Sol's review of 5062961). NON-CANON lab design.
ALL bodies. ALL sponsors. 2026-2226.

kT rulings (Sol recommendations forwarded by kT): diameter 3.8 m; rover returns as a REMOVABLE MISSION KIT in a combined
cargo/rover bay behind a flush door (not in base dry mass); field-off water take-off limitation accepted (W3 EXCEPTION,
recorded, not passed); Titan: tank-level rule plus optional flotation kit, no permanent floats.

Geometry: capsule, length 12.8 m, hemispherical ends, diameter 3.8 m. Axis at y = z = 0, nose tip x = 0 (docking hatch on
the axis, F7). Inner surface = outer - 0.12 m. Continuous deck at z = DECK; water cells below it and in the lower domes.
Layout fore to aft: nose dome (hatch + 0.8 m passage, avionics, parachutes) | cabin (6 couches 3x2) | module bay (8 t core +
flywheel) | cargo/rover bay (floodable, flush side door in the lower flank, W4; 6 m3 rigid cargo or the rover kit) | aft dome
(torch, power unit, RCS). Whatever is not allocated stays empty (kT/Sol: do not fill it because it exists).
Hydrostatics: every section is a circle centred on the axis, so buoyancy acts through the axis: roll GM = -z_CG (exact),
less the free-surface corrections of slack cells and the flooded bay. Every assumption is labelled ASSUMPTION."""
import os, sys, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import closure_screen as CS
E = CS.E
TV = json.load(open(os.path.join(H, 'tictac_vs_shuttle.json')))
L, D, WALL, TANK, PAY = 12.8, 3.8, 0.12, 23.1, 1.1
R = D / 2; G = 9.81; RHO_SW = 1.025
DECK = -0.85                                  # ASSUMPTION: deck height; ~0.9 m bilge for water cells (low mass centre)
COUCH = dict(w=0.65, l=1.85, h=0.95, gap=0.05)
CABIN_LEN, MODULE_LEN = 3.95, 1.60            # ASSUMPTION: 2 couch rows + aisle; core cube + flywheel drum + service gap
CHUTE_FRAC = 0.035                            # ASSUMPTION: parachute system ~3.5% of the full-tank landing mass (Apollo ~4.5%)
POWER_UNIT_T = 1.0                            # ASSUMPTION: cooling / flywheel recharge power unit (no lift fans)
DOCK = dict(l=3.4, w=2.1)                     # ASSUMPTION: wet dock = rover 3.0 x 1.9 m + 0.2 m clearance, walled off inside the bay against the door side
SURVIVE = dict(water=10.0, land=6.0)          # ASSUMPTION (as the shuttle card): survivable vertical impact, m/s
ROVER = dict(t=0.973 + 0.258 + 0.6, w=1.9, l=3.0, h=1.7,   # b4s_mass.json standard_A2 chassis + light shell + outfit; 1.9 x 3.0 m (B4-S); height ASSUMPTION
             source='b4s_mass.json standard_A2: rover_chassis_crab + rover_light_cabin_shell + rover_outfit_life_support_power')

def r_out(x):
    if x < R: return math.sqrt(max(R * R - (R - x) ** 2, 0.0))
    if x > L - R: return math.sqrt(max(R * R - (x - (L - R)) ** 2, 0.0))
    return R
def r_in(x):
    ri = R - WALL
    if x < R: return math.sqrt(max(ri * ri - (R - x) ** 2, 0.0))
    if x > L - R: return math.sqrt(max(ri * ri - (x - (L - R)) ** 2, 0.0))
    return ri
def seg_below(r, z):
    if r <= 0 or z <= -r: return 0.0
    if z >= r: return math.pi * r * r
    return r * r * math.acos(-z / r) + z * math.sqrt(r * r - z * z)
def seg_cz_below(r, z):
    A = seg_below(r, z)
    if A <= 0 or z >= r: return 0.0
    return -(2.0 / 3.0) * (r * r - z * z) ** 1.5 / A
XS = np.linspace(0.0, L, 2561); DX = XS[1] - XS[0]
def zone(x0, x1, zlo=None, zhi=None, rf=r_in):
    V = Mx = Mz = 0.0
    for x in XS[(XS >= x0) & (XS < x1)]:
        r = rf(x); lo = -r if zlo is None else max(zlo, -r); hi = r if zhi is None else min(zhi, r)
        if hi <= lo: continue
        A = seg_below(r, hi) - seg_below(r, lo)
        if A <= 0: continue
        zc = (seg_below(r, hi) * seg_cz_below(r, hi) - seg_below(r, lo) * seg_cz_below(r, lo)) / A
        V += A * DX; Mx += A * DX * x; Mz += A * DX * zc
    return (V, Mx / V if V else 0.0, Mz / V if V else 0.0)
def box_in(x0, x1, y0, y1, z0, z1):
    for x in np.linspace(x0, x1, 7):
        r = r_in(x)
        for y in (y0, y1):
            for z in (z0, z1):
                if y * y + z * z > r * r: return False
    return True

def build():
    out = dict(D=D, R=R, L=L)
    # ------------------------------------------------ mass ledger (tictac_vs_shuttle rules)
    base = TV['tictac']; mi = dict(base['mass_items']); mi['fans_reactor'] = POWER_UNIT_T; mi['floats'] = 0.0
    host = sum(mi.values()); fly = 0.0
    for _ in range(40):
        lift = host + CS.MODULE['installed_t'] + fly + PAY + TANK; Es, P, fn = CS.cushion_energy(lift)
        chutes = CHUTE_FRAC * (host + CS.MODULE['installed_t'] + fn + PAY + TANK)
        if abs(fn - fly) < 1e-8: break
        fly = fn
    dry = host + CS.MODULE['installed_t'] + fly + chutes
    out['mass'] = dict(items={k: round(v, 3) for k, v in mi.items()}, host_t=round(host, 2), module_t=CS.MODULE['installed_t'], flywheel_t=round(fly, 3),
                       chutes_t=round(chutes, 2), dry_t=round(dry, 2), margin_t=round(52.5 - dry, 2), rover_kit_t=round(ROVER['t'], 2),
                       margin_with_rover_t=round(52.5 - dry - ROVER['t'], 2), cushion_GJ=round(Es / 1e9, 2), cushion_MW=round(P / 1e6),
                       note='rover is a removable mission kit: not in base dry mass')
    dv_h = CS.climb_dv(2e3)[0]; legs = [(200, .1, 1), (round(3000 - dv_h), 1.4, 9.81), (6400, .8, 9.81), (400, .1, 1)]
    w = E.water_chk(dry, PAY, legs); wr = E.water_chk(dry + ROVER['t'], PAY, legs)
    out['water'] = dict(earth_cushion_t=w[0], earth_cushion_with_rover_t=wr[0], tank_t=TANK, ok=w[0] <= TANK and not w[1] and wr[0] <= TANK,
                        earth_torch_only_t=E.water_chk(dry, PAY, E.S2.MISSIONS['R1 Earth: sea to orbit, 6 pax + 2 t']['legs'])[0])
    # ------------------------------------------------ layout
    xa = R; xb = xa + CABIN_LEN; xc = xb + MODULE_LEN; xe = L - R
    Z = dict(nose_dome=zone(0, xa), aft_dome=zone(xe, L), cabin=zone(xa, xb, DECK), module_bay=zone(xb, xc, DECK), bay=zone(xc, xe, DECK), bilge=zone(xa, xe, None, DECK))
    inner_total = zone(0, L)[0]
    need = dict(cabin=21.0, water=1.05 * TANK, cargo=6.0, aft=7.0 + 0.04 * 6.0, avionics=3.0, chutes=1.0, passage=math.pi * 0.16 * R,
                module=2.0, flywheel=fly / 2.0, install=0.3)
    nose_items = need['avionics'] + need['chutes'] + need['passage']; aft_items = need['aft']; mod_items = need['module'] + need['flywheel'] + need['install']
    water_vol = Z['bilge'][0] + (Z['nose_dome'][0] - nose_items) + (Z['aft_dome'][0] - aft_items)
    rows = [(xb - COUCH['gap'] - COUCH['l'], xb - COUCH['gap']), (xb - 2 * (COUCH['gap'] + COUCH['l']), xb - 2 * COUCH['gap'] - COUCH['l'])]
    ys = [(-1.5 * COUCH['w'] - COUCH['gap'], -0.5 * COUCH['w'] - COUCH['gap']), (-0.5 * COUCH['w'], 0.5 * COUCH['w']), (0.5 * COUCH['w'] + COUCH['gap'], 1.5 * COUCH['w'] + COUCH['gap'])]
    couches_ok = all(box_in(x0, x1, y0, y1, DECK + 0.02, DECK + 0.02 + COUCH['h']) for x0, x1 in rows for y0, y1 in ys) and rows[1][0] >= xa
    core = need['module'] ** (1 / 3); fdh = need['flywheel'] / (math.pi * 0.25)
    module_ok = box_in(xb + 0.05, xb + 0.05 + core, -core - 0.05, -0.05, DECK + 0.02, DECK + 0.02 + core) and box_in(xb + 0.05, xb + 1.05, 0.05, 1.05, DECK + 0.02, DECK + 0.02 + fdh)
    rover_x = (xc + 0.2, xc + 0.2 + ROVER['l'])
    rover_ok = rover_x[1] <= xe and box_in(rover_x[0], rover_x[1], -ROVER['w'] / 2, ROVER['w'] / 2, DECK + 0.02, DECK + 0.02 + ROVER['h'])
    cargo_box = None
    for hw in np.arange(1.6, 0.6, -0.02):
        ht = 1.68; ln = need['cargo'] / (2 * hw * ht)
        if ln <= xe - xc - 0.1 and box_in(xc + 0.05, xc + 0.05 + ln, -hw, hw, DECK + 0.02, DECK + 0.02 + ht):
            cargo_box = dict(volume_m3=round(2 * hw * ht * ln, 2), length=round(ln, 2), width=round(2 * hw, 2), height=ht); break
    unalloc = inner_total - (need['cabin'] + need['cargo'] + mod_items + nose_items + aft_items + need['water'])
    out['layout'] = dict(x=dict(nose_dome=(0, xa), cabin=(xa, xb), module_bay=(xb, xc), bay=(xc, xe), aft_dome=(xe, L)), deck_z=DECK,
                         zones_m3={k: round(v[0], 2) for k, v in Z.items()}, inner_total_m3=round(inner_total, 1), need_m3={k: round(v, 2) for k, v in need.items()},
                         water_cells_m3=round(water_vol, 2), water_ok=water_vol >= need['water'], couches_ok=couches_ok, rows=rows, ys=ys,
                         headroom_m=round((R - WALL) - DECK, 2), module_ok=module_ok, core_edge_m=round(core, 3), flywheel_drum=dict(d=1.0, h=round(fdh, 3)),
                         bay_len_m=round(xe - xc, 2), rover_x=rover_x, rover_ok=rover_ok, cargo_box=cargo_box,
                         unallocated_m3=round(unalloc, 1), unallocated_note='left empty: comfort and growth, not filled because it exists',
                         passage_at_nose='0.8 m passage from the nose tip on the axis (fixes the B4-S-family nose-passage gap)')
    # ------------------------------------------------ mass properties
    cab = Z['cabin']; bil = Z['bilge']
    items = [('shell: hull, cabin wall, gear, mounts', mi['hull_structure'] + mi['cabin_wall'] + mi['gear_door'] + mi['crash_mounts'], L / 2, 0.0),
             ('entry TPS (windward = belly)', mi['entry_tps'], L / 2, -0.85 * R),
             ('torch, belly RCS, power distribution', mi['torch'] + mi['belly_rcs'] + mi['power_dist'], L - 0.75, 0.0),
             ('power unit', mi['fans_reactor'], L - 1.3, -0.6),
             ('cabin outfit, custody, payload', mi['cabin'] + mi['custody'] + PAY, cab[1], DECK + 0.6),
             ('avionics', mi['avionics'], 0.9, 0.3), ('parachutes (upper nose)', chutes, 0.9, 0.9),
             ('relational module', CS.MODULE['installed_t'], xb + 0.05 + core / 2, DECK + 0.02 + core / 2),
             ('flywheel', fly, xb + 0.55, DECK + 0.02 + fdh / 2), ('water tank cells (structure)', mi['water_tank'], bil[1], bil[2])]
    rover_item = ('rover kit', ROVER['t'], 0.5 * sum(rover_x), DECK + 0.02 + 0.45 * ROVER['h'])
    cells = [(bil[0], bil[1], bil[2]), (Z['nose_dome'][0] - nose_items, *zone(0, xa, None, 0.0)[1:]), (Z['aft_dome'][0] - aft_items, *zone(xe, L, None, 0.0)[1:])]
    def props(water_t, rover):
        its = list(items) + ([rover_item] if rover else []); left = water_t
        for v, x, z in cells:
            cap = v / 1.05; take = min(left, cap); its.append(('water', take, x, z if take >= cap - 1e-9 else z - 0.15)); left -= take
        m = sum(i[1] for i in its); return m, sum(i[1] * i[2] for i in its) / m, sum(i[1] * i[3] for i in its) / m
    out['mass_centre_full_tank'] = dict(zip(('mass_t', 'x', 'z'), [round(v, 3) for v in props(TANK, False)]))
    # ------------------------------------------------ hydrostatics (outer hull)
    def disp(zw): return sum(seg_below(r_out(x), zw) for x in XS) * DX
    def waterline(m_t):
        lo, hi = -R, R
        for _ in range(60):
            mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if disp(mid) * RHO_SW < m_t else (lo, mid)
        return 0.5 * (lo + hi)
    Vh = disp(R + 1)
    bw = 2 * math.sqrt((R - WALL) ** 2 - DECK ** 2); bl = xe - xa
    I_bilge = 8 * ((bl / 4) * (bw / 2) ** 3 / 12)    # ASSUMPTION: baffled cells, 4 longitudinal x 2 transverse
    def case(water_t, flood, rover, sea_ballast_t=0.0, dock=True):
        fill = min(TANK * 1.0, water_t + sea_ballast_t)              # sea ballast fills empty cells (density 1.025 vs 1.0: small)
        m, xg, zg = props(fill, rover); zw = waterline(m); slack = 0 < fill < TANK - 0.5
        fs = (I_bilge * (1.0 if slack else 0.25) / RHO_SW) / (m / RHO_SW)
        fv = 0.0
        if flood and not dock:                                       # whole bay open to the sea
            m0 = m
            for _ in range(4):
                fv = max(0.0, zone(xc, xe, DECK, zw)[0] - (ROVER['w'] * ROVER['l'] * max(0.0, min(zw, DECK + ROVER['h']) - DECK) if rover else 0.0))
                m = m0 + fv * RHO_SW; zw = waterline(m)
            zg = (m0 * zg + fv * RHO_SW * zone(xc, xe, DECK, zw)[2]) / m if fv > 0 else zg
            fs += ((xe - xc) * (2 * math.sqrt(max((R - WALL) ** 2 - zw ** 2, 0))) ** 3 / 12) / (m / RHO_SW) if fv > 0 else 0.0
        elif flood:                                                  # wet dock: watertight-walled slot beside the door, rover-sized
            m0 = m
            for _ in range(4):
                depth = max(0.0, zw - DECK)
                fv = max(0.0, DOCK['l'] * DOCK['w'] * depth - (ROVER['w'] * ROVER['l'] * min(depth, ROVER['h']) if rover else 0.0))
                m = m0 + fv * RHO_SW; zw = waterline(m)
            zg = (m0 * zg + fv * RHO_SW * 0.5 * (DECK + zw)) / m if fv > 0 else zg
            fs += (DOCK['l'] * DOCK['w'] ** 3 / 12) / (m / RHO_SW) if fv > 0 else 0.0   # conservative: full dock surface even with the rover in it
        gm = -zg - fs
        return dict(mass_t=round(m, 2), cg_x=round(xg, 2), cg_z=round(zg, 3), waterline_z=round(zw, 3), draft_m=round(zw + R, 2), GM_roll_m=round(gm, 3),
                    free_surface_m=round(fs, 3), flooded_m3=round(fv, 2), deck_below_waterline_m=round(zw - DECK, 2), reserve_buoyancy=round(Vh * RHO_SW / m - 1, 2))
    cases = {}
    for name, wt, fl, rv in (('full tank', TANK, False, False), ('light (2 t water)', 2.0, False, False), ('light, dock flooded', 2.0, True, False),
                             ('full tank, rover aboard, dock flooded', TANK, True, True), ('light, rover aboard, dock flooded', 2.0, True, True)):
        cases[name] = case(wt, fl, rv)
    def ballast_needed(rover, dock=True):
        for b in np.arange(0.0, TANK - 2.0 + 0.01, 0.5):
            if case(2.0, True, rover, b, dock)['GM_roll_m'] >= 0.3: return float(b)
        return None
    cases_open = {n: case(wt, True, rv, 0.0, False) for n, wt, rv in (('light, whole bay flooded', 2.0, False), ('light, rover aboard, whole bay flooded', 2.0, True),
                                                                    ('full tank, rover aboard, whole bay flooded', TANK, True))}
    bn, bnr = ballast_needed(False), ballast_needed(True)
    if bn is not None: cases['light, dock flooded, sea ballast'] = dict(case(2.0, True, False, bn), sea_ballast_t=bn)
    if bnr is not None: cases['light, rover aboard, dock flooded, sea ballast'] = dict(case(2.0, True, True, bnr), sea_ballast_t=bnr)
    out['hydrostatics'] = dict(hull_m3=round(Vh, 1), cases=cases, whole_bay_flooded_rejected=cases_open, dock=DOCK, sea_ballast_rule_t=dict(no_rover=bn, rover_aboard=bnr, target_GM_m=0.3),
                               status='OPEN RULE, not a pass: flood only the rover-sized wet dock (flooding the whole bay is unstable light); afloat light, take on the stated sea ballast before opening the dock door',
                               note='roll GM exact for circular sections; pitch stability large (length 12.8 m)')
    # ------------------------------------------------ W3 (torch clear of the water): EXCEPTION
    zw_full = cases['full tank']['waterline_z']
    out['W3'] = dict(status='EXCEPTION (kT accepted 2026-11-22), not passed', torch_exit_z=0.0, waterline_full_z=zw_full, required_z=round(zw_full + 1.0, 2),
                     reason='axis torch is horizontal and at the waterline afloat; field-off take-off from water not possible',
                     accepted_state='field off afloat: stable recovery state; waits for field restart or Wayfarer recovery; no extra propulsion added')
    # ------------------------------------------------ field-off fallback (hover, from rest)
    m_full = props(TANK, False)[0]
    def chute_fall(h0, m_t, CdA, t_deploy=1.0, t_inflate=2.5, rho=1.225, dt=0.002):
        z, v, t = h0, 0.0, 0.0
        while z > 0:
            f = 0.0 if t < t_deploy else min(1.0, (t - t_deploy) / t_inflate)
            a = G - 0.5 * rho * v * v * CdA * f / (m_t * 1e3); v += a * dt; z -= v * dt; t += dt
        return v
    CdA = 2 * m_full * 1e3 * G / (1.225 * 8.0 ** 2)
    def hmin(t_inf):
        return float(next(h for h in np.arange(2, 600, 1.0) if all(chute_fall(hh, m_full, CdA, t_inflate=t_inf) <= SURVIVE['water'] for hh in np.arange(h, h + 60, 5))))
    sens = {f'inflate_{t:g}s': hmin(t) for t in (2.5, 4.0, 6.0)}
    out['fallback'] = dict(drop_survivable_water_m=round(SURVIVE['water'] ** 2 / (2 * G), 1), drop_survivable_land_m=round(SURVIVE['land'] ** 2 / (2 * G), 1),
                           chute_CdA_m2=round(CdA), chute_min_hover_alt_water_m=sens['inflate_2.5s'], chute_min_alt_sensitivity_m=sens,
                           status='SCREENING ASSUMPTION, not a demonstrated capability: ~17,400 m2 effective drag area (a cluster of ~11 canopies of ~50 m) with 2.5 s inflation from a hover',
                           chute_assumptions='mortar deploy 1.0 s, linear inflation, cluster CdA for 8 m/s at full-tank mass; survivable 10 m/s water / 6 m/s land',
                           torch='axis torch is horizontal: arresting a fall needs a 90 deg pitch-up first (not credited)',
                           shuttle_for_comparison=dict(no_recovery_band_m=[5.1, 46.8], above='torch (1-3 s start)'))
    # ------------------------------------------------ bay exit (F8, F10)
    out['bay'] = dict(F8_radius_m=R, F8_ok=R <= 2.15, F10_width_m=D, F10_limit=3.8, F10_ok=True, F10_extra_margin_m=0.0, roll='any (round)',
                      F9_length_m=L, collar='not needed', rule='nothing may protrude beyond the 3.8 m diameter (flush doors, hatches, sensors)')
    # ------------------------------------------------ Titan
    tw = E.water_chk(dry, PAY, E.S2.MISSIONS['R3 Titan']['legs'])[0]; m_t = dry + PAY + tw
    def max_water(rho, reserve): return round(Vh * rho / 1e3 / (1 + reserve) - dry - PAY, 1)
    out['titan'] = dict(ascent_water_t=tw, landed_t=round(m_t, 1), rule='tank-level rule; optional flotation kit; no permanent floats; landings restricted until equipped',
                        liquids={f'{n} ({rho} kg/m3)': dict(rho=rho, reserve=round(Vh * rho / 1e3 / m_t - 1, 2), full_tank_reserve=round(Vh * rho / 1e3 / (dry + PAY + TANK) - 1, 2),
                                 max_water_for_50pct_t=max_water(rho, 0.5), max_water_to_float_t=max_water(rho, 0.0),
                                 kit_m3_for_50pct=round(max(0.0, 1.5 * m_t * 1e3 / rho - Vh), 1)) for n, rho in (('Ligeia-like', 551), ('near-pure methane', 447))})
    return out

if __name__ == '__main__':
    o = build(); o.update(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__)
    json.dump(o, open(os.path.join(H, 'tictac_v1.json'), 'w'), indent=1, default=float)
    print(json.dumps({k: o[k] for k in ('mass', 'water', 'W3', 'titan', 'mass_centre_full_tank')}, indent=1, default=float))
    print(json.dumps({k: v for k, v in o['layout'].items() if k not in ('rows', 'ys')}, default=float))
    for k, v in o['hydrostatics']['cases'].items(): print(k, v)
    print(o['hydrostatics']['sea_ballast_rule_t'], o['fallback']['chute_min_alt_sensitivity_m'])
