from pathlib import Path
import json
import unittest
from engineering.civprop.contracts.certification_institutions_v0_3 import *

P=str(Path(__file__).resolve().parents[1] / "candidate_inputs" / "LOOM_GROUP_AGENT_SEED_2026_v0.3.json")

class CertificationInstitutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(P) as f:
            cls.seed=json.load(f)
        cls.rows=certification_institutions_from_seed(cls.seed)

    def test_seed_has_25_certification_candidates(self):
        self.assertEqual(len(self.rows),25)

    def test_identity_does_not_grant_ceres_authority(self):
        for x in self.rows:
            a=authority_for(
                institution=x, claim_domain="SPACE_RESOURCE_CHARACTERIZATION",
                jurisdiction="CERES", explicit_authority=False,
                basis="NO_ADOPTED_SPACE_RESOURCE_CODE_2026")
            self.assertEqual(a.authority_status,"UNKNOWN")
            self.assertFalse(may_qualify(a))

    def test_lors101_remains_unadopted(self):
        x=next(x for x in self.rows if x.actor_id=="CERT_LORS101")
        self.assertEqual(x.status_2026,"PROPOSAL_NOT_ADOPTED")
        self.assertFalse(may_qualify(authority_for(
            institution=x, claim_domain="SPACE_RESOURCE_CHARACTERIZATION",
            jurisdiction="CERES", explicit_authority=False,
            basis="PROPOSAL_NOT_ADOPTED")))

    def test_explicit_future_authority_can_activate_without_mutating_seed_identity(self):
        x=next(x for x in self.rows if x.actor_id=="CERT_CRIRSCO")
        a=authority_for(
            institution=x, claim_domain="SPACE_RESOURCE_CHARACTERIZATION",
            jurisdiction="TEST", explicit_authority=True,
            basis="AUTHORED_PHASE6_MACHINERY_TEST")
        self.assertTrue(may_qualify(a))
        self.assertEqual(x.authority_class,"NON_CANON_2026_INSTITUTION_CANDIDATE")

    def test_rankings_are_not_engine_authority(self):
        self.assertTrue(self.seed["rankings"]["engine_use"].startswith("None."))

if __name__=="__main__":
    unittest.main()
