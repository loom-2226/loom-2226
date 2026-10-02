import copy, json, unittest
from pathlib import Path
from engineering.civprop.contracts.gate_c_named_lunar_service_v0_3 import assess_named_service

E = Path(__file__).resolve().parents[1] / "contracts/gate_c_blue_ghost_2_evidence_v0_3.json"

class GateCNamedService(unittest.TestCase):
    def setUp(self):
        self.e = json.loads(E.read_text())
        self.cap = {"CLPS_NAMED_LUNAR_DELIVERY_ACCESS": "ACCESS"}

    def a(self, e=None, cap=None, year=2027):
        return assess_named_service(actor_id="NASA", year=year,
            actor_capabilities=self.cap if cap is None else cap,
            evidence=self.e if e is None else e)

    def test_positive_named_service(self):
        a=self.a()
        self.assertEqual(a.status,"FEASIBLE_NAMED_SERVICE")
        self.assertEqual(a.cargo_mass_tonnes,0.09)
        self.assertEqual(a.provider_surface_capacity_tonnes,0.24)
        self.assertEqual(a.limiting_constraints,())

    def test_remove_actor_access(self):
        self.assertEqual(self.a(cap={}).status,"UNKNOWN")
        self.assertIn("ACTOR_ACCESS_UNKNOWN",self.a(cap={}).limiting_constraints)

    def test_remove_vehicle_capability(self):
        e=copy.deepcopy(self.e); e["provider_surface_capacity_kg"]=None
        self.assertEqual(self.a(e=e).status,"UNKNOWN")
        self.assertIn("VEHICLE_ENVELOPE_UNKNOWN",self.a(e=e).limiting_constraints)

    def test_before_evidence(self):
        self.assertEqual(self.a(year=2022).status,"INFEASIBLE")
        self.assertIn("SERVICE_NOT_YET_EVIDENCED",self.a(year=2022).limiting_constraints)

    def test_payload_exceeds_envelope(self):
        e=copy.deepcopy(self.e); e["payload_mass_kg"]=241
        self.assertEqual(self.a(e=e).status,"INFEASIBLE")
        self.assertIn("PAYLOAD_EXCEEDS_PROVIDER_SURFACE_CAPACITY",self.a(e=e).limiting_constraints)

    def test_unknown_payload_never_guessed(self):
        e=copy.deepcopy(self.e); e["payload_mass_kg"]=None
        self.assertEqual(self.a(e=e).status,"UNKNOWN")
        self.assertIsNone(self.a(e=e).cargo_mass_tonnes)

    def test_wrong_actor_cannot_inherit_nasa_contract(self):
        a=assess_named_service(actor_id="AUS",year=2027,
          actor_capabilities=self.cap,evidence=self.e)
        self.assertEqual(a.status,"UNKNOWN")
        self.assertIn("ACTOR_OUT_OF_SCOPE",a.limiting_constraints)

if __name__=="__main__": unittest.main()
