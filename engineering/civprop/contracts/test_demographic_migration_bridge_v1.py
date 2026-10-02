import unittest
from types import SimpleNamespace
from engineering.civprop.contracts.demographic_migration_bridge_v1 import *

def route(*,year=2100,origin="EARTH_SURFACE",dest="MARS",pax=10):
 return SimpleNamespace(year=year,origin_location_id=origin,destination_location_id=dest,
                        realized_passenger_movements=pax)
def demand(*,n=8):
 return MigrationDemandV1(2100,"EARTH_SURFACE","MARS",n,("fixture",))

class MigrationBridgeTests(unittest.TestCase):
 def test_migration_bounded_by_realized_passengers(self):
  a=authorize_migration(demand=demand(n=20),route_traffic_state=route(pax=7),origin_population=100)
  self.assertEqual(a.authorized_migrants,7)
 def test_passengers_do_not_automatically_become_migrants(self):
  a=authorize_migration(demand=demand(n=3),route_traffic_state=route(pax=50),origin_population=100)
  self.assertEqual(a.authorized_migrants,3)
 def test_unknown_passenger_flow_stays_unknown(self):
  a=authorize_migration(demand=demand(),route_traffic_state=route(pax=None),origin_population=100)
  self.assertEqual(a.status,"UNKNOWN"); self.assertIsNone(a.authorized_migrants)
 def test_unknown_migration_demand_stays_unknown(self):
  a=authorize_migration(demand=demand(n=None),route_traffic_state=route(pax=10),origin_population=100)
  self.assertEqual(a.status,"UNKNOWN")
 def test_wrong_od_rejected(self):
  with self.assertRaisesRegex(ValueError,"OD_MISMATCH"):
   authorize_migration(demand=demand(),route_traffic_state=route(dest="CERES"),origin_population=100)
 def test_wrong_year_rejected(self):
  with self.assertRaisesRegex(ValueError,"YEAR_MISMATCH"):
   authorize_migration(demand=demand(),route_traffic_state=route(year=2101),origin_population=100)
 def test_origin_population_is_hard_bound(self):
  a=authorize_migration(demand=demand(n=20),route_traffic_state=route(pax=20),origin_population=4)
  self.assertEqual(a.authorized_migrants,4)
 def test_transfer_conserves_population(self):
  a=authorize_migration(demand=demand(n=8),route_traffic_state=route(pax=10),origin_population=100)
  p=apply_conserved_migration(populations={"EARTH_SURFACE":100,"MARS":2},authorization=a)
  self.assertEqual(p,{"EARTH_SURFACE":92,"MARS":10}); self.assertEqual(sum(p.values()),102)
 def test_unknown_cannot_move_population(self):
  a=authorize_migration(demand=demand(),route_traffic_state=route(pax=None),origin_population=100)
  with self.assertRaisesRegex(ValueError,"NOT_AUTHORIZED"):
   apply_conserved_migration(populations={"EARTH_SURFACE":100,"MARS":0},authorization=a)
if __name__=="__main__": unittest.main()
