import subprocess,unittest
from engineering.civprop.contracts.gate_l_postgres_runtime_v0_3 import SCHEMA,TABLES,qualification_invariants
class GateL(unittest.TestCase):
 @staticmethod
 def q(sql):
  return subprocess.check_output(["psql","-X","-At","-v","ON_ERROR_STOP=1","-d","loom_dev","-c",sql],text=True).strip()
 def test_schema_isolated(self): self.assertEqual(self.q("select count(*) from information_schema.tables where table_schema='loom_gate_l_qual'"),"4")
 def test_expected_tables(self):
  got=tuple(self.q("select table_name from information_schema.tables where table_schema='loom_gate_l_qual' order by table_name").splitlines()); self.assertEqual(got,tuple(sorted(TABLES)))
 def test_durable_state_visible_new_connection(self): self.assertEqual(self.q("select value::text from loom_gate_l_qual.runtime_state where key='budget:NASA'"),"30")
 def test_transaction_durable(self): self.assertEqual(self.q("select count(*) from loom_gate_l_qual.transaction_ledger where transaction_id='TX_L'"),"1")
 def test_event_durable_and_processed(self): self.assertEqual(self.q("select status from loom_gate_l_qual.event_queue where event_id='EVENT_L_REVIEW'"),"PROCESSED")
 def test_event_idempotence_marker(self): self.assertEqual(self.q("select count(*) from loom_gate_l_qual.processed_events where event_id='EVENT_L_REVIEW'"),"1")
 def test_authority_not_shadowed(self): self.assertEqual(self.q("select count(*) from information_schema.tables where table_schema in ('loom_earth','loom_timeline') and table_name like 'gate_l%'"),"0")
 def test_contract_invariants_declared(self): self.assertEqual(len(qualification_invariants()),6)
if __name__=="__main__": unittest.main()
