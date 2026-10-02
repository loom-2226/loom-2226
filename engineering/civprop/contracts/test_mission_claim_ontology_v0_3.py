import unittest
from engineering.civprop.contracts.mission_claim_ontology_v0_3 import (
    MissionOpportunityV03, characterization_claim_from_knowledge,
)
from engineering.civprop.contracts.mission_knowledge_v1 import (
    CharacterizationKnowledgeStateV1, KnowledgeQuestion,
)


class MissionClaimOntologyV03Tests(unittest.TestCase):
    def question(self):
        return KnowledgeQuestion(
            question_id="Q:CERES:WATER", question_kind="UNRESOLVED_CHARACTERIZATION",
            subject_id="CERES::WATER", location_id="CERES", prior_probability=None,
            prior_status="NOT_AUTHORIZED", visibility="PRIVATE", provenance_refs=("M4B",),
            evidence_disposition="UNKNOWN_AFTER_SEARCH",
        )

    def test_question_is_not_mission_opportunity(self):
        q=self.question()
        o=MissionOpportunityV03("OP:CERES",q.question_id,"EARTH","CERES","RECON","SOLAR",())
        self.assertNotEqual(q.question_id,o.opportunity_id)
        self.assertEqual(o.authority_class,"NON_CANON_MISSION_OPPORTUNITY")

    def test_uncompleted_knowledge_cannot_claim(self):
        q=self.question()
        k=CharacterizationKnowledgeStateV1("A",q.question_id,q.subject_id,q.location_id,
            "UNRESOLVED","unresolved",2026,evidence_disposition=q.evidence_disposition)
        with self.assertRaisesRegex(ValueError,"uncompleted"):
            characterization_claim_from_knowledge(knowledge=k,question=q,year=2026)

    def test_completed_observation_yields_evidence_claim_not_resource_truth(self):
        q=self.question()
        k=CharacterizationKnowledgeStateV1("A",q.question_id,q.subject_id,q.location_id,
            "CHARACTERIZATION_COMPLETED","obs-1",2030,observation_ids=("obs-1",),
            evidence_disposition=q.evidence_disposition)
        c=characterization_claim_from_knowledge(knowledge=k,question=q,year=2030)
        self.assertEqual(c.claim_kind,"CHARACTERIZATION_RESULT")
        self.assertEqual(c.claim_status,"EVIDENCE_AVAILABLE")
        self.assertEqual(c.evidence_disposition,"UNKNOWN_AFTER_SEARCH")
        self.assertFalse(hasattr(c,"probability"))
        self.assertFalse(hasattr(c,"abundance"))
        self.assertFalse(hasattr(c,"recoverability"))
        self.assertFalse(hasattr(c,"economic_value"))


if __name__ == "__main__": unittest.main()
