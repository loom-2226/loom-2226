import unittest

from src.wayfarer_rcs_physical_requirement_envelope import build_physical_requirement_envelope


class TestWayfarerRCSPhysicalRequirementEnvelope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_physical_requirement_envelope()

    def test_preserves_requirement_not_hardware_boundary(self):
        r = self.result
        self.assertEqual(r["authority"]["claim"], "PHYSICAL_REQUIREMENT_ENVELOPE_ONLY")
        self.assertFalse(r["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(r["authority"]["working_fluid_certified"])
        self.assertEqual(r["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(r["authority"]["llm_calculation_authority"], "ZERO")

    def test_binds_sampled_demand_without_promoting_trace_artifacts(self):
        r = self.result
        demand = r["sampled_demand_basis"]
        self.assertGreater(demand["maximum_sampled_thrust_N"], 0.0)
        self.assertGreater(demand["sampled_exact_trace_mib_upper_bound_Ns"], 0.0)
        self.assertEqual(
            r["requirements"]["minimum_impulse_control"],
            "RESOLVE_AT_OR_BELOW_SAMPLED_EXACT_TRACE_UPPER_BOUND_THEN_REQUALIFY_DISCRETIZED_LOOP",
        )
        self.assertEqual(
            r["requirements"]["response"],
            "MEET_CLOSED_LOOP_DEMAND_WITH_EVIDENCE_BACKED_RESPONSE_MODEL_THEN_REQUALIFY",
        )

    def test_requires_life_and_installation_evidence_without_inventing_values(self):
        req = self.result["requirements"]
        self.assertEqual(req["cycle_life"], "DERIVE_FROM_MISSION_DUTY_AND_TOTAL_IMPULSE_PROFILE")
        self.assertEqual(req["plume"], "FINITE_PLUME_CLEARANCE_AND_EXTERNAL_HARDWARE_INTERFERENCE_REQUIRED")
        self.assertEqual(req["structure"], "MOUNT_LOAD_PATH_AND_LOCAL_STRUCTURE_QUALIFICATION_REQUIRED")
        self.assertIsNone(req["selected_working_fluid"])
        self.assertIsNone(req["selected_exhaust_velocity_m_s"])
        self.assertIsNone(req["selected_vectoring_mechanism"])

    def test_next_step_is_physical_trade(self):
        self.assertEqual(
            self.result["qualified_next_step"],
            "TRADE_PROPELLANT_ACTUATOR_AND_VECTORING_CANDIDATES_AGAINST_REQUIREMENT_ENVELOPE",
        )


if __name__ == "__main__":
    unittest.main()
