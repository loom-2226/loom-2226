import unittest
from types import SimpleNamespace
from engineering.civprop.method_lab.demographic_lane_v1 import DemographicRuntimeV1

class Rec:
 def __init__(self): self.flows=[]
 def migration(self,y,o,d,a): self.flows.append((y,o,d,a))
def state(n): return SimpleNamespace(biological_population=float(n))
def route(y,p):
 return SimpleNamespace(year=y,origin_location_id="EARTH_SURFACE",
  destination_location_id="MARS",realized_passenger_movements=p)

class DemographicLaneTests(unittest.TestCase):
 def runtime(self,demand=()):
  return DemographicRuntimeV1(
   {"earth_biological_population_by_year":[{"year":2100,"biological_population":100},
     {"year":2101,"biological_population":110}],"provenance_refs":["loom_earth:S"]},
   {"rows":list(demand)})
 def test_authority_updates_annual_earth_baseline(self):
  r=self.runtime(); s={"EARTH_SURFACE":state(1),"MARS":state(0)}
  r.apply_earth_baseline(year=2100,states=s); self.assertEqual(s["EARTH_SURFACE"].biological_population,100)
  r.apply_earth_baseline(year=2101,states=s); self.assertEqual(s["EARTH_SURFACE"].biological_population,110)
 def test_migration_delta_persists_over_next_authority_year(self):
  d=[{"year":2100,"origin_location_id":"EARTH_SURFACE","destination_location_id":"MARS",
      "requested_persons":10,"provenance_refs":["fixture"]}]
  r=self.runtime(d); s={"EARTH_SURFACE":state(0),"MARS":state(0)}; rec=Rec()
  r.apply_earth_baseline(year=2100,states=s); r.migrate(year=2100,states=s,route_traffic_states=[route(2100,8)],recorder=rec)
  self.assertEqual((s["EARTH_SURFACE"].biological_population,s["MARS"].biological_population),(92,8))
  r.apply_earth_baseline(year=2101,states=s)
  self.assertEqual(s["EARTH_SURFACE"].biological_population,102)
  self.assertEqual(s["MARS"].biological_population,8)
 def test_passenger_without_migration_demand_moves_nobody(self):
  r=self.runtime(); s={"EARTH_SURFACE":state(0),"MARS":state(0)}; rec=Rec()
  r.apply_earth_baseline(year=2100,states=s); r.migrate(year=2100,states=s,route_traffic_states=[route(2100,50)],recorder=rec)
  self.assertEqual(s["MARS"].biological_population,0); self.assertEqual(rec.flows,[])
 def test_missing_authority_year_fails_closed(self):
  r=self.runtime(); s={"EARTH_SURFACE":state(0)}
  with self.assertRaisesRegex(ValueError,"YEAR_MISSING"): r.apply_earth_baseline(year=2099,states=s)
if __name__=="__main__": unittest.main()
