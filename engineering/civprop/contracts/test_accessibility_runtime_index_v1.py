"""Regression coverage for indexed accessibility and opportunity cost queries."""
import copy
from dataclasses import replace
import unittest

from .accessibility_v1 import (
    AccessibilityPackage, AccessibilityRequest, AccessibilityRuntime,
    GeometryContext, LocationBinding, load_accessibility_package,
)
from .test_accessibility_v1 import _actor_state, _package


class AccessibilityRuntimeIndexTests(unittest.TestCase):
    def test_geometry_index_is_symmetric_without_changing_row(self):
        geometry = GeometryContext(
            "EARTH", "MARS", "2030-01-01T00:00:00Z", 1.0, 2.0, None,
            "ECLIPJ2000", "BODY_CENTER_STRAIGHT_LINE", (),
        )
        package = AccessibilityPackage(
            "CIVPROP_ACCESSIBILITY_V1", "1.0.0", "UTC",
            (LocationBinding("E", "EARTH"), LocationBinding("M", "MARS")),
            (geometry,), (),
        )
        request = AccessibilityRequest("AUS", "M", "E", geometry.epoch_utc, "M", "S")
        self.assertIs(AccessibilityRuntime(package)._geometry_for(request), geometry)

    def feasible_package(self):
        package = _package()
        service = package["service_paths"][0]
        service.update(status="FEASIBLE", limiting_constraints=[], target_year=None)
        service["cost_components"] = [{
            "component_id": "SERVICE_PRICE", "status": "KNOWN", "value": 10.0,
            "unit": "AUD/kg", "uncertainty": None,
        }]
        service["generalized_cost"] = {
            "status": "KNOWN", "value": 10.0, "unit": "AUD/kg", "uncertainty": None,
        }
        return package

    def assert_cost_matches_assess(self, package, *, actor=None, tech=None, year=2030,
                                 subject="ROO_VER_WITH_NASA_MNP", expected=None):
        runtime = AccessibilityRuntime(load_accessibility_package(package))
        actor = _actor_state() if actor is None else actor
        tech = {} if tech is None else tech
        assessment = runtime.assess(
            AccessibilityRequest(
                "AUS", "EARTH_SURFACE", "LUNA_SURFACE", f"{year}-07-01T00:00:00Z",
                "NAMED_PAYLOAD_DELIVERY", "CLPS_LUNAR_DELIVERY", subject,
            ), actor_state=actor, technology_state=tech,
        )
        reference = (assessment.generalized_cost.value
                     if assessment.status == "FEASIBLE"
                     and assessment.generalized_cost.status == "KNOWN" else None)
        fast = runtime.best_known_feasible_cost(
            actor_id="AUS", actor_state=actor, origins=("EARTH_SURFACE", "LUNA_SURFACE"),
            destination_location_id="LUNA_SURFACE", year=year,
            mission_class="NAMED_PAYLOAD_DELIVERY", service_class="CLPS_LUNAR_DELIVERY",
            subject_id=subject, technology_state=tech,
        )
        self.assertEqual(reference, expected)
        self.assertEqual(fast, reference)

    def test_authored_constraints_and_zero_cost_match_assess(self):
        for code, expected in (
            ("REQUIRED_TRANSPORT_TECHNOLOGY_UNKNOWN", None),
            ("REQUEST_EPOCH_OUTSIDE_DOCUMENTED_TARGET_YEAR", None),
            ("other authored constraint", 10.0),
        ):
            with self.subTest(code=code):
                package = self.feasible_package()
                package["service_paths"][0]["limiting_constraints"] = [code]
                self.assert_cost_matches_assess(package, expected=expected)
        package = self.feasible_package()
        package["service_paths"][0]["generalized_cost"]["value"] = 0.0
        self.assert_cost_matches_assess(package, expected=0.0)
        self.assert_cost_matches_assess(_package())

    def test_first_service_wins_even_when_later_service_is_feasible_or_cheaper(self):
        for blocked in ("UNKNOWN", "INFEASIBLE", "ACCESS", "TECH", "TARGET", "FEASIBLE"):
            with self.subTest(blocked=blocked):
                package = self.feasible_package()
                first = package["service_paths"][0]
                first["service_id"] = "A"
                later = copy.deepcopy(first)
                later["service_id"] = "Z"
                later["generalized_cost"]["value"] = 1.0
                package["service_paths"] = [later, first]
                if blocked in ("UNKNOWN", "INFEASIBLE"):
                    first["status"] = blocked
                elif blocked == "ACCESS":
                    first["provider_id"] = "OTHER"
                elif blocked == "TECH":
                    first["required_technology_ids"] = ["T"]
                elif blocked == "TARGET":
                    first["target_year"] = 2031
                self.assert_cost_matches_assess(
                    package, expected=10.0 if blocked == "FEASIBLE" else None,
                )

    def test_subject_validity_and_technology_match_assess(self):
        package = self.feasible_package()
        self.assert_cost_matches_assess(package, expected=10.0)
        self.assert_cost_matches_assess(package, subject="OTHER")
        self.assert_cost_matches_assess(package, year=2025)
        package["service_paths"][0]["valid_to_year"] = 2030
        self.assert_cost_matches_assess(package, year=2031)
        package["service_paths"][0]["required_technology_ids"] = ["T"]
        for status in ("USABLE", "UNKNOWN", "UNUSABLE"):
            with self.subTest(status=status):
                self.assert_cost_matches_assess(
                    package, tech={"T": status}, expected=10.0 if status == "USABLE" else None,
                )

    def test_actor_access_is_not_cached_across_queries(self):
        package = self.feasible_package()
        actor = _actor_state()
        self.assert_cost_matches_assess(package, actor=actor, expected=10.0)
        self.assert_cost_matches_assess(package, actor=replace(actor, actor_id="OTHER"))
        self.assert_cost_matches_assess(
            package, actor=replace(actor, provider_service_access=replace(
                actor.provider_service_access, status="UNKNOWN", records=(),
            )),
        )
