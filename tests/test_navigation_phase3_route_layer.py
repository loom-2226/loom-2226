import copy
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loom.navigation import (
    FlightPlan,
    LegacyRouteLayerAdapter,
    LoomRouteLayerV1,
    NavigationContext,
    RouteCandidate,
    RouteLayerError,
    ROUTE_LAYER_VERSION,
)


class RouteLayerV1Test(unittest.TestCase):
    def setUp(self):
        self.candidate = RouteCandidate(
            route_id="R1",
            origin="CERES",
            destination="MARS",
            departure_epoch="2226-01-01T00:00:00Z",
            arrival_epoch="2226-01-02T00:00:00Z",
            strategy="EXPEDITE/PRECISION_COLLAPSE",
            payload={"metric": "EXPEDITE", "torch": "PRECISION_COLLAPSE"},
        )
        self.runtime_flight = {
            "flight_id": "F1",
            "final_epoch_utc": "2226-01-02T00:00:00Z",
            "mass_ledger": {"final_remass_t": 244.5, "final_wet_mass_t": 994.5},
            "legs": [
                {
                    "kind": "DIRECT",
                    "phases": [
                        {
                            "type": "TORCH",
                            "phase": "DEPARTURE_TORCH",
                            "start_epoch_utc": "2226-01-01T00:00:00Z",
                            "end_epoch_utc": "2226-01-01T01:00:00Z",
                            "start_position_km": [1.0, 2.0, 3.0],
                            "end_position_km": [4.0, 5.0, 6.0],
                            "acceleration_g": 0.05,
                        },
                        {
                            "type": "METRIC",
                            "phase": "METRIC_TRANSIT",
                            "start_epoch_utc": "2226-01-01T01:00:00Z",
                            "end_epoch_utc": "2226-01-01T23:00:00Z",
                            "trajectory": {"frame": "BARYCENTRIC", "points": [[4, 5, 6], [7, 8, 9]]},
                        },
                    ],
                }
            ],
            "waypoints": [{"body_id": "CERES"}, {"body_id": "MARS"}],
            "maneuvers": [{"type": "ARRIVAL_ACQUISITION", "epoch_utc": "2226-01-02T00:00:00Z"}],
        }
        self.plan = FlightPlan(
            flight_id="F1",
            candidate=self.candidate,
            payload={
                "runtime": {"flight": self.runtime_flight},
                "determinism": {"canonical_runtime_sha256": "abc123"},
            },
        )
        self.context = NavigationContext(
            campaign_state={
                "epoch_utc": "2226-01-01T00:00:00Z",
                "location_token": "CERES",
                "status": "DOCKED",
                "ship": {"wet_mass_t": 1000.0, "remass_t": 250.0},
            }
        )

    def test_contract_contains_governing_minimum_fields(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context)
        self.assertEqual(layer.contract, ROUTE_LAYER_VERSION)
        self.assertEqual(layer.route_id, "R1")
        self.assertEqual(layer.flight_id, "F1")
        self.assertEqual(layer.origin, "CERES")
        self.assertEqual(layer.destination, "MARS")
        self.assertEqual(layer.departure_epoch, "2226-01-01T00:00:00Z")
        self.assertEqual(layer.arrival_epoch, "2226-01-02T00:00:00Z")
        self.assertEqual(layer.strategy, "EXPEDITE/PRECISION_COLLAPSE")
        self.assertEqual(len(layer.segments), 2)
        self.assertEqual(len(layer.waypoints), 2)
        self.assertEqual([b.role for b in layer.bodies], ["ORIGIN", "DESTINATION"])
        self.assertEqual(len(layer.maneuvers), 1)
        self.assertEqual(layer.current_vehicle_state["location_token"], "CERES")
        self.assertEqual(layer.arrival_state["location"], "MARS")

    def test_segment_promotes_physics_without_recalculating(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context)
        torch = layer.segments[0]
        self.assertEqual(torch.type, "TORCH")
        self.assertEqual(torch.phase, "DEPARTURE_TORCH")
        self.assertEqual(torch.start_position, {"values": [1.0, 2.0, 3.0]})
        self.assertEqual(torch.end_position, {"values": [4.0, 5.0, 6.0]})
        self.assertEqual(torch.acceleration, {"value": 0.05})
        self.assertEqual(torch.payload["acceleration_g"], 0.05)

    def test_contract_is_display_agnostic(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context).to_dict()
        forbidden = {"color", "colour", "icon", "stroke", "fill", "opacity", "line_width", "symbol", "css"}

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(str(key).lower(), forbidden)
                    walk(child)
            elif isinstance(value, (list, tuple)):
                for child in value:
                    walk(child)

        walk(layer)

    def test_adapter_does_not_mutate_plan_or_campaign_state(self):
        plan_before = copy.deepcopy(dict(self.plan.payload))
        state_before = copy.deepcopy(dict(self.context.campaign_state))
        LegacyRouteLayerAdapter().build(self.plan, self.context)
        self.assertEqual(dict(self.plan.payload), plan_before)
        self.assertEqual(dict(self.context.campaign_state), state_before)

    def test_canonical_hash_is_deterministic(self):
        a = LegacyRouteLayerAdapter().build(self.plan, self.context)
        b = LegacyRouteLayerAdapter().build(self.plan, self.context)
        self.assertEqual(a.sha256(), b.sha256())
        self.assertEqual(a.canonical_json(), b.canonical_json())

    def test_unknown_contract_version_fails_closed(self):
        with self.assertRaises(RouteLayerError):
            LoomRouteLayerV1(
                route_id="R",
                flight_id="F",
                origin="A",
                destination="B",
                departure_epoch=None,
                arrival_epoch=None,
                strategy=None,
                status="PLANNED",
                contract="LOOM_ROUTE_LAYER_V2",
            )


if __name__ == "__main__":
    unittest.main()
