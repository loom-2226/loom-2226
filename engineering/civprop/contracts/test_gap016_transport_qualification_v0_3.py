import copy,json,unittest
from pathlib import Path
from .gap016_transport_qualification_v0_3 import qualify_gap016
E=Path(__file__).with_name('gate_c_blue_ghost_2_evidence_v0_3.json')
class Gap016Qualification(unittest.TestCase):
 def setUp(self): self.e=json.loads(E.read_text()); self.cap={"CLPS_NAMED_LUNAR_DELIVERY_ACCESS":"ACCESS"}
 def q(self,e=None,cap=None): return qualify_gap016(year=2027,actor_id='NASA',actor_capabilities=self.cap if cap is None else cap,named_service_evidence=self.e if e is None else e)
 def test_scope_is_partial_not_global_closure(self):
  q=self.q(); self.assertEqual(q.status,'PARTIAL_CLOSURE_NAMED_SERVICE_ONLY'); self.assertEqual(len(q.qualified_scope),1); self.assertEqual(len(q.open_scope),4)
 def test_generic_chemical_remains_unsolved(self): self.assertIn('ROCKET_EQUATION_AVAILABLE',self.q().generic_chemical_status)
 def test_future_propulsion_remains_solver_gated(self):
  q=self.q(); self.assertTrue(all(x=='PROPULSION_PERFORMANCE_SOLVER_NOT_IMPLEMENTED' for x in (q.nuclear_electric_status,q.fusion_torch_status,q.metric_vessel_status)))
 def test_no_access_reopens_even_named_scope(self): self.assertEqual(self.q(cap={}).status,'OPEN')
 def test_no_vehicle_envelope_reopens_even_named_scope(self):
  e=copy.deepcopy(self.e); e['provider_surface_capacity_kg']=None; self.assertEqual(self.q(e=e).status,'OPEN')
if __name__=='__main__': unittest.main()
