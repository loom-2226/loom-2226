from __future__ import annotations

import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from governed_ship_synthesis import build_wayfarer_governed_synthesis  # noqa: E402
from minimum_spatial_validation import (  # noqa: E402
    CHECK_PASS as R2_CHECK_PASS,
    PAIRWISE_OVERLAP,
    build_minimum_spatial_validation,
)
from semantic_geometry import build_semantic_geometry  # noqa: E402
from spatial_rule_contract import (  # noqa: E402
    DOMAIN_ADMITTED_COMPLETE,
    DOMAIN_CLEARANCE,
    DOMAIN_OPEN,
    REQUIRED_DOMAINS,
    PairClearanceRule,
    SpatialRuleContractError,
    SpatialRuleDomainState,
    build_spatial_rule_contract,
    build_wayfarer_spatial_rule_contract,
    canonical_json as rule_json,
    validate_spatial_rule_contract,
)
from spatial_validation_with_rules import (  # noqa: E402
    CHECK_OPEN,
    CHECK_PASS,
    CHECK_REVIEW,
    READINESS_BLOCKED,
    R2A_AUTHORITY,
    SpatialValidationWithRulesError,
    build_spatial_validation_with_rules,
    canonical_json as r2a_json,
    validate_spatial_validation_with_rules,
)


class WayfarerSpatialRuleContractR2ATests(unittest.TestCase):
    def base(self):
        source = build_wayfarer_governed_synthesis(2226)
        semantic = build_semantic_geometry(source)
        r2 = build_minimum_spatial_validation(source, semantic)
        rules = build_wayfarer_spatial_rule_contract(source, semantic)
        r2a = build_spatial_validation_with_rules(source, semantic, r2=r2, rules=rules)
        return source, semantic, r2, rules, r2a

    def _domains_with_clearance_complete(self, source, semantic):
        return tuple(
            SpatialRuleDomainState(
                domain=domain,
                status=DOMAIN_ADMITTED_COMPLETE if domain == DOMAIN_CLEARANCE else DOMAIN_OPEN,
                rationale="Synthetic test rule coverage only; not Wayfarer engineering admission.",
                provenance_refs=(source.design_state.candidate_id, semantic.package_hash, "TEST_ONLY"),
            )
            for domain in REQUIRED_DOMAINS
        )

    def _separated_pair(self, r2):
        for row in r2.checks:
            if row.check_type != PAIRWISE_OVERLAP or row.status != R2_CHECK_PASS:
                continue
            gap = math.sqrt(sum(max(v, 0.0) ** 2 for v in row.metric_m))
            if gap > 0.0:
                return row.subject_ids, gap
        self.fail("Wayfarer R2 fixture contains no separated admitted-envelope pair")

    def test_wayfarer_registers_all_rule_domains_as_open_without_inventing_rules(self):
        _, _, _, rules, r2a = self.base()
        self.assertEqual({row.domain for row in rules.domains}, set(REQUIRED_DOMAINS))
        self.assertTrue(all(row.status == DOMAIN_OPEN for row in rules.domains))
        self.assertEqual(rules.pair_clearance_rules, ())
        self.assertEqual(rules.exclusion_rules, ())
        self.assertEqual(len(r2a.evaluations), len(REQUIRED_DOMAINS))
        self.assertTrue(all(row.status == CHECK_OPEN for row in r2a.evaluations))
        self.assertEqual(r2a.readiness_status, READINESS_BLOCKED)
        self.assertFalse(r2a.visual_realization_ready)

    def test_r2a_is_derived_only_and_hash_bound_to_r2_and_rule_contract(self):
        source, semantic, r2, rules, r2a = self.base()
        self.assertEqual(r2a.authority_status, R2A_AUTHORITY)
        self.assertEqual(r2a.source_governed_package_hash, source.package_hash)
        self.assertEqual(r2a.source_semantic_package_hash, semantic.package_hash)
        self.assertEqual(r2a.source_r2_package_hash, r2.package_hash)
        self.assertEqual(r2a.source_rule_contract_hash, rules.package_hash)
        self.assertFalse(r2a.flight_dynamics_authority)
        self.assertFalse(r2a.structural_qualification)
        self.assertFalse(r2a.canon_changed)
        self.assertFalse(r2a.production_shipclasses_changed)
        self.assertFalse(r2a.design_state_mutated)

    def test_admitted_clearance_rule_can_close_that_domain_to_pass(self):
        source, semantic, r2, _, _ = self.base()
        subjects, gap = self._separated_pair(r2)
        domains = self._domains_with_clearance_complete(source, semantic)
        rule = PairClearanceRule(
            rule_id="TEST::CLEARANCE::PASS",
            semantic_object_a=subjects[0],
            semantic_object_b=subjects[1],
            minimum_clearance_m=gap / 2.0,
            rationale="Synthetic governed-rule test only.",
            provenance_refs=("TEST_ONLY",),
        )
        rules = build_spatial_rule_contract(source, semantic, domains=domains, pair_clearance_rules=(rule,))
        r2a = build_spatial_validation_with_rules(source, semantic, r2=r2, rules=rules)
        clearance_rows = [row for row in r2a.evaluations if row.domain == DOMAIN_CLEARANCE]
        self.assertEqual(len(clearance_rows), 1)
        self.assertEqual(clearance_rows[0].status, CHECK_PASS)
        self.assertGreaterEqual(clearance_rows[0].metric_m, clearance_rows[0].threshold_m)
        self.assertFalse(r2a.visual_realization_ready)  # other governed domains remain OPEN

    def test_admitted_clearance_rule_violation_becomes_review_not_fake_pass(self):
        source, semantic, r2, _, _ = self.base()
        subjects, gap = self._separated_pair(r2)
        domains = self._domains_with_clearance_complete(source, semantic)
        rule = PairClearanceRule(
            rule_id="TEST::CLEARANCE::REVIEW",
            semantic_object_a=subjects[0],
            semantic_object_b=subjects[1],
            minimum_clearance_m=gap * 2.0,
            rationale="Synthetic governed-rule test only.",
            provenance_refs=("TEST_ONLY",),
        )
        rules = build_spatial_rule_contract(source, semantic, domains=domains, pair_clearance_rules=(rule,))
        r2a = build_spatial_validation_with_rules(source, semantic, r2=r2, rules=rules)
        clearance_rows = [row for row in r2a.evaluations if row.domain == DOMAIN_CLEARANCE]
        self.assertEqual(clearance_rows[0].status, CHECK_REVIEW)
        self.assertFalse(r2a.visual_realization_ready)

    def test_complete_domain_without_explicit_rule_fails_closed(self):
        source, semantic, _, _, _ = self.base()
        domains = self._domains_with_clearance_complete(source, semantic)
        with self.assertRaises(SpatialRuleContractError):
            build_spatial_rule_contract(source, semantic, domains=domains)

    def test_rule_and_r2a_outputs_are_deterministic(self):
        source_a, semantic_a, r2_a, rules_a, r2a_a = self.base()
        source_b, semantic_b, r2_b, rules_b, r2a_b = self.base()
        self.assertEqual(rules_a, rules_b)
        self.assertEqual(r2a_a, r2a_b)
        self.assertEqual(rule_json(rules_a, source_a, semantic_a), rule_json(rules_b, source_b, semantic_b))
        self.assertEqual(r2a_json(r2a_a, source_a, semantic_a, r2_a, rules_a), r2a_json(r2a_b, source_b, semantic_b, r2_b, rules_b))

    def test_hash_or_authority_tampering_fails_closed(self):
        source, semantic, r2, rules, r2a = self.base()
        with self.assertRaises(SpatialRuleContractError):
            validate_spatial_rule_contract(replace(rules, flight_dynamics_authority=True), source, semantic)
        with self.assertRaises(SpatialValidationWithRulesError):
            validate_spatial_validation_with_rules(
                replace(r2a, source_rule_contract_hash="0" * 64), source, semantic, r2, rules
            )
        with self.assertRaises(SpatialValidationWithRulesError):
            validate_spatial_validation_with_rules(
                replace(r2a, visual_realization_ready=True, readiness_status="READY_FOR_NON_AUTHORITATIVE_VISUAL_REALIZATION"),
                source,
                semantic,
                r2,
                rules,
            )


if __name__ == "__main__":
    unittest.main()
