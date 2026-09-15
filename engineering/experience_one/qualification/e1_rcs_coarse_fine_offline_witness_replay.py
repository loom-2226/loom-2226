from __future__ import annotations

import json
from pathlib import Path

from src.wayfarer_rcs_actuator_requirement_envelope import build_actuator_requirement_envelope
from src.wayfarer_rcs_coarse_fine_authority_envelope import _simulate_case
from src.wayfarer_rcs_time_domain_mount_coupling import _CASES

RESULT_PATH = Path('engineering/experience_one/results/e1_rcs_coarse_fine_offline_sweep.json')
# Pixel does not repeat the 45-run sweep. Replay the four sampled corners against
# one nominal and one degraded case; PR #198 already qualified the interior
# 0.20/0.50 witness against the same bounded case pair.
REPLAY_WITNESSES = ((0.10,0.25),(0.10,1.00),(0.30,0.25),(0.30,1.00))
REPLAY_CASES = ('NOMINAL_MIXED_TRANSLATION_ATTITUDE','DEGRADED_MIXED_TRANSLATION_ATTITUDE_A')


def qualify() -> dict:
    persisted = json.loads(RESULT_PATH.read_text(encoding='utf-8'))
    allowed = {(x['coarse_activation_fraction'], x['fine_quantization_fraction']) for x in persisted['pixel_witnesses']}
    assert set(REPLAY_WITNESSES).issubset(allowed)
    demand = build_actuator_requirement_envelope()['aggregate_sampled_actuator_demand']
    trace_mib_ns = float(demand['sampled_exact_trace_mib_upper_bound_Ns'])
    rows = []
    for coarse, fine in REPLAY_WITNESSES:
        cases = {
            name: _simulate_case(name, _CASES[name], coarse_fraction=coarse, fine_fraction=fine, trace_mib_ns=trace_mib_ns)
            for name in REPLAY_CASES
        }
        rows.append({'coarse_activation_fraction': coarse, 'fine_quantization_fraction': fine,
                     'pass': all(x['pass'] for x in cases.values()), 'cases': cases})
    passed = all(x['pass'] for x in rows)
    return {
        'schema': 'LOOM_E1_RCS_COARSE_FINE_OFFLINE_WITNESS_REPLAY_V1',
        'status': 'PASS' if passed else 'FAIL',
        'claim': 'BOUNDED_REPLAY_OF_SAMPLED_OFFLINE_REGION_WITNESSES_ONLY',
        'offline_source_result_sha256': persisted['source_result_sha256'],
        'full_offline_sweep_reexecuted_on_pixel': False,
        'continuous_region_interpolation_certified': False,
        'hardware_certified': False,
        'campaign_state_mutation': 'ZERO',
        'llm_calculation_authority': 'ZERO',
        'replay': rows,
    }


if __name__ == '__main__':
    result = qualify()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
