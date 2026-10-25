from __future__ import annotations

import hashlib
import json
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "qualification" / "e1_flight_runtime_determinism.py"
spec = importlib.util.spec_from_file_location("e1_flight_runtime_determinism", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FakeWorkflowError(RuntimeError):
    pass


class FakeCore:
    WorkflowError = FakeWorkflowError

    def __init__(self):
        self.calls = 0
        self.target_determinism_gate = lambda *a, **k: (_ for _ in ()).throw(AssertionError("original gate called"))

    @staticmethod
    def canonical_json_bytes(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @staticmethod
    def sha256_bytes(value):
        return hashlib.sha256(value).hexdigest()

    def solve_sequence_a(self, normalized, acquisition, cache_dir):
        self.calls += 1
        return {"mission": normalized, "flight": {"id": "F1"}, "ephemeris": acquisition}, {"status": "PASS"}


def test_runtime_gate_runs_authoritative_solver_twice_and_passes():
    core = FakeCore()
    mod.install_flight_runtime_determinism(core)
    runtime, payloads, html, validation, det = core.target_determinism_gate(
        {"route": ["CERES", "NEPTUNE_SYSTEM"]}, {"entries": [1, 2]}, Path("."), Path("b1.zip")
    )
    assert core.calls == 2
    assert runtime["flight"]["id"] == "F1"
    assert payloads == {}
    assert "presentation is explicitly out of scope" in html
    assert validation["status"] == "PASS"
    assert validation["presentation"] == "OUT_OF_SCOPE_SEQUENCE_B_C_D"
    assert det["status"] == "PASS"
    assert det["checks"]["canonical_runtime_hash"] is True


def test_runtime_gate_fails_closed_on_divergent_runtime():
    core = FakeCore()

    def divergent(normalized, acquisition, cache_dir):
        core.calls += 1
        return {"flight": {"solve": core.calls}}, {"status": "PASS"}

    core.solve_sequence_a = divergent
    mod.install_flight_runtime_determinism(core)
    try:
        core.target_determinism_gate({}, {}, Path("."), Path("b1.zip"))
    except FakeWorkflowError as exc:
        assert "runtime hashes differ" in str(exc)
    else:
        raise AssertionError("divergent authoritative runtime passed determinism gate")


def test_install_is_idempotent():
    core = FakeCore()
    mod.install_flight_runtime_determinism(core)
    installed = core.target_determinism_gate
    mod.install_flight_runtime_determinism(core)
    assert core.target_determinism_gate is installed
