import unittest
from engineering.civprop.contracts.knowledge_transmission_v0_3 import *
from engineering.civprop.contracts.mission_knowledge_v1 import KnowledgeClaimV1

def claim():
    return KnowledgeClaimV1("CL1","PROSPECTOR_A","Q1","CERES::WATER","CERES",
        "CHARACTERIZATION_RESULT","EVIDENCE_AVAILABLE","UNKNOWN_AFTER_SEARCH",
        ("OBS1",),2040)

class KnowledgeTransmissionTests(unittest.TestCase):
    def test_declared_channel_and_satisfied_lag_delivers(self):
        c=claim()
        t=transmit_claim(claim=c,source_actor_id="PROSPECTOR_A",
            recipient_actor_id="CERTIFIER_B",channel="CONTRACT",lag_class="L1",
            visibility="COUNTERPARTY",released_year=2040,delivery_authorized=True)
        r=receive_claim(transmission=t,claim=c,lag_satisfied=True,received_year=2041)
        self.assertEqual(r.recipient_actor_id,"CERTIFIER_B")
        self.assertEqual(r.claim.claim_id,c.claim_id)

    def test_no_telepathy_without_release(self):
        c=claim()
        t=transmit_claim(claim=c,source_actor_id="PROSPECTOR_A",
            recipient_actor_id="CERTIFIER_B",channel="CONTRACT",lag_class="L1",
            visibility="PRIVATE",released_year=2040,delivery_authorized=False)
        with self.assertRaises(PermissionError):
            receive_claim(transmission=t,claim=c,lag_satisfied=True,received_year=2041)

    def test_lag_is_required_but_duration_not_invented(self):
        c=claim()
        t=transmit_claim(claim=c,source_actor_id="PROSPECTOR_A",
            recipient_actor_id="CERTIFIER_B",channel="PUBLICATION",lag_class="L3",
            visibility="PUBLIC",released_year=2040,delivery_authorized=True)
        with self.assertRaisesRegex(PermissionError,"LAG_NOT_SATISFIED"):
            receive_claim(transmission=t,claim=c,lag_satisfied=False,received_year=2200)

    def test_undeclared_channel_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNDECLARED_INFORMATION_CHANNEL"):
            transmit_claim(claim=claim(),source_actor_id="PROSPECTOR_A",
                recipient_actor_id="X",channel="TELEPATHY",lag_class="L0",
                visibility="PUBLIC",released_year=2040,delivery_authorized=True)

    def test_non_owner_cannot_publish_claim(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_ACTOR_DOES_NOT_OWN_CLAIM"):
            transmit_claim(claim=claim(),source_actor_id="OTHER",
                recipient_actor_id="X",channel="SALE",lag_class="L1",
                visibility="COUNTERPARTY",released_year=2040,delivery_authorized=True)

    def test_transmission_does_not_mutate_epistemic_content(self):
        c=claim()
        t=transmit_claim(claim=c,source_actor_id=c.actor_id,recipient_actor_id="X",
            channel="TREATY_FILING",lag_class="L2",visibility="PUBLIC",
            released_year=2040,delivery_authorized=True)
        r=receive_claim(transmission=t,claim=c,lag_satisfied=True,received_year=2040)
        self.assertIs(r.claim,c)
        for x in ("abundance","recoverability","economic_value","probability"):
            self.assertFalse(hasattr(r.claim,x))

if __name__=="__main__": unittest.main()
