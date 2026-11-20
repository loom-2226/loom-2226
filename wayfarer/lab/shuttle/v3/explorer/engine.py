"""LOOM shuttle v3 design explorer: generate shuttle + kit concepts inside Wayfarer's bay
and score them against performance and capability. ALL bodies. ALL sponsors. 2026-2226.

NON-CANON engineering screen. Every model is the same ROM used in the v3 steps:
  geometry  : B-family angular body (build_v2b key stations) with growth/morph parameters
  aero      : aero_test.newtonian (hypersonic), aero_test.entry (3-D Earth entry), aero_test.subsonic
  propulsion: step2_propulsion.water (fixed jet power, variable exhaust speed)
  fans      : lift_fans momentum theory; slow_flight blown-flap rule
  mass      : B4-S part masses (b4s_mass.json, mid) scaled by geometry, 8 g rule, fans, floats
Hard gates (a design that fails any is INFEASIBLE, never 'nearly'):
  bay fit r <= 2.15 m (F-series, G8 margins included) | length 12.8 m
  dry docked mass <= 52.5 t (kT reserve share) | Earth sortie water <= tank
  interior volume closes | W2: hull + floats >= 1.5 x displaced at heaviest float mass, hull >= displaced
Run: python3 engine.py --n 1600 --seed 2226   (writes explorer_results.json)"""
import sys, os, json, math, argparse, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); V3 = os.path.join(HERE, '..')
sys.path.insert(0, V3); sys.path.insert(0, os.path.join(V3, '..', 'v2_lifting_body'))
import build_v2b as B, aero_test as AT, step2_propulsion as S2

L, R_ENV, CEIL_T, RHO_SW = 12.8, 2.15, 52.5, 1.025
B4S = json.load(open(os.path.join(V3, '..', 'v2_lifting_body', 'b4s_mass.json')))['standard_A2']['parts_mid_t']
BASE_KEYS = np.array([  # build_v2b.section key stations: x, ridge_z, sh_y, sh_z, ch_y, ch_z, bc_y, bc_z
    (0.00, -0.42, 0.00, -0.42, 0.00, -0.50, 0.00, -0.58), (0.60, -0.20, 0.16, -0.24, 0.40, -0.40, 0.24, -0.66),
    (2.40, 0.42, 0.55, 0.30, 1.30, -0.16, 0.95, -0.86), (4.60, 1.02, 1.02, 0.86, 1.92, 0.08, 1.58, -0.95),
    (6.30, 1.50, 1.52, 1.40, 2.13, 0.20, 1.85, -0.95), (11.70, 1.50, 1.52, 1.40, 2.13, 0.20, 1.85, -0.95),
    (12.80, 1.30, 1.42, 1.22, 2.00, 0.18, 1.72, -0.86)])

# ------------------------------------------------------------------ parameters
SPACE = {  # name: (low, high) continuous, or list = choices
 'ridge': (-0.2, 0.65), 'shoulder_z': (-0.1, 0.4), 'shoulder_y': (-0.35, 0.1), 'keel': (0.0, 0.45),
 'chine_z': (-0.35, 0.35), 'belly_w': (0.80, 1.04), 'nose': (0.75, 1.35), 'base': (0.75, 1.0),
 'wing': ['none', 'fold', 'telescoping'], 'span': (8.0, 16.0), 'chord': (1.0, 2.4),
 'fan_m2': [0, 6, 8, 10, 12], 'floats_m3': [0, 10, 20, 30, 40], 'water_t': [18, 20, 23.1, 26, 30],
 'seats': [4, 6, 8], 'rover': [True, False], 'fan_venus': [True, False],
}
def sample(rng):
    p = {}
    for k, v in SPACE.items():
        p[k] = rng.choice(v) if isinstance(v, list) else round(rng.uniform(*v), 3)
    if p['wing'] == 'fold': p['span'] = min(p['span'], 9.0)
    if p['wing'] == 'none': p['span'], p['chord'] = 4.26, 0.0
    return p
B5 = dict(ridge=0.45, shoulder_z=0.22, shoulder_y=-0.10, keel=0.30, chine_z=0.0, belly_w=1.0, nose=1.0, base=1.0,
          wing='telescoping', span=14.0, chord=1.8, fan_m2=8, floats_m3=20, water_t=23.1, seats=6, rover=True, fan_venus=True)

# ------------------------------------------------------------------ geometry
def keys(p):
    K = BASE_KEYS.copy()
    for i in (1, 2, 3):                       # nose stations stretch or squash, capped before the parallel body
        K[i, 0] = min(K[i, 0] * p['nose'], 6.0 - 0.3 * (3 - i))
    s = np.clip(K[:, 4] / 2.13, 0, 1)         # local size for scaling growth
    K[:, 1] += p['ridge'] * s; K[:, 3] += p['shoulder_z'] * s; K[:, 2] += p['shoulder_y'] * s
    K[:, 5] += p['chine_z'] * s; K[:, 6] = np.minimum(K[:, 6] * p['belly_w'], K[:, 4] - 0.05)
    K[-1, 1:] *= p['base']; K[-1, 0] = L
    return K
def section(K, x, keel):
    r = np.array([np.interp(x, K[:, 0], K[:, i]) for i in range(1, 8)]); rz, sy, sz, cy, cz, by, bz = r
    s = min(1.0, cy / 2.13); kz = bz - keel * s
    return np.array([(0, rz), (sy, sz), (cy, cz), (by, bz), (0, kz), (-by, bz), (-cy, cz), (-sy, sz)])
STATIONS = [0.6, 2.4, 4.6, 5.45, 6.3, 9.0, 11.7, 12.8]
def loft(p):
    K = keys(p); st = sorted(set([0.6] + list(K[1:4, 0]) + [6.3, 9.0, 11.7, 12.8]))
    V, F, base_ids = [], [], []; rings = []
    for x in st: rings.append(len(V)); V += [(x, y, z) for y, z in section(K, x, p['keel'])]
    nose = len(V); V.append((0.0, 0.0, K[0, 5])); tail = len(V); V.append((L, 0.0, K[-1, 5]))
    for k in range(len(st) - 1):
        a0, b0 = rings[k], rings[k + 1]
        for i in range(8):
            j = (i + 1) % 8; F += [(a0 + i, a0 + j, b0 + i), (a0 + j, b0 + j, b0 + i)]
    for i in range(8):
        j = (i + 1) % 8; F.append((nose, rings[0] + j, rings[0] + i)); base_ids.append(len(F)); F.append((rings[-1] + i, rings[-1] + j, tail))
    V = np.array(V, float); F = np.array(F)[:, ::-1]
    return V, F, K, base_ids, st
def poly_area(S): return 0.5 * abs(float(np.dot(S[:, 0], np.roll(S[:, 1], -1)) - np.dot(S[:, 1], np.roll(S[:, 0], -1))))
def inset(S, d):
    n = len(S); out = []; c0 = S.mean(0)
    for i in range(n):
        q, a, b = S[i], S[i - 1], S[(i + 1) % n]
        e1 = (q - a) / (np.linalg.norm(q - a) + 1e-9); e2 = (b - q) / (np.linalg.norm(b - q) + 1e-9)
        n1 = np.array([e1[1], -e1[0]]); n2 = np.array([e2[1], -e2[0]])
        if n1 @ (q - c0) < 0: n1, n2 = -n1, -n2
        bis = n1 + n2; bis /= (np.linalg.norm(bis) + 1e-9); c = max(bis @ n1, .35); out.append(q - d / c * bis)
    return np.array(out)

# ------------------------------------------------------------------ thresholds (evidence class in brackets)
THRESH = {
 'land_light_ms': (40.0, 'kT landing rule 2026-11-21: light landings in 2 m waves at 30-36, US-2 class [threshold]'),
 'land_heavy_ms': (50.0, 'kT landing rule 2026-11-21: heavy ~50 m/s in ~1 m waves [threshold]'),
 'sprint_t': (5.0, 'sprint water kit ~5 t (kit list 2026-11-21) [assumption]'),
 'venus_kit_water_t': (13.0, 'Venus kit carries up to ~13 t extra water (step 2 estimate 8-13 t) [assumption]'),
}
CLS = {'geometry': 'direct geometry / accounting', 'model': 'physics-model prediction', 'coef': 'empirical or assumed coefficient', 'threshold': 'threshold classification'}
def _src_hash():
    import hashlib
    h = hashlib.sha1()
    for f in (os.path.join(HERE, 'engine.py'), os.path.join(V3, 'step2_propulsion.py'),
              os.path.join(V3, '..', 'v2_lifting_body', 'aero_test.py'), os.path.join(V3, '..', 'v2_lifting_body', 'build_v2b.py'),
              os.path.join(V3, '..', 'v2_lifting_body', 'variants.py'), os.path.join(V3, '..', 'v2_lifting_body', 'b4s_mass.json'),
              os.path.join(V3, '..', 'shuttle_inputs.json')):
        h.update(open(f, 'rb').read())
    return h.hexdigest()[:12]
MODEL_VERSION = _src_hash()
def input_hash(p):
    import hashlib
    return hashlib.sha1(json.dumps(p, sort_keys=True).encode()).hexdigest()[:12]

# ------------------------------------------------------------------ models
def fan_model(p, m_land):
    A = p['fan_m2']
    if A == 0: return dict(MWe=0.0, mass_t=0.0, static_kN=0.0)
    def hover(m, g, rho): T = m * 1e3 * g * 1.15; return T ** 1.5 / math.sqrt(2 * rho * A) / 0.78 / 0.93 / 1e6
    def static(MW): return (MW * 1e6 * 0.78 * 0.93 * math.sqrt(2 * 1.225 * A)) ** (2 / 3) / 1e3
    W = m_land * 1e3 * 9.81; take = (0.25 * W) ** 1.5 / math.sqrt(2 * 1.225 * A) / 0.78 / 0.93 / 1e6
    cruise = W / 5.0 * 100 / 0.75 / 0.93 / 1e6
    needs = [take, cruise, hover(m_land, 1.35, 5.4)] + ([hover(m_land + 15.2, 8.87, 65.0)] if p.get('fan_venus', True) else [])
    MW = max(needs)
    mass = MW * 3.095 / 75 + MW / 20 + MW / 50 + A * 0.06
    return dict(MWe=round(MW, 1), mass_t=round(mass, 2), static_kN=round(static(MW)))

def evaluate(p, full_entry=True):
    V, F, K, base_ids, st = loft(p); T = V[F]
    r = dict(params=p, feasible=True, fails=[])
    # bay fit
    pts = np.vstack([section(K, x, p['keel']) for x in np.linspace(0, L, 41)])
    zs = np.linspace(pts[:, 1].min(), pts[:, 1].max(), 121); rr = [np.hypot(pts[:, 0], pts[:, 1] - z).max() for z in zs]
    r['fit_r_m'] = round(min(rr), 3)
    if min(rr) > R_ENV: r['fails'].append('bay fit')
    # volumes
    xs = np.linspace(0.05, L, 160)
    Vh = float(np.trapezoid([poly_area(section(K, x, p['keel'])) for x in xs], xs))
    Vin = float(np.trapezoid([poly_area(inset(section(K, x, p['keel']), 0.12)) for x in xs], xs))
    plan = float(np.trapezoid([2 * section(K, x, p['keel'])[2][0] for x in xs], xs))
    n, A = AT.geom(T); Swet = float(A.sum()); Abase = float(A[base_ids].sum())
    r.update(hull_m3=round(Vh, 1), inner_m3=round(Vin, 1), planform_m2=round(plan, 1), swet_m2=round(Swet, 1))
    # mass
    sw, ch = p['span'], p['chord']; Sw = max(0.0, (sw - 4.26) * ch) if p['wing'] != 'none' else 0.0
    g8 = 0.4 + 0.6 * math.sqrt(2.0)
    m = dict(hull_structure=B4S['hull_thermal_structure_t'] * Swet / SWET0 * g8,
             entry_tps=B4S['base_entry_tps_core_t'] * plan / PLAN0,
             wings=(0.123 * Sw * (1.3 if p['wing'] == 'telescoping' else 1.0) * math.sqrt(2.0)),
             cabin=B4S['cabin_wall_heat_tolerant_t'] * (p['seats'] / 6) ** (2 / 3) + B4S['cabin_hatches_seals_t'] + B4S['crew_habitat_thermal_package_6_seats_t'] * p['seats'] / 6,
             water_tank=B4S['water_tank_insulated_t'] * p['water_t'] / 23.1,
             rover=(B4S['rover_chassis_crab_t'] + B4S['rover_light_cabin_shell_t'] + B4S['rover_outfit_life_support_power_t']) if p['rover'] else 0.0,
             torch=B4S['torch_low_high_engine_t'], belly_rcs=B4S['small_belly_thrusters_t'], power_dist=B4S['reactor_power_distribution_t'],
             custody=B4S['custody_capsule_dry_t'], avionics=B4S['avionics_controls_yaw_t'], gear_door=B4S['landing_gear_door_ramp_t'],
             crash_mounts=0.3, floats=0.03 * p['floats_m3'])
    pay = 0.1 * p['seats'] + 2.0
    dry0 = sum(m.values()); fans = fan_model(p, dry0 + 6 + pay + 18)
    m['fans_reactor'] = fans['mass_t']; dry = sum(m.values())
    r.update(dry_t=round(dry, 2), mass_t={k: round(v, 2) for k, v in m.items()}, fans=fans, payload_t=round(pay, 2))
    if dry > CEIL_T: r['fails'].append('mass ceiling')
    # interior closure
    need = 4.5 * p['seats'] + 1.05 * p['water_t'] + (11.5 if p['rover'] else 6.0) + 5.0 + 7.0 + 3.0 + 0.04 * fans['MWe']
    r['interior_need_m3'] = round(need, 1); r['interior_margin_m3'] = round(Vin - need, 1)
    if Vin < need: r['fails'].append('interior')
    # propellant
    earth = S2.MISSIONS['R1 Earth: sea to orbit, 6 pax + 2 t']['legs']
    w_e = S2.water(dry, pay, earth)[0]; r['earth_water_t'] = w_e; r['earth_margin_t'] = round(p['water_t'] - w_e, 1)
    if w_e > p['water_t']: r['fails'].append('Earth water')
    hard = [(200, .1, 1), (300, 1.3, 9.81), (3000, 2.5, 9.81), (6400, .8, 9.81), (400, .1, 1)]
    r['hot_egress_water_t'] = S2.water(dry, pay, hard)[0]
    r['venus_water_t'] = S2.water(dry + 15.2, 0.3, S2.MISSIONS['R2 Venus: kit, 3 crew, ascent 10.5 km/s from rotor handover']['legs'])[0]
    vac_dry = dry - m['wings'] - m['floats'] - m['fans_reactor'] - 0.5 * m['entry_tps'] + 1.5   # vacuum kit: legs + H2/O2
    r['moon_water_t'] = S2.water(vac_dry, pay, S2.MISSIONS['R5 Moon']['legs'])[0]
    r['mars_water_t'] = S2.water(dry, pay, S2.MISSIONS['R4 Mars (0.8 km/s powered descent)']['legs'])[0]
    # buoyancy (W2 amended)
    m_float = dry + pay + p['water_t']; disp = m_float / RHO_SW
    r['buoyancy_total_m3'] = round(Vh + p['floats_m3'], 1); r['buoyancy_need_m3'] = round(1.5 * disp, 1)
    if Vh + p['floats_m3'] < 1.5 * disp or Vh < disp: r['fails'].append('buoyancy')
    # aero
    hyp = max(float(np.divide(*AT.newtonian(T, plan, Swet, a, 1.2))) for a in range(10, 56, 5))
    v = dict(T=T, S_body=plan, S_wing=Sw, span=max(sw, 4.26), Swet=Swet, Abase=max(Abase, 1.0), sharp=True, rn=0.25)
    r['hyper_LD'] = round(hyp, 2)
    m_entry = dry + pay + 0.8 * p['water_t']
    if full_entry:
        e = AT.entry(dict(v, S_wing=0.0, span=4.26), 'Earth', m_entry * 1e3, 40)
        r['crossrange_km'] = round(e['crossrange_km']); r['peak_heat_Wcm2'] = round(e['peak_q_Wcm2']); r['entry_g'] = round(e['peak_g'], 2)
    al = np.linspace(0, 32, 65); pol = [AT.subsonic(v, a) for a in al]; CL = np.array([q[0] for q in pol]); CD = np.array([q[1] for q in pol]); S = pol[0][2]
    r['glide_LD'] = round(float(max(CL / np.maximum(CD, 1e-6))), 2)
    cl20 = float(CL[al <= 20].max()); clmax = min(4.0, cl20 + 2.6 * fans['MWe'] / 28.0) if p['fan_m2'] else cl20 + (1.2 * Sw / S if Sw else 0)
    m_heavy = dry + pay + w_e
    def vtd(mm): return math.sqrt(2 * max(mm * 1e3 * 9.81 - fans['static_kN'] * 1e3, 1.0) / (1.225 * S * clmax))
    r['touchdown_heavy_ms'] = round(vtd(m_heavy), 1); r['touchdown_light_ms'] = round(vtd(dry + pay + 2.0), 1)
    W = m_heavy * 1e3 * 9.81; Vc = math.sqrt(8 * W / (0.5 * 1.225 * S * float(CL.max())))
    Vt = min(Vc, 272.0); nt = min(8.0, 0.5 * 1.225 * Vt ** 2 * S * float(CL.max()) / W)   # corner speed, capped at the ROM's Mach 0.8
    r['max_turn_dps'] = round(math.degrees(9.81 * math.sqrt(max(nt * nt - 1, 0)) / Vt), 1); r['corner_ms'] = round(Vt, 1)
    # capabilities (kits)
    tank = p['water_t']
    r['capabilities'] = {
        'Earth sea-to-orbit (core)': w_e <= tank,
        'Hot egress to orbit (+sprint kit)': r['hot_egress_water_t'] <= tank + THRESH['sprint_t'][0],
        'Light water landing, 2 m waves': r['touchdown_light_ms'] <= THRESH['land_light_ms'][0],
        'Heavy water landing, ~1 m waves': r['touchdown_heavy_ms'] <= THRESH['land_heavy_ms'][0],
        'Titan hover (fans)': p['fan_m2'] > 0,
        'Venus hover + kit water': p['fan_m2'] > 0 and p.get('fan_venus', True) and r['venus_water_t'] <= tank + THRESH['venus_kit_water_t'][0],
        'Moon (vacuum kit)': r['moon_water_t'] <= tank, 'Mars': r['mars_water_t'] <= tank}
    r['capability_count'] = int(sum(r['capabilities'].values()))
    # Wayfarer cost: docked dry + full water
    r['docked_t'] = round(dry + tank, 1)
    G = lambda name, val, lim, sense, unit, cls, src: dict(name=name, value=round(float(val), 2), limit=round(float(lim), 2), sense=sense, unit=unit,
        headroom=round(float(lim - val if sense == '<=' else val - lim), 2), rel=round(float((lim - val if sense == '<=' else val - lim) / max(abs(lim), 1e-9)), 3), cls=cls, source=src)
    r['gates'] = [
        G('Bay fit radius (stowed hull only)', r['fit_r_m'], R_ENV, '<=', 'm', 'geometry', 'F-series envelope r 2.15 m; folded wings/fans/floats, 3.8 m slot, roll and G8 exit path NOT checked'),
        G('Dry mass', dry, CEIL_T, '<=', 't', 'coef', 'kT reserve share ceiling 52.5 t; masses scaled from B4-S parts'),
        G('Earth trip water: required vs carried', w_e, tank, '<=', 't', 'model', 'step2 fixed-power torch, R1 legs'),
        G('Interior: usable vs allocated', Vin, need, '>=', 'm3', 'coef', 'allocations 4.5 m3/couch, rover 11.5 (else 6), door 5, aft 7, avionics 3'),
        G('Buoyancy: hull + floats vs 1.5 x displaced', Vh + p['floats_m3'], 1.5 * disp, '>=', 'm3', 'geometry', 'W2 amended 2026-11-21; stability (W6) NOT checked'),
        G('Buoyancy: hull alone vs displaced', Vh, disp, '>=', 'm3', 'geometry', 'W2 amended 2026-11-21')]
    r['capability_margins'] = [
        G('Light water landing (2 m waves)', r['touchdown_light_ms'], THRESH['land_light_ms'][0], '<=', 'm/s', 'coef', THRESH['land_light_ms'][1] + '; blown-flap CL rule is an assumed line through one QSRA-class point'),
        G('Heavy water landing (~1 m waves)', r['touchdown_heavy_ms'], THRESH['land_heavy_ms'][0], '<=', 'm/s', 'coef', THRESH['land_heavy_ms'][1]),
        G('Hot egress water vs tank + sprint', r['hot_egress_water_t'], tank + THRESH['sprint_t'][0], '<=', 't', 'model', THRESH['sprint_t'][1]),
        G('Venus water vs tank + kit water', r['venus_water_t'], tank + THRESH['venus_kit_water_t'][0], '<=', 't', 'model', THRESH['venus_kit_water_t'][1]),
        G('Moon water (vacuum kit) vs tank', r['moon_water_t'], tank, '<=', 't', 'coef', 'vacuum-kit dry = core - wings - floats - fans - half TPS + 1.5 t (assumed)'),
        G('Mars water vs tank', r['mars_water_t'], tank, '<=', 't', 'model', 'step2 R4 legs')]
    lim = min(r['gates'], key=lambda g: g['rel']); r['limiting'] = lim['name']
    r['model_version'] = MODEL_VERSION; r['input_hash'] = input_hash(p)
    r['feasible'] = not r['fails']
    # small geometry for drawing
    r['draw'] = dict(section=[[round(a, 3), round(b, 3)] for a, b in section(K, 9.0, p['keel'])],
                     top=[[round(x, 2), round(float(np.interp(x, K[:, 0], K[:, 1])), 3)] for x in np.linspace(0, L, 17)],
                     keel=[[round(x, 2), round(float(section(K, x, p['keel'])[4][1]), 3)] for x in np.linspace(0, L, 17)],
                     plan=[[round(x, 2), round(float(np.interp(x, K[:, 0], K[:, 4])), 3)] for x in np.linspace(0, L, 17)])
    return r

_V0, _F0, _K0, _b0, _ = loft(dict(B5, ridge=0, shoulder_z=0, shoulder_y=0, keel=0)); _n0, _A0 = AT.geom(_V0[_F0])
SWET0 = float(_A0.sum()); _x = np.linspace(0.05, L, 160); PLAN0 = float(np.trapezoid([2 * section(_K0, x, 0)[2][0] for x in _x], _x))

def _job(args):
    i, p = args
    try:
        r = evaluate(p); r['id'] = i; return r
    except Exception as ex:
        return dict(id=i, params=p, feasible=False, fails=[f'error: {ex}'])

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=1600); ap.add_argument('--seed', type=int, default=2226)
    a = ap.parse_args(); rng = random.Random(a.seed)
    designs = [(0, dict(B5))] + [(i, sample(rng)) for i in range(1, a.n)]
    from multiprocessing import Pool
    with Pool(2) as pool: res = pool.map(_job, designs, chunksize=8)
    json.dump({'header': 'ALL bodies. ALL sponsors. 2026-2226.', 'doc': __doc__, 'space': {k: (v if isinstance(v, list) else list(v)) for k, v in SPACE.items()},
               'reference_B5': B5, 'n': len(res), 'results': res}, open(os.path.join(HERE, 'explorer_results.json'), 'w'), default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    feas = [r for r in res if r.get('feasible')]
    print('designs', len(res), 'feasible', len(feas))
    from collections import Counter; print(Counter(f for r in res for f in r.get('fails', [])))
