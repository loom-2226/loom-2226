"""Hostile contract tests for CIVPROP Mission / Knowledge V1."""
from __future__ import annotations

from dataclasses import replace
import copy
import json
from pathlib import Path
import unittest

from .mission_knowledge_v1 import (
    BinaryObservationRuntime,
    KnowledgeRuntime,
    MissionDecisionInputs,
    MissionKnowledgeRuntime,
    load_mission_knowledge_package,
)


HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "mission_knowledge_v1.json"


class MissionKnowledgeV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(PARAMETERS.read_text())
        cls.package = load_mission_knowledge_package(cls.raw)
        cls.runtime = MissionKnowledgeRuntime(cls.package)

    def test_missions_are_actions_not_infrastructure(self):
        self.assertEqual(
            {x.mission_archetype_id for x in self.package.missions},
            {"LUNAR_RESOURCE_PROSPECTING_SURVEY"},
        )
        mission = self.package.missions[0]
        self.assertEqual(mission.action_kind, "MISSION")
        self.assertEqual(mission.project_economics_id, "PROSPECTING_SURVEY")
        self.assertEqual(mission.target_question_id, "MOON_POLAR_WATER_PRESENT")

    def test_default_follow_on_value_is_unknown_not_invented(self):
        decision = self.package.decision_models[0]
        self.assertEqual(decision.success_value.status, "UNKNOWN")
        self.assertIsNone(decision.success_value.value)
        self.assertEqual(decision.success_value.unit, "USD_2026_billion")

    def test_unknown_follow_on_value_forces_wait(self):
        state = self.runtime.initial_knowledge(
            actor_id="AUS",
            question_id="MOON_POLAR_WATER_PRESENT",
            year=2026,
        )
        decision = self.runtime.evaluate(
            state,
            MissionDecisionInputs(
                year=2026,
                actor_id="AUS",
                mission_archetype_id="LUNAR_RESOURCE_PROSPECTING_SURVEY",
                access_status="FEASIBLE",
                capability_status="USABLE",
                budget_status="KNOWN",
                budget_amount=100.0,
                budget_unit="USD_2026_billion",
                mission_cost=0.25,
                continuation_cost=3.0,
                continuation_unit="USD_2026_billion",
            ),
        )
        self.assertEqual(decision.action, "WAIT")
        self.assertIn("FOLLOW_ON_VALUE_UNKNOWN", decision.rationale_codes)

    def test_known_fixture_value_can_produce_positive_voi_without_hidden_truth(self):
        raw = copy.deepcopy(self.raw)
        raw["decision_models"][0]["success_value"] = {
            "status": "SCENARIO_ASSUMPTION",
            "value": 5.0,
            "unit": "USD_2026_billion",
            "provenance_refs": ["test:decision-value"],
        }
        runtime = MissionKnowledgeRuntime(load_mission_knowledge_package(raw))
        state = runtime.initial_knowledge(
            actor_id="LAB_PUBLIC",
            question_id="MOON_POLAR_WATER_PRESENT",
            year=2029,
        )
        decision = runtime.evaluate(
            state,
            MissionDecisionInputs(
                year=2029,
                actor_id="LAB_PUBLIC",
                mission_archetype_id="LUNAR_RESOURCE_PROSPECTING_SURVEY",
                access_status="FEASIBLE",
                capability_status="USABLE",
                budget_status="KNOWN",
                budget_amount=70.0,
                budget_unit="USD_2026_billion",
                mission_cost=0.25,
                continuation_cost=3.0,
                continuation_unit="USD_2026_billion",
            ),
        )
        self.assertEqual(decision.action, "COMMIT_MISSION")
        self.assertGreater(decision.expected_value_of_information, 0.0)

    def test_observation_is_seeded_and_hidden_truth_only_enters_observation_runtime(self):
        observer = BinaryObservationRuntime(self.package, seed=42)
        mission = self.runtime.mission_record(
            actor_id="AUS",
            mission_archetype_id="LUNAR_RESOURCE_PROSPECTING_SURVEY",
            committed_year=2029,
            execution_year=2031,
            capital_cost=0.25,
            capital_unit="USD_2026_billion",
        )
        first = observer.observe(
            mission=mission,
            hidden_present=True,
            year=2031,
        )
        second = observer.observe(
            mission=mission,
            hidden_present=True,
            year=2031,
        )
        self.assertEqual(first, second)
        self.assertEqual(first.authority_class, "SIMULATED_OBSERVATION")
        self.assertEqual(first.error_model, "BERNOULLI_CONFUSION_MATRIX_V1")

    def test_unrelated_observation_does_not_change_keyed_draw(self):
        observer = BinaryObservationRuntime(self.package, seed=42)
        mission = self.runtime.mission_record(
            actor_id="AUS",
            mission_archetype_id="LUNAR_RESOURCE_PROSPECTING_SURVEY",
            committed_year=2029,
            execution_year=2031,
            capital_cost=0.25,
            capital_unit="USD_2026_billion",
        )
        before = observer.observe(
            mission=mission,
            hidden_present=True,
            year=2031,
        )
        _ = observer.keyed_unit(
            "unrelated",
            "mission:someone-else",
            2030,
        )
        after = observer.observe(
            mission=mission,
            hidden_present=True,
            year=2031,
        )
        self.assertEqual(before, after)

    def test_favourable_and_adverse_observations_update_bayes_correctly(self):
        state = self.runtime.initial_knowledge(
            actor_id="AUS",
            question_id="MOON_POLAR_WATER_PRESENT",
            year=2026,
        )
        model = self.package.observation_models[0]
        favourable = self.runtime.synthetic_observation_for_test(
            actor_id="AUS",
            mission_id="m-positive",
            question_id=state.question_id,
            year=2027,
            detected=True,
        )
        adverse = replace(
            favourable,
            observation_id="obs-negative",
            mission_id="m-negative",
            detected=False,
        )
        positive = KnowledgeRuntime.update(state, favourable)
        negative = KnowledgeRuntime.update(state, adverse)

        p = state.probability
        expected_positive = (
            p * model.sensitivity
            / (
                p * model.sensitivity
                + (1 - p) * model.false_positive_probability
            )
        )
        expected_negative = (
            p * (1 - model.sensitivity)
            / (
                p * (1 - model.sensitivity)
                + (1 - p) * (1 - model.false_positive_probability)
            )
        )
        self.assertAlmostEqual(positive.probability, expected_positive, places=12)
        self.assertAlmostEqual(negative.probability, expected_negative, places=12)
        self.assertGreater(positive.probability, state.probability)
        self.assertLess(negative.probability, state.probability)

    def test_duplicate_wrong_scope_and_backward_observation_fail_closed(self):
        state = self.runtime.initial_knowledge(
            actor_id="AUS",
            question_id="MOON_POLAR_WATER_PRESENT",
            year=2026,
        )
        observation = self.runtime.synthetic_observation_for_test(
            actor_id="AUS",
            mission_id="m1",
            question_id=state.question_id,
            year=2027,
            detected=True,
        )
        updated = KnowledgeRuntime.update(state, observation)
        with self.assertRaises(ValueError):
            KnowledgeRuntime.update(updated, observation)

        wrong_scope = replace(
            observation,
            observation_id="wrong-scope",
            location_id="EARTH_ORBIT",
        )
        with self.assertRaises(ValueError):
            KnowledgeRuntime.update(state, wrong_scope)

        backward = replace(
            observation,
            observation_id="backward",
            year=2025,
        )
        with self.assertRaises(ValueError):
            KnowledgeRuntime.update(state, backward)

    def test_success_value_unit_must_match_project_capital_unit(self):
        raw = copy.deepcopy(self.raw)
        raw["decision_models"][0]["success_value"]["unit"] = "AUD"
        with self.assertRaises(ValueError):
            load_mission_knowledge_package(raw)


if __name__ == "__main__":
    unittest.main()
