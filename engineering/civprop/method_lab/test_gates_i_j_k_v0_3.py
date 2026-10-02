import unittest
from engineering.civprop.contracts.gate_i_physical_capacity_feedback_v0_3 import project_capacity
from engineering.civprop.contracts.gate_j_endogenous_opportunity_v0_3 import detect_capacity_opportunity
from engineering.civprop.contracts.gate_k_interacting_causal_network_v0_3 import run_network,run_competing_network
ACTIVE={"project_id":"A","status":"ACTIVE","capital":1}
class IJK(unittest.TestCase):
 def test_i_active(self): self.assertEqual(project_capacity(project=ACTIVE,years=(2030,),installed_capacity=5)[0].usable_capacity,5)
 def test_i_inactive(self): self.assertEqual(project_capacity(project={"project_id":"A","status":"COMMITTED"},years=(2030,),installed_capacity=5)[0].usable_capacity,0)
 def test_i_failure(self): self.assertEqual([x.usable_capacity for x in project_capacity(project=ACTIVE,years=(2030,2031,2032),installed_capacity=5,failure_year=2031)],[5,0,0])
 def test_j_creates(self):
  s=project_capacity(project=ACTIVE,years=(2030,),installed_capacity=5); self.assertEqual(detect_capacity_opportunity(states=s,year=2030,required_capacity=4).status,"ELIGIBLE")
 def test_j_blocks(self):
  s=project_capacity(project=ACTIVE,years=(2030,),installed_capacity=3); self.assertEqual(detect_capacity_opportunity(states=s,year=2030,required_capacity=4).reason_codes,("INSUFFICIENT_PHYSICAL_CAPACITY",))
 def test_j_failure_removes(self):
  s=project_capacity(project=ACTIVE,years=(2030,2031),installed_capacity=5,failure_year=2031); self.assertEqual(detect_capacity_opportunity(states=s,year=2031,required_capacity=1).status,"BLOCKED")
 def test_k_chain(self):
  r=run_network(project=ACTIVE,start_year=2030,end_year=2032,installed_capacity=2,failure_year=None,initial_inventory=0,annual_input=2,production_per_capacity=3,annual_demand=6)
  self.assertEqual([(x.production,x.demand_served,x.shortage) for x in r.years],[(6,6,0),(6,6,0),(6,6,0)])
 def test_k_failure_propagates(self):
  r=run_network(project=ACTIVE,start_year=2030,end_year=2032,installed_capacity=2,failure_year=2031,initial_inventory=0,annual_input=2,production_per_capacity=3,annual_demand=6)
  self.assertEqual((r.years[1].production,r.years[1].shortage,r.final_inventory),(0,6,4))
 def test_k_no_capacity_no_production(self):
  r=run_network(project={"project_id":"A","status":"COMMITTED"},start_year=2030,end_year=2030,installed_capacity=2,failure_year=None,initial_inventory=0,annual_input=2,production_per_capacity=3,annual_demand=6); self.assertEqual(r.years[0].production,0)
 def test_k_conservation(self):
  r=run_network(project=ACTIVE,start_year=2030,end_year=2032,installed_capacity=2,failure_year=2031,initial_inventory=1,annual_input=2,production_per_capacity=3,annual_demand=6)
  self.assertAlmostEqual(1+6-sum(x.production/3 for x in r.years),r.final_inventory)
 def test_k_two_consumers_compete_for_same_output(self):
  cs=({"consumer_id":"LIFE_SUPPORT","priority":2,"demand":4},{"consumer_id":"INDUSTRY","priority":1,"demand":4})
  r=run_competing_network(project=ACTIVE,start_year=2030,end_year=2030,installed_capacity=2,failure_year=None,annual_input=2,production_per_capacity=3,consumers=cs)
  self.assertEqual([(x.consumer_id,x.served,x.shortage) for x in r[0].allocations],[("LIFE_SUPPORT",4,0),("INDUSTRY",2,2)])
  self.assertEqual(sum(x.served for x in r[0].allocations)+r[0].unallocated_output,r[0].production)
 def test_k_competition_order_independent(self):
  a=({"consumer_id":"LIFE_SUPPORT","priority":2,"demand":4},{"consumer_id":"INDUSTRY","priority":1,"demand":4})
  kw=dict(project=ACTIVE,start_year=2030,end_year=2030,installed_capacity=2,failure_year=None,annual_input=2,production_per_capacity=3)
  x=run_competing_network(consumers=a,**kw); y=run_competing_network(consumers=tuple(reversed(a)),**kw)
  self.assertEqual(x,y)
 def test_k_failure_hits_both_consumers(self):
  cs=({"consumer_id":"LIFE_SUPPORT","priority":2,"demand":4},{"consumer_id":"INDUSTRY","priority":1,"demand":4})
  r=run_competing_network(project=ACTIVE,start_year=2030,end_year=2031,installed_capacity=2,failure_year=2031,annual_input=2,production_per_capacity=3,consumers=cs)
  self.assertTrue(all(x.served==0 for x in r[1].allocations)); self.assertEqual(sum(x.shortage for x in r[1].allocations),8)
 def test_k_deterministic(self):
  kw=dict(project=ACTIVE,start_year=2030,end_year=2032,installed_capacity=2,failure_year=2031,initial_inventory=0,annual_input=2,production_per_capacity=3,annual_demand=6)
  self.assertEqual(run_network(**kw).canonical_sha256,run_network(**kw).canonical_sha256)
if __name__=="__main__": unittest.main()
