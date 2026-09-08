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
    execute_designer_response,
)

RAW_PATH = ROOT / "research" / "model_runs" / "wayfarer_2026-09-08_run001" / "designer_raw.json"
EXPECTED_PACKET_HASH = "65008bca2acfeb352ff48991a728010796c6aa31add924cc35d6881ad00698d6"


class WayfarerRealModelPacketExportTests(unittest.TestCase):
    def test_execute_first_real_designer_response_and_export_critic_packet(self):
        packet = build_designer_packet(2226)
        prompt = designer_prompt(packet)
        self.assertEqual(packet.authority_status, "MODEL_INPUT_ONLY")
        self.assertEqual(packet.packet_hash, EXPECTED_PACKET_HASH)

        raw = RAW_PATH.read_text(encoding="utf-8")
        packet2, proposal, child, execution, child_eval, evidence = execute_designer_response(raw, seed=2226)
        self.assertEqual(packet2, packet)
        self.assertEqual(proposal.proposer_model, "GPT-5.6 Sol")
        self.assertEqual(proposal.authority_claim, "PROPOSAL_ONLY")
        self.assertEqual(execution.authority_status, "CANDIDATE_DERIVATION_ONLY")
        self.assertFalse(evidence.flight_dynamics_authority)
        self.assertFalse(evidence.canon_changed)
        self.assertFalse(evidence.production_shipclasses_changed)

        trace = build_trace(
            role="DESIGNER",
            identity=ModelIdentity(
                model_id="GPT-5.6 Sol",
                provider="OpenAI ChatGPT",
                configuration="interactive-project-session; hidden sampling configuration",
            ),
            prompt=prompt,
            input_packet_hash=packet.packet_hash,
            raw_response=raw,
            parsed_output=proposal,
            parent_candidate_id=packet.parent_candidate_id,
            child_candidate_id=child.candidate_id,
            evaluation_hash=evidence.evaluation_hash,
            evidence_package_hash=evidence.package_hash,
        )
        self.assertEqual(trace.authority_status, "MODEL_EXPERIMENT_TRACE_ONLY")

        critic_packet = build_critic_packet(child=child, child_eval=child_eval, evidence=evidence)
        print("LOOM_REAL_MODEL_DESIGNER_RESULT=" + json.dumps({
            "proposal": asdict(proposal),
            "execution": asdict(execution),
            "hard_constraints": [asdict(row) for row in child_eval.hard_constraints],
            "objective_vector": [asdict(row) for row in child_eval.objective_vector],
            "evidence_package_hash": evidence.package_hash,
            "evaluation_hash": evidence.evaluation_hash,
            "trace": asdict(trace),
        }, sort_keys=True, separators=(",", ":")))
        print("LOOM_REAL_MODEL_CRITIC_PACKET_JSON=" + json.dumps(asdict(critic_packet), sort_keys=True, separators=(",", ":")))
        print("LOOM_REAL_MODEL_CRITIC_PROMPT=" + critic_prompt(critic_packet))


if __name__ == "__main__":
    unittest.main()
