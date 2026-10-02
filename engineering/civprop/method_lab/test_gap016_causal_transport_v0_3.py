import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.compile_inputs_v1 import capture_live_authority
from engineering.civprop.contracts.gap014_scenario_bridge_v1 import inject_demographic_authority
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world

ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'engineering/civprop/contracts/gate_c_blue_ghost_2_evidence_v0_3.json'

class Gap016CausalTransportV03(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.e=json.loads(E.read_text())
  cls.td=tempfile.TemporaryDirectory(); p=Path(cls.td.name); build_bundle_dir(p)
  cap=capture_live_authority(p/'gap014.json',database='loom_dev')
  sp=p/'scenario_v1.json'; sc=json.loads(sp.read_text()); sp.write_text(json.dumps(inject_demographic_authority(scenario=sc,capture=cap),indent=2,sort_keys=True)+'\n')
  mp=p/'manifest_v1.json'; m=json.loads(mp.read_text()); sb=sp.read_bytes(); tb=(p/m['truth_file']).read_bytes()
  m['sha256'][m['scenario_file']]=hashlib.sha256(sb).hexdigest(); m['bundle_sha256']=hashlib.sha256(sb+b'\n'+tb).hexdigest(); mp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
  cls.bundle=load_bundle(p)
 @classmethod
 def tearDownClass(cls): cls.td.cleanup()

 def service(self,e=None,cap=None):
  return {"year":2027,"actor_id":"NASA","actor_capabilities":{"CLPS_NAMED_LUNAR_DELIVERY_ACCESS":"ACCESS"} if cap is None else cap,"evidence":self.e if e is None else e}

 def execute(self,service):
  return run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2028,named_transport_services=(service,))

 def test_named_physical_service_reaches_world_traffic(self):
  r=self.execute(self.service())
  rows=[x for x in r.voyage_states if x.service_id=='NASA_LUSEE_NIGHT_BLUE_GHOST_2']
  self.assertEqual(len(rows),1); self.assertEqual(rows[0].cargo_tonnes,0.09); self.assertEqual(rows[0].passenger_movements,0.0)
  moon=[x for x in r.location_traffic_states if x.location_id=='LUNA_FAR_SIDE' and x.year==2027 and x.metric_scope=='GATE_C_NAMED_SERVICE_QUALIFICATION_REALIZATION']
  self.assertEqual(len(moon),1); self.assertEqual(moon[0].cargo_inbound_tonnes,0.09)

 def test_remove_actor_access_service_disappears(self):
  r=self.execute(self.service(cap={}))
  self.assertFalse(any(x.service_id=='NASA_LUSEE_NIGHT_BLUE_GHOST_2' for x in r.voyage_states))

 def test_remove_vehicle_envelope_service_disappears(self):
  e=copy.deepcopy(self.e); e['provider_surface_capacity_kg']=None
  r=self.execute(self.service(e=e))
  self.assertFalse(any(x.service_id=='NASA_LUSEE_NIGHT_BLUE_GHOST_2' for x in r.voyage_states))

 def test_overmass_payload_service_disappears(self):
  e=copy.deepcopy(self.e); e['payload_mass_kg']=241
  r=self.execute(self.service(e=e))
  self.assertFalse(any(x.service_id=='NASA_LUSEE_NIGHT_BLUE_GHOST_2' for x in r.voyage_states))

 def test_named_service_does_not_create_migration(self):
  r=self.execute(self.service())
  self.assertTrue(all(x.passenger_movements==0 for x in r.voyage_states if x.service_id=='NASA_LUSEE_NIGHT_BLUE_GHOST_2'))

if __name__=='__main__': unittest.main()
