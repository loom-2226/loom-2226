import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from physical_design_core import (
    BoxGeometry,
    CandidateDesign,
    PhysicalComponentInstance,
    PhysicalComponentType,
    PointMassContribution,
    Transform,
    evaluate_mass_inertia,
)
from proposal_mutation_executor import MutationExecutionError, execute_proposal
from shipyard_agent_contracts import DesignMutation, DesignProposal


class ProposalMutationExecutorTests(unittest.TestCase):
    def parent(self):
        return CandidateDesign(
            candidate_id="PARENT-1",
            seed=2226,
            component_types=(
                PhysicalComponentType(
                    type_id="HAB",
                    mass_kg=1000.0,
                    admitted_geometry=BoxGeometry(4.0, 2.0, 2.0),
                    authority_status="ADMITTED",
                    provenance="fixture",
                ),
            ),
            component_instances=(
                PhysicalComponentInstance(
                    instance_id="hab-1",
                    component_type_id="HAB",
                    transform=Transform((0.0, 0.0, 0.0)),
                ),
            ),
            point_masses=(
                PointMassContribution(
                    source_id="store",
                    mass_kg=100.0,
                    centroid_m=(10.0, 0.0, 0.0),
                    authority_status="ADMITTED",
                    provenance="fixture",
                ),
            ),
            provenance_map={"origin": "fixture"},
            solver_version="BASIC-PY-FIXTURE",
        )

    def proposal(self, *mutations):
        return DesignProposal(
            proposal_id="PROP-1",
            parent_candidate_id="PARENT-1",
            requirements_hash="REQ-HASH",
            institution_context_hash="INST-HASH",
            architecture_family="AXIAL",
            mutations=tuple(mutations),
            experiment_question="Does the move improve the candidate?",
            proposer_id="designer-a",
            proposer_model="model-neutral",
        )

    def test_translation_returns_normal_candidate_consumable_by_existing_core(self):
        proposal = self.proposal(
            DesignMutation(
                mutation_id="M1",
                operation="SET_INSTANCE_TRANSLATION",
                target="hab-1",
                value_json='{"translation_m":[2.0,0.0,0.0]}',
                rationale="Move habitation aft for COM study",
                evidence_refs=("E-COM-1",),
            )
        )
        child, record = execute_proposal(self.parent(), proposal)
        self.assertNotEqual(child.candidate_id, "PARENT-1")
        self.assertEqual(child.component_instances[0].transform.translation_m, (2.0, 0.0, 0.0))
        self.assertEqual(record.authority_status, "CANDIDATE_DERIVATION_ONLY")
        self.assertFalse(record.flight_dynamics_authority)
        self.assertFalse(record.canon_changed)
        self.assertFalse(record.production_shipclasses_changed)

        # Critical compatibility test: the existing basic deterministic core consumes the child unchanged.
        mass, com, *_ = evaluate_mass_inertia(child)
        self.assertAlmostEqual(mass, 1100.0)
        self.assertGreater(com[0], 2.0)

    def test_execution_is_deterministic(self):
        mutation = DesignMutation(
            mutation_id="M1",
            operation="SET_INSTANCE_TRANSLATION",
            target="hab-1",
            value_json='{"translation_m":[2,0,0]}',
            rationale="COM study",
        )
        a, ra = execute_proposal(self.parent(), self.proposal(mutation))
        b, rb = execute_proposal(self.parent(), self.proposal(mutation))
        self.assertEqual(a.candidate_id, b.candidate_id)
        self.assertEqual(ra, rb)

    def test_unknown_target_fails_closed(self):
        mutation = DesignMutation(
            mutation_id="M1",
            operation="SET_INSTANCE_ACTIVE",
            target="missing",
            value_json="false",
            rationale="test",
        )
        with self.assertRaises(MutationExecutionError):
            execute_proposal(self.parent(), self.proposal(mutation))

    def test_unknown_operation_fails_closed(self):
        mutation = DesignMutation(
            mutation_id="M1",
            operation="SET_ENGINEERING_PASS",
            target="hab-1",
            value_json="true",
            rationale="illegal authority mutation",
        )
        with self.assertRaises(MutationExecutionError):
            execute_proposal(self.parent(), self.proposal(mutation))

    def test_translation_schema_is_exact(self):
        mutation = DesignMutation(
            mutation_id="M1",
            operation="SET_INSTANCE_TRANSLATION",
            target="hab-1",
            value_json='{"translation_m":[2,0,0],"authority":"PASS"}',
            rationale="smuggle authority",
        )
        with self.assertRaises(MutationExecutionError):
            execute_proposal(self.parent(), self.proposal(mutation))

    def test_parent_mismatch_fails_closed(self):
        proposal = DesignProposal(
            proposal_id="PROP-X",
            parent_candidate_id="OTHER",
            requirements_hash="REQ-HASH",
            institution_context_hash="INST-HASH",
            architecture_family="AXIAL",
            mutations=(
                DesignMutation("M1", "SET_INSTANCE_ACTIVE", "hab-1", "false", "test"),
            ),
            experiment_question="test",
            proposer_id="designer-a",
            proposer_model="model-neutral",
        )
        with self.assertRaises(MutationExecutionError):
            execute_proposal(self.parent(), proposal)

    def test_active_toggle_uses_json_boolean_only(self):
        bad = DesignMutation("M1", "SET_INSTANCE_ACTIVE", "hab-1", '"false"', "test")
        with self.assertRaises(MutationExecutionError):
            execute_proposal(self.parent(), self.proposal(bad))


if __name__ == "__main__":
    unittest.main()
