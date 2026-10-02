import unittest
from types import SimpleNamespace
from engineering.civprop.method_lab.demographic_lane_v1 import DemographicRuntimeV1

def st(n): return SimpleNamespace(biological_population=float(n))
def rt(y,o,d,p): return SimpleNamespace(year=y,origin_location_id=o,destination_location_id=d,realized_passenger_movements=p)
class Rec:
 def __init__(self): self.flows=[]
 def migration(self,y,o,d,a): self.flows.append((y,o,d,a))

class HostileGap014(unittest.TestCase):
 def lane(self,rows=()):
  return DemographicRuntimeV1({"earth_biological_population_by_year":[
   {"year":2100,"biological_population":100.0},{"year":2101,"biological_population":110.0},
   {"year":2102,"biological_population":120.0}],"provenance_refs":["authority:test"]},{"rows":list(rows)})
 def test_outbound_then_inbound_delta_survives_baseline_changes(self):
  rows=[{"year":2100,"origin_location_id":"EARTH_SURFACE","destination_location_id":"MARS","requested_persons":10,"provenance_refs":["d"]},
        {"year":2101,"origin_location_id":"MARS","destination_location_id":"EARTH_SURFACE","requested_persons":3,"provenance_refs":["d"]}]
  x=self.lane(rows); s={"EARTH_SURFACE":st(0),"MARS":st(0)}; q=Rec()
  x.apply_earth_baseline(year=2100,states=s); x.migrate(year=2100,states=s,route_traffic_states=[rt(2100,"EARTH_SURFACE","MARS",10)],recorder=q)
  x.apply_earth_baseline(year=2101,states=s); x.migrate(year=2101,states=s,route_traffic_states=[rt(2101,"MARS","EARTH_SURFACE",3)],recorder=q)
  x.apply_earth_baseline(year=2102,states=s)
  self.assertEqual((s["EARTH_SURFACE"].biological_population,s["MARS"].biological_population),(113,7))
 def test_transport_capacity_caps_migration(self):
  row={"year":2100,"origin_location_id":"EARTH_SURFACE","destination_location_id":"MARS","requested_persons":50,"provenance_refs":["d"]}
  x=self.lane([row]); s={"EARTH_SURFACE":st(0),"MARS":st(0)}; q=Rec(); x.apply_earth_baseline(year=2100,states=s)
  x.migrate(year=2100,states=s,route_traffic_states=[rt(2100,"EARTH_SURFACE","MARS",8)],recorder=q)
  self.assertEqual((s["EARTH_SURFACE"].biological_population,s["MARS"].biological_population),(92,8))
 def test_unknown_demand_moves_nobody(self):
  row={"year":2100,"origin_location_id":"EARTH_SURFACE","destination_location_id":"MARS","requested_persons":None,"provenance_refs":["d"]}
  x=self.lane([row]); s={"EARTH_SURFACE":st(0),"MARS":st(0)}; q=Rec(); x.apply_earth_baseline(year=2100,states=s)
  x.migrate(year=2100,states=s,route_traffic_states=[rt(2100,"EARTH_SURFACE","MARS",8)],recorder=q)
  self.assertEqual((s["EARTH_SURFACE"].biological_population,s["MARS"].biological_population),(100,0))
 def test_unknown_transport_moves_nobody(self):
  row={"year":2100,"origin_location_id":"EARTH_SURFACE","destination_location_id":"MARS","requested_persons":8,"provenance_refs":["d"]}
  x=self.lane([row]); s={"EARTH_SURFACE":st(0),"MARS":st(0)}; q=Rec(); x.apply_earth_baseline(year=2100,states=s)
  x.migrate(year=2100,states=s,route_traffic_states=[rt(2100,"EARTH_SURFACE","MARS",None)],recorder=q)
  self.assertEqual(s["MARS"].biological_population,0)
 def test_missing_route_does_not_fake_movement(self):
  row={"year":2100,"origin_location_id":"EARTH_SURFACE","destination_location_id":"MARS","requested_persons":8,"provenance_refs":["d"]}
  x=self.lane([row]); s={"EARTH_SURFACE":st(0),"MARS":st(0)}; q=Rec(); x.apply_earth_baseline(year=2100,states=s)
  x.migrate(year=2100,states=s,route_traffic_states=[],recorder=q)
  self.assertEqual((s["EARTH_SURFACE"].biological_population,s["MARS"].biological_population),(100,0))
 def test_origin_population_caps_migration(self):
  row={"year":2100,"origin_location_id":"MARS","destination_location_id":"EARTH_SURFACE","requested_persons":50,"provenance_refs":["d"]}
  x=self.lane([row]); s={"EARTH_SURFACE":st(0),"MARS":st(4)}; q=Rec(); x.apply_earth_baseline(year=2100,states=s)
  x.migrate(year=2100,states=s,route_traffic_states=[rt(2100,"MARS","EARTH_SURFACE",50)],recorder=q)
  self.assertEqual((s["EARTH_SURFACE"].biological_population,s["MARS"].biological_population),(104,0))
 def test_duplicate_matching_routes_do_not_double_move(self):
  row={"year":2100,"origin_location_id":"EARTH_SURFACE","destination_location_id":"MARS","requested_persons":8,"provenance_refs":["d"]}
  x=self.lane([row]); s={"EARTH_SURFACE":st(0),"MARS":st(0)}; q=Rec(); x.apply_earth_baseline(year=2100,states=s)
  x.migrate(year=2100,states=s,route_traffic_states=[rt(2100,"EARTH_SURFACE","MARS",8),rt(2100,"EARTH_SURFACE","MARS",8)],recorder=q)
  self.assertEqual(s["MARS"].biological_population,0)
 def test_missing_authority_year_fails_closed(self):
  x=self.lane(); s={"EARTH_SURFACE":st(0)}
  with self.assertRaisesRegex(ValueError,"YEAR_MISSING"): x.apply_earth_baseline(year=2099,states=s)
 def test_missing_provenance_fails_closed(self):
  with self.assertRaisesRegex(ValueError,"PROVENANCE_MISSING"):
   DemographicRuntimeV1({"earth_biological_population_by_year":[{"year":2100,"biological_population":100}],"provenance_refs":[]},{"rows":[]})
 def test_negative_baseline_after_delta_fails_closed(self):
  x=self.lane(); x.earth_migration_delta=-101; s={"EARTH_SURFACE":st(0)}
  with self.assertRaisesRegex(ValueError,"NEGATIVE"): x.apply_earth_baseline(year=2100,states=s)
if __name__=="__main__": unittest.main()
