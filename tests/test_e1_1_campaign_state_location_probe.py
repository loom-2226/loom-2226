from __future__ import annotations

import json
from pathlib import Path

import importlib.util


MODULE = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_campaign_state_location_probe.py"
spec = importlib.util.spec_from_file_location("campaign_state_location_probe", MODULE)
assert spec and spec.loader
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def test_probe_is_read_only_and_non_authoritative():
    raw = json.dumps({"location": "CERES", "authority": {"python": "AUTHORITATIVE"}}).encode()
    out = probe.build_probe(raw, Path("LOOM_STATE_V1.json"))
    assert out["authority"]["read_only"] is True
    assert out["authority"]["model_call"] is False
    assert out["authority"]["state_authority"] == "NONE"
    assert out["authority"]["campaign_mutation"] is False


def test_probe_finds_location_related_scalar_paths():
    raw = json.dumps(
        {
            "campaign": {"epoch_utc": "2226-01-01T00:00:00Z"},
            "ship": {"kinematic_boundary": {"status": "BODY_RENDEZVOUS"}},
            "other": {"note": "ignore me"},
        }
    ).encode()
    out = probe.build_probe(raw, Path("state.json"))
    paths = {x["path"] for x in out["location_candidate_fields"]}
    assert "$.campaign.epoch_utc" in paths
    assert "$.ship.kinematic_boundary.status" in paths
    assert "$.other.note" not in paths


def test_probe_hashes_exact_source_bytes():
    raw = b'{"location":"CERES"}'
    out1 = probe.build_probe(raw, Path("a.json"))
    out2 = probe.build_probe(raw, Path("b.json"))
    assert out1["source"]["sha256"] == out2["source"]["sha256"]


def test_probe_rejects_non_object_root():
    try:
        probe.build_probe(b"[]", Path("bad.json"))
    except ValueError as exc:
        assert "root" in str(exc)
    else:
        raise AssertionError("expected ValueError")
