import unittest
from engineering.civprop.propagate_solar_v0_3 import canonical_sha
class SolarPropagateV03Tests(unittest.TestCase):
 def test_hash_deterministic(self): self.assertEqual(canonical_sha({'b':2,'a':1}),canonical_sha({'a':1,'b':2}))
 def test_hash_changes(self): self.assertNotEqual(canonical_sha({'a':1}),canonical_sha({'a':2}))
if __name__=='__main__': unittest.main()
