"""Qualification contract for Phase-4 earned Solar authority promotion."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
M009=ROOT/"data/postgres/migrations/009_solar_ephemeris_foundation.sql"
M012=ROOT/"data/postgres/migrations/012_solar_phase4_earned_authority.sql"

class EarnedAuthorityContractTests(unittest.TestCase):
    def test_exact_earned_set_and_holes_are_not_overstated(self):
        sql=M012.read_text()
        self.assertIn("expected 19 bodies/19 qualified coverage rows",sql)
        self.assertIn("'CERES_SPK_2025_2227','CERES'",sql)
        self.assertIn("'2226-12-31T23:58:50.816Z'",sql)
        self.assertIn("'JPL_SAT441','SATURN'",sql)
        self.assertIn("'2250-01-05T23:58:50.816055Z'",sql)
        self.assertNotIn("'JUPITER','Jupiter'",sql)
        self.assertNotIn("'PLUTO','Pluto'",sql)
        for pair in (("JUPITER_SYSTEM_BARYCENTER","5"),("PLUTO_SYSTEM_BARYCENTER","9"),
                     ("EARTH","399"),("MOON","301"),("CERES","20000001")):
            self.assertIn(f"('{pair[0]}','NAIF','NAIF_ID','{pair[1]}'",sql)

    def test_migration_is_transactional_and_fails_closed_on_nonempty_solar(self):
        sql=M012.read_text()
        self.assertIn("BEGIN;",sql)
        self.assertIn("COMMIT;",sql)
        self.assertIn("expects empty loom_solar metadata tables",sql)

@unittest.skipUnless(os.environ.get("SOLAR_PG_INTEGRATION")=="1","Requires disposable PostgreSQL")
class EarnedAuthorityPostgresTests(unittest.TestCase):
    database=os.environ.get("SOLAR_PG_TEST_DB","loom_solar_phase4_earned_test")
    def psql(self,sql):
        return subprocess.run(["psql","-X","-v","ON_ERROR_STOP=1","-d",self.database,"-Atqc",sql],
                              check=True,capture_output=True,text=True).stdout.strip()
    @classmethod
    def setUpClass(cls):
        subprocess.run(["psql","-X","-v","ON_ERROR_STOP=1","-d",cls.database,"-f",str(M009)],check=True,capture_output=True,text=True)
        subprocess.run(["psql","-X","-v","ON_ERROR_STOP=1","-d",cls.database,"-f",str(M012)],check=True,capture_output=True,text=True)
    @classmethod
    def tearDownClass(cls):
        subprocess.run(["psql","-X","-v","ON_ERROR_STOP=1","-d",cls.database,"-c","DROP SCHEMA IF EXISTS loom_solar CASCADE"],check=True,capture_output=True,text=True)
    def test_counts_and_identity(self):
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body"),"19")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body_identifier"),"19")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.ephemeris_source"),"6")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.ephemeris_coverage"),"19")
        self.assertEqual(self.psql("SELECT identifier_value FROM loom_solar.body_identifier WHERE body_id='JUPITER_SYSTEM_BARYCENTER'"),"5")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body WHERE body_id='JUPITER'"),"0")
    def test_known_horizon_holes_are_preserved(self):
        self.assertEqual(self.psql("SELECT valid_until::text FROM loom_solar.ephemeris_coverage WHERE body_id='CERES'"),"2226-12-31 23:58:50.816+00")
        self.assertEqual(self.psql("SELECT valid_until::text FROM loom_solar.ephemeris_coverage WHERE body_id='SATURN'"),"2250-01-05 23:58:50.816055+00")
