import json,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
B=R/'dev/solar_baseline_02_wgccre/LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
P=R/'dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3'
class T(unittest.TestCase):
 def test_contract_uses_existing_ddl(self):
  p=subprocess.run([sys.executable,str(R/'dev/solar_civprop_resource_contract/audit_contract.py'),str(B),str(P)],capture_output=True,text=True,check=True)
  d=json.loads(p.stdout); self.assertTrue(d['existing_material_ddl_satisfies_contract']); self.assertEqual(d['ddl_decision'],'NO_NEW_MATERIAL_TABLE_REQUIRED')
 def test_view_preserves_unknown(self):
  src=sqlite3.connect(P); tmp=sqlite3.connect(':memory:'); src.backup(tmp)
  tmp.executescript((R/'dev/solar_civprop_resource_contract/RESOURCE_STATE_CONTRACT_V1.sql').read_text())
  n=tmp.execute("select count(*) from civprop_material_state_v1 where abundance_semantics='UNKNOWN' and civprop_resource_state='UNKNOWN'").fetchone()[0]
  self.assertEqual(n,6)
if __name__=='__main__': unittest.main()
