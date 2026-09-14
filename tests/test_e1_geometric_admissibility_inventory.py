import sqlite3
import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.qualification.e1_geometric_admissibility_inventory import (
    qualify_neptune_inputs,
)


class TestGeometricAdmissibilityInventory(unittest.TestCase):
    def _db(self, sql: str) -> tuple[tempfile.TemporaryDirectory, Path]:
        td = tempfile.TemporaryDirectory()
        db = Path(td.name) / "test.sqlite3"
        conn = sqlite3.connect(db)
        conn.executescript(sql)
        conn.close()
        return td, db

    def test_qualification_uses_exact_physical_fields_not_keyword_matches(self):
        td, db = self._db(
            """
            CREATE TABLE celestial_properties(
                entity_id TEXT, gm_km3_s2 REAL, mean_radius_km REAL,
                source_id TEXT, status TEXT
            );
            INSERT INTO celestial_properties VALUES
                ('NE', 6836529.0, 24622.0, 'PHYS', 'ENGINEERING_REFERENCE_NONCANON');

            CREATE TABLE celestial_dynamics(
                entity_id TEXT, gm_km3_s2 REAL, mean_radius_km REAL,
                atmosphere_class TEXT, source TEXT, metadata_status TEXT,
                feeder_density REAL, dry_mass_kg REAL
            );
            INSERT INTO celestial_dynamics VALUES
                ('NE', 6836529.0, 24622.0, 'HYDROGEN_HELIUM_METHANE',
                 'DYN', 'REFERENCE', 999.0, 888.0);

            CREATE TABLE states(
                entity_id TEXT, epoch_utc TEXT, source TEXT, navigation_grade INTEGER,
                reference_frame TEXT, reference_plane TEXT
            );
            INSERT INTO states VALUES
                ('NE', '2226-08-22T00:00:00Z', 'SOURCE-010', 1, 'J2000', 'ECLIPTIC');
            """
        )
        try:
            report = qualify_neptune_inputs(db)
        finally:
            td.cleanup()

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["body"], "NE")
        self.assertEqual(report["available"]["gravity"]["gm_km3_s2"], 6836529.0)
        self.assertEqual(report["available"]["geometry"]["mean_radius_km"], 24622.0)
        self.assertEqual(report["available"]["matter_environment"]["atmosphere_class"], "HYDROGEN_HELIUM_METHANE")
        self.assertEqual(report["available"]["provenance_quality"]["navigation_grade"], 1)
        available_rendered = repr(report["available"])
        self.assertNotIn("feeder_density", available_rendered)
        self.assertNotIn("dry_mass_kg", available_rendered)
        self.assertIn(
            "transport_feeder_density_is_not_local_matter_density",
            report["rejected_false_positive_classes"],
        )
        self.assertIn(
            "infrastructure_mass_fields_are_not_local_gravity",
            report["rejected_false_positive_classes"],
        )

    def test_missing_required_families_remain_explicitly_missing(self):
        td, db = self._db(
            """
            CREATE TABLE celestial_properties(
                entity_id TEXT, gm_km3_s2 REAL, source_id TEXT, status TEXT
            );
            INSERT INTO celestial_properties VALUES ('NE', 6836529.0, 'PHYS', 'REFERENCE');
            """
        )
        try:
            report = qualify_neptune_inputs(db)
        finally:
            td.cleanup()

        self.assertIn("electromagnetic_environment", report["missing_required_families"])
        self.assertIn("physical_uncertainty", report["missing_required_families"])
        self.assertIn("loom_coherence", report["missing_required_families"])
        self.assertIn("local_matter_density", report["missing_required_families"])
        self.assertEqual(report["available"]["electromagnetic_environment"], {})
        self.assertEqual(report["available"]["physical_uncertainty"], {})
        self.assertEqual(report["available"]["loom_coherence"], {})


if __name__ == "__main__":
    unittest.main()
