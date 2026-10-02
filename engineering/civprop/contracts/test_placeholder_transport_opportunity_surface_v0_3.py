import unittest
from engineering.civprop.contracts.placeholder_transport_opportunity_surface_v0_3 import evaluate,semantics
class PlaceholderTransportSurfaceV03Tests(unittest.TestCase):
 def test_scalar_is_explicit_placeholder(self):
  x=evaluate("EARTH_SURFACE","CERES_ORBITAL",2050)
  self.assertEqual(x.value,1.0); self.assertEqual(x.unit,"DIMENSIONLESS_PLACEHOLDER"); self.assertEqual(x.gap_owner,"GAP-016")
 def test_not_physical_or_production_authority(self):
  s=semantics(); self.assertFalse(s["physical_claim"]); self.assertFalse(s["production_eligible"])
 def test_scope(self):
  with self.assertRaises(ValueError): evaluate("A","B",2227)
if __name__=="__main__": unittest.main()
