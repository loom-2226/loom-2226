import copy
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loom.gis.navigation_overlay import (
    GIS_NAV_OVERLAY_VERSION,
    build_navigation_overlay,
    client_extension_js,
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
                    geometry={
                        "mode": "AUTHORITATIVE_SEQUENCE_B_MIXED_GEOMETRY",
                        "coordinate_frame": "J2000_ECLIPTIC",
                        "semantics": "RELATIONAL DISPLACEMENT / NOT ORDINARY-SPACE OCCUPANCY",
                        "ordinary_space_occupancy": False,
                    },
                    phase="METRIC_TRANSIT",
                    payload={"velocity_memory_km_s": [1.0, 2.0, 3.0]},
                ),
                RouteLayerSegmentV1(
                    type="TERMINAL_BURN",
                    start_epoch="2226-01-01T01:40:00Z",
                    end_epoch="2226-01-01T02:00:00Z",
                    geometry={
                        "points": [[1.0e8, 2.0e8, 3.0e6], [1.1e8, 2.1e8, 3.1e6], [1.2e8, 2.2e8, 3.2e6]],
                        "authority": "PYTHON_AUTHORED_SEQUENCE_B",
                        "ordinary_space_occupancy": True,
                    },
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
            payload={
                "trajectory": {
                    "authority": "PYTHON_AUTHORED_SEQUENCE_B",
                    "sample_count": 3,
                    "samples": [
                        {"sample_index": 0, "position_semantics_code": 0, "relational_progress": 0.0},
                        {"sample_index": 1, "position_semantics_code": 1, "ordinary_pos_x_km": 1.1e8, "ordinary_pos_y_km": 2.1e8, "ordinary_pos_z_km": 3.1e6},
                        {"sample_index": 2, "position_semantics_code": 1, "ordinary_pos_x_km": 1.2e8, "ordinary_pos_y_km": 2.2e8, "ordinary_pos_z_km": 3.2e6},
                    ],
                }
            },
        )

    def test_overlay_contract_and_controls(self):
        overlay = build_navigation_overlay(self.route())
        self.assertEqual(overlay.contract, GIS_NAV_OVERLAY_VERSION)
        self.assertIsNotNone(overlay.active_route)
        self.assertEqual(overlay.current_vehicle_state["location_token"], "CERES")
        self.assertIn("ACTIVE_ROUTE", overlay.controls)
        self.assertIn("TRAFFIC_CIVSTATE", overlay.controls)

    def test_symbology_is_owned_by_gis(self):
        src = self.route()
        before = copy.deepcopy(src.to_dict())
        rendered = route_to_gis(src)
        self.assertEqual(src.to_dict(), before)
        self.assertEqual(rendered.segments[0].style["stroke"], "#bda5ff")
        self.assertNotIn("style", src.segments[0].payload)

    def test_metric_route_does_not_invent_polyline(self):
        rendered = route_to_gis(self.route())
        metric = rendered.segments[0]
        self.assertEqual(metric.geometry_points_j2000_ecliptic_km, ())
        self.assertFalse(metric.geometry_semantics["ordinary_space_occupancy"])
        collapse = [a for a in rendered.anchors if a.anchor_type == "METRIC_COLLAPSE"]
        self.assertEqual(len(collapse), 1)
        self.assertEqual(collapse[0].position_j2000_ecliptic_km, (1.0e8, 2.0e8, 3.0e6))

    def test_sampled_geometry_is_passed_through_not_recomputed(self):
        rendered = route_to_gis(self.route())
        terminal = rendered.segments[1]
        self.assertEqual(terminal.geometry_authority, "PYTHON_AUTHORED_SEQUENCE_B")
        self.assertEqual(
            terminal.geometry_points_j2000_ecliptic_km,
            ((1.0e8, 2.0e8, 3.0e6), (1.1e8, 2.1e8, 3.1e6), (1.2e8, 2.2e8, 3.2e6)),
        )
        self.assertEqual(rendered.trajectory["sample_count"], 3)
        self.assertEqual(len(rendered.trajectory["samples"]), 3)

    def test_phase_engineering_values_are_preserved(self):
        rendered = route_to_gis(self.route())
        terminal = rendered.segments[1]
        self.assertEqual(terminal.engineering["dv_km_s"], 12.5)
        self.assertEqual(terminal.engineering["initial_accel_g"], 0.05)
        self.assertEqual(terminal.engineering["final_accel_g"], 0.2)

    def test_historical_overlay_uses_explicit_live_campaign_vehicle_state(self):
        overlay = build_navigation_overlay(
            historical_routes=(self.route(),),
            current_vehicle_state={"location_token": "MARS", "revision": 5},
        )
        self.assertIsNone(overlay.active_route)
        self.assertEqual(overlay.historical_routes[0].role, "HISTORICAL")
        self.assertEqual(overlay.historical_routes[0].current_vehicle_state["location_token"], "CERES")
        self.assertEqual(overlay.current_vehicle_state["location_token"], "MARS")
        js = client_extension_js()
        self.assertIn("navDrawVehicle(navOverlay.current_vehicle_state||{})", "".join(js.split()))

    def test_browser_camera_contract_uses_authoritative_route_envelope(self):
        js = client_extension_js()
        normalized = "".join(js.split())
        self.assertIn("functionnavRouteWorldVectors(route)", normalized)
        self.assertIn("geometry_semantics?.ordinary_space_occupancy!==false", normalized)
        self.assertIn("functionnavRouteNeedsFit(route)", normalized)
        self.assertIn("functionfitNavigationRoute(route)", normalized)
        self.assertIn("functionmaybeAutoFitNavigationRoute()", normalized)
        self.assertIn("FITROUTE", normalized)
        self.assertIn("sessionStorage.getItem('loomNavAutoFitRoute')", normalized)
        self.assertIn("if(alpha>=.75)", normalized)

    def test_empty_overlay_is_valid(self):
        overlay = build_navigation_overlay()
        self.assertIsNone(overlay.active_route)
        self.assertEqual(overlay.alternate_routes, ())
        self.assertEqual(overlay.historical_routes, ())
        self.assertEqual(overlay.current_vehicle_state, {})


if __name__ == "__main__": unittest.main()
