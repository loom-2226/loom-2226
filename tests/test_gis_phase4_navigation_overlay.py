import copy
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loom.gis.navigation_overlay import (
    GIS_NAV_OVERLAY_VERSION,
    build_navigation_overlay,
    route_to_gis,
)
from loom.navigation import LoomRouteLayerV1, RouteLayerBodyV1, RouteLayerSegmentV1


class GISPhase4NavigationOverlayTest(unittest.TestCase):
    def route(self):
        return LoomRouteLayerV1(
            route_id="R1",
            flight_id="F1",
            origin="CERES",
            destination="MARS",
            departure_epoch="2226-01-01T00:00:00Z",
            arrival_epoch="2226-01-01T02:00:00Z",
            strategy="EXPEDITE/PRECISION_COLLAPSE",
            status="PLANNED",
            segments=(
                RouteLayerSegmentV1(
                    type="METRIC",
                    start_epoch="2226-01-01T00:20:00Z",
                    end_epoch="2226-01-01T01:40:00Z",
                    end_position={"values": [1.0e8, 2.0e8, 3.0e6]},
                    phase="METRIC_TRANSIT",
                    payload={"velocity_memory_km_s": [1.0, 2.0, 3.0]},
                ),
                RouteLayerSegmentV1(
                    type="TERMINAL_BURN",
                    start_epoch="2226-01-01T01:40:00Z",
                    end_epoch="2226-01-01T02:00:00Z",
                    phase="TERMINAL_BURN",
                    payload={"dv_km_s": 12.5, "initial_accel_g": 0.05, "final_accel_g": 0.2},
                ),
            ),
            bodies=(RouteLayerBodyV1("CERES", role="ORIGIN"), RouteLayerBodyV1("MARS", role="DESTINATION")),
            maneuvers=(
                {"type": "METRIC_COLLAPSE", "epoch_utc": "2226-01-01T01:40:00Z"},
                {"type": "TERMINAL_BURN", "epoch_utc": "2226-01-01T01:40:00Z"},
            ),
            current_vehicle_state={"location_token": "CERES", "epoch_utc": "2226-01-01T00:00:00Z"},
            arrival_state={"location": "MARS", "epoch_utc": "2226-01-01T02:00:00Z"},
        )

    def test_overlay_contract_and_controls(self):
        overlay = build_navigation_overlay(self.route())
        self.assertEqual(overlay.contract, GIS_NAV_OVERLAY_VERSION)
        self.assertIsNotNone(overlay.active_route)
        self.assertIn("ACTIVE_ROUTE", overlay.controls)
        self.assertIn("TRAFFIC_CIVSTATE", overlay.controls)

    def test_symbology_is_owned_by_gis(self):
        src = self.route()
        before = copy.deepcopy(src.to_dict())
        rendered = route_to_gis(src)
        self.assertEqual(src.to_dict(), before)
        self.assertEqual(rendered.segments[0].style["stroke"], "#bda5ff")
        self.assertNotIn("style", src.segments[0].payload)

    def test_unsampled_route_does_not_invent_polyline(self):
        rendered = route_to_gis(self.route())
        metric = rendered.segments[0]
        self.assertEqual(metric.geometry_points_j2000_ecliptic_km, ())
        self.assertEqual(metric.geometry_authority, "AUTHORITATIVE_PHASE_ANCHORS_ONLY")
        collapse = [a for a in rendered.anchors if a.anchor_type == "METRIC_COLLAPSE"]
        self.assertEqual(len(collapse), 1)
        self.assertEqual(collapse[0].position_j2000_ecliptic_km, (1.0e8, 2.0e8, 3.0e6))

    def test_sampled_geometry_is_passed_through_not_recomputed(self):
        src = self.route()
        sampled = RouteLayerSegmentV1(
            type="COAST",
            start_epoch="2226-01-01T00:00:00Z",
            end_epoch="2226-01-01T00:10:00Z",
            geometry={"points": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
            phase="COAST",
        )
        src2 = LoomRouteLayerV1(
            route_id=src.route_id, flight_id=src.flight_id, origin=src.origin, destination=src.destination,
            departure_epoch=src.departure_epoch, arrival_epoch=src.arrival_epoch, strategy=src.strategy,
            status=src.status, segments=(sampled,), waypoints=src.waypoints, bodies=src.bodies,
            maneuvers=src.maneuvers, current_vehicle_state=src.current_vehicle_state,
            arrival_state=src.arrival_state, payload=src.payload,
        )
        rendered = route_to_gis(src2)
        self.assertEqual(rendered.segments[0].geometry_authority, "AUTHORITATIVE_SAMPLED_GEOMETRY")
        self.assertEqual(rendered.segments[0].geometry_points_j2000_ecliptic_km, ((1.0,2.0,3.0),(4.0,5.0,6.0),(7.0,8.0,9.0)))

    def test_phase_engineering_values_are_preserved(self):
        rendered = route_to_gis(self.route())
        terminal = rendered.segments[1]
        self.assertEqual(terminal.engineering["dv_km_s"], 12.5)
        self.assertEqual(terminal.engineering["initial_accel_g"], 0.05)
        self.assertEqual(terminal.engineering["final_accel_g"], 0.2)

    def test_empty_overlay_is_valid(self):
        overlay = build_navigation_overlay()
        self.assertIsNone(overlay.active_route)
        self.assertEqual(overlay.alternate_routes, ())
        self.assertEqual(overlay.historical_routes, ())


if __name__ == "__main__":
    unittest.main()
