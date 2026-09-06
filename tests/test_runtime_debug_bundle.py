import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from loom_debug_bundle import build_bundle


class RuntimeDebugBundleTest(unittest.TestCase):
    def test_bundle_captures_split_roots_without_mutating_campaign(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); app=root/'runtime'; data=root/'data'; campaign=root/'campaign'; audit=root/'audit'
            (app/'src/loom').mkdir(parents=True); data.mkdir(); (campaign/'logs').mkdir(parents=True); audit.mkdir()
            (app/'src/loom_gis.py').write_text('x=1\n',encoding='utf-8')
            (app/'src/loom/runtime.py').write_text('x=1\n',encoding='utf-8')
            (app/'src/loom/campaign').mkdir(parents=True)
            (app/'src/loom/campaign/execution.py').write_text('x=1\n',encoding='utf-8')
            state={'state_id':'S9','revision':9,'epoch_utc':'2226-01-01T00:00:00Z','location_token':'CERES','last_flight':{'flight_id':'F9'}}
            state_path=campaign/'LOOM_STATE_V1.json'; state_path.write_text(json.dumps(state),encoding='utf-8')
            (campaign/'LOOM_CAMPAIGN_HISTORY.jsonl.gz').write_bytes(b'history')
            (campaign/'logs/loom-trace.jsonl').write_text('{"trace":"ok"}\n',encoding='utf-8')
            (app/'LOOM_PHASE6_HTTP_20260906_000000.log').write_text('HTTP OK\n',encoding='utf-8')
            (root/'cache/LOOM_Navigator_Cache_v1').mkdir(parents=True)
            before=state_path.read_bytes()
            out=build_bundle(app_root=app,data_root=data,campaign_root=campaign,output=root/'debug.zip')
            self.assertEqual(state_path.read_bytes(),before)
            self.assertTrue(out.is_file())
            with zipfile.ZipFile(out) as z:
                names=set(z.namelist())
                self.assertTrue({'summary.json','diagnostics.json','runtime_audit.txt','campaign_state.json','logs/latest_http_tail.log','logs/trace_tail.jsonl'}.issubset(names))
                diag=json.loads(z.read('diagnostics.json'))
                self.assertEqual(diag['campaign']['state']['revision'],9)
                self.assertEqual(diag['campaign']['state']['location_token'],'CERES')
                self.assertEqual(diag['campaign']['navigator_cache']['root'],'cache_root')
                self.assertTrue(diag['campaign']['navigator_cache']['exists'])


if __name__=='__main__':unittest.main()
