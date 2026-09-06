from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from loom.campaign import CampaignExecutionError, LegacyCampaignExecutionService
from loom.navigation import FlightExecutionResult, FlightPlan, NavigationContext, RouteCandidate


class _Ledger:
    def __init__(self, root, state):
        self.root=Path(root); self.state=state
    def append(self, record_type, state_before, state_after, details=None, flight_id=None, event_epoch_utc=None, state_after_snapshot=None, **kwargs):
        p=self.root/'LOOM_CAMPAIGN_HISTORY.jsonl.gz'
        rec={'record_number':1,'record_type':record_type,'record_sha256':'abc123','flight_id':flight_id}
        p.write_text(json.dumps(rec),encoding='utf-8')
        return rec


class _Core:
    STATE_FILE='LOOM_STATE_V1.json'; BACKUP_FILE='LOOM_STATE_V1.bak'; HISTORY_FILE='LOOM_CAMPAIGN_HISTORY.jsonl.gz'
    HistoryLedger=_Ledger
    loaded_core_path=None
    @staticmethod
    def _validate_state(state):
        for k in ('state_id','revision','epoch_utc','location_token','ship'):
            if k not in state: raise RuntimeError(k)
    @classmethod
    def _load_core(cls,path): cls.loaded_core_path=Path(path); return object()
    @staticmethod
    def _outcome_summary(*args): return {'ok':True}
    @staticmethod
    def _atomic_save(path,bak,state):
        if path.exists(): bak.write_bytes(path.read_bytes())
        path.write_text(json.dumps(state,sort_keys=True),encoding='utf-8')
        return path.stat().st_size


def _state(rev=4,loc='CERES',epoch='2226-08-01T00:00:00Z',sid='S4',remass=250.0):
    return {'state_id':sid,'revision':rev,'epoch_utc':epoch,'location_token':loc,'status':'READY','ship':{'remass_t':remass,'wet_mass_t':1210.0}}


class Phase6CampaignExecutionTest(unittest.TestCase):
    def test_campaign_commit_persists_exact_arrival_once(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); app=base/'runtime'; campaign=base/'campaign'; app.mkdir(); campaign.mkdir()
            before=_state(); (campaign/'LOOM_STATE_V1.json').write_text(json.dumps(before),encoding='utf-8')
            candidate=RouteCandidate('r1','CERES','MARS',payload={})
            plan=FlightPlan('F1',candidate,payload={'runtime':{},'determinism':{'canonical_runtime_sha256':'runsha'},'html':'','plan_sha256':'plansha'})
            after=_state(5,'MARS','2226-08-02T00:00:00Z','S5',240.0)
            after['last_flight']={'flight_id':'F1','departure_state_id':'S4','runtime_sha256':'runsha','committed_plan_sha256':'plansha'}
            execution=FlightExecutionResult('F1','ARRIVED_HOLD',after,{'persistence_owner':'CAMPAIGN'})
            context=NavigationContext(before,runtime_root=app)
            with patch.dict('os.environ',{'LOOM_APP_ROOT':str(app),'LOOM_CAMPAIGN_ROOT':str(campaign)},clear=True):
                result=LegacyCampaignExecutionService(_Core()).commit_flight(plan,execution,context)
            self.assertEqual(result.revision_after,5)
            self.assertEqual(json.loads((campaign/'LOOM_STATE_V1.json').read_text()),after)
            self.assertTrue((campaign/'LOOM_STATE_V1.bak').exists())
            self.assertEqual(result.history_record_sha256,'abc123')
            self.assertEqual(_Core.loaded_core_path,app/'LOOM_Navigator_Internal_SequenceH')

    def test_stale_planning_snapshot_is_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); app=base/'runtime'; campaign=base/'campaign'; app.mkdir(); campaign.mkdir()
            planned=_state(); current=_state(5,'LUNA','2226-08-01T01:00:00Z','S5')
            (campaign/'LOOM_STATE_V1.json').write_text(json.dumps(current),encoding='utf-8')
            candidate=RouteCandidate('r1','CERES','MARS')
            plan=FlightPlan('F1',candidate,payload={})
            execution=FlightExecutionResult('F1','ARRIVED_HOLD',current,{'persistence_owner':'CAMPAIGN'})
            with patch.dict('os.environ',{'LOOM_APP_ROOT':str(app),'LOOM_CAMPAIGN_ROOT':str(campaign)},clear=True):
                with self.assertRaisesRegex(CampaignExecutionError,'changed after planning'):
                    LegacyCampaignExecutionService(_Core()).commit_flight(plan,execution,NavigationContext(planned,runtime_root=app))
            self.assertFalse((campaign/'LOOM_CAMPAIGN_HISTORY.jsonl.gz').exists())


if __name__=='__main__': unittest.main()
