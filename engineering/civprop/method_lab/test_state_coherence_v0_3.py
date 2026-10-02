import unittest
from types import SimpleNamespace

from engineering.civprop.run_civprop_v1 import (
    _apply_demographic_output_semantics,
    _base_gaps,
)


class StateCoherenceV03Tests(unittest.TestCase):
    def bundle(self, authority=True):
        return SimpleNamespace(
            scenario=SimpleNamespace(
                demographic_authority_v1=(
                    {"format": "CIVPROP_DEMOGRAPHIC_AUTHORITY_V1"}
                    if authority else None
                )
            )
        )

    def test_earth_unowned_fields_fail_closed_when_demographic_authority_active(self):
        result = {
            "annual_states": [{
                "year": 2100,
                "location_id": "EARTH_SURFACE",
                "biological_population": 9_000_000_000.0,
                "workforce": 2_656_643_452.0,
                "capacities": {"habitat": 8_266_245_291.0, "power": 100.0},
            }]
        }
        out = _apply_demographic_output_semantics(result, self.bundle())
        earth = out["annual_states"][0]
        self.assertIsNone(earth["workforce"])
        self.assertIsNone(earth["capacities"]["habitat"])
        self.assertEqual(earth["capacities"]["power"], 100.0)
        self.assertEqual(
            earth["state_authority"]["biological_population"],
            "EARTH_PROMOTED_DEMOGRAPHIC_AUTHORITY",
        )
        self.assertIn("UNKNOWN", earth["state_authority"]["workforce"])
        self.assertIn("UNKNOWN", earth["state_authority"]["habitat"])

    def test_offworld_state_is_not_rewritten(self):
        row = {
            "year": 2100,
            "location_id": "LUNA_SURFACE",
            "biological_population": 5.0,
            "workforce": 3.0,
            "capacities": {"habitat": 10.0},
        }
        result = {"annual_states": [row.copy() | {"capacities": dict(row["capacities"])}]}
        out = _apply_demographic_output_semantics(result, self.bundle())
        self.assertEqual(out["annual_states"][0]["workforce"], 3.0)
        self.assertEqual(out["annual_states"][0]["capacities"]["habitat"], 10.0)
        self.assertNotIn("state_authority", out["annual_states"][0])

    def test_no_demographic_authority_preserves_legacy_output(self):
        result = {"annual_states": [{
            "year": 2026, "location_id": "EARTH_SURFACE",
            "workforce": 4.0, "capacities": {"habitat": 8.0},
        }]}
        out = _apply_demographic_output_semantics(result, self.bundle(False))
        self.assertEqual(out["annual_states"][0]["workforce"], 4.0)
        self.assertEqual(out["annual_states"][0]["capacities"]["habitat"], 8.0)

    def test_gap016_is_explicit_in_public_gap_register(self):
        gaps = {x["gap_id"]: x for x in _base_gaps()}
        self.assertIn("GAP-016", gaps)
        self.assertEqual(gaps["GAP-016"]["status"], "OPEN")
        self.assertIn("transport", gaps["GAP-016"]["name"].lower())


if __name__ == "__main__":
    unittest.main()
