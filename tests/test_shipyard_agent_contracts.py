from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "qualification" / "synthesis" / "shipyard_agent_contracts.py"
spec = importlib.util.spec_from_file_location("shipyard_agent_contracts", PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class ShipyardAgentContractTests(unittest.TestCase):
    def context(self):
        return mod.ShipyardInstitutionContext(
            institution_id="YARD_TEST",
            context_date="2226-01-01",
            progenitor_cultures=("CULTURE_A",),
            engineering_lineage=("MINING",),
            design_doctrine=("FIELD_REPAIRABLE",),
            aesthetic_principles=("STRUCTURAL_HONESTY",),
            manufacturing_capabilities=("ROBOTIC_WELDING",),
            material_constraints=("TITANIUM_LIMITED",),
            economic_constraints=("CAPEX_CONSTRAINED",),
            historical_design_refs=("CLASS_2190_A",),
            provenance_refs=("CANON_REF_1",),
            authority_status="QUALIFICATION_ONLY",
        )

    def test_institution_context_valid_and_deterministic(self):
        ctx = self.context()
        mod.validate_institution_context(ctx)
        self.assertEqual(mod.content_hash(ctx), mod.content_hash(ctx))

    def test_context_rejects_string_as_sequence(self):
        ctx = self.context()
        bad = mod.ShipyardInstitutionContext(**{**ctx.__dict__, "progenitor_cultures": "NOT_A_SEQUENCE"})
        with self.assertRaises(mod.AgentContractError):
            mod.validate_institution_context(bad)

    def test_designer_is_proposal_only(self):
        mutation = mod.DesignMutation("M1", "SET", "tank.count", "6", "Explore alternate tank topology")
        row = mod.DesignProposal("P1", "C1", "REQ", "INST", "SIX_TANK", (mutation,), "Does this improve packaging?", "SOL", "MODEL")
        mod.validate_proposal(row)
        bad = mod.DesignProposal(**{**row.__dict__, "authority_claim": "PHYSICS_PASS"})
        with self.assertRaises(mod.AgentContractError):
            mod.validate_proposal(bad)

    def test_mutation_requires_machine_readable_value(self):
        mutation = mod.DesignMutation("M1", "SET", "tank.count", "six tanks please", "Try it")
        row = mod.DesignProposal("P1", "C1", "REQ", "INST", "ALT", (mutation,), "Question", "SOL", "MODEL")
        with self.assertRaises(mod.AgentContractError):
            mod.validate_proposal(row)

    def test_critic_is_critique_only(self):
        issue = mod.CritiqueIssue("I1", "MAINTAINABILITY", "HIGH", "Reactor extraction path is obstructed", ("EVAL:ACCESS:4",), "Test reactor removal envelope")
        row = mod.DesignCritique("CR1", "C1", "EVAL", "INST", (issue,), "SOL", "MODEL", "REVISE")
        mod.validate_critique(row)
        bad = mod.DesignCritique(**{**row.__dict__, "authority_claim": "REJECTED_BY_PHYSICS"})
        with self.assertRaises(mod.AgentContractError):
            mod.validate_critique(bad)

    def test_duplicate_issue_ids_fail_closed(self):
        issue = mod.CritiqueIssue("I1", "AESTHETIC", "LOW", "Poor axial hierarchy", (), "Generate alternate composition")
        row = mod.DesignCritique("CR1", "C1", "EVAL", "INST", (issue, issue), "SOL", "MODEL", "REVISE")
        with self.assertRaises(mod.AgentContractError):
            mod.validate_critique(row)


if __name__ == "__main__":
    unittest.main(verbosity=2)
