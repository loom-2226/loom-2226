import copy
import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loom.navigation.contracts import ContractError, NavigationContext, NavigationRequest, RouteCandidate
from loom.navigation.service import LegacyNavigationService


class FakeSequenceH:
    def validate_and_normalize_mission(self, mission):
        mission = dict(mission)
        mission["route"] = list(mission["route"])
        return mission

    def target_determinism_gate(self, normalized, acq, cache, b1):
        runtime = {
            "flight": {
                "flight_id": "F-TEST",
                "final_epoch_utc": "2226-01-02T00:00:00Z",
                "mass_ledger": {
                    "final_remass_t": 244.5,
                    "final_wet_mass_t": 994.5,
                    "total_remass_used_t": 5.5,
                },
                "legs": [
                    {
                        "kind": "DIRECT",
                        "arrival": {"target_state_source_units": "KM-S"},
                    }
                ],
            }
        }
        return (
            runtime,
            {"ok": True},
            "<html></html>",
            {"pass": True},
            {"stable": True, "canonical_runtime_sha256": "runtime-hash"},
        )

    def build_canonical_dependency_index(self, acquisition, cache):
        return {"time_axis": ["2226-01-01T00:00:00Z"], "opaque": acquisition}, {"axis": "PASS"}


class FakeCore:
    def _load_core(self, internal):
        return FakeSequenceH()

    def _candidate_plans(self, nav, normalized, acq, cache, state, priority):
        self.seen = (normalized, acq, cache, state, priority)
        return [
            {
                "metric": "EXPEDITE",
                "torch": "PRECISION_COLLAPSE",
                "arrival_epoch_utc": "2226-01-02T00:00:00Z",
                "arrival_remass_t": 244.5,
            }
        ]

    def _deepcopy(self, value):
        return copy.deepcopy(value)

    def _validate_state(self, state):
        if "revision" not in state:
            raise RuntimeError("revision missing")

    def _stamp_state(self, state, revision):
        out = copy.deepcopy(state)
        out["revision"] = revision
        out["state_id"] = f"S{revision}"
        out["state_sha256"] = f"hash-{revision}"
        return out


class ContractsTest(unittest.TestCase):
    def test_request_generates_legacy_mission_without_losing_payload(self):
        req = NavigationRequest("CERES", "MARS", payload={"cargo": 7})
        mission = req.to_legacy_mission()
        self.assertEqual(mission["route"], ["CERES", "MARS"])
        self.assertEqual(mission["cargo"], 7)

    def test_timezone_required(self):
        with self.assertRaises(ContractError):
            RouteCandidate("R1", "CERES", "MARS", arrival_epoch="2226-01-02T00:00:00")


class LegacyServiceTest(unittest.TestCase):
    def setUp(self):
        self.core = FakeCore()
        self.service = LegacyNavigationService(self.core)
        self.tmp = tempfile.TemporaryDirectory()
        self.ctx = NavigationContext(
            campaign_state={
                "epoch_utc": "2226-01-01T00:00:00Z",
                "revision": 1,
                "state_id": "S1",
                "state_sha256": "abc",
                "location_token": "CERES",
                "status": "DOCKED",
                "ship": {"wet_mass_t": 1000.0, "remass_t": 250.0},
            },
            acquisition="ACQ",
            cache_dir=Path(self.tmp.name) / "cache",
            b1_package="B1",
            runtime_root=self.tmp.name,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_discover_routes_delegates_to_legacy_candidate_plans(self):
        req = NavigationRequest("CERES", "MARS", priority="fast")
        rows = self.service.discover_routes(req, self.ctx)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].origin, "CERES")
        self.assertEqual(rows[0].destination, "MARS")
        self.assertEqual(rows[0].arrival_epoch, "2226-01-02T00:00:00Z")
        self.assertEqual(self.core.seen[-1], "FAST")

    def test_plan_flight_runs_existing_determinism_gate(self):
        req = NavigationRequest("CERES", "MARS")
        plan = self.service.plan_flight(req, self.ctx)
        self.assertEqual(plan.flight_id, "F-TEST")
        self.assertEqual(plan.payload["runtime"]["flight"]["legs"][0]["kind"], "DIRECT")

    def test_ephemeris_snapshot_delegates_to_sequence_h_canonical_index(self):
        snap = self.service.get_ephemeris(self.ctx)
        self.assertEqual(snap.epoch_utc, "2226-01-01T00:00:00Z")
        self.assertEqual(snap.payload["provider"], "LEGACY_SEQUENCE_H_CANONICAL")
        self.assertEqual(snap.payload["axis_validation"], {"axis": "PASS"})
        self.assertEqual(snap.payload["canonical_dependency_index"]["opaque"], "ACQ")

    def test_execute_flight_returns_arrival_without_mutating_campaign_context(self):
        original = copy.deepcopy(dict(self.ctx.campaign_state))
        plan = self.service.plan_flight(NavigationRequest("CERES", "MARS"), self.ctx)
        result = self.service.execute_flight(plan, self.ctx)
        self.assertEqual(result.status, "ARRIVED_HOLD")
        self.assertEqual(result.final_state["location_token"], "MARS")
        self.assertEqual(result.final_state["epoch_utc"], "2226-01-02T00:00:00Z")
        self.assertEqual(result.final_state["ship"]["remass_t"], 244.5)
        self.assertEqual(result.final_state["last_flight"]["runtime_sha256"], "runtime-hash")
        self.assertEqual(result.payload["persistence_owner"], "CAMPAIGN")
        self.assertEqual(dict(self.ctx.campaign_state), original)

    def test_execute_accepts_route_scoped_runtime_digest_alias(self):
        plan = self.service.plan_flight(NavigationRequest("CERES", "MARS"), self.ctx)
        plan.payload["determinism"] = {"runtime_sha256": "route-scoped-hash"}
        result = self.service.execute_flight(plan, self.ctx)
        self.assertEqual(result.final_state["last_flight"]["runtime_sha256"], "route-scoped-hash")
        self.assertEqual(result.payload["runtime_sha256"], "route-scoped-hash")


if __name__ == "__main__":
    unittest.main()
