import csv,json,subprocess,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; M=R/'dev/solar_civprop_resource_contract/M4A_POPULATION_MANIFEST_V1.json'; DB=R/'dev/solar_baseline_02_wgccre/LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
class T(unittest.TestCase):
 def test_manifest_is_finite_and_firewalled(self):
  d=json.loads(M.read_text()); self.assertEqual(len(d['required_questions']),4); self.assertIn('UNKNOWN_AFTER_SEARCH',d['coverage_dispositions']); self.assertIn('100 percent coverage accounting',d['success_metric']); self.assertNotIn('SPACECRAFT',d['eligibility']['included_body_classes'])
 def test_queue_is_exact_cartesian_product_of_eligible_bodies_and_four_questions(self):
  p=subprocess.run([sys.executable,str(R/'dev/solar_civprop_resource_contract/build_m4a_queue.py'),str(M),str(DB)],capture_output=True,text=True,check=True)
  rows=list(csv.DictReader(p.stdout.splitlines())); bodies={x['body_id'] for x in rows}
  self.assertEqual(len(rows),len(bodies)*4); self.assertEqual({x['resource_family'] for x in rows},{'VOLATILES','METALS','SILICATES_ROCK','CARBONACEOUS_ORGANICS'})
  self.assertTrue(all(x['initial_disposition']=='UNASSESSED' for x in rows))
if __name__=='__main__': unittest.main()
