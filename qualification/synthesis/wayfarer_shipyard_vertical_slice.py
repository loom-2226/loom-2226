from __future__ import annotations

import dataclasses
import hashlib
import json

from architectural_review import (
    DesignReviewFinding,
    DesignReviewReport,
    content_hash as architectural_hash,
    functional_expressionism_doctrine,
    validate_report,
)
from proposal_mutation_executor import execute_proposal
from shipyard_agent_contracts import DesignMutation, DesignProposal
from wayfarer_s1_adapter import evaluate_candidate
from wayfarer_s1_solver import DEFAULT_SEED, solve

EXPERIMENT_VERSION = "LOOM_WAYFARER_SHIPYARD_VERTICAL_SLICE_v0.1"
STATUS = ("ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION")


def _evaluation_hash(row) -> str:
    payload = json.dumps(dataclasses.asdict(row), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run(seed: int = DEFAULT_SEED) -> dict:
    baseline = solve(seed)
    parent = baseline.candidate
    parent_eval = baseline.evaluation
    launch = next(row for row in parent.component_instances if row.instance_id == "planetary_launch")
    x, y, z = launch.transform.translation_m

    # One deliberately modest admitted change. The Designer role proposes; it does not evaluate.
    proposed_x = float(x) + 0.25
    proposal = DesignProposal(
        proposal_id="WAYFARER-VSLICE-PROP-001",
        parent_candidate_id=parent.candidate_id,
        requirements_hash="WAYFARER_S1_EXISTING_REQUIREMENTS",
        institution_context_hash="WAYFARER_VERTICAL_SLICE_FIXTURE_CONTEXT",
        architecture_family="WAYFARER_COURIER_BASELINE",
        mutations=(DesignMutation(
            mutation_id="WAYFARER-VSLICE-MUT-001",
            operation="SET_INSTANCE_TRANSLATION",
            target="planetary_launch",
            value_json=json.dumps({"translation_m": [proposed_x, float(y), float(z)]}, separators=(",", ":")),
            rationale="Probe whether a small aft launch-envelope relocation remains legal under the existing Wayfarer S1 evaluator.",
            evidence_refs=("qualification/synthesis/wayfarer_s1_solver.py",),
        ),),
        experiment_question="Does a +0.25 m axial launch-envelope relocation remain legal under the unchanged Wayfarer S1 deterministic evaluator?",
        proposer_id="DESIGNER_FIXTURE",
        proposer_model="MODEL_NEUTRAL_TEST_FIXTURE",
    )

    child, execution = execute_proposal(parent, proposal)
    child_eval = evaluate_candidate(child)

    doctrine = functional_expressionism_doctrine()
    evidence_hash = _evaluation_hash(child_eval)
    all_hard_pass = all(row.passed for row in child_eval.hard_constraints)
    finding = DesignReviewFinding(
        finding_id="SOL-VSLICE-001",
        criterion_id="SOL-LEGIBILITY",
        severity="NOTE" if all_hard_pass else "REJECT",
        claim=(
            "The mutation remains a legible axial placement change, but numerical S1 evidence alone is insufficient for a stronger architectural judgment."
            if all_hard_pass else
            "The proposed placement is not a viable architectural candidate because the unchanged deterministic evaluator rejects at least one hard constraint."
        ),
        evidence_refs=(f"evaluation_sha256:{evidence_hash}", f"candidate:{child.candidate_id}"),
        experiment_request="Render parent and child from the same viewpoint and compare load-path, service-access, and axial-hierarchy legibility before making a stronger architectural claim.",
    )
    report = DesignReviewReport(
        report_id="SOL-WAYFARER-VSLICE-001",
        candidate_id=child.candidate_id,
        evidence_package_hash=evidence_hash,
        doctrine_hash=architectural_hash(doctrine),
        reviewer_id="SOL_FIXTURE",
        reviewer_model="MODEL_NEUTRAL_TEST_FIXTURE",
        findings=(finding,),
        overall_recommendation="ACCEPT" if all_hard_pass else "REJECT",
        architectural_summary="First closed-loop Wayfarer mutation review. Architectural authority remains separate from engineering evaluation.",
    )
    validate_report(report, doctrine)

    return {
        "experiment_version": EXPERIMENT_VERSION,
        "status": STATUS,
        "parent_candidate_id": parent.candidate_id,
        "child_candidate_id": child.candidate_id,
        "proposal_authority": proposal.authority_claim,
        "execution_authority": execution.authority_status,
        "parent_evaluation_hash": _evaluation_hash(parent_eval),
        "child_evaluation_hash": evidence_hash,
        "parent_launch_x_m": float(x),
        "child_launch_x_m": proposed_x,
        "child_hard_constraints_pass": all_hard_pass,
        "sol_recommendation": report.overall_recommendation,
        "sol_finding": finding.claim,
        "sol_experiment_request": finding.experiment_request,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }
