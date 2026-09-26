import unittest
from pathlib import Path
from src.loom_solar_contracts.navigation import assess,NAV1_REQUIRED,NAV1_NOT_REQUIRED_BY_CURRENT_DIRECT_SOLVER
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"dev/solar_baseline_02_wgccre/LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3"
MAN=ROOT/"manifests/solar"
class TestNavContract(unittest.TestCase):
    def test_contract_is_consumer_minimal(self):
        self.assertIn("QUALIFIED_POSITION_VELOCITY_EPHEMERIS_AT_EPOCH",NAV1_REQUIRED)
        self.assertIn("GM",NAV1_NOT_REQUIRED_BY_CURRENT_DIRECT_SOLVER)
        self.assertNotIn("GM",NAV1_REQUIRED)
    def test_current_authority_assessment(self):
        r=assess(DB,MAN)
        self.assertEqual(r["counts"]["bodies"],110)
        self.assertEqual(r["counts"]["nav0_supported"],108)
        self.assertEqual(r["counts"]["nav1_supported"],103)
        self.assertEqual(r["counts"]["nav1_supported"]+r["counts"]["nav1_missing"],110)
    def test_no_candidate_fact_promoted_by_readiness(self):
        self.assertEqual(assess(DB,MAN)["authority_rule"],"MEASURE_EXISTING_AUTHORITY_ONLY_NO_PROMOTION")
if __name__=="__main__": unittest.main()
