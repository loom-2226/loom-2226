import unittest
from engineering.civprop.method_lab.test_causal_world_v0_3 import CausalWorldV03Tests

class CausalMigrationWorldV03(CausalWorldV03Tests):
 def control(self,**kw):
  x={"year":2030,"origin_location_id":"EARTH_SURFACE","destination_location_id":"LUNA_SURFACE","requested_migrants":12,"realized_passenger_movements":20,"demand_provenance_refs":["AUTHORED_MACHINERY_CONTROL"]}; x.update(kw); return x
 def test_migration_control_changes_residence_and_persists(self):
  r=self.run_world(self.control()) if hasattr(self,'run_world') else None
  # use shared bundle directly; production authority remains untouched
  from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2029,end_year=2031,migration_controls=(self.control(),))
  flows=[x for x in r.flows if x.flow_type=='MIGRATION']
  self.assertEqual(len(flows),1); self.assertEqual(flows[0].amount,12)
  luna=[x for x in r.annual_states if x.year==2031 and x.location_id=='LUNA_SURFACE'][0]
  self.assertEqual(luna.biological_population,12)
 def test_passengers_without_residence_demand_do_not_migrate(self):
  from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2029,end_year=2030,migration_controls=(self.control(requested_migrants=None),))
  self.assertFalse(any(x.flow_type=='MIGRATION' for x in r.flows))
 def test_demand_without_passenger_realization_does_not_migrate(self):
  from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2029,end_year=2030,migration_controls=(self.control(realized_passenger_movements=None),))
  self.assertFalse(any(x.flow_type=='MIGRATION' for x in r.flows))

if __name__=='__main__': unittest.main()
