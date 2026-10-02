import unittest
from .chemical_vehicle_performance_v0_3 import assess_chemical_vehicle
V={'dry_mass_kg':1000,'usable_propellant_mass_kg':1000,'specific_impulse_s':450,'provenance_refs':['AUTHORED_SOLVER_CONTROL']}
class ChemicalVehiclePerformance(unittest.TestCase):
 def a(self,**kw):
  x=dict(required_delta_v_km_s=2.0,vehicle=V,payload_mass_kg=100,infrastructure_status='AVAILABLE',actor_access_status='ACCESS'); x.update(kw); return assess_chemical_vehicle(**x)
 def test_equation_control_feasible(self): self.assertEqual(self.a().status,'FEASIBLE')
 def test_required_dv_can_make_vehicle_infeasible(self): self.assertEqual(self.a(required_delta_v_km_s=20).status,'INFEASIBLE')
 def test_missing_propellant_fails_unknown(self):
  v=dict(V); v['usable_propellant_mass_kg']=None; self.assertEqual(self.a(vehicle=v).status,'UNKNOWN')
 def test_missing_isp_fails_unknown(self):
  v=dict(V); v['specific_impulse_s']=None; self.assertEqual(self.a(vehicle=v).status,'UNKNOWN')
 def test_missing_payload_fails_unknown(self): self.assertEqual(self.a(payload_mass_kg=None).status,'UNKNOWN')
 def test_missing_infrastructure_fails_unknown(self): self.assertEqual(self.a(infrastructure_status='UNKNOWN').status,'UNKNOWN')
 def test_missing_actor_access_fails_unknown(self): self.assertEqual(self.a(actor_access_status='UNKNOWN').status,'UNKNOWN')
 def test_power_is_explicitly_not_applicable_to_impulsive_chemical_model(self): self.assertEqual(self.a().power_constraint_status,'NOT_APPLICABLE_CHEMICAL_IMPULSIVE')
if __name__=='__main__': unittest.main()
