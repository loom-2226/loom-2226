import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loom.navigation.contracts import ContractError, NavigationContext, NavigationRequest, RouteCandidate
from loom.navigation.service import LegacyNavigationService, NavigationServiceError


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
                "legs": [{"kind": "DIRECT"}],
            }
        }
        return runtime, {"ok": True}, "<html></html>", {"pass": True}, {"stable": True}


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
                "state_id": "S1",
                "state_sha256": "abc",
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

    def test_execution_not_duplicated(self):
        with self.assertRaises(NavigationServiceError):
            self.service.execute_flight(None)


if __name__ == "__main__":
    unittest.main()
