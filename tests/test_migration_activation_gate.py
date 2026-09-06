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

if __name__=='__main__':unittest.main()
