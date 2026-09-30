from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPIKE = ROOT / "engineering" / "experience_one" / "spikes" / "e1_0_spike_a_multiroute.py"


def _load_spike():
    spec = importlib.util.spec_from_file_location("e1_0_spike_a_multiroute", SPIKE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_candidate_public_view_excludes_raw_leg_and_is_fingerprint_stable():
    spike = _load_spike()
    raw = {
        "metric": "FAST",
        "torch": "CRUISE",
        "total_s": 12.5,
        "remass_used_t": 1.25,
        "arrival_remass_t": 248.75,
        "thermal": "SUSTAINABLE",
        "arrival_epoch_utc": "2226-08-22T00:00:00+00:00",
        "delta_v_km_s": 1.0,
        "metric_distance_km": 2.0,
        "metric_duration_s": 3.0,
        "metric_beta_c": 0.5,
        "metric_effective_speed_km_s": 4.0,
        "ordinary_departure_speed_km_s": 5.0,
        "torch_burn_s": 6.0,
        "ve_km_s": 7.0,
        "jet_power_TW": 8.0,
        "thrust_MN": 9.0,
        "mdot_kg_s": 10.0,
        "initial_accel_g": 0.1,
        "final_accel_g": 0.2,
        "leg": {"large": "solver payload"},
    }
    view = spike.candidate_public_view(raw)
    assert "leg" not in view
    assert view["metric"] == "FAST"
    assert spike.fingerprint([view]) == spike.fingerprint([dict(reversed(list(view.items())))])


def test_materially_distinct_requires_two_metric_torch_pairs():
    spike = _load_spike()
    assert not spike.materially_distinct([
        {"metric": "FAST", "torch": "CRUISE"},
        {"metric": "FAST", "torch": "CRUISE"},
    ])
    assert spike.materially_distinct([
        {"metric": "FAST", "torch": "CRUISE"},
        {"metric": "EXPEDITE", "torch": "HARD"},
    ])


def test_campaign_hashes_detects_no_files_without_creating_anything(tmp_path):
    spike = _load_spike()
    before = set(tmp_path.iterdir())
    hashes = spike.campaign_hashes(tmp_path)
    after = set(tmp_path.iterdir())
    assert before == after == set()
    assert all(value is None for value in hashes.values())
