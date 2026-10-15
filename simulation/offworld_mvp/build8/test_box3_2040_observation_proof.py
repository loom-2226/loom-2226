"""Build 8 Box 3: offline invariants; optional private PG replay proof."""
import json
import os
import unittest
from decimal import Decimal as D
from unittest.mock import patch

from offworld_kernel.build3 import Build3Kernel, RunIdentity
from simulation.offworld_mvp.build8.box3_2040_observation_proof import (
    SEED, STUDY_START_YEAR, STUDY_PAYMENT_AND_OBSERVATION_YEAR,
    SYNTHETIC_2026_PROJECT_CAPITAL, SYNTHETIC_2040_STUDY_SUPPLY_CLAIM,
    run_2040_paid_study,
)


class Box32040OfflineTests(unittest.TestCase):
    def test_explicit_scope_and_synthetic_amounts(self):
        self.assertEqual((STUDY_START_YEAR, STUDY_PAYMENT_AND_OBSERVATION_YEAR), (2039, 2040))
        self.assertEqual(SYNTHETIC_2026_PROJECT_CAPITAL, D("2"))
        self.assertEqual(SYNTHETIC_2040_STUDY_SUPPLY_CLAIM, D("2"))
        self.assertEqual(SEED, "BUILD7-I5-QUAL-POSITIVE-V3")

    def test_rejects_nonprivate_service_configuration(self):
        with patch.dict(os.environ, {"PGSERVICEFILE": "/home/ubuntu/.config/loom/offworld.pg_service.conf"}):
            with self.assertRaisesRegex(RuntimeError, "BOX3_PRIVATE_SERVICE_FILE_REQUIRED"):
                run_2040_paid_study("NOT_A_REAL_RUN")

    def test_repeated_same_year_uses_same_draw(self):
        k = Build3Kernel(RunIdentity("SYNTHETIC", "v1", "FIXTURE", "NONCANON", ()))
        keys = ("OBS", 15, "SPN", "BODY:REGION:FAMILY", "REGION")
        self.assertEqual(k.keyed_draw(*keys), k.keyed_draw(*keys))
        self.assertNotEqual(k.keyed_draw(*keys), k.keyed_draw("OBS", 16, *keys[2:]))

    def test_negative_remains_nonzero_illustrative_bayes(self):
        prior, detection, false_positive = D(".5"), D(".8"), D(".2")
        posterior = ((1 - detection) * prior) / (
            (1 - detection) * prior + (1 - false_positive) * (1 - prior))
        self.assertEqual(posterior, D(".2"))


@unittest.skipUnless(os.getenv("BOX3_ALLOW_PRIVATE_PERSISTENCE") == "1",
                     "Opt-in disposable private PostgreSQL 18.6 required")
class Box32040PrivatePostgresTests(unittest.TestCase):
    def test_2040_observation_reopens_without_changes(self):
        run_id = os.environ["BOX3_2026_SEALED_RUN_ID"]
        a = run_2040_paid_study(run_id)
        b = run_2040_paid_study(run_id)
        self.assertEqual(json.loads(json.dumps(a)), json.loads(json.dumps(b)))
        self.assertEqual(a["payment_and_observation_year"], 2040)
        self.assertEqual(a["project_status"], "EXPLORING")
        self.assertEqual(a["review_count"], 0)
        self.assertEqual(a["study_expense"], "2")
        self.assertEqual(a["earth_spent"], "2")
        self.assertTrue(all(s == "ALREADY_MATCHED" for _, s in b["epoch_commits"]))
        self.assertTrue(all(D(r["posterior"]) > 0 for r in a["observations"]
                            if r["signal"] == "NEGATIVE"))


if __name__ == "__main__":
    unittest.main()
