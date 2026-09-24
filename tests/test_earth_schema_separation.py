import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EarthSchemaSeparationTests(unittest.TestCase):
    def test_forward_migration_moves_only_earth_tables(self):
        sql = (ROOT / "data/postgres/migrations/008_earth_schema_separation.sql").read_text()
        for name in (
            "earth_area", "earth_biological_cohort_year", "earth_demographic_year",
            "earth_derivation", "earth_economic_year", "earth_labor_composition_year",
            "earth_legacy_labor_year", "earth_sector_asset_year", "earth_sector_year",
        ):
            self.assertIn(f"ALTER TABLE loom_civ.{name} SET SCHEMA loom_earth", sql)
        self.assertNotIn("ALTER TABLE loom_civ.civ_", sql)

    def test_runtime_and_qualification_use_earth_namespace(self):
        tool = (ROOT / "tools/earth_temporal_pg.py").read_text()
        verifier = (ROOT / "tools/verify_earth_schema_separation.py").read_text()
        self.assertNotIn("loom_civ.earth_", tool)
        self.assertIn("loom_earth.earth_", tool)
        self.assertIn("loom_earth", verifier)


if __name__ == "__main__":
    unittest.main()
