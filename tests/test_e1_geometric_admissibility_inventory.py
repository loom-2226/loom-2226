import sqlite3
import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.qualification.e1_geometric_admissibility_inventory import (
    inventory_schema,
)


class TestGeometricAdmissibilityInventory(unittest.TestCase):
    def test_inventory_reports_only_fields_that_exist(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "test.sqlite3"
            conn = sqlite3.connect(db)
            conn.executescript(
                """
                CREATE TABLE celestial_properties(
                    entity_id TEXT,
                    gm_km3_s2 REAL,
                    mean_radius_km REAL,
                    source_id TEXT,
                    status TEXT
                );
                CREATE TABLE environment(
                    entity_id TEXT,
                    atmospheric_density_kg_m3 REAL,
                    magnetic_flux_density_t REAL,
                    measurement_sigma REAL
                );
                """
            )
            conn.close()

            report = inventory_schema(db)

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["classification"], "DATA_AVAILABILITY_AUDIT_ONLY_NOT_ADMISSIBILITY_POLICY")
        self.assertIn("celestial_properties.gm_km3_s2", report["families"]["gravity"])
        self.assertIn("celestial_properties.mean_radius_km", report["families"]["geometry"])
        self.assertIn("environment.atmospheric_density_kg_m3", report["families"]["matter_environment"])
        self.assertIn("environment.magnetic_flux_density_t", report["families"]["electromagnetic_environment"])
        self.assertIn("environment.measurement_sigma", report["families"]["uncertainty"])
        self.assertIn("celestial_properties.source_id", report["families"]["provenance_quality"])
        self.assertIn("celestial_properties.status", report["families"]["provenance_quality"])

    def test_inventory_does_not_invent_missing_families(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "test.sqlite3"
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE celestial_properties(entity_id TEXT, gm_km3_s2 REAL)")
            conn.close()

            report = inventory_schema(db)

        self.assertEqual(report["families"]["gravity"], ["celestial_properties.gm_km3_s2"])
        self.assertEqual(report["families"]["geometry"], [])
        self.assertEqual(report["families"]["matter_environment"], [])
        self.assertEqual(report["families"]["electromagnetic_environment"], [])
        self.assertEqual(report["families"]["uncertainty"], [])
        self.assertEqual(report["families"]["provenance_quality"], [])


if __name__ == "__main__":
    unittest.main()
