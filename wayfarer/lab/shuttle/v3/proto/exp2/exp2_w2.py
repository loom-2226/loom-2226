"""Experiment 2, W2: four departure scenarios from a hot-extraction landing zone. NON-CANON prototype lane.
ALL bodies. ALL sponsors. 2026-2226.
Reference vehicle: W1 + Osteon cautious (#2643, 17 m, 18 t tank), hot profile 'hard25' (missions.json).
Corrections vs lane note 2026-11-21: the earlier '~3 GJ' was (mgh + 1/2 m v^2)/eta with v = 125 m/s and eta = 0.6 for ~60 t;
mgh alone is ~1.2 GJ. The '20 s' climb was inconsistent with its own 0.4 g profile (that reaches 2 km in ~32 s).
The '1 t flywheel' used kT's DECLARED 2226 storage (1 kWh/kg, 150 kW/kg, ship_power 2026-11-01), ~10x an ordinary flywheel.
Labels: MODEL (kinematics, explorer burn model), ASSUMPTION (brackets), REQUIRED (what the device must do), UNKNOWN (left open)."""
import sys, os, json, math
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..', 'explorer'))
import engine as E, missions as MI
D = json.load(open(os.path.join(H, '..', '..', 'explorer', 'explorer_results.json'))); G2643 = {r['id']: r for r in D['results']}[2643]['params']
G = 9.81; P_T = 7.7e9; VE_MIN = 10e3; T_MAX = 2 * P_T / VE_MIN
REF = dict(G2643, wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=18.0)
HEAVY = dict(REF, length=14.3, seats=8)                                   # 14.3 m contingency, 8 couches (thrust-short on hot)
HOT = MI.MJ['profiles']['hot']; LEGS = [tuple(x) for x in MI.MJ['legs']['hard25']['dv']]
CARRIED = lambda p: p['water_t'] + HOT['sprint_t']
STORE = dict(declared_2226=dict(kWh_kg=1.0, kW_kg=150.0), ordinary_2026=dict(kWh_kg=0.1, kW_kg=10.0))

# ---------------------------------------------------------------- the three mechanisms, kept apart
MECH = {
 'M1 reduced effective gravitational loading': dict(
    does='an upward force on the shuttle equal to f x weight; reaction delivered to the planet (gravitationally or through a footprint)',
    hover_ideal_power='~0: a static force does no work (like standing on ground); real cost = losses + field upkeep [UNKNOWN]',
    energy='work done = force x height; every joule of mgh + 1/2 mv^2 comes from the onboard source',
    momentum='closed with the planet (recoil negligible); if the reaction is local, the footprint feels F/A',
    crew='if it acts on all mass uniformly: crew feel only the non-field forces (weightless in a field-only climb). If it acts on the structure: crew feel (field + torch)/m',
    classification='NEW CONSTITUTIVE RELATION (switchable gravitational coupling or a new planet-referenced force). If framed as reducing gravitational mass it is in TENSION with the equivalence principle (tested to ~1e-15 for ordinary matter) - so frame it as an applied, switched coupling, not changed matter.',
    useful_for_departure=True),
 'M2 modified inertial response': dict(
    does='lowers the inertia the torch must accelerate; leaves weight unchanged',
    hover_ideal_power='no help: hover thrust = weight, unchanged',
    energy='switching inertia at speed changes 1/2 m v^2 or p = m v; one of them must be paid to or taken from the field [UNKNOWN which]',
    momentum='in tension on switch-off: either momentum or energy conservation needs the field to carry the difference',
    crew='crew of reduced inertia feel less force at the same acceleration',
    classification='IN TENSION WITH A GOVERNING INVARIANT (equivalence principle; momentum at switching). Highest bar; no departure benefit because weight is unchanged.',
    useful_for_departure=False),
 'M3 engineered local spacetime geometry': dict(
    does='a finite region whose interior is in free fall while the region itself is held or moved (canon-family metric engineering, M2 miracle)',
    hover_ideal_power='region held against the planet: same accounting as M1 (planet or canon Sun partner takes the reaction)',
    energy='canon ENERGY-B: metric transit conserves mechanical energy, so height must be paid (powered channel) - same mgh as M1',
    momentum='declared nonlocal partner (canon Sun, §7.1b) or the planet',
    crew='weightless interior (canon 10 s ramps to 0.27c imply inertial interior)',
    classification='CONSISTENT WITH CANON PHYSICS (inside the M2 miracle) but BEYOND CANON TECHNOLOGY (near-body, small, powered). Domain continuity: the wall may not cut hull, water or people - so it cannot start from a floating or landed shuttle unless the boundary may cross matter [UNKNOWN].',
    useful_for_departure='only from a hover or a cleared volume'),
}

def kin(a, h):  # constant acceleration from rest to height h: (t, v)
    t = math.sqrt(2 * h / a); return t, a * t
def after(h0, v0, a, h):  # time from (h0, v0) to h at constant acceleration a
    return (-v0 + math.sqrt(v0 * v0 + 2 * a * (h - h0))) / a

def scenario(name, p, field_net_g, h_hand, tw_after, pulse=None, mod_t=0.0, eta=0.6, E_est=0.05e9, P_up=0.5e6, store='declared_2226'):
    """field_net_g: net upward acceleration (g) during the field-only climb; h_hand: torch light-off height (0 = conventional).
    pulse: (f, t_p) partial field assistance alongside the torch from lift-off. Returns kinematics, energy, water, exposure."""
    r = E.evaluate(p); pay = HOT['payload_t'] + HOT['t_per_person'] * p['seats']; dry0 = r['dry_t']
    li = 1; post = LEGS[li + 1:]                                            # legs after landing: climb, orbit, rendezvous
    tw0 = post[0][1]; a0 = (tw0 - 1) * G
    # storage sized iteratively
    st_t = 0.0
    for _ in range(6):
        dry = dry0 + mod_t + st_t
        w_post = E.water_chk(dry, pay, post)[0]; m0 = dry + pay + w_post          # lift-off mass (t), MODEL
        W = m0 * 1e3 * G
        if pulse:                                                            # torch + partial field, same 2.5 g net profile
            f, tp = pulse; h_p = 0.5 * a0 * tp * tp; v_p = a0 * tp
            E_ship = f * W * h_p; P_peak = f * W * v_p / eta; t_field = tp
            legs = [(round((tw0 - f) * G * tp), tw0 - f, G), (round(post[0][0] - tw0 * G * tp), tw0, G)] + post[1:]
            prof = [('torch+field', 0, h_p, a0)]
            t_200, t_2k = kin(a0, 200)[0], kin(a0, 2000)[0]; v_hand = None
        elif h_hand > 0:
            af = field_net_g * G; t_f, v_f = kin(af, h_hand)
            E_ship = W * h_hand + 0.5 * m0 * 1e3 * v_f ** 2; P_peak = (1 + field_net_g) * W * v_f / eta; t_field = t_f
            t_c, v_c = kin(a0, h_hand); credit = tw0 * G * t_c - (v_c - v_f)    # torch dv the conventional climb spent, less speed still owed
            legs = [(round(post[0][0] - credit), tw_after, G)] + post[1:]
            aa = (tw_after - 1) * G
            t_200 = kin(af, min(200, h_hand))[0] if h_hand >= 200 else t_f + after(h_hand, v_f, aa, 200)
            t_2k = kin(af, 2000)[0] if h_hand >= 2000 else t_f + after(h_hand, v_f, aa, 2000); v_hand = v_f
        else:
            E_ship = 0.0; P_peak = 0.0; t_field = 0.0; legs = list(post)
            t_200, t_2k = kin(a0, 200)[0], kin(a0, 2000)[0]; v_hand = None
        E_src = (E_est + E_ship / eta + P_up * t_field) if (pulse or h_hand > 0) else 0.0
        reactor = r['fans']['MWe'] * 1e6 * 0.9 * t_field                    # fan reactor can feed the field during the climb [ASSUMPTION 90%]
        E_store = max(E_src - reactor, 0.0); s = STORE[store]
        st_new = max(E_store / 3.6e6 / s['kWh_kg'], max(P_peak - r['fans']['MWe'] * 1e6, 0) / 1e3 / s['kW_kg']) / 1e3 if E_src else 0.0
        if abs(st_new - st_t) < 0.01: st_t = st_new; break
        st_t = st_new
    dry = dry0 + mod_t + st_t
    full = list(LEGS[:li + 1]) + legs
    need, short = E.water_chk(dry, pay, full)
    pre = E.water_chk(dry, pay, legs)[0]                                     # water aboard at the departure point
    td = MI.touchdown(r, dry + pay + pre)                                    # conventional water landing with the module aboard
    crew_field_uniform = 0.0 if (h_hand > 0 and not pulse) else (tw0 - (pulse[0] if pulse else 0))
    crew_field_structure = (1 + field_net_g) if (h_hand > 0 and not pulse) else tw0
    return dict(scenario=name, liftoff_t=round(m0, 1), module_t=mod_t, storage_t=round(st_t, 2), dry_t=round(dry, 2),
                t_to_200m_s=round(t_200, 1), t_to_2km_s=round(t_2k, 1), speed_at_handover_ms=None if v_hand is None else round(v_hand),
                field_time_s=round(t_field, 1), torch_tw_after=tw_after if h_hand > 0 else tw0,
                crew_g_during_field_uniform=crew_field_uniform, crew_g_during_field_structure=round(crew_field_structure, 2),
                crew_g_at_torch=tw_after if (h_hand > 0 and not pulse) else tw0,
                energy_to_shuttle_GJ=round(E_ship / 1e9, 2), field_source_GJ=round(E_src / 1e9, 2), peak_power_MW=round(P_peak / 1e6),
                from_storage_GJ=round(E_store / 1e9, 2), reaction_impulse_MNs=round((1 + field_net_g) * W * t_field / 1e6, 1) if h_hand > 0 and not pulse else (round(pulse[0] * W * pulse[1] / 1e6, 1) if pulse else 0),
                footprint_pressure_kPa_if_local=round(((1 + field_net_g) if h_hand > 0 and not pulse else (pulse[0] if pulse else 0)) * W / r['land']['S'] / 1e3, 1),
                torch_lightoff_m=h_hand if not pulse else 0, hot_water_t=need, carried_t=CARRIED(p), water_ok=need <= CARRIED(p), thrust_short=short,
                dry_ok=dry <= E.CEIL_T, touchdown_ms_conventional_landing=td)

def plume(h):  # crude torch-plume ground exposure at light-off height (ASSUMPTION brackets)
    out = {}
    for frad in (0.01, 0.1, 0.3):
        out[f'radiant_kW_m2_at_{h}m_frad_{frad}'] = round(frad * P_T / (4 * math.pi * max(h, 30) ** 2) / 1e3, 2)
    rj = max(h, 30) * math.tan(math.radians(15)); out['jet_axis_power_density_kW_m2_if_pointed_down'] = round(0.3 * P_T / (math.pi * rj ** 2) / 1e3)
    return out

def run_set(p, label, mod_t=0.0, **kw):
    return [scenario('S0 conventional torch lift-off (T/W 2.5)', p, 0, 0, 2.5, mod_t=mod_t, **kw),
            scenario('S1 10-20 s partial assist (field 0.5 W for 15 s, torch 2.0)', p, 0, 0, 2.5, pulse=(0.5, 15.0), mod_t=mod_t, **kw),
            scenario('S2 field climb to 200 m (net 0.5 g), torch 2.0 pitched', p, 0.5, 200, 2.0, mod_t=mod_t, **kw),
            scenario('S3 field climb to 2 km (net 0.5 g), torch 1.4', p, 0.5, 2000, 1.4, mod_t=mod_t, **kw)]

def ceiling(p, which, **kw):  # largest module (t) that keeps hot extraction closing (water, thrust, dry ceiling)
    best = None
    for m in [x * 0.5 for x in range(0, 61)]:
        s = run_set(p, '', mod_t=m, **kw)[which]
        if s['water_ok'] and not s['thrust_short'] and s['dry_ok']: best = m
        else: break
    return best

base = run_set(REF, 'W1+Osteon')
heavy = run_set(HEAVY, '14.3 m 8 couches')
ceil = {}
for i, nm in enumerate(['S0', 'S1', 'S2', 'S3']):
    if i == 0: continue
    ceil[nm] = dict(central=ceiling(REF, i), pessimistic=ceiling(REF, i, eta=0.3, E_est=0.3e9, P_up=5e6),
                    ordinary_storage=ceiling(REF, i, store='ordinary_2026'), heavy_14p3_8c=ceiling(HEAVY, i))
sens = {f'S3 net {a} g': scenario(f'S3 net {a} g', REF, a, 2000, 1.4) for a in (0.25, 0.5, 1.0)}
sens.update({f'S2 net {a} g': scenario(f'S2 net {a} g', REF, a, 200, 2.0) for a in (0.25, 0.5, 1.0)})
r = E.evaluate(REF); m_ref = base[0]['liftoff_t']
hover = dict(liftoff_t=m_ref, fans_static_share_of_weight=round(r['fans']['static_kN'] * 1e3 / (m_ref * 1e3 * G), 2),
             torch_hover_water_t_per_min=round(m_ref * 1e3 * G / (2 * P_T / (m_ref * 1e3 * G)) * 60 / 1e3, 2),
             field_share_needed_with_fans=round(1 - r['fans']['static_kN'] * 1e3 / (m_ref * 1e3 * G), 2),
             field_hover_energy='losses only [UNKNOWN]; at the bracket 0.5-5 MW upkeep: 0.03-0.3 GJ per minute',
             vertical_land_touchdown_absorb_from_200m_GJ=round(m_ref * 1e3 * G * 200 / 1e9, 3))
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) experiment 2, W2', model_version=E.MODEL_VERSION,
           corrections=dict(mgh_60t_2km_GJ=round(60e3 * G * 2000 / 1e9, 2), previous_3GJ='(mgh + 1/2 m v^2)/eta, v 125 m/s, eta 0.6',
                            previous_20s='inconsistent: 0.4 g net reaches 2 km in %.0f s at %.0f m/s; 2 km in 20 s needs ~1 g net' % kin(0.4 * G, 2000),
                            storage='1 kWh/kg is kT-declared 2226 (ship_power 2026-11-01); ordinary 2026 flywheels ~0.05-0.1 kWh/kg system'),
           mechanisms=MECH, assumptions=dict(eta_central=0.6, E_establish_central_GJ=0.05, upkeep_central_MW=0.5, pessimistic='eta 0.3, 0.3 GJ, 5 MW',
                                              fan_reactor_feeds_field='%.1f MWe at 90%%' % r['fans']['MWe'], module_mass='free variable: the ceiling is an integration limit, not a prediction'),
           scenarios=base, heavy_14p3_8c=heavy, module_ceiling_t=ceil, sensitivity=sens, hover=hover,
           plume=dict(at_0m=plume(0), at_200m=plume(200), at_2000m=plume(2000)))
json.dump(out, open(os.path.join(H, 'exp2_w2.json'), 'w'), indent=1)
if __name__ == '__main__':
    print(out['corrections'])
    for s in base + heavy: print({k: s[k] for k in ('scenario', 'liftoff_t', 'storage_t', 'dry_t', 't_to_200m_s', 't_to_2km_s', 'speed_at_handover_ms', 'energy_to_shuttle_GJ', 'field_source_GJ', 'peak_power_MW', 'from_storage_GJ', 'hot_water_t', 'carried_t', 'thrust_short', 'touchdown_ms_conventional_landing', 'footprint_pressure_kPa_if_local')})
    print(ceil); print(hover); print(out['plume'])
    for k, s in sens.items(): print(k, s['t_to_200m_s'], s['t_to_2km_s'], s['field_source_GJ'], s['peak_power_MW'], s['storage_t'], s['hot_water_t'])
