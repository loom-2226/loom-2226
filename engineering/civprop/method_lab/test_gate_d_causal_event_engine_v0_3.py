import copy,json,unittest
from pathlib import Path
from engineering.civprop.contracts.gate_d_causal_event_engine_v0_3 import run_named_service_event

E=Path(__file__).resolve().parents[1]/"contracts/gate_c_blue_ghost_2_evidence_v0_3.json"
CAP={"NASA":{"CLPS_NAMED_LUNAR_DELIVERY_ACCESS":"ACCESS"}}
UNIVERSE=("NASA","FIREFLY_AEROSPACE","AUS","CNSA","ESA","SPACEX","JAXA")

class GateDSelectiveCausalEngine(unittest.TestCase):
 def setUp(self): self.e=json.loads(E.read_text())
 def execute(self,e=None,cap=CAP):
  return run_named_service_event(year=2027,evidence=self.e if e is None else e,
   actor_capabilities=cap,actor_universe=UNIVERSE)

 def test_event_executes_full_chain(self):
  r=self.execute()
  self.assertEqual([x.event_type for x in r.events],[
   "NAMED_SERVICE_OPPORTUNITY","PHYSICAL_SERVICE_ASSESSMENT",
   "TRAFFIC_FLEET_REALIZATION","CIVPROP_TRANSPORT_CONSEQUENCE",
   "CAUSAL_NEIGHBORHOOD_DEMOTION"])
  self.assertEqual(r.consequences[0].amount,0.09)
  self.assertEqual(r.consequences[0].location_id,"LUNA_FAR_SIDE")

 def test_only_causal_neighborhood_wakes(self):
  r=self.execute()
  activated={x.actor_id for x in r.activations if x.status=="ACTIVATED"}
  self.assertEqual(activated,{"NASA","FIREFLY_AEROSPACE"})
  self.assertEqual(set(r.dormant_actor_ids),set(UNIVERSE)-activated)

 def test_resolved_neighborhood_demotes(self):
  r=self.execute()
  self.assertEqual(r.final_active_actor_ids,())
  self.assertEqual({x.actor_id for x in r.activations if x.status=="DEMOTED"},
                   {"NASA","FIREFLY_AEROSPACE"})

 def test_parent_chain_is_unbroken(self):
  r=self.execute()
  ids={x.event_id for x in r.events}
  for i,e in enumerate(r.events):
   if i==0: self.assertEqual(e.parent_event_ids,())
   else:
    self.assertEqual(len(e.parent_event_ids),1)
    self.assertIn(e.parent_event_ids[0],ids)
  self.assertEqual(r.consequences[0].parent_event_id,r.events[-2].event_id)

 def test_missing_access_stops_before_traffic(self):
  r=self.execute(cap={"NASA":{}})
  kinds=[x.event_type for x in r.events]
  self.assertNotIn("TRAFFIC_FLEET_REALIZATION",kinds)
  self.assertNotIn("CIVPROP_TRANSPORT_CONSEQUENCE",kinds)
  self.assertEqual(r.consequences,())
  self.assertEqual(r.final_active_actor_ids,())

 def test_unknown_vehicle_envelope_stops_before_traffic(self):
  e=copy.deepcopy(self.e); e["provider_surface_capacity_kg"]=None
  r=self.execute(e=e)
  self.assertEqual(r.consequences,())
  self.assertNotIn("TRAFFIC_FLEET_REALIZATION",[x.event_type for x in r.events])

 def test_irrelevant_actor_cannot_be_smuggled_into_neighborhood(self):
  e=copy.deepcopy(self.e); e["causal_neighborhood_actor_ids"].append("CNSA")
  with self.assertRaisesRegex(ValueError,"exact customer/provider"):
   self.execute(e=e)

 def test_no_population_or_migration_consequence_is_created(self):
  r=self.execute()
  self.assertTrue(all(x.consequence_type=="NAMED_CARGO_DELIVERY" for x in r.consequences))
  self.assertTrue(all("population" not in str(x.payload).lower() for x in r.events))

 def test_deterministic_replay(self):
  self.assertEqual(self.execute().canonical_sha256,self.execute().canonical_sha256)

if __name__=="__main__": unittest.main()
