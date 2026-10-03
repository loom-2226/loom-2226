import json,unittest
from pathlib import Path
from .project_hypothesis_v0_3 import *
from .proposition_commitment_bridge_v0_3 import *
from ..contracts.gate_h_closed_loop_causality_v0_3 import run_closed_loop
ROOT=Path(__file__).resolve().parents[3]
X=json.loads((ROOT/'engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/scenario_v1.json').read_text())
A=X['actor_state_v1']['actors'][0]
def hyp():
 return from_observed_mission(actor_id='AUS',subject_id='ROO_VER',objective='Execute observed Australian lunar rover mission',actor_state=A,accessibility=X['accessibility_v1'])
def st():
 return {'budgets':{'AUS':42000000.0},'provider_capacity':{'INTUITIVE_MACHINES':1.0},'reservations':{},'projects':{},'future_events':[],'provenance_ledger':[],'committed_transaction_ids':[]}
def ap(h,t):
 refs=h.provenance_refs+('STEP_C_ROOVER_CONTROL',); aa=[]
 for x in REQUIRED_AUTHORITIES:
  aa.append((FeasibilityAuthorityV03(x,AuthorityStatus.KNOWN,t,refs) if t is not None else unknown(x,*refs)) if x=='TRANSPORT_FEASIBILITY' else known(x,*refs))
 return AssembledPropositionV03(h.hypothesis_id,'AUS','INTUITIVE_MACHINES',1000000.0,1.0,tuple(aa),('INTUITIVE_MACHINES',),refs)
class T(unittest.TestCase):
 def test_real_unknown_blocks(self):
  h=hyp();before=st();out,r=commit_assembled_proposition(state=before,proposition=ap(h,None),project_id='ROOVER_CONTROL',commit_year=2030)
  self.assertEqual(r.transaction_status,'NOT_ATTEMPTED');self.assertIn('TRANSPORT_FEASIBILITY_UNKNOWN',r.transaction_reason_codes);self.assertEqual(out,before)
 def test_positive_control_changes_existing_project_state(self):
  h=hyp();r=refine(h,resolved_requirements=h.unresolved_requirements,new_provenance=('QUALIFIED_SYNTHETIC_CONTROL',))
  out,c=commit_assembled_proposition(state=st(),proposition=ap(r,True),project_id='ROOVER_CONTROL',commit_year=2030)
  self.assertEqual(c.transaction_status,'COMMITTED');loop=run_closed_loop(committed_state=out,start_year=2030,end_year=2031)
  self.assertEqual(loop.final_state['projects']['ROOVER_CONTROL']['status'],'ACTIVE')
 def test_transport_negative_control_blocks(self):
  h=hyp();out,c=commit_assembled_proposition(state=st(),proposition=ap(h,False),project_id='ROOVER_CONTROL',commit_year=2030)
  self.assertEqual(c.transaction_status,'NOT_ATTEMPTED');self.assertIn('TRANSPORT_FEASIBILITY_UNSATISFIED',c.transaction_reason_codes)
if __name__=='__main__':unittest.main()
