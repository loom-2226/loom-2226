import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'dev/resource_economics/dorrington_olsen/m2/DORRINGTON_OLSEN_CIVPROP_INPUT_CONTRACT.json'
DB=ROOT/'dev/solar_baseline_02_wgccre/LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
class TestM2(unittest.TestCase):
 def test_contract_boundary(self):
  d=json.loads(CONTRACT.read_text())
  self.assertTrue(d['boundary'].startswith('Solar Facts supplies empirical object state.'))
  self.assertTrue(any(x['name']=='resource_presence_and_abundance' for x in d['object_empirical_inputs']))
  self.assertTrue(all(x['sqlite_solar_facts'] is False for x in d['transport_inputs']))
 def test_current_sqlite_assessment_runs(self):
  p=subprocess.run([sys.executable,str(ROOT/'dev/resource_economics/dorrington_olsen/m2/assess_sqlite_readiness.py'),str(DB)],capture_output=True,text=True,check=True)
  d=json.loads(p.stdout)
  self.assertEqual(d['bodies'],110)
  self.assertEqual(d['empirical_object_lanes']['resource_presence_abundance']['assessment'],'BLOCKING_FOR_RESOURCE_SPECIFIC_CIVPROP')
if __name__=='__main__': unittest.main()
