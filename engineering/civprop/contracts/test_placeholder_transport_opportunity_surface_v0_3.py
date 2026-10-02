import unittest
from engineering.civprop.contracts.placeholder_transport_opportunity_surface_v0_3 import evaluate,friction_for_body,semantics
class PlaceholderTransportSurfaceV03Tests(unittest.TestCase):
 def test_geography_has_strong_nonlinear_friction(self):
  mars=friction_for_body("MARS","PLANET"); ceres=friction_for_body("CERES","DWARF_PLANET"); pluto=friction_for_body("PLUTO","DWARF_PLANET")
  self.assertEqual((mars,ceres,pluto),(6.0,18.0,500.0))
  self.assertGreater(pluto,25*mars); self.assertGreater(pluto,20*ceres)
 def test_giant_planet_system_satellites_inherit_coarse_system_band(self):
  self.assertEqual(friction_for_body("EUROPA","NATURAL_SATELLITE"),55.0)
  self.assertEqual(friction_for_body("TITAN","NATURAL_SATELLITE"),100.0)
  self.assertEqual(friction_for_body("TRITON","NATURAL_SATELLITE"),320.0)
 def test_scalar_is_explicit_placeholder(self):
  x=evaluate("EARTH_SURFACE","CERES_ORBITAL",2050,destination_body_id="CERES",destination_body_class="DWARF_PLANET")
  self.assertEqual(x.value,18.0); self.assertEqual(x.gap_owner,"GAP-016")
 def test_not_physical_or_production_authority(self):
  s=semantics(); self.assertFalse(s["physical_claim"]); self.assertFalse(s["production_eligible"]); self.assertFalse(s["constant_across_destinations"])
 def test_scope(self):
  with self.assertRaises(ValueError): evaluate("A","B",2227,destination_body_id="MARS",destination_body_class="PLANET")
if __name__=="__main__": unittest.main()
