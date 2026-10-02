import copy,json,unittest
from pathlib import Path
from engineering.civprop.contracts.gate_c_named_lunar_service_v0_3 import assess_named_service
from engineering.civprop.contracts.gate_c_named_service_traffic_v0_3 import realize_named_service

E=Path(__file__).resolve().parents[1]/"contracts/gate_c_blue_ghost_2_evidence_v0_3.json"

class GateCTraffic(unittest.TestCase):
 def setUp(self):
  self.e=json.loads(E.read_text())
 def assessment(self,e=None,cap=None):
  return assess_named_service(actor_id="NASA",year=2027,
   actor_capabilities={"CLPS_NAMED_LUNAR_DELIVERY_ACCESS":"ACCESS"} if cap is None else cap,
   evidence=self.e if e is None else e)
 def test_feasible_service_becomes_bounded_traffic_fleet_voyage(self):
  r=realize_named_service(assessment=self.assessment(),year=2027)
  self.assertEqual(r.voyage.cargo_tonnes,0.09)
  self.assertEqual(r.voyage.passenger_movements,0.0)
  moon=[x for x in r.location_states if x.location_id=="LUNA_FAR_SIDE"][0]
  self.assertEqual(moon.cargo_inbound_tonnes,0.09)
  self.assertEqual(moon.arrival_calls,1)
  self.assertEqual(moon.metric_scope,"GATE_C_NAMED_SERVICE_QUALIFICATION_REALIZATION")
 def test_unknown_access_cannot_enter_traffic_fleet(self):
  with self.assertRaisesRegex(ValueError,"only FEASIBLE"):
   realize_named_service(assessment=self.assessment(cap={}),year=2027)
 def test_unknown_vehicle_envelope_cannot_enter_traffic_fleet(self):
  e=copy.deepcopy(self.e); e["provider_surface_capacity_kg"]=None
  with self.assertRaisesRegex(ValueError,"only FEASIBLE"):
   realize_named_service(assessment=self.assessment(e=e),year=2027)
 def test_over_envelope_cannot_enter_traffic_fleet(self):
  e=copy.deepcopy(self.e); e["payload_mass_kg"]=241
  with self.assertRaisesRegex(ValueError,"only FEASIBLE"):
   realize_named_service(assessment=self.assessment(e=e),year=2027)
if __name__=="__main__": unittest.main()
