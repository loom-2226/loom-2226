import copy
import unittest

from qualification.synthesis.shipyard_campaign_binding import (
    BINDING_AUTHORITY,
    ShipyardCampaignBindingError,
    validate_campaign_binding,
)
from qualification.synthesis.vehicle_dynamics_contract import build_wayfarer_contract_family
from loom_navigator_core import _new_state


class ShipyardCampaignBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = build_wayfarer_contract_family(2226)[0]

    def test_live_navigator_new_state_matches_shipyard_contract(self):
        state = _new_state("SHIPYARD-BINDING-TEST", "WAYFARER-TEST")
        before = copy.deepcopy(state)
        report = validate_campaign_binding(self.contract, state)
        self.assertEqual(state, before)
        self.assertEqual(report["authority_status"], BINDING_AUTHORITY)
        self.assertTrue(report["compatible_for_navigator_consumption"])
        self.assertTrue(report["checks"]["wet_mass_matches_contract"])
        self.assertTrue(report["checks"]["remass_capacity_matches_contract"])
        self.assertTrue(report["checks"]["current_remass_within_contract_capacity"])
        self.assertEqual(report["campaign_wet_mass_t"], 1158.5)
        self.assertEqual(report["campaign_remass_t"], 250.0)
        self.assertEqual(report["campaign_remass_capacity_t"], 250.0)
        self.assertFalse(report["campaign_state_mutated"])
        self.assertFalse(report["navigator_authority_changed"])
        self.assertFalse(report["flight_dynamics_authority"])
        self.assertFalse(report["canon_changed"])

    def test_partially_depleted_campaign_remass_is_compatible(self):
        state = _new_state("SHIPYARD-BINDING-TEST", "WAYFARER-TEST")
        state["ship"]["remass_t"] = 125.0
        report = validate_campaign_binding(self.contract, state)
        self.assertTrue(report["compatible_for_navigator_consumption"])
        self.assertEqual(report["campaign_remass_t"], 125.0)

    def test_wet_mass_drift_fails_closed(self):
        state = _new_state("SHIPYARD-BINDING-TEST", "WAYFARER-TEST")
        state["ship"]["wet_mass_t"] += 1.0
        with self.assertRaisesRegex(ShipyardCampaignBindingError, "wet_mass_matches_contract"):
            validate_campaign_binding(self.contract, state)

    def test_remass_capacity_drift_fails_closed(self):
        state = _new_state("SHIPYARD-BINDING-TEST", "WAYFARER-TEST")
        state["ship"]["remass_capacity_t"] = 249.0
        state["ship"]["remass_t"] = 249.0
        with self.assertRaisesRegex(ShipyardCampaignBindingError, "remass_capacity_matches_contract"):
            validate_campaign_binding(self.contract, state)

    def test_wrong_ship_identity_fails_closed(self):
        state = _new_state("SHIPYARD-BINDING-TEST", "WAYFARER-TEST")
        state["ship_identity"]["ship_class"] = "NOT_WAYFARER"
        with self.assertRaisesRegex(ShipyardCampaignBindingError, "ship_class mismatch"):
            validate_campaign_binding(self.contract, state)


if __name__ == "__main__":
    unittest.main()
