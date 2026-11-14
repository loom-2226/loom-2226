"""Shuttle v2-B4 (side-door rover) core dry mass and G8 gate screen vs v1.
NON-CANON research screen. ALL bodies. ALL sponsors. 2026-2226.
Core = the 13 sizer core components (kit excluded, carried as Wayfarer payload
per Gate A2). Independent uniform sampling of every range, same as the
2026-11-03 rover trade. Every v2 factor below is an ASSUMPTION (Claude, for kT)."""
import json, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, '..', 'shuttle_inputs.json')))['mass']
CORE = ['pressure_pod_titanium_shell_t', 'hull_thermal_structure_t', 'pressure_pod_fittings_seals_t', 'folding_rover_chassis_t',
        'torch_low_high_engine_t', 'small_belly_thrusters_t', 'reactor_power_distribution_t', 'crew_habitat_thermal_package_t',
        'custody_capsule_dry_t', 'avionics_controls_yaw_t', 'landing_gear_door_ramp_t', 'water_tank_insulated_t', 'base_entry_tps_core_t']
LIMIT = M['max_docked_dry_t']['value']
AREA = json.load(open(os.path.join(HERE, 'shuttle_v2b_manifest.json')))['area_ratio_v2_over_v1']
V2 = {   # multiplier ranges [lo, hi] and added masses [lo, hi] t
 'pressure_pod_titanium_shell_t': dict(mul=[2 * (1.9 / 2.5) ** 3] * 2, why='two 1.9 m spheres vs one 2.5 m: buckling-governed shell ~R^3 (rover trade exponent 3)'),
 'pressure_pod_fittings_seals_t': dict(mul=[2 * (1.9 / 2.5) ** 2] * 2, add=[0.15, 0.35], why='fittings ~R^2 per sphere (exponent 2) + tunnel and second hatch'),
 'hull_thermal_structure_t': dict(mul=[AREA * 1.10, AREA * 1.35], add=[0.2, 0.5], why=f'wetted area x{AREA} (mesh), flat-panel/non-circular penalty x1.10-1.35, longerons around the 4.2 m side opening'),
 'base_entry_tps_core_t': dict(mul=[AREA, 1.0], why='windward area scales with the smaller body, up to unchanged'),
 'folding_rover_chassis_t': dict(mul=[1.0, 1.2], add=[0.05, 0.15], why='wider two-sphere chassis + crab steering'),
}
WINGS = dict(add=[1.2, 2.0], why='B4 double-fold wing panels, shoulder hinges (also door hinge), actuators, locks')
def sample(n, v2, rng):
    tot = np.zeros(n); parts = {}
    for k in CORE:
        lo, hi = M[k]['min'], M[k]['max']; x = rng.uniform(lo, hi, n)
        if v2 and k in V2:
            f = V2[k]; x = x * rng.uniform(*f['mul'], n) + (rng.uniform(*f['add'], n) if 'add' in f else 0)
        parts[k] = x; tot += x
    if v2:
        parts['b4_wings_t'] = rng.uniform(*WINGS['add'], n); tot += parts['b4_wings_t']
    return tot, parts
rng = np.random.default_rng(2026); N = 200000
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON research screen; v2 factors are ASSUMPTIONS',
           limit_G8_docked_dry_t=LIMIT, samples=N, seed=2026, v2_factors={k: v['why'] for k, v in V2.items()} | {'b4_wings_t': WINGS['why']})
for name, v2 in (('v1_baseline_A', False), ('v2_B4_side_door', True)):
    t, parts = sample(N, v2, rng)
    out[name] = dict(p5=round(float(np.percentile(t, 5)), 2), mid=round(float(np.median(t)), 2), p95=round(float(np.percentile(t, 95)), 2),
                     mean=round(float(t.mean()), 2), pass_G8_fraction=round(float((t <= LIMIT).mean()), 3),
                     margin_at_median_t=round(LIMIT - float(np.median(t)), 2),
                     changed_parts_mid_t={k: round(float(np.median(v)), 3) for k, v in parts.items() if (k in V2 or k == 'b4_wings_t')})
out['delta_mid_t'] = round(out['v2_B4_side_door']['mid'] - out['v1_baseline_A']['mid'], 2)
json.dump(out, open(os.path.join(HERE, 'b4_mass_gate.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
