import unittest
from engineering.civprop.contracts.solar_causal_vertical_slice_v0_3 import *
from engineering.civprop.contracts.certification_institutions_v0_3 import CertificationAuthorityV03

def q(loc,fam="WATER",disp="UNKNOWN_AFTER_SEARCH"):
    return KnowledgeQuestion(f"SOLAR_RESOURCE::{loc}::{fam}","UNRESOLVED_CHARACTERIZATION",f"{loc}::{fam}",loc,None,"NOT_AUTHORIZED","PRIVATE",("M4B",),disp)

def auth(loc):
    return CertificationAuthorityV03(
        "CERT_TEST","SPACE_RESOURCE_CHARACTERIZATION",loc,"AUTHORIZED",
        "AUTHORED_PHASE7_MACHINERY_TEST")

def run(loc,authority=None,**over):
    kw=dict(question=q(loc),actor_id="PRO_TEST",certifier_id="CERT_TEST",
        financier_id="CAP_TEST",observation_id=f"OBS::{loc}",year=2040,
        authority=authority,standard_id="AUTHORED_PHASE7_TEST_STANDARD",
        qualified_person=True,chain_of_custody=True,auditable_data=True,
        sampling_sufficient=True)
    kw.update(over); return run_solar_machinery_slice(**kw)

class SolarGeneralizationTests(unittest.TestCase):
    def test_multiple_non_lunar_targets_share_same_causal_contract(self):
        for loc in ("MARS","VESTA","PSYCHE","EUROPA","TITAN","PLUTO"):
            r=run(loc,auth(loc))
            self.assertEqual(r.location_id,loc)
            self.assertEqual(r.before.action,"WAIT")
            self.assertEqual(r.qualification.status,"QUALIFIED")
            self.assertEqual(r.after.action,"ADVANCE_DUE_DILIGENCE")
            self.assertEqual(r.claim.claim_kind,"CHARACTERIZATION_RESULT")

    def test_no_authority_means_no_qualification(self):
        r=run("VESTA")
        self.assertIsNone(r.qualification)
        self.assertEqual(r.after.action,"WAIT")
        self.assertEqual(r.qualification_gate,"NO_AUTHORIZED_CERTIFIER")

    def test_authority_actor_mismatch_is_blocked(self):
        a=CertificationAuthorityV03("CERT_OTHER","SPACE_RESOURCE_CHARACTERIZATION",
            "MARS","AUTHORIZED","AUTHORED_TEST")
        self.assertIsNone(run("MARS",a).qualification)

    def test_decline_still_blocks_downstream_action(self):
        r=run("PSYCHE",auth("PSYCHE"),chain_of_custody=False)
        self.assertEqual(r.qualification.status,"DECLINED")
        self.assertIn("NO_CHAIN_OF_CUSTODY",r.qualification.rationale_codes)
        self.assertEqual(r.after.action,"WAIT")

    def test_no_resource_truth_or_economics_created(self):
        r=run("TITAN",auth("TITAN"))
        for x in ("abundance","stock_tonnes","grade","recoverability","economic_value","price","probability"):
            self.assertFalse(hasattr(r.claim,x))

    def test_binary_question_rejected(self):
        question=KnowledgeQuestion("Q","BINARY_PRESENCE","MARS::WATER","MARS",0.5,"AUTHORIZED","PRIVATE",("TEST",),None)
        with self.assertRaises(ValueError):
            run_solar_machinery_slice(question=question,actor_id="A",certifier_id="C",
                financier_id="F",observation_id="O",year=2040,authority=None,
                standard_id="S",qualified_person=True,chain_of_custody=True,
                auditable_data=True,sampling_sufficient=True)

if __name__=="__main__": unittest.main()
