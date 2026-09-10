import unittest

from qualification.synthesis.generative_candidate_compiler import compile_wayfarer_survivor_family
from qualification.synthesis.shipyard_m2a_attitude_coupling import (
    Q4_SOURCE_COMMIT,
    candidate_attitude_signature,
    maneuver_aware_leg_summary,
)


class ShipyardM2AAttitudeCouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.family = compile_wayfarer_survivor_family(2226)

    def test_q4_source_is_pinned(self):
        self.assertEqual(Q4_SOURCE_COMMIT, "e2df887d5e901eed9378c7aeb7d4964040b9a7e6")

    def test_survivor_layouts_produce_distinct_qualified_attitude_signatures(self):
        signatures = [candidate_attitude_signature(row) for row in self.family]
        self.assertGreaterEqual(len(signatures), 2)
        self.assertGreater(len({round(row["pitch_inertia_kg_m2"], 6) for row in signatures}), 1)
        self.assertGreater(len({round(row["pitch_180_s"], 6) for row in signatures}), 1)
        for row in signatures:
            self.assertEqual(row["authority"], "Q4_HUD_FINITE_ATTITUDE_ENGINEERING_QUALIFICATION")
            self.assertFalse(row["flight_dynamics_authority"])

    def test_same_raw_navigator_leg_gets_candidate_dependent_maneuver_time(self):
        raw_leg = {
            "solver_model": "NAV-V1-A",
            "arrival": {"total_nav_time_s": 123456.0},
            "terminal_burn": {"remass_used_t": 12.5},
        }
        summaries = [maneuver_aware_leg_summary(row, raw_leg) for row in self.family]
        self.assertEqual({row["raw_navigator_time_s"] for row in summaries}, {123456.0})
        self.assertGreater(len({round(row["brake_flip_time_s"], 6) for row in summaries}), 1)
        self.assertGreater(len({round(row["maneuver_aware_total_time_s"], 6) for row in summaries}), 1)
        for row in summaries:
            self.assertFalse(row["raw_navigator_output_modified"])
            self.assertEqual(row["m2a_disposition"], "COUPLED_MISSION_DIFFERENTIATION_DEMONSTRATED")


if __name__ == "__main__":
    unittest.main()
