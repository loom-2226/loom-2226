from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from loom.navigation.service import (
    NavigationServiceError,
    _is_global_sequence_b_local_completeness_error,
    _route_scoped_dependency_rows,
    _route_scoped_sequence_b_flight_gate,
)


class FakeNav:
    BASE_MAP_OBJECTS = {"SOL": {}, "CE": {}, "MA": {}}
    LOCAL_SYSTEMS = {
        "CE": {"moons": {}},
        "MA": {"moons": {"PH": {}, "DE": {}}},
        "JU": {"moons": {"IO": {}}},
    }

    def __init__(self, *, mismatch=False):
        self.mismatch = mismatch
        self.compile_count = 0

    def _load_rows(self, dep, cache):
        return dep["rows"]

    def _route_parent_system_id(self, token):
        return {"CER": "CE", "MA": "MA"}[token]

    def _median(self, values):
        rows = sorted(values)
        return rows[len(rows) // 2]

    def _local_scale(self, refs, contract):
        return {"mode": "TEST", "reference_count": len(refs)}

    def solve_sequence_a(self, normalized, acquisition, cache):
        runtime = {
            "mission": {"route": ["CER", "MA"]},
            "ephemeris": {
                "time_axis": {"row_count": 2},
                "dependencies": [
                    {"scope": "BASE", "id": "CE", "row_count": 2, "rows": _rows(4.0e8)},
                    {"scope": "BASE", "id": "MA", "row_count": 2, "rows": _rows(2.0e8)},
                    {"scope": "LOCAL", "system_id": "MA", "id": "PH", "row_count": 2, "rows": _rows(10_000.0)},
                    {"scope": "LOCAL", "system_id": "MA", "id": "DE", "row_count": 2, "rows": _rows(20_000.0)},
                    {"scope": "LOCAL", "system_id": "JU", "id": "IO", "row_count": 0},
                ],
            },
            "flight": {"legs": [{"leg_id": "L1"}]},
        }
        return runtime, {"status": "PASS"}

    def load_locked_b1_reference(self, b1_package):
        cams = {"TOP": {"name": "test"}}
        return {
            "contract": {"canvas": {"local": {"max_orbit_radius_px": 100.0}}},
            "reference_ephemeris_meta": {
                "solar_view_modes": {"cameras": cams},
                "local_view_modes": {"cameras": cams},
            },
        }

    def compile_flight_payload(self, runtime, ep_meta, ep_aux, ref):
        self.compile_count += 1
        self.assert_bundle(ep_aux)
        raw = b"authoritative-flight-payload"
        if self.mismatch and self.compile_count == 2:
            raw += b"-different"
        return raw, {}, {"status": "PASS", "payload": "flightSolutionsPayload"}, {}

    def assert_bundle(self, ep_aux):
        assert set(ep_aux["base_rows"]) == {"CE", "MA"}
        assert set(ep_aux["local_rows"]) == {("MA", "PH"), ("MA", "DE")}
        assert "JU" not in ep_aux["local_models"]
        assert set(ep_aux["local_models"]) == {"CE", "MA"}


def _rows(radius):
    return [
        [0.0, radius, 0.0, 0.0, 0.0, 1.0, 0.0],
        [1.0, 0.0, radius, 0.0, -1.0, 0.0, 0.0],
    ]


class RouteScopedSequenceBTest(unittest.TestCase):
    def test_classifier_is_exact_to_global_local_gate(self):
        self.assertTrue(_is_global_sequence_b_local_completeness_error(
            RuntimeError("Sequence B requires direct B1-supported local ephemeris; missing [('JU', 'IO')]")
        ))
        self.assertFalse(_is_global_sequence_b_local_completeness_error(
            RuntimeError("Sequence B requires complete base-map ephemeris; missing ['MA']")
        ))
        self.assertFalse(_is_global_sequence_b_local_completeness_error(RuntimeError("HTTP 503")))

    def test_route_scoped_gate_omits_unrelated_missing_local_and_is_deterministic(self):
        nav = FakeNav()
        with TemporaryDirectory() as td:
            runtime, payloads, html, validation, determinism = _route_scoped_sequence_b_flight_gate(
                nav, {}, {}, Path(td), Path(td) / "b1.zip"
            )
        self.assertEqual(nav.compile_count, 2)
        self.assertEqual(payloads["flightSolutionsPayload"], b"authoritative-flight-payload")
        self.assertEqual(html, "")
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(validation["scope"], "ROUTE_SCOPED_FLIGHT_PAYLOAD_ONLY")
        self.assertEqual(determinism["status"], "PASS")
        self.assertEqual(runtime["mission"]["route"], ["CER", "MA"])

    def test_route_scoped_gate_fails_on_payload_nondeterminism(self):
        nav = FakeNav(mismatch=True)
        with TemporaryDirectory() as td:
            with self.assertRaisesRegex(NavigationServiceError, "flight payload mismatch"):
                _route_scoped_sequence_b_flight_gate(nav, {}, {}, Path(td), Path(td) / "b1.zip")

    def test_base_dependency_remains_fail_closed(self):
        nav = FakeNav()
        runtime, _ = nav.solve_sequence_a({}, {}, Path("."))
        runtime["ephemeris"]["dependencies"] = [
            dep for dep in runtime["ephemeris"]["dependencies"]
            if not (dep.get("scope") == "BASE" and dep.get("id") == "MA")
        ]
        with self.assertRaisesRegex(NavigationServiceError, "complete base ephemeris"):
            _route_scoped_dependency_rows(nav, runtime, Path("."))


if __name__ == "__main__":
    unittest.main()
