import copy
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loom.navigation import (
    FlightPlan,
    GEOMETRY_MODE,
    LegacyRouteLayerAdapter,
    LoomRouteLayerV1,
    NavigationContext,
    RouteCandidate,
    RouteLayerError,
    ROUTE_LAYER_VERSION,
)


class RouteLayerV1Test(unittest.TestCase):
    def setUp(self):
        self.collapse = [123.0, 456.0, 789.0]
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
            "final_epoch_utc": "2226-01-02T00:00:00Z",
            "model": "NAV-V1-A",
            "model_status": "QUALIFIED",
            "mass_ledger": {"final_remass_t": 244.5, "final_wet_mass_t": 994.5},
            "legs": [
                {
                    "leg_id": "L1",
                    "origin_id": "CERES",
                    "destination_id": "MARS",
                    "departure_epoch_utc": "2226-01-01T00:00:00Z",
                    "metric_mode": "EXPEDITE",
                    "torch_mode": "PRECISION_COLLAPSE",
                    "metric_segment": {
                        "beta_c": 0.42,
                        "collapse_epoch_utc": "2226-01-01T23:30:00Z",
                        "collapse_position_km_j2000_ecliptic": self.collapse,
                        "distance_km": 123456.0,
                        "duration_s": 84600.0,
                        "ramp_s": 120.0,
                        "semantics": "PRECISION_COLLAPSE",
                    },
                    "ordinary_velocity_memory": {
                        "collapse_velocity_km_s": [1.0, 2.0, 3.0],
                        "acquisition_velocity_km_s": [0.1, 0.2, 0.3],
                        "frame": "J2000_ECLIPTIC",
                        "status": "VALID",
                    },
                    "engineering_checkpoints": [
                        {
                            "fraction": 0.5,
                            "epoch_utc": "2226-01-01T12:00:00Z",
                            "accel_g": 0.05,
                            "wet_mass_t": 997.0,
                        }
                    ],
                    "terminal_burn": {
                        "burn_s": 1800.0,
                        "delta_v_km_s": 4.25,
                        "delta_v_vec_km_s": [4.0, 1.0, 0.5],
                        "initial_accel_g": 0.03,
                        "final_accel_g": 0.02,
                        "remass_used_t": 5.5,
                        "thrust_MN": 2.1,
                    },
                    "arrival": {
                        "epoch_utc": "2226-01-02T00:00:00Z",
                        "ship_position_residual_km": 0.0,
                        "ship_velocity_residual_km_s": 0.0,
                        "total_nav_time_s": 86400.0,
                    },
                }
            ],
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
                "last_flight": None,
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
        self.assertEqual([s.type for s in layer.segments], ["METRIC", "TERMINAL_BURN"])
        self.assertEqual(len(layer.waypoints), 0)
        self.assertEqual([b.role for b in layer.bodies], ["ORIGIN", "DESTINATION"])
        self.assertEqual([m["type"] for m in layer.maneuvers], ["METRIC_COLLAPSE", "TERMINAL_BURN"])
        self.assertEqual(layer.current_vehicle_state["location_token"], "CERES")
        self.assertEqual(layer.arrival_state["location"], "MARS")
        self.assertEqual(layer.payload["geometry_mode"], GEOMETRY_MODE)

    def test_metric_segment_promotes_authoritative_collapse_anchor(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context)
        metric = layer.segments[0]
        self.assertEqual(metric.type, "METRIC")
        self.assertEqual(metric.start_epoch, "2226-01-01T00:00:00Z")
        self.assertEqual(metric.end_epoch, "2226-01-01T23:30:00Z")
        self.assertEqual(metric.end_position["coordinate_frame"], "J2000_ECLIPTIC")
        self.assertEqual(metric.end_position["position_km"], self.collapse)
        self.assertEqual(metric.geometry["mode"], GEOMETRY_MODE)
        self.assertEqual(metric.geometry["collapse_position_km"], self.collapse)
        self.assertEqual(metric.velocity["collapse_velocity_km_s"], [1.0, 2.0, 3.0])
        self.assertEqual(metric.acceleration["engineering_checkpoints"][0]["accel_g"], 0.05)
        self.assertEqual(metric.payload["metric_segment"]["beta_c"], 0.42)

    def test_terminal_burn_preserves_dv_and_acceleration(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context)
        terminal = layer.segments[1]
        self.assertEqual(terminal.type, "TERMINAL_BURN")
        self.assertEqual(terminal.phase, "ARRIVAL_ACQUISITION")
        self.assertEqual(terminal.start_epoch, "2226-01-01T23:30:00Z")
        self.assertEqual(terminal.end_epoch, "2226-01-02T00:00:00Z")
        self.assertEqual(terminal.start_position["position_km"], self.collapse)
        self.assertEqual(terminal.velocity["delta_v_km_s"], 4.25)
        self.assertEqual(terminal.acceleration["initial_accel_g"], 0.03)
        self.assertEqual(terminal.acceleration["final_accel_g"], 0.02)
        self.assertEqual(terminal.payload["terminal_burn"]["remass_used_t"], 5.5)

    def test_no_sampled_track_is_invented(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context)
        for segment in layer.segments:
            self.assertNotIn("points", segment.geometry)
            self.assertNotIn("polyline", segment.geometry)
            self.assertNotIn("sampled_track", segment.geometry)
        self.assertEqual(layer.payload["geometry_mode"], "AUTHORITATIVE_PHASE_ANCHORS_ONLY")

    def test_null_prior_flight_is_valid_departure_state(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context)
        self.assertEqual(layer.status, "PLANNED")
        self.assertIsNone(layer.current_vehicle_state["last_flight"])

    def test_contract_is_display_agnostic(self):
        layer = LegacyRouteLayerAdapter().build(self.plan, self.context).to_dict()
        forbidden = {"color", "colour", "icon", "stroke", "fill", "opacity", "line_width", "symbol", "css", "style", "symbology"}

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
