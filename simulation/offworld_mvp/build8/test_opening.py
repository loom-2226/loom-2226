import unittest
from pathlib import Path
from offworld_kernel.boundary import validate_opening
from .opening import build_country_opening

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'promoted Earth v4 local baseline absent')
class CountryOpeningTests(unittest.TestCase):
    def test_deterministic_validated_opening(self):
        first,_,capacities,_=build_country_opening(ROOT)
        second,_,_,_=build_country_opening(ROOT)
        self.assertEqual(len(capacities),800)
        self.assertEqual(first.boundary_manifest.opening_state_hash,second.boundary_manifest.opening_state_hash)
        self.assertEqual(first.boundary_manifest.input_snapshot_id,second.boundary_manifest.input_snapshot_id)
        self.assertEqual(len([a for a in first.boundary_manifest.assertions if a.assertion_id.startswith('B8:')]),800)
        self.assertEqual(len([a for a in first.state.accounts if a.startswith('b8_funds:')]),80)
        validate_opening(first)
