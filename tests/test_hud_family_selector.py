import unittest

from loom.hud.hud_family_selector import (
    AUTHORITY,
    CONTRACT,
    HudFamily,
    HudFamilyContext,
    live_qualification_selection_payload,
    rendezvous_selection_payload,
    select_hud_family,
    selection_payload,
)


class HudFamilySelectorTests(unittest.TestCase):
    def test_metric_phase_outranks_local_contact_cues(self):
        result = select_hud_family(HudFamilyContext(metric_phase=True, established_contacts=True))
        self.assertEqual(result.family, HudFamily.NAV_METRIC)
        self.assertEqual(result.selection_mode, "AUTO")

    def test_incomplete_reacquisition_selects_sensor_wide(self):
        result = select_hud_family(HudFamilyContext(local_reacquisition_complete=False))
        self.assertEqual(result.family, HudFamily.SENSOR_WIDE)

    def test_strategic_planning_selects_nav_flight_plan(self):
        result = select_hud_family(HudFamilyContext(strategic_planning=True))
        self.assertEqual(result.family, HudFamily.NAV_FLIGHT_PLAN)

    def test_tactical_quality_selects_tactical_track(self):
        result = select_hud_family(HudFamilyContext(tactical_quality_state=True))
        self.assertEqual(result.family, HudFamily.TACTICAL_TRACK)

    def test_local_context_selects_plain_tactical_without_track_claim(self):
        for kwargs in (
            {"near_infrastructure": True},
            {"maneuver_hazard": True},
            {"established_contacts": True},
        ):
            with self.subTest(kwargs=kwargs):
                result = select_hud_family(HudFamilyContext(**kwargs))
                self.assertEqual(result.family, HudFamily.TACTICAL)

    def test_manual_override_changes_presentation_only_and_preserves_auto_result(self):
        result = select_hud_family(
            HudFamilyContext(metric_phase=True), manual_override=HudFamily.TACTICAL
        )
        self.assertEqual(result.family, HudFamily.TACTICAL)
        self.assertEqual(result.automatic_family, HudFamily.NAV_METRIC)
        self.assertEqual(result.selection_mode, "MANUAL_OVERRIDE_PRESENTATION_ONLY")
        self.assertEqual(result.authority, AUTHORITY)

    def test_unknown_manual_override_fails_closed(self):
        with self.assertRaises(ValueError):
            select_hud_family(HudFamilyContext(), manual_override="WUNDER-HUD")

    def test_payload_is_explicitly_presentation_only(self):
        payload = selection_payload(select_hud_family(HudFamilyContext(tactical_quality_state=True)))
        self.assertEqual(payload["contract"], CONTRACT)
        self.assertEqual(payload["family"], "TACTICAL / TRACK")
        self.assertEqual(payload["authority"], "PRESENTATION_ONLY_CANON_RULE_APPLICATION")

    def test_live_adapter_promotes_only_complete_relative_geometry(self):
        complete = {
            "moon": {
                "relative_to_wayfarer_km": [1.0, 2.0, 3.0],
                "velocity_earth_centered_km_s": [0.1, 0.2, 0.3],
            },
            "wayfarer": {"velocity_earth_centered_km_s": [0.0, 0.0, 0.0]},
        }
        payload = live_qualification_selection_payload(complete)
        self.assertEqual(payload["family"], "TACTICAL / TRACK")
        self.assertEqual(payload["reason"], "LOCAL_GEOMETRY_TACTICAL_QUALITY")

        incomplete = {
            "moon": {"relative_to_wayfarer_km": [1.0, 2.0, 3.0]},
            "wayfarer": {"velocity_earth_centered_km_s": [0.0, 0.0, 0.0]},
        }
        fallback = live_qualification_selection_payload(incomplete)
        self.assertEqual(fallback["family"], "TACTICAL")
        self.assertEqual(fallback["reason"], "DEFAULT_LOCAL_PRESENTATION_NO_HIGHER_PHASE_CLAIM")

    def test_rendezvous_adapter_emits_nav_only_for_solved_feasibility(self):
        solved = rendezvous_selection_payload(
            {"quality": {"status": "SOLVED_TRANSLATIONAL_FEASIBILITY"}}
        )
        self.assertIsNotNone(solved)
        self.assertEqual(solved["family"], "NAV / FLIGHT PLAN")
        self.assertEqual(solved["reason"], "STRATEGIC_PLANNING")

        unsolved = rendezvous_selection_payload({"quality": {"status": "NOT_SOLVED"}})
        self.assertIsNone(unsolved)


if __name__ == "__main__":
    unittest.main()
