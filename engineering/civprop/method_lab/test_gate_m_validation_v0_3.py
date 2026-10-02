import unittest
from engineering.civprop.contracts.gate_k_interacting_causal_network_v0_3 import run_network,run_competing_network
ACTIVE={"project_id":"M","status":"ACTIVE","capital":1}
class GateMValidation(unittest.TestCase):
 def run(self,*a,**kw): return super().run(*a,**kw)
 def test_sensitivity_more_capacity_never_reduces_output_without_failure(self):
  vals=[]
  for cap in (1,2,3,4):
   r=run_network(project=ACTIVE,start_year=2030,end_year=2032,installed_capacity=cap,failure_year=None,initial_inventory=0,annual_input=4,production_per_capacity=2,annual_demand=100)
   vals.append(sum(x.production for x in r.years))
  self.assertEqual(vals,sorted(vals))
 def test_sensitivity_failure_weakly_reduces_total_output(self):
  kw=dict(project=ACTIVE,start_year=2030,end_year=2033,installed_capacity=2,initial_inventory=0,annual_input=2,production_per_capacity=3,annual_demand=100)
  healthy=sum(x.production for x in run_network(failure_year=None,**kw).years)
  failed=sum(x.production for x in run_network(failure_year=2032,**kw).years)
  self.assertLess(failed,healthy)
 def test_conservation_sweep(self):
  for cap in (1,2,4):
   for fail in (None,2031,2032):
    r=run_network(project=ACTIVE,start_year=2030,end_year=2033,installed_capacity=cap,failure_year=fail,initial_inventory=3,annual_input=2,production_per_capacity=5,annual_demand=100)
    consumed=sum(x.production/5 for x in r.years)
    self.assertAlmostEqual(3+4*2-consumed,r.final_inventory)
 def test_competing_allocation_never_exceeds_production_sweep(self):
  consumers=({"consumer_id":"A","priority":2,"demand":4},{"consumer_id":"B","priority":1,"demand":7})
  for cap in (1,2,5):
   for fail in (None,2031):
    rows=run_competing_network(project=ACTIVE,start_year=2030,end_year=2032,installed_capacity=cap,failure_year=fail,annual_input=3,production_per_capacity=2,consumers=consumers)
    for row in rows: self.assertAlmostEqual(sum(x.served for x in row.allocations)+row.unallocated_output,row.production)
 def test_ensemble_parameter_sweep_is_deterministic(self):
  def ensemble():
   return tuple(run_network(project=ACTIVE,start_year=2030,end_year=2032,installed_capacity=cap,failure_year=fail,initial_inventory=0,annual_input=2,production_per_capacity=3,annual_demand=6).canonical_sha256 for cap in (1,2,3) for fail in (None,2031,2032))
  self.assertEqual(ensemble(),ensemble())
 def test_priority_changes_distribution_not_conservation(self):
  a=({"consumer_id":"A","priority":2,"demand":5},{"consumer_id":"B","priority":1,"demand":5})
  b=({"consumer_id":"A","priority":1,"demand":5},{"consumer_id":"B","priority":2,"demand":5})
  kw=dict(project=ACTIVE,start_year=2030,end_year=2030,installed_capacity=2,failure_year=None,annual_input=2,production_per_capacity=3)
  x=run_competing_network(consumers=a,**kw)[0]; y=run_competing_network(consumers=b,**kw)[0]
  self.assertEqual(sum(z.served for z in x.allocations),sum(z.served for z in y.allocations))
  self.assertNotEqual({z.consumer_id:z.served for z in x.allocations},{z.consumer_id:z.served for z in y.allocations})
if __name__=="__main__": unittest.main()
