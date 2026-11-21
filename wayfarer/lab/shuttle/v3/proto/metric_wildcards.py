"""Prototype lane W2 (local metric ascent assist) and W3 (metric impulse manoeuvring).
NON-CANON hypothesis ledger: numbers here are what the hypotheses would REQUIRE, not results.
ALL bodies. ALL sponsors. 2026-2226.
Canon anchors: CANON II v2.5 §3 (plant), §5 (card), §6.2 (L^2 law = candidate fit, not canon), §7.1a (ENERGY-B arrival rule),
§7.1b (Sun as declared nonlocal partner), §7.3 (conservation firewall), §8 (RSET adiabatic screen), §9 (ramp), §14 (torch/metric
exclusivity), §18A, §21 (hard kills). Flywheel 1 kWh/kg, 150 kW/kg (kt ship_power storage_revision 2026-11-01)."""
import sys, os, json, math
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'explorer'))
import engine as E, missions as MI
G = 9.81
D = json.load(open(os.path.join(H, '..', 'explorer', 'explorer_results.json'))); by = {r['id']: r for r in D['results']}
# ---------------------------------------------------------------- module sizing under scaling hypotheses
WF = dict(plant_t=88.0, mc_kg=10.0, nodes=208, bank_GJ=2.0, boundary_m2=1900.0, cryo_normal_MW=3.5, rad_normal_m2=106.0, cryo_hard_MW=23.9, rad_hard_m2=719.0)
def ellipsoid_area(a, b, c, p=1.6075): return 4 * math.pi * (((a * b) ** p + (a * c) ** p + (b * c) ** p) / 3) ** (1 / p)
WALL = 1.5   # m clearance+wall around the hull (ASSUMPTION; reference wall is 6 m on Wayfarer)
A_env = ellipsoid_area(12.8 / 2 + WALL, 4.26 / 2 + WALL, 3.4 / 2 + WALL)
scal = {}
for law, f in (('L2 (area, candidate fit §6.2)', A_env / WF['boundary_m2']), ('L1 (sqrt area)', math.sqrt(A_env / WF['boundary_m2'])), ('none (Wayfarer plant)', 1.0)):
    scal[law] = dict(fraction=round(f, 3), plant_t=round(WF['plant_t'] * f, 1), mc_kg=round(WF['mc_kg'] * f, 2), nodes=round(WF['nodes'] * f),
                     bank_GJ=round(WF['bank_GJ'] * f, 2), cryo_normal_MW=round(WF['cryo_normal_MW'] * f, 2), rad_normal_m2_900K=round(WF['rad_normal_m2'] * f, 1),
                     cryo_hard_MW=round(WF['cryo_hard_MW'] * f, 2), rad_hard_m2_900K=round(WF['rad_hard_m2'] * f, 1))
# ---------------------------------------------------------------- W2: local metric ascent assist (first 10 km)
def climb_dv(h=10e3, tw=1.4):
    a = (tw - 1) * G; t = math.sqrt(2 * h / a); return tw * G * t, a * t, t        # torch dv spent, speed at h, time
dv10, v10, t10 = climb_dv()
def w2(case, base, module_t, eta, t_assist):
    p = dict(base); r = E.evaluate(p); dry = r['dry_t'] + module_t; pay = 0.5 + 0.1 * p['seats']
    m = dry + pay + p['water_t']                       # worst case: full tank at lift-off
    E_up = m * 1e3 * (G * 10e3 + 0.5 * v10 ** 2)       # J: potential + handover kinetic energy (Earth frame)
    E_src = E_up / eta; P = E_src / t_assist
    fly_t = max(E_src / 3.6e6 / 1.0e3, P / 150e3 / 1e3)  # t of flywheel (1 kWh/kg, 150 kW/kg)
    E_down = m * 1e3 * G * 10e3                         # descent: potential to absorb (regenerate or dump)
    dT_water = E_down / (p['water_t'] * 1e3 * 4186)     # if dumped into the tank as heat
    legs_conv = [(200, .1, 1), (300, 1.3, 9.81), (3000, 2.5, 9.81), (6400, .8, 9.81), (400, .1, 1)]
    legs_met = [(200, .1, 1), (round(3000 - dv10), 1.4, 9.81), (6400, .8, 9.81), (400, .1, 1)]   # no landing burn, torch lights at 10 km
    w_conv, sh_conv = E.water_chk(r['dry_t'], pay, legs_conv); w_met, sh_met = E.water_chk(dry + fly_t, pay, legs_met)
    return dict(case=case, dry_without_module_t=r['dry_t'], module_t=module_t, flywheel_t=round(fly_t, 2), liftoff_t=round(m, 1), eta=eta, assist_s=t_assist,
                energy_up_GJ=round(E_up / 1e9, 2), source_GJ=round(E_src / 1e9, 2), power_MW=round(P / 1e6), descent_absorb_GJ=round(E_down / 1e9, 2),
                tank_temp_rise_if_dumped_K=round(dT_water, 1), hot_water_conventional_t=w_conv, hot_thrust_short_conventional=sh_conv,
                hot_water_metric_t=w_met, hot_thrust_short_metric=sh_met, tank_t=p['water_t'], fits_tank=w_met <= p['water_t'],
                dry_with_module_t=round(dry + fly_t, 2), under_ceiling=dry + fly_t <= 52.5)
bases = {'B5': dict(E.B5), '#2643': dict(by[2643]['params']), '#2643 + Osteon cautious': dict(by[2643]['params'], wildcard='osteon_cautious'),
         '#2643 14.3 m, 8 couches, Osteon cautious': dict(by[2643]['params'], wildcard='osteon_cautious', length=14.3, seats=8, water_t=23.1)}
w2_rows = []
for law in ('L2 (area, candidate fit §6.2)', 'L1 (sqrt area)'):
    mod = scal[law]['plant_t'] + 1.0     # + thermal storage plumbing / nodes mounts (ASSUMPTION)
    for name, b in bases.items():
        for eta, ts in ((0.6, 60), (0.3, 30)):
            row = w2(f'{name} | {law} | eta {eta} | {ts} s', b, mod, eta, ts); row['law'] = law; w2_rows.append(row)
# ---------------------------------------------------------------- W3: metric impulse hops (ledger under the canon ENERGY-B rule and under W2's powered metric)
def hop(m_t, dx, dz, t_hop, v0=0.0, rho=1.225, vol_m3=None):
    vol = vol_m3 or 4 / 3 * math.pi * (12.8 / 2 + WALL) * (4.26 / 2 + WALL) * (3.4 / 2 + WALL)
    vbar = math.hypot(dx, dz) / t_hop
    dE_energyB = 0.0 if dz <= 0 else None                 # ENERGY-B: mechanical energy conserved; up-hops need paid speed
    zoom_needed = math.sqrt(2 * G * dz) if dz > 0 else 0.0  # speed that ENERGY-B would require to gain dz
    dE_powered = m_t * 1e3 * G * dz                         # powered-metric (W2 effect) cost of the height gain
    air_E = 0.5 * rho * vbar ** 2 * vol                     # order of energy given to the swept/vacated air
    return dict(m_t=m_t, dx_m=dx, dz_m=dz, t_s=t_hop, mean_coord_speed_ms=round(vbar), mach_sea_level=round(vbar / 340, 1),
                energyB_extra_energy=('~0 (level or down; down-hops arrive FASTER by sqrt(2 g dz))' if dz <= 0 else f'forbidden unless already moving at >= {zoom_needed:.0f} m/s'),
                powered_metric_GJ=round(dE_powered / 1e9, 3), air_disturbance_GJ=round(air_E / 1e9, 2),
                rset_ramp_to_light_crossing=f'{0.1 / (2 * WALL / 3e8):.1e} for a 0.1 s ramp (canon screen: 10 s / 6 m wall ~ {10 / (6 / 3e8):.1e})')
w3_rows = [hop(45, 1000, 0, 1.0), hop(45, 1000, 0, 0.5), hop(45, 0, 1000, 1.0), hop(45, 0, -1000, 1.0), hop(45, 300, 0, 0.3, rho=0.41), hop(45, 5000, 0, 2.0, rho=0.41)]
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon): REQUIRED-VALUE hypotheses, not results', model_version=E.MODEL_VERSION,
           envelope=dict(wall_clearance_m=WALL, envelope_area_m2=round(A_env)), scaling=scal,
           conventional_first_10km=dict(torch_dv_ms=round(dv10), speed_at_10km_ms=round(v10), time_s=round(t10)),
           w2=w2_rows, w3=w3_rows)
json.dump(out, open(os.path.join(H, 'metric_wildcards.json'), 'w'), indent=1)
print('envelope m2', round(A_env)); [print(k, v) for k, v in scal.items()]
print('first 10 km conventional', out['conventional_first_10km'])
for r in w2_rows: print(r['case'], 'mod', r['module_t'], 'fly', r['flywheel_t'], 'dry', r['dry_with_module_t'], 'E', r['source_GJ'], 'P', r['power_MW'], 'hot conv', r['hot_water_conventional_t'], r['hot_thrust_short_conventional'], 'metric', r['hot_water_metric_t'], r['hot_thrust_short_metric'], 'tank', r['tank_t'], 'dT', r['tank_temp_rise_if_dumped_K'])
for r in w3_rows: print(r)

# ---------------------------------------------------------------- W2b: short "cushion" variant (lift-off / landing to 2 km) and the break-even module mass
def cushion(base, module_t, h=2e3, eta=0.6, t_assist=20.0):
    r = E.evaluate(dict(base)); pay = 0.5 + 0.1 * base['seats']; dv_h, v_h, _ = climb_dv(h)
    m = r['dry_t'] + module_t + pay + base['water_t']
    E_src = m * 1e3 * (G * h + 0.5 * v_h ** 2) / eta; P = E_src / t_assist
    fly = max(E_src / 3.6e6 / 1e3, P / 150e3 / 1e3)
    legs = [(200, .1, 1), (round(3000 - dv_h), 1.4, 9.81), (6400, .8, 9.81), (400, .1, 1)]
    w, sh = E.water_chk(r['dry_t'] + module_t + fly, pay, legs)
    return dict(module_t=module_t, flywheel_t=round(fly, 2), dry_t=round(r['dry_t'] + module_t + fly, 2), source_GJ=round(E_src / 1e9, 2), power_MW=round(P / 1e6),
                hot_water_t=w, thrust_short=sh, tank_t=base['water_t'], fits=(w <= base['water_t'] and r['dry_t'] + module_t + fly <= 52.5 and not sh))
cush = {}
for name in ('#2643 + Osteon cautious', '#2643 14.3 m, 8 couches, Osteon cautious'):
    b = dict(bases[name], water_t=23.1)
    cush[name] = {m: cushion(b, m) for m in (2, 4, 6, 8, 10, 12, 14.2)}
out['w2_cushion_2km'] = cush
json.dump(out, open(os.path.join(H, 'metric_wildcards.json'), 'w'), indent=1)
for k, v in cush.items():
    print(k); [print('  ', m, x) for m, x in v.items()]

# ---------------------------------------------------------------- W2b alone (no Osteon) and combinations, module 8 / 12 / 14.2 t
alone = {}
for name, b in (('B5', dict(E.B5)), ('#2643', dict(by[2643]['params'], water_t=23.1)), ('#2643 + programmable 17 m', dict(by[2643]['params'], wildcard='programmable', span=17.0, chord=1.8, water_t=23.1)),
                ('#2643 + Osteon cautious + programmable 17 m', dict(by[2643]['params'], wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=23.1)),
                ('#2643 14.3 m 8c + Osteon cautious + programmable 17 m', dict(by[2643]['params'], wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=23.1, length=14.3, seats=8))):
    alone[name] = {m: cushion(b, m) for m in (8, 12, 14.2)}
out['w2_cushion_alone_and_combos'] = alone
json.dump(out, open(os.path.join(H, 'metric_wildcards.json'), 'w'), indent=1)
for k, v in alone.items(): print(k, {m: (x['dry_t'], x['hot_water_t'], x['fits']) for m, x in v.items()})
