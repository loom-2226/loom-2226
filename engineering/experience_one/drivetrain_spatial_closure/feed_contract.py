"""PR B feed interface verification; source-backed, no physical feed design."""
from __future__ import annotations
import math
from dataclasses import dataclass

MODES = ('ECON', 'CRUISE', 'EXPEDITE', 'FAST', 'HARD', 'LIMIT')

@dataclass(frozen=True)
class FeedInventory:
    normal_t: float
    protected_t: float
    external_t: float = 0.0

    def __post_init__(self):
        if any(not math.isfinite(v) or v < 0 for v in (self.normal_t, self.protected_t, self.external_t)):
            raise ValueError('inventory must be finite and nonnegative')

    def consume_normal(self, tonnes: float) -> 'FeedInventory':
        if not math.isfinite(tonnes) or tonnes < 0 or tonnes > self.normal_t:
            raise ValueError('invalid normal-remass withdrawal')
        return FeedInventory(self.normal_t - tonnes, self.protected_t, self.external_t)

    def consume_external(self, tonnes: float) -> 'FeedInventory':
        if not math.isfinite(tonnes) or tonnes < 0 or tonnes > self.external_t:
            raise ValueError('invalid external-pack withdrawal')
        return FeedInventory(self.normal_t, self.protected_t, self.external_t - tonnes)


def verify_source_contract(baseline: dict, performance: dict) -> dict:
    """Reject disagreement between source builders; do not duplicate mode constants."""
    if baseline.get('status') != 'PASS' or performance.get('status') != 'PASS':
        raise ValueError('source builders did not pass')
    vi = baseline['vehicle_interfaces']
    env = performance['normal_remass_envelope']
    cards = performance['operating_cards']
    if set(cards) != set(MODES) or set(baseline['exhaust_velocity_cards_km_s']) != set(MODES):
        raise ValueError('mode set mismatch')
    if not vi['torch_and_high_metric_thermal_field_states_mutually_exclusive']:
        raise ValueError('torch/metric exclusion absent')
    if vi['primary_torch_count'] != 1:
        raise ValueError('torch count mismatch')
    if not math.isclose(vi['dry_mass_excluding_working_fluid_water_t'] + vi['working_fluid_water_inventory_t'], vi['reference_wet_mass_t'], rel_tol=0, abs_tol=1e-8):
        raise ValueError('wet/dry accounting mismatch')
    if not math.isclose(vi['normal_remass_allowance_t'] + vi['protected_water_reserve_t'], vi['working_fluid_water_inventory_t'], rel_tol=0, abs_tol=1e-8):
        raise ValueError('normal/reserve accounting mismatch')
    if not math.isclose(vi['reference_wet_mass_t'] - vi['normal_remass_allowance_t'], vi['post_normal_remass_reference_mass_t'], rel_tol=0, abs_tol=1e-8):
        raise ValueError('post-burn mass mismatch')
    for key, expected in [('reference_wet_mass_t', vi['reference_wet_mass_t']), ('normal_remass_available_t', vi['normal_remass_allowance_t']), ('protected_water_reserve_t', vi['protected_water_reserve_t']), ('post_normal_remass_reference_mass_t', vi['post_normal_remass_reference_mass_t'])]:
        if not math.isclose(env[key], expected, rel_tol=0, abs_tol=1e-8):
            raise ValueError('performance/baseline mismatch: ' + key)
    flows = []
    for mode in MODES:
        row = cards[mode]
        if not math.isclose(row['exhaust_velocity_km_s'], baseline['exhaust_velocity_cards_km_s'][mode], rel_tol=0, abs_tol=1e-8):
            raise ValueError('exhaust velocity mismatch: ' + mode)
        thrust = row['initial_thrust_N_at_reference_wet_mass']
        flow = row['initial_mass_flow_kg_s_at_reference_wet_mass']
        ve = row['exhaust_velocity_m_s']
        if not all(math.isfinite(v) and v > 0 for v in (thrust, flow, ve)) or not math.isclose(ve, row['exhaust_velocity_km_s'] * 1000, rel_tol=0, abs_tol=1e-8) or not math.isclose(flow * ve, thrust, rel_tol=1e-10):
            raise ValueError('flow/thrust/velocity unit mismatch: ' + mode)
        flows.append(flow)
        burn = env['constant_card_full_normal_remass_burn'][mode]
        if burn['normal_remass_consumed_t'] != vi['normal_remass_allowance_t'] or burn['protected_water_consumed_t'] != 0 or burn['final_mass_t'] != vi['post_normal_remass_reference_mass_t']:
            raise ValueError('burn reserve violation: ' + mode)
    if not math.isclose(max(flows) / min(flows), 250, rel_tol=1e-9):
        raise ValueError('flow turndown mismatch')
    return {'status': 'PASS', 'modes': list(MODES), 'min_flow_kg_s': min(flows), 'max_flow_kg_s': max(flows), 'turndown': max(flows) / min(flows), 'normal_t': vi['normal_remass_allowance_t'], 'protected_t': vi['protected_water_reserve_t'], 'external_pack': 'SEPARATE_OPTIONAL_UNQUALIFIED'}


def verify_live_sources() -> dict:
    from src.wayfarer_torch_baseline_recovery import build_torch_baseline_recovery
    from src.wayfarer_torch_performance_remass_envelope import build_torch_performance_remass_envelope
    return verify_source_contract(build_torch_baseline_recovery(), build_torch_performance_remass_envelope())

if __name__ == '__main__':
    import json
    print(json.dumps(verify_live_sources(), indent=2))
