from __future__ import annotations
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from loom.gis.flight_planning import GISFlightPlanningSession
from loom.navigation import FlightExecutionResult, FlightPlan, NavigationContext, RouteCandidate
from loom.navigation.route_layer import LoomRouteLayerV1, RouteLayerBodyV1, RouteLayerSegmentV1

class _Nav:
    def prepare_context(self, request, context, *, offline=False, refresh=False): return context
    def discover_routes(self, request, context): return (RouteCandidate("R1",request.origin,request.destination,departure_epoch="2226-01-01T00:00:00Z",arrival_epoch="2226-01-02T00:00:00Z",payload={}),)
    def compile_flight(self, request, candidate, context): return FlightPlan("F1",candidate,payload={})
    def get_route_layer(self, plan, context):
        c=plan.candidate
        return LoomRouteLayerV1(route_id=c.route_id,flight_id=plan.flight_id,origin=c.origin,destination=c.destination,departure_epoch=c.departure_epoch,arrival_epoch=c.arrival_epoch,strategy=c.strategy,status="PLANNED",segments=(RouteLayerSegmentV1(type="METRIC",end_epoch=c.arrival_epoch,end_position={"position_km":[1,2,3]}),),bodies=(RouteLayerBodyV1(c.origin,"ORIGIN"),RouteLayerBodyV1(c.destination,"DESTINATION")),current_vehicle_state=context.campaign_state,arrival_state={"location":c.destination,"epoch_utc":c.arrival_epoch})
    def execute_flight(self, plan, context):
        after=copy.deepcopy(dict(context.campaign_state)); after.update(state_id="S2",revision=2,location_token="MARS",epoch_utc="2226-01-02T00:00:00Z")
        return FlightExecutionResult(plan.flight_id,"ARRIVED_HOLD",after,{"persistence_owner":"CAMPAIGN"})

class _Campaign:
    def __init__(self): self.calls=0
    def commit_flight(self, plan, execution, context):
        self.calls+=1
        return SimpleNamespace(flight_id=plan.flight_id,state_before_id="S1",state_after_id="S2",revision_before=1,revision_after=2,origin="CERES",destination="MARS",departure_epoch_utc="2226-01-01T00:00:00Z",arrival_epoch_utc="2226-01-02T00:00:00Z",remass_before_t=250.0,remass_after_t=245.0,state_path="state.json",history_path="history.gz",history_record_number=1,history_record_sha256="abc",final_state=execution.final_state,to_dict=lambda:{"flight_id":"F1","revision_after":2})

class GISCampaignShadowWriteTest(unittest.TestCase):
    def _session(self):
        before={"state_id":"S1","revision":1,"epoch_utc":"2226-01-01T00:00:00Z","location_token":"CERES","ship":{"remass_t":250.0}}
        campaign=_Campaign(); session=GISFlightPlanningSession(_Nav(),NavigationContext(before,runtime_root="."),offline=True,campaign_execution_service=campaign); session.discover("MARS"); session.preview("R1"); session.commit("R1"); return session,campaign

    @patch("loom.gis.flight_planning.CampaignShadowLedger")
    def test_shadow_write_occurs_only_after_canonical_commit_and_reconciles(self, ledger_cls):
        session,campaign=self._session(); ledger=ledger_cls.return_value; ledger.path="shadow.sqlite3"; ledger.reconcile_commit.return_value={"status":"MATCH","match":True}
        state=session.execute()
        self.assertEqual(campaign.calls,1); ledger.mirror_commit.assert_called_once(); ledger.reconcile_commit.assert_called_once(); self.assertEqual(state.last_execution["shadow_sql"]["status"],"MATCH"); self.assertEqual(state.origin,"MARS")

    @patch("loom.gis.flight_planning.CampaignShadowLedger")
    def test_shadow_failure_cannot_invalidate_canonical_commit_or_arrival(self, ledger_cls):
        session,campaign=self._session(); ledger_cls.return_value.mirror_commit.side_effect=OSError("disk unavailable")
        state=session.execute()
        self.assertEqual(campaign.calls,1); self.assertEqual(state.origin,"MARS"); self.assertEqual(state.last_execution["shadow_sql"]["status"],"ERROR"); self.assertIn("disk unavailable",state.last_execution["shadow_sql"]["error"])

if __name__=="__main__": unittest.main()
