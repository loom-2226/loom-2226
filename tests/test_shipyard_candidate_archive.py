from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from design_ledger import DesignLedger
from qualification.synthesis.generative_shipyard_campaign import canonical_report, run_and_persist_wayfarer_campaign
from qualification.synthesis.shipyard_candidate_archive import (
    ARCHIVE_AUTHORITY,
    archive_wayfarer_campaign,
    campaign_summary,
    list_campaign_candidates,
)
from qualification.synthesis.vehicle_dynamics_contract import (
    READINESS_BLOCKED,
    build_wayfarer_contract_family,
    dynamics_readiness_report,
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
        self.assertEqual(report["next_blocker"], READINESS_BLOCKED)
        self.assertEqual(
            report["next_admission_priority"],
            "ADMIT_ONE_CANDIDATE_DEPENDENT_PHYSICAL_DRIVER_FROM_GOVERNED_ENGINEERING_EVIDENCE",
        )
        self.assertFalse(report["dynamics_readiness"]["phase10_phase11_may_supply_live_dynamics_inputs"])
        canonical_report(report)
        con = sqlite3.connect(str(db))
        try:
            count = con.execute("SELECT count(*) FROM visual_library_asset WHERE artifact_class='GOVERNED_SEMANTIC'").fetchone()[0]
            self.assertEqual(count, 6)
        finally:
            con.close()

    def test_dynamics_readiness_names_missing_admissions_without_promoting_phase11(self):
        contracts = build_wayfarer_contract_family(2226)
        readiness = dynamics_readiness_report(contracts)
        self.assertEqual(readiness["status"], READINESS_BLOCKED)
        self.assertFalse(readiness["translational_core_ready"])
        self.assertEqual(readiness["candidate_count"], 6)
        self.assertEqual(len(readiness["missing_required_admissions"]), 3)
        self.assertIn("CANDIDATE_DEPENDENT_WET_OR_DRY_MASS_STATE", readiness["missing_required_admissions"])
        self.assertIn("CANDIDATE_DEPENDENT_NORMAL_REMASS_STATE_OR_CAPACITY", readiness["missing_required_admissions"])
        self.assertIn("CANDIDATE_DEPENDENT_ADMITTED_PROPULSION_PERFORMANCE_OR_DUTY_LIMIT", readiness["missing_required_admissions"])
        self.assertFalse(readiness["phase10_phase11_may_supply_live_dynamics_inputs"])
        feed = readiness["remass_feed_evidence"]
        self.assertEqual(feed["phase11_authority"], "ANALYTIC_FEED_BOUND_EVIDENCE_ONLY")
        self.assertEqual(feed["phase11_selection_status"], "NO_FEED_ARCHITECTURE_SELECTED")
        self.assertEqual(feed["phase11_live_engineering_input_admission_count"], 0)
        self.assertFalse(feed["phase11_propulsion_inlet_pressure_admitted"])
        self.assertFalse(feed["phase11_pump_efficiency_admitted"])
        self.assertEqual(len(readiness["report_hash"]), 64)

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
