"""Regression coverage for the additive Solar ephemeris migration."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "data/postgres/migrations/009_solar_ephemeris_foundation.sql"


class SolarEphemerisMigrationContractTests(unittest.TestCase):
    def setUp(self):
        self.sql = MIGRATION.read_text()

    def test_body_id_is_nullable_and_class_constraint_is_explicit(self):
        self.assertIn("body_id text NULL REFERENCES loom_solar.body(body_id)", self.sql)
        self.assertIn("UNIQUE NULLS NOT DISTINCT (ephemeris_source_id, body_id, valid_from)", self.sql)
        self.assertNotIn("PRIMARY KEY (ephemeris_source_id, body_id, valid_from)", self.sql)
        self.assertIn("coverage_class = 'PRODUCT' AND body_id IS NULL", self.sql)
        self.assertIn("coverage_class IN ('BODY', 'DERIVED') AND body_id IS NOT NULL", self.sql)

    def test_migration_creates_only_the_four_solar_tables(self):
        self.assertEqual(
            self.sql.count("CREATE TABLE loom_solar."),
            4,
        )
        for table in ("body", "body_identifier", "ephemeris_source", "ephemeris_coverage"):
            self.assertIn(f"CREATE TABLE loom_solar.{table}", self.sql)


@unittest.skipUnless(
    os.environ.get("SOLAR_PG_INTEGRATION") == "1",
    "Requires disposable PostgreSQL integration database",
)
class SolarEphemerisMigrationPostgresTests(unittest.TestCase):
    database = os.environ.get("SOLAR_PG_TEST_DB", "loom_solar_ephemeris_test")

    def psql(self, sql: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", self.database, "-Atqc", sql],
            check=check,
            capture_output=True,
            text=True,
        )

    def setUp(self):
        self.psql(MIGRATION.read_text())
        self.psql(
            """
            INSERT INTO loom_solar.body(body_id, canonical_name, body_class, status)
            VALUES ('TEST_BODY', 'Test body', 'TEST', 'ACTIVE');
            INSERT INTO loom_solar.ephemeris_source(
                ephemeris_source_id, provider, product_name, product_version,
                asset_filename, sha256, byte_count, source_url, acquired_at, status
            ) VALUES (
                'TEST_SOURCE', 'TEST', 'TEST', '1', 'test.bsp',
                repeat('a', 64), 1, 'test://source', now(), 'CANDIDATE'
            );
            """
        )

    def tearDown(self):
        self.psql("DROP SCHEMA IF EXISTS loom_solar CASCADE;")

    def insert_coverage(self, body_id: str | None, coverage_class: str, check: bool):
        value = "NULL" if body_id is None else "'" + body_id + "'"
        sql = f"""
            INSERT INTO loom_solar.ephemeris_coverage(
                ephemeris_source_id, body_id, valid_from, valid_until,
                reference_frame, units, coverage_class, status
            ) VALUES (
                'TEST_SOURCE', {value}, '2026-01-01T00:00:00Z',
                '2226-01-01T00:00:00Z', 'ECLIPJ2000', 'km,km/s',
                '{coverage_class}', 'CANDIDATE'
            );
        """
        return self.psql(sql, check=check)

    def test_product_null_body_succeeds(self):
        self.insert_coverage(None, "PRODUCT", check=True)

    def test_product_non_null_body_fails(self):
        result = self.insert_coverage("TEST_BODY", "PRODUCT", check=False)
        self.assertNotEqual(result.returncode, 0)

    def test_body_valid_body_succeeds(self):
        self.insert_coverage("TEST_BODY", "BODY", check=True)

    def test_body_null_body_fails(self):
        result = self.insert_coverage(None, "BODY", check=False)
        self.assertNotEqual(result.returncode, 0)

    def test_derived_requires_body(self):
        self.insert_coverage("TEST_BODY", "DERIVED", check=True)
        result = self.insert_coverage(None, "DERIVED", check=False)
        self.assertNotEqual(result.returncode, 0)

    def test_orphan_body_id_fails_fk(self):
        result = self.insert_coverage("MISSING_BODY", "BODY", check=False)
        self.assertNotEqual(result.returncode, 0)
