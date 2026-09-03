from __future__ import annotations

import copy
import unittest

from loom.gis.flight_planning import GISFlightPlanningError, GISFlightPlanningSession, _candidate_summary
from loom.navigation import NavigationContext, RouteCandidate, FlightPlan
from loom.navigation.route_layer import LoomRouteLayerV1, RouteLayerBodyV1, RouteLayerSegmentV1


class FakeNavigationService:
    def __init__(self):
        self.prepare_calls = 0
        self.discover_calls = 0
        self.compile_calls = 0

    def prepare_context(self, request, context, *, offline=False, refresh=False):
        self.prepare_calls += 1
        return NavigationContext(
            campaign_state=context.campaign_state,
            acquisition={"prepared": True, "offline": offline},
            cache_dir=context.cache_dir,
            b1_package=context.b1_package,
            runtime_root=context.runtime_root,
        )

    def discover_routes(self, request, context):
        self.discover_calls += 1
        return (
            RouteCandidate(
                route_id="R1", origin=request.origin, destination=request.destination,
                departure_epoch="2226-08-22T00:00:00Z", arrival_epoch="2226-08-22T12:00:00Z",
                strategy="PRECISION_COLLAPSE/EXPEDITE",
                payload={"total_minutes":720.0,"stage_remass_t":4.5,"holonomy":0.48,"C_M":0.86,"selectable":True},
            ),
            RouteCandidate(
                route_id="R2", origin=request.origin, destination=request.destination,
                departure_epoch="2226-08-22T00:00:00Z", arrival_epoch="2226-08-22T13:00:00Z",
                strategy="PRECISION_COLLAPSE/FAST",
                payload={"total_minutes":780.0,"stage_remass_t":4.0,"holonomy":0.61,"C_M":0.82,"selectable":True},
            ),
        )

    def compile_flight(self, request, candidate, context):
        self.compile_calls += 1
        return FlightPlan("F1", candidate, payload={})

    def get_route_layer(self, plan, context):
        c = plan.candidate
        return LoomRouteLayerV1(
            route_id=c.route_id, flight_id=plan.flight_id, origin=c.origin, destination=c.destination,
            departure_epoch=c.departure_epoch, arrival_epoch=c.arrival_epoch, strategy=c.strategy, status="PLANNED",
            segments=(RouteLayerSegmentV1(type="METRIC", end_epoch=c.arrival_epoch, end_position={"position_km":[1,2,3]}),),
            bodies=(RouteLayerBodyV1(c.origin,"ORIGIN"),RouteLayerBodyV1(c.destination,"DESTINATION")),
            current_vehicle_state=context.campaign_state,
            arrival_state={"location":c.destination,"epoch_utc":c.arrival_epoch},
        )


class Phase5PlanningTest(unittest.TestCase):
    def setUp(self):
        self.state={"state_id":"S1","epoch_utc":"2226-08-22T00:00:00Z","location_token":"CERES","ship":{"remass_t":200.0}}
        self.original=copy.deepcopy(self.state)
        self.service=FakeNavigationService()
        self.session=GISFlightPlanningSession(
            self.service,
            NavigationContext(campaign_state=self.state,cache_dir="cache",b1_package="b1",runtime_root="root"),
            offline=True,
        )

    def test_discover_is_navigator_delegated_and_read_only(self):
        out=self.session.discover("MARS")
        self.assertEqual(self.service.prepare_calls,1)
        self.assertEqual(self.service.discover_calls,1)
        self.assertEqual(len(out.candidates),2)
        self.assertEqual(out.candidates[0].summary["duration_minutes"],720.0)
        self.assertEqual(out.candidates[0].summary["remass_t"],4.5)
        self.assertEqual(dict(self.session.context.campaign_state),self.original)

    def test_live_direct_candidate_seconds_are_normalized_without_fake_quality_values(self):
        candidate=RouteCandidate(
            route_id="LIVE1",origin="MARS",destination="CERES",
            departure_epoch="2226-09-03T00:00:00Z",arrival_epoch="2226-09-03T08:00:00Z",
            strategy="HARD/CRUISE",
            payload={
                "metric":"HARD","torch":"CRUISE","total_s":28800.0,
                "remass_used_t":11.886,"arrival_remass_t":220.114,
                "thermal":"SUSTAINABLE","leg":{"arrival":{"total_nav_time_s":28800.0}},
            },
        )
        summary=_candidate_summary(candidate)
        self.assertEqual(summary["duration_minutes"],480.0)
        self.assertEqual(summary["remass_t"],11.886)
        self.assertEqual(summary["metric_mode"],"HARD")
        self.assertEqual(summary["torch_mode"],"CRUISE")
        self.assertEqual(summary["thermal_posture"],"SUSTAINABLE")
        self.assertEqual(summary["arrival_remass_t"],220.114)
        self.assertIsNone(summary["holonomy"])
        self.assertIsNone(summary["confidence"])

    def test_preview_compiles_and_emits_phase4_overlay(self):
        self.session.discover("MARS")
        out=self.session.preview("R1")
        self.assertEqual(self.service.compile_calls,1)
        self.assertEqual(out.preview_route_id,"R1")
        self.assertEqual(out.preview_overlay["contract"],"LOOM_GIS_NAVIGATION_OVERLAY_V1")
        self.assertEqual(out.preview_overlay["active_route"]["origin"],"CERES")
        self.assertEqual(dict(self.session.context.campaign_state),self.original)

    def test_commit_only_locks_planning_choice(self):
        self.session.discover("MARS")
        out=self.session.commit("R2")
        self.assertEqual(out.committed_route_id,"R2")
        self.assertEqual(out.preview_route_id,"R2")
        self.assertIsNotNone(self.session.committed_plan())
        self.assertEqual(dict(self.session.context.campaign_state),self.original)

    def test_cancel_clears_preview_and_commit(self):
        self.session.discover("MARS")
        self.session.commit("R1")
        out=self.session.cancel()
        self.assertIsNone(out.preview_route_id)
        self.assertIsNone(out.committed_route_id)
        self.assertIsNone(out.preview_overlay)

    def test_invalid_destination_and_route_fail_closed(self):
        with self.assertRaises(GISFlightPlanningError): self.session.discover("CERES")
        self.session.discover("MARS")
        with self.assertRaises(GISFlightPlanningError): self.session.preview("NOPE")


if __name__ == "__main__":
    unittest.main()
