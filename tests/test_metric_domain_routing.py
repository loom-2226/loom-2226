import unittest

from src.loom_metric_domain_routing import (
    DomainKind,
    DomainRule,
    NavigationPreferences,
    resolve_metric_route,
)


class MetricDomainRoutingTests(unittest.TestCase):
    def test_nested_target_resolves_to_outer_metric_entry_domain(self):
        rules = {
            "JUPITER_SYSTEM": DomainRule("JUPITER_SYSTEM", None, DomainKind.METRIC_ENTRY),
            "EUROPA": DomainRule("EUROPA", "JUPITER_SYSTEM", DomainKind.LOCAL_ONLY),
        }
        route = resolve_metric_route("EUROPA", rules, NavigationPreferences())
        self.assertEqual(route.metric_entry_domain, "JUPITER_SYSTEM")
        self.assertEqual(route.local_target, "EUROPA")

    def test_normal_navigation_obeys_regulatory_exclusions(self):
        prefs = NavigationPreferences()
        self.assertTrue(prefs.obey_regulatory_exclusions)

    def test_override_request_can_relax_regulatory_but_never_physical_exclusion(self):
        prefs = NavigationPreferences(regulatory_override_requested=True)
        self.assertFalse(prefs.obey_regulatory_exclusions)
        self.assertTrue(prefs.obey_physical_exclusions)

    def test_metric_entry_target_resolves_to_itself(self):
        rules = {"CERES": DomainRule("CERES", None, DomainKind.METRIC_ENTRY)}
        route = resolve_metric_route("CERES", rules, NavigationPreferences())
        self.assertEqual(route.metric_entry_domain, "CERES")
        self.assertEqual(route.local_target, "CERES")

    def test_unknown_target_fails_closed(self):
        with self.assertRaises(KeyError):
            resolve_metric_route("UNKNOWN", {}, NavigationPreferences())


if __name__ == "__main__":
    unittest.main()
