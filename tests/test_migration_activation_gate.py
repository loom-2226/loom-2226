import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('loom_migrate_activation',ROOT/'deploy/loom_migrate.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class ActivationGateTest(unittest.TestCase):
    def test_activate_requires_authoritative_runtime_data_and_campaign_files(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); source=base/'source'; target=base/'target'; source.mkdir(); target.mkdir()
            plan={'contract':m.CONTRACT,'source_root':str(source),'target_root':str(target),'unknown_count':0,'items':[]}
            with self.assertRaisesRegex(RuntimeError,'authoritative root files missing'):
                m.activate(plan)

    def test_activate_writes_contract_after_required_files_exist(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); source=base/'source'; target=base/'target'; source.mkdir(); target.mkdir()
            for p in [target/'runtime/src/loom_gis.py',target/'runtime/src/loom_navigator.py',target/'data/LOOM_2226.sqlite3',target/'data/LOOM_2226_CIVSTATE.sqlite3',target/'campaign/LOOM_STATE_V1.json',target/'campaign/LOOM_CAMPAIGN_HISTORY.jsonl.gz']:
                p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b'x')
            plan={'contract':m.CONTRACT,'source_root':str(source),'target_root':str(target),'unknown_count':0,'items':[]}
            result=m.activate(plan)
            self.assertEqual(result['roots']['app_root'],str((target/'runtime').resolve()))
            self.assertEqual(result['roots']['data_root'],str((target/'data').resolve()))
            self.assertEqual(result['roots']['campaign_root'],str((target/'campaign').resolve()))
            self.assertEqual(len(result['required_files_verified']),6)
            self.assertTrue((target/'audit/runtime_roots.json').exists())

    def test_activate_allows_qualified_application_replacement_but_not_campaign_drift(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); source=base/'source'; target=base/'target'; source.mkdir()
            (source/'src').mkdir(); (source/'src/loom_gis.py').write_text('legacy gis'); (source/'src/loom_navigator.py').write_text('legacy nav')
            (source/'LOOM_STATE_V1.json').write_text('{"revision":1}'); (source/'LOOM_CAMPAIGN_HISTORY.jsonl.gz').write_bytes(b'history')
            plan=m.audit(source,target); m.stage(plan)
            (target/'runtime/src/loom_gis.py').write_text('qualified converged gis')
            (target/'runtime/src/loom_navigator.py').write_text('qualified converged nav')
            (target/'data').mkdir(parents=True,exist_ok=True); (target/'data/LOOM_2226.sqlite3').write_bytes(b'world'); (target/'data/LOOM_2226_CIVSTATE.sqlite3').write_bytes(b'civ')
            result=m.activate(plan)
            self.assertTrue(result['validation']['valid']); self.assertIn('application',result['validation']['excluded_classes']); self.assertEqual(result['validation']['skipped_files'],2)
            (target/'campaign/LOOM_STATE_V1.json').write_text('{"revision":2}')
            with self.assertRaisesRegex(RuntimeError,'not fully staged and validated'):
                m.activate(plan)

if __name__=='__main__':unittest.main()
