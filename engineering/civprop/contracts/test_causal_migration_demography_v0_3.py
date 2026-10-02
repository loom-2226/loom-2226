import unittest
from types import SimpleNamespace
from .causal_migration_demography_v0_3 import *
def route(pax):
 return SimpleNamespace(year=2030,origin_location_id='EARTH_SURFACE',destination_location_id='LUNA_SURFACE',realized_passenger_movements=pax)
class CausalMigrationDemography(unittest.TestCase):
 def test_passengers_are_not_automatically_migrants(self):
  r=realize_migration(year=2030,origin_location_id='EARTH_SURFACE',destination_location_id='LUNA_SURFACE',requested_migrants=3,demand_provenance_refs=('DEMAND',),route_traffic_state=route(50),origin_population=100)
  self.assertEqual(r.realized_migrants,3)
 def test_unknown_demand_cannot_create_migration(self):
  r=realize_migration(year=2030,origin_location_id='EARTH_SURFACE',destination_location_id='LUNA_SURFACE',requested_migrants=None,demand_provenance_refs=('DEMAND',),route_traffic_state=route(50),origin_population=100)
  self.assertEqual(r.status,'UNKNOWN'); self.assertIsNone(r.realized_migrants)
 def test_unknown_passenger_capacity_cannot_create_migration(self):
  r=realize_migration(year=2030,origin_location_id='EARTH_SURFACE',destination_location_id='LUNA_SURFACE',requested_migrants=10,demand_provenance_refs=('DEMAND',),route_traffic_state=route(None),origin_population=100)
  self.assertEqual(r.status,'UNKNOWN')
 def test_transfer_conserves_and_creates_destination_cohort(self):
  r=realize_migration(year=2030,origin_location_id='EARTH_SURFACE',destination_location_id='LUNA_SURFACE',requested_migrants=20,demand_provenance_refs=('DEMAND',),route_traffic_state=route(12),origin_population=100)
  p,c=apply_migration_and_create_cohort(populations={'EARTH_SURFACE':100,'LUNA_SURFACE':0},realization=r)
  self.assertEqual(p,{'EARTH_SURFACE':88,'LUNA_SURFACE':12}); self.assertEqual(sum(p.values()),100); self.assertEqual(c.population,12)
 def test_unknown_rates_do_not_freeze_or_invent_descendants(self):
  c=CohortStateV1('C','LUNA_SURFACE',12,2030,('MIGRATION',))
  t=continue_offworld_cohort(cohort=c,year=2031,rates=DemographicRatesV1(None,None,('NO_AUTHORIZED_OFFWORLD_RATES',)))
  self.assertEqual(t.status,'UNKNOWN_RATES'); self.assertIsNone(t.closing_population); self.assertIsNone(t.births); self.assertIsNone(t.deaths)
 def test_authored_control_rates_can_exercise_demographic_math(self):
  c=CohortStateV1('C','LUNA_SURFACE',100,2030,('MIGRATION',))
  t=continue_offworld_cohort(cohort=c,year=2031,rates=DemographicRatesV1(.02,.01,('AUTHORED_MACHINERY_CONTROL',)))
  self.assertEqual(t.status,'RESOLVED_MACHINERY_TEST'); self.assertEqual(t.births,2); self.assertEqual(t.deaths,1); self.assertEqual(t.closing_population,101)
if __name__=='__main__': unittest.main()
