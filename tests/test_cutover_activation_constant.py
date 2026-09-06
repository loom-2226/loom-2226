import importlib.util,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location('migrate_const',R/'deploy/loom_migrate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Contract(unittest.TestCase):
 def test_contract(self):self.assertEqual(m.ACTIVATION_CONTRACT,'LOOM_RUNTIME_ROOTS_ACTIVATION_V1')
if __name__=='__main__':unittest.main()
