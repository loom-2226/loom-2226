"""Shuttle B4-S mass model: standard shuttle (6 seats, light rover) and the Venus kit, Gates A2 / A vs G8 34.2 t.
NON-CANON research screen. ALL bodies. ALL sponsors. 2026-2226.
Same method as b4_mass_gate.py and the v1 sizer: every component range from ../shuttle_inputs.json sampled uniformly and
independently; every B4-S change below is an ASSUMPTION (Claude, for kT). Geometry (areas) from build_b4s.py.
  A2 = standard docked dry (no Venus kit): what G8 34.2 t applies to.
  A  = Venus-configured dry: A2 minus the light rover cabin shell (left in Wayfarer) plus the Venus kit (comparator, as v1).
Heat-tolerant cabin: on Venus the cabin is vented to 92 bar CO2 at 735 K for ~18 h, so its wall is titanium/ceramic-matrix
(15-25 kg/m2 incl. frames), not polymer composite; seats and soft outfit come out as part of the kit setup.
Writes b4s_mass.json."""
import json, os, numpy as np
import build_b4s as S, b4_mass_gate as G
HERE = os.path.dirname(os.path.abspath(__file__))
M = G.M; LIMIT = G.LIMIT; AREA = G.AREA
A = json.load(open(os.path.join(HERE, 'aero_results.json')))
HL = A['entry']['Venus']['B4 double fold']['heat_load_MJm2'] / A['entry']['Venus']['v1 biconic']['heat_load_MJm2']
def tri_area(VF):
    V, F = VF; a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]; return float(0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum())
P = S.shuttle('flight'); CAB_A = tri_area(P['cabin']); LR_A = tri_area(P['rover_light'])
N = 200000; rng = np.random.default_rng(2026); U = lambda lo, hi: rng.uniform(lo, hi, N)
base = {k: U(M[k]['min'], M[k]['max']) for k in G.CORE}
KIT_KEYS = ['single_12m_rotor_blades_hub_mast_t', 'tipjet_ducts_compressors_t', 'venus_hot_loop_thermal_kit_t', 'venus_cooler_t', 'kit_house_reactor_t', 'kit_house_exchanger_ducts_t']
kitb = {k: U(M[k]['min'], M[k]['max']) for k in KIT_KEYS}
tps_total = U(M['entry_tps_t']['min'], M['entry_tps_t']['max']); hl = HL ** U(.5, 1.0)

std = dict(
 hull_thermal_structure_t=base['hull_thermal_structure_t'] * U(AREA * 1.10, AREA * 1.35) + U(.2, .5),
 base_entry_tps_core_t=base['base_entry_tps_core_t'] * U(AREA, 1.0) * hl,
 cabin_wall_heat_tolerant_t=CAB_A * U(15, 25) / 1e3,
 cabin_hatches_seals_t=base['pressure_pod_fittings_seals_t'] * U(.8, 1.2),
 crew_habitat_thermal_package_6_seats_t=base['crew_habitat_thermal_package_t'] * U(1.6, 2.0),
 water_tank_insulated_t=base['water_tank_insulated_t'] * U(1.2, 1.6),
 rover_chassis_crab_t=base['folding_rover_chassis_t'] * U(1.0, 1.2) + U(.05, .15),
 rover_light_cabin_shell_t=LR_A * U(8, 15) / 1e3,
 rover_outfit_life_support_power_t=U(.4, .8),
 b4_wings_t=U(*G.WINGS['add']))
for k in ('torch_low_high_engine_t', 'small_belly_thrusters_t', 'reactor_power_distribution_t', 'custody_capsule_dry_t', 'avionics_controls_yaw_t', 'landing_gear_door_ramp_t'):
    std[k] = base[k]
kit = dict(
 ti_capsule_shell_t=base['pressure_pod_titanium_shell_t'] * U(.85, 1.15),     # thin-shell sizing: 1.9x3.0 m stiffened capsule ~0.9x the 2.5 m sphere
 ti_capsule_fittings_seals_t=base['pressure_pod_fittings_seals_t'] * U(.9, 1.2),
 extra_venus_entry_tps_t=(tps_total - base['base_entry_tps_core_t']) * U(AREA, 1.0) * hl,
 **kitb)
a2 = sum(std.values()); kit_t = sum(kit.values()); a = a2 - std['rover_light_cabin_shell_t'] + kit_t
# v1 for comparison, same draws
v1_a2 = sum(base.values()); v1_kit = sum(kitb.values()) + (tps_total - base['base_entry_tps_core_t'])
pc = lambda x: {k: round(float(np.percentile(x, q)), 2) for k, q in (('p5', 5), ('mid', 50), ('p95', 95))}
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON screen; every B4-S factor is an ASSUMPTION',
           decisions=['shuttle_b4_standard_rover_venus_kit_2026_11_19'], G8_limit_t=LIMIT, samples=N, seed=2026,
           geometry=dict(cabin_wall_area_m2=round(CAB_A, 1), light_rover_shell_area_m2=round(LR_A, 1), heat_load_ratio_venus=round(HL, 3)),
           standard_A2=dict(dry_t=pc(a2), pass_G8=round(float((a2 <= LIMIT).mean()), 3), parts_mid_t={k: round(float(np.median(v)), 3) for k, v in std.items()}),
           venus_kit=dict(kit_t=pc(kit_t), parts_mid_t={k: round(float(np.median(v)), 3) for k, v in kit.items()}),
           venus_configured_A=dict(dry_t=pc(a), under_34_2_fraction=round(float((a <= LIMIT).mean()), 3)),
           v1_same_draws=dict(A2_dry_t=pc(v1_a2), A2_pass_G8=round(float((v1_a2 <= LIMIT).mean()), 3), kit_t=pc(v1_kit)),
           booked_v1_t=30.732248081255836)
out['delta_A2_vs_v1_mid_t'] = round(out['standard_A2']['dry_t']['mid'] - out['v1_same_draws']['A2_dry_t']['mid'], 2)
json.dump(out, open(os.path.join(HERE, 'b4s_mass.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
