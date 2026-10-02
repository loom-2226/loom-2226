import unittest
from pathlib import Path
from engineering.civprop.contracts.placeholder_transport_opportunity_surface_v0_3 import build_placeholder_surface
ROOT=Path(__file__).resolve().parents[3]
class T(unittest.TestCase):
 @classmethod
 def setUpClass(c): c.p=build_placeholder_surface(ROOT/'reports/solar_civprop/NAV_READINESS_V1.json')
 def test_scalar(self): self.assertEqual(self.p['placeholder_transport_opportunity'],1.0)
 def test_spice_independent(self): self.assertTrue(self.p['semantics']['independent_of_spice'])
 def test_liens_excluded(self):
  b={x['destination_body_id'] for x in self.p['rows']}; self.assertTrue(all(x not in b for x in ('DACTYL','SELAM','NIX','HYDRA','KERBEROS','STYX','PROTEUS')))
