import math, unittest
from engineering.civprop.contracts.solar_transport_opportunity_v0_3 import lambert_universal, opportunity_from_states
class SolarTransportOpportunityV03Tests(unittest.TestCase):
 def test_known_vallado_style_case(self):
  r1=(5000.0,10000.0,2100.0); r2=(-14600.0,2500.0,7000.0)
  v1,v2=lambert_universal(r1,r2,3600.0,398600.0)
  for got,want in zip(v1,(-5.9925,1.9254,3.2456)): self.assertAlmostEqual(got,want,places=3)
  for got,want in zip(v2,(-3.3125,-4.1966,-0.3853)): self.assertAlmostEqual(got,want,places=3)
 def test_opportunity_is_geometry_only(self):
  # synthetic circular-ish heliocentric states, deliberately not a mission claim
  o=(149597870.7,0,0,0,29.78,0); d=(0,227939200,0,-24.13,0,0)
  x=opportunity_from_states("EARTH","MARS","2030-01-01T00:00:00Z","2030-09-01T00:00:00Z",o,d,"SYNTHETIC_TEST")
  self.assertEqual(x.status,"GEOMETRY_OPPORTUNITY_ONLY")
  self.assertGreater(x.c3_km2_s2,0)
 def test_bad_tof_fails(self):
  with self.assertRaises(ValueError): lambert_universal((1,0,0),(0,1,0),0)
if __name__=="__main__": unittest.main()
