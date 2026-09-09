from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from design_ledger import DesignLedger
from qualification.synthesis.generative_shipyard_campaign import run_and_persist_wayfarer_campaign
from qualification.synthesis.shipyard_candidate_archive import (
    ARCHIVE_AUTHORITY,
    archive_wayfarer_campaign,
    campaign_summary,
    list_campaign_candidates,
)


class ShipyardCandidateArchiveTests(unittest.TestCase):
    def _db(self) -> Path:
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        tmp.close()
        path = Path(tmp.name)
        path.unlink()
        with DesignLedger(path):
            pass
        return path

    def test_campaign_archive_is_deterministic_and_authority_safe(self):
        db = self._db()
        cid1 = archive_wayfarer_campaign(db, 2226)
        cid2 = archive_wayfarer_campaign(db, 2226)
        self.assertEqual(cid1, cid2)
        rows = list_campaign_candidates(db, cid1)
        self.assertEqual(len(rows), 10)
        self.assertEqual(sum(r.status == "SURVIVED_SCREEN" for r in rows), 6)
        self.assertEqual(sum(r.status.startswith("REJECTED_") for r in rows), 4)
        self.assertEqual(sum(r.pareto_member for r in rows), 4)
        self.assertTrue(all(r.archive_authority == ARCHIVE_AUTHORITY for r in rows))
        self.assertTrue(all(not r.dynamics_authority for r in rows))

    def test_campaign_executor_registers_survivor_glbs_without_claiming_flight(self):
        db = self._db()
        report = run_and_persist_wayfarer_campaign(db, 2226)
        self.assertEqual(report["interpretation"], "FIRST_BOUNDED_ITERATIVE_SHIPBUILDING_CAMPAIGN_CLOSED")
        self.assertEqual(report["candidate_count"], 10)
        self.assertEqual(report["survivor_count"], 6)
        self.assertEqual(report["rejected_count"], 4)
        self.assertEqual(report["pareto_count"], 4)
        self.assertEqual(report["visual_asset_count"], 6)
        self.assertFalse(report["flight_dynamics_authority"])
        self.assertFalse(report["dynamics_differentiation"]["translational_mission_behavior_differentiated"])
        self.assertIn("PACKAGING_ONLY", report["next_blocker"])
        con = sqlite3.connect(str(db))
        try:
            count = con.execute("SELECT count(*) FROM visual_library_asset WHERE artifact_class='GOVERNED_SEMANTIC'").fetchone()[0]
            self.assertEqual(count, 6)
        finally:
            con.close()

    def test_campaign_summary_hash_and_rejections_survive_round_trip(self):
        db = self._db()
        cid = archive_wayfarer_campaign(db, 2226)
        summary = campaign_summary(db, cid)
        self.assertEqual(summary["candidate_count"], 10)
        self.assertEqual(summary["survivor_count"], 6)
        self.assertEqual(summary["rejected_count"], 4)
        self.assertEqual(len(summary["summary_hash"]), 64)
        rejected = [r for r in summary["candidates"] if r["status"].startswith("REJECTED_")]
        self.assertEqual(len(rejected), 4)


if __name__ == "__main__":
    unittest.main()
