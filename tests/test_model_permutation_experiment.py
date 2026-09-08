from __future__ import annotations

import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

SYNTH = Path(__file__).resolve().parents[1] / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from model_permutation_experiment import (  # noqa: E402
    ARCHITECTURAL_REVIEW_AUTHORITY,
    CRITIC_PACKET_AUTHORITY,
    DESIGNER_PACKET_AUTHORITY,
    ModelIdentity,
    ModelPermutationError,
    build_critic_packet,
    build_designer_packet,
    build_trace,
    critic_prompt,
    designer_prompt,
    execute_critic_response,
    execute_designer_response,
    parse_critic_response,
    parse_designer_response,
)
from shipyard_agent_contracts import AgentContractError  # noqa: E402


class ModelPermutationExperimentTests(unittest.TestCase):
    def _designer_raw(self, packet, *, dx=0.10):
        launch = next(row for row in packet.candidate_instances if row.instance_id == "planetary_launch")
        x, y, z = launch.translation_m
        return json.dumps({
            "proposal_id": "MODEL-PROP-001",
            "parent_candidate_id": packet.parent_candidate_id,
            "requirements_hash": packet.requirements_hash,
            "institution_context_hash": packet.institution_context_hash,
            "architecture_family": packet.architecture_family,
            "mutations": [{
                "mutation_id": "MODEL-MUT-001",
                "operation": "SET_INSTANCE_TRANSLATION",
                "target": "planetary_launch",
                "value_json": json.dumps({"translation_m": [x + dx, y, z]}, separators=(",", ":")),
                "rationale": "Probe a small axial placement change without asserting feasibility.",
                "evidence_refs": ["candidate_instance:planetary_launch"],
            }],
            "experiment_question": "Does this modest axial relocation survive the unchanged deterministic evaluator?",
            "proposer_id": "TEST_DESIGNER",
            "proposer_model": "TEST_MODEL",
            "authority_claim": "PROPOSAL_ONLY",
        }, separators=(",", ":"))

    def _critic_raw(self, packet):
        return json.dumps({
            "report_id": "MODEL-CRIT-001",
            "candidate_id": packet.candidate_id,
            "evidence_package_hash": packet.evidence_package_hash,
            "doctrine_hash": packet.doctrine_hash,
            "reviewer_id": "TEST_SOL",
            "reviewer_model": "TEST_MODEL",
            "findings": [{
                "finding_id": "MODEL-FIND-001",
                "criterion_id": "SOL-LEGIBILITY",
                "severity": "NOTE",
                "claim": "The supplied numerical evidence does not establish visual legibility.",
                "evidence_refs": [f"evidence_package_sha256:{packet.evidence_package_hash}"],
                "experiment_request": "Render parent and child from the same viewpoint before judging visual legibility.",
                "authority_status": ARCHITECTURAL_REVIEW_AUTHORITY,
            }],
            "overall_recommendation": "ACCEPT",
            "architectural_summary": "No stronger visual judgment is supported by the supplied evidence.",
            "physical_feasibility_claimed": False,
            "flight_dynamics_authority_claimed": False,
            "canon_change_claimed": False,
            "production_shipclass_change_claimed": False,
            "authority_status": ARCHITECTURAL_REVIEW_AUTHORITY,
        }, separators=(",", ":"))

    def test_designer_packet_is_deterministic_and_model_input_only(self):
        first = build_designer_packet(2226)
        second = build_designer_packet(2226)
        self.assertEqual(first, second)
        self.assertEqual(first.authority_status, DESIGNER_PACKET_AUTHORITY)
        self.assertEqual(len(first.packet_hash), 64)
        self.assertIn("SET_INSTANCE_TRANSLATION", first.allowed_operations)
        self.assertTrue(any(row.instance_id == "planetary_launch" for row in first.candidate_instances))
        self.assertEqual(designer_prompt(first), designer_prompt(second))

    def test_valid_designer_output_runs_through_existing_wayfarer_backend(self):
        packet = build_designer_packet(2226)
        raw = self._designer_raw(packet)
        packet2, proposal, child, execution, child_eval, evidence = execute_designer_response(raw, seed=2226)
        self.assertEqual(packet, packet2)
        self.assertEqual(proposal.authority_claim, "PROPOSAL_ONLY")
        self.assertEqual(execution.authority_status, "CANDIDATE_DERIVATION_ONLY")
        self.assertTrue(child.candidate_id.startswith("CAND-MUT-"))
        self.assertEqual(evidence.candidate_id, child.candidate_id)
        self.assertEqual(evidence.evaluation_hash, packet2 and evidence.evaluation_hash)
        self.assertFalse(evidence.flight_dynamics_authority)
        self.assertFalse(evidence.canon_changed)
        self.assertFalse(evidence.production_shipclasses_changed)
        self.assertTrue(all(row.passed for row in child_eval.hard_constraints))

    def test_designer_output_is_strict_no_extra_keys_no_unknown_target_no_authority_escalation(self):
        packet = build_designer_packet(2226)
        row = json.loads(self._designer_raw(packet))
        row["engineering_pass"] = True
        with self.assertRaises(ModelPermutationError):
            parse_designer_response(json.dumps(row), packet)

        row = json.loads(self._designer_raw(packet))
        row["mutations"][0]["target"] = "invented_magic_lattice"
        with self.assertRaises(ModelPermutationError):
            parse_designer_response(json.dumps(row), packet)

        row = json.loads(self._designer_raw(packet))
        row["authority_claim"] = "ENGINEERING_PASS"
        with self.assertRaises(AgentContractError):
            parse_designer_response(json.dumps(row), packet)

    def test_critic_packet_and_response_are_hash_linked_and_evidence_bounded(self):
        designer_packet = build_designer_packet(2226)
        _, _, child, _, child_eval, evidence = execute_designer_response(self._designer_raw(designer_packet), seed=2226)
        packet = build_critic_packet(child=child, child_eval=child_eval, evidence=evidence)
        self.assertEqual(packet.authority_status, CRITIC_PACKET_AUTHORITY)
        self.assertEqual(packet.candidate_id, child.candidate_id)
        self.assertEqual(packet.evidence_package_hash, evidence.package_hash)
        self.assertEqual(len(packet.packet_hash), 64)
        self.assertIn("Numerical evidence is not visual evidence", packet.hard_rule)
        self.assertIn(packet.packet_hash, critic_prompt(packet))

        raw = self._critic_raw(packet)
        packet2, report, critique = execute_critic_response(raw, child=child, child_eval=child_eval, evidence=evidence)
        self.assertEqual(packet, packet2)
        self.assertEqual(report.authority_status, ARCHITECTURAL_REVIEW_AUTHORITY)
        self.assertEqual(critique.authority_claim, "CRITIQUE_ONLY")
        self.assertEqual(critique.evaluation_hash, evidence.evaluation_hash)
        self.assertEqual(critique.candidate_id, child.candidate_id)

    def test_critic_response_fails_closed_on_hash_mismatch_or_authority_claim(self):
        designer_packet = build_designer_packet(2226)
        _, _, child, _, child_eval, evidence = execute_designer_response(self._designer_raw(designer_packet), seed=2226)
        packet = build_critic_packet(child=child, child_eval=child_eval, evidence=evidence)

        row = json.loads(self._critic_raw(packet))
        row["evidence_package_hash"] = "0" * 64
        with self.assertRaises(ModelPermutationError):
            parse_critic_response(json.dumps(row), packet)

        row = json.loads(self._critic_raw(packet))
        row["physical_feasibility_claimed"] = True
        with self.assertRaises(Exception):
            parse_critic_response(json.dumps(row), packet)

    def test_trace_records_model_prompt_raw_and_parsed_hashes_without_authority(self):
        packet = build_designer_packet(2226)
        raw = self._designer_raw(packet)
        packet2, proposal, child, _, child_eval, evidence = execute_designer_response(raw, seed=2226)
        prompt = designer_prompt(packet2)
        trace = build_trace(
            role="DESIGNER",
            identity=ModelIdentity(model_id="MODEL-A", provider="TEST", configuration="temperature=0"),
            prompt=prompt,
            input_packet_hash=packet2.packet_hash,
            raw_response=raw,
            parsed_output=proposal,
            parent_candidate_id=packet2.parent_candidate_id,
            child_candidate_id=child.candidate_id,
            evaluation_hash=evidence.evaluation_hash,
            evidence_package_hash=evidence.package_hash,
        )
        self.assertEqual(trace.authority_status, "MODEL_EXPERIMENT_TRACE_ONLY")
        self.assertEqual(len(trace.prompt_hash), 64)
        self.assertEqual(len(trace.raw_response_hash), 64)
        self.assertEqual(len(trace.parsed_output_hash), 64)
        self.assertFalse(trace.flight_dynamics_authority)
        self.assertFalse(trace.canon_changed)
        self.assertFalse(trace.production_shipclasses_changed)

    def test_packet_authority_escalation_is_rejected(self):
        packet = build_designer_packet(2226)
        with self.assertRaises(ModelPermutationError):
            designer_prompt(replace(packet, authority_status="ENGINEERING_PASS"))


if __name__ == "__main__":
    unittest.main()
