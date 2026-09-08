from __future__ import annotations

import json
import sys
import unittest
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from model_permutation_experiment import (  # noqa: E402
    ModelIdentity,
    build_critic_packet,
    build_designer_packet,
    build_trace,
    critic_prompt,
    designer_prompt,
    execute_critic_response,
    execute_designer_response,
)

RUN_DIR = ROOT / "research" / "model_runs" / "wayfarer_2026-09-08_run001"
DESIGNER_RAW_PATH = RUN_DIR / "designer_raw.json"
CRITIC_RAW_PATH = RUN_DIR / "critic_raw.json"
EXPECTED_DESIGNER_PACKET_HASH = "65008bca2acfeb352ff48991a728010796c6aa31add924cc35d6881ad00698d6"
EXPECTED_CRITIC_PACKET_HASH = "ae379dc0c2dc5833e3c7e39e6adc5ba67661376fd58149488db48d552b70bf35"
EXPECTED_EVALUATION_HASH = "802647c25969505e8ad14a5864d7eac4ba40fbfef74c354339a92992187cc835"
EXPECTED_EVIDENCE_HASH = "621d31b78ca8e78450b2d190bf1733ee6913d8b77154b266bfdfdc6ede82bb0a"
EXPECTED_CHILD = "CAND-MUT-CB6ACB18C6768B2E0EF9"


def _identity() -> ModelIdentity:
    return ModelIdentity(
        model_id="GPT-5.6 Sol",
        provider="OpenAI ChatGPT",
        configuration="interactive-project-session; hidden sampling configuration",
    )


class WayfarerRealModelPacketExportTests(unittest.TestCase):
    def test_execute_first_real_designer_and_sol_critic_responses(self):
        designer_packet = build_designer_packet(2226)
        designer_prompt_text = designer_prompt(designer_packet)
        self.assertEqual(designer_packet.authority_status, "MODEL_INPUT_ONLY")
        self.assertEqual(designer_packet.packet_hash, EXPECTED_DESIGNER_PACKET_HASH)

        designer_raw = DESIGNER_RAW_PATH.read_text(encoding="utf-8")
        packet2, proposal, child, execution, child_eval, evidence = execute_designer_response(designer_raw, seed=2226)
        self.assertEqual(packet2, designer_packet)
        self.assertEqual(proposal.proposer_model, "GPT-5.6 Sol")
        self.assertEqual(proposal.authority_claim, "PROPOSAL_ONLY")
        self.assertEqual(execution.authority_status, "CANDIDATE_DERIVATION_ONLY")
        self.assertEqual(child.candidate_id, EXPECTED_CHILD)
        self.assertEqual(evidence.evaluation_hash, EXPECTED_EVALUATION_HASH)
        self.assertEqual(evidence.package_hash, EXPECTED_EVIDENCE_HASH)
        self.assertTrue(all(row.passed for row in child_eval.hard_constraints))
        self.assertFalse(evidence.flight_dynamics_authority)
        self.assertFalse(evidence.canon_changed)
        self.assertFalse(evidence.production_shipclasses_changed)

        designer_trace = build_trace(
            role="DESIGNER",
            identity=_identity(),
            prompt=designer_prompt_text,
            input_packet_hash=designer_packet.packet_hash,
            raw_response=designer_raw,
            parsed_output=proposal,
            parent_candidate_id=designer_packet.parent_candidate_id,
            child_candidate_id=child.candidate_id,
            evaluation_hash=evidence.evaluation_hash,
            evidence_package_hash=evidence.package_hash,
        )
        self.assertEqual(designer_trace.authority_status, "MODEL_EXPERIMENT_TRACE_ONLY")

        critic_packet = build_critic_packet(child=child, child_eval=child_eval, evidence=evidence)
        self.assertEqual(critic_packet.packet_hash, EXPECTED_CRITIC_PACKET_HASH)
        critic_prompt_text = critic_prompt(critic_packet)
        critic_raw = CRITIC_RAW_PATH.read_text(encoding="utf-8")
        packet3, report, critique = execute_critic_response(
            critic_raw,
            child=child,
            child_eval=child_eval,
            evidence=evidence,
        )
        self.assertEqual(packet3, critic_packet)
        self.assertEqual(report.reviewer_model, "GPT-5.6 Sol")
        self.assertEqual(report.authority_status, "ARCHITECTURAL_REVIEW_ONLY")
        self.assertEqual(report.overall_recommendation, "REVISE")
        self.assertEqual(critique.authority_claim, "CRITIQUE_ONLY")
        self.assertEqual(critique.candidate_id, EXPECTED_CHILD)
        self.assertEqual(critique.evaluation_hash, EXPECTED_EVALUATION_HASH)
        self.assertTrue(any(row.criterion_id == "SOL-LEGIBILITY" and row.severity == "WARN" for row in report.findings))
        self.assertFalse(report.physical_feasibility_claimed)
        self.assertFalse(report.flight_dynamics_authority_claimed)
        self.assertFalse(report.canon_change_claimed)
        self.assertFalse(report.production_shipclass_change_claimed)

        critic_trace = build_trace(
            role="CRITIC",
            identity=_identity(),
            prompt=critic_prompt_text,
            input_packet_hash=critic_packet.packet_hash,
            raw_response=critic_raw,
            parsed_output=report,
            parent_candidate_id=designer_packet.parent_candidate_id,
            child_candidate_id=child.candidate_id,
            evaluation_hash=evidence.evaluation_hash,
            evidence_package_hash=evidence.package_hash,
        )
        self.assertEqual(critic_trace.authority_status, "MODEL_EXPERIMENT_TRACE_ONLY")

        print("LOOM_REAL_MODEL_RUN001_RESULT=" + json.dumps({
            "proposal": asdict(proposal),
            "execution": asdict(execution),
            "hard_constraints": [asdict(row) for row in child_eval.hard_constraints],
            "objective_vector": [asdict(row) for row in child_eval.objective_vector],
            "evidence_package_hash": evidence.package_hash,
            "evaluation_hash": evidence.evaluation_hash,
            "designer_trace": asdict(designer_trace),
            "critic_packet_hash": critic_packet.packet_hash,
            "report": asdict(report),
            "critique": asdict(critique),
            "critic_trace": asdict(critic_trace),
            "flight_dynamics_authority": False,
            "canon_changed": False,
            "production_shipclasses_changed": False,
        }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
