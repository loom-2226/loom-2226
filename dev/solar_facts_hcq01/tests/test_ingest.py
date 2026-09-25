from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from ingest.acquire import acquire
from ingest.audit import audit
from ingest.extract.research_json import extract
from ingest.load import ensure_identity_anchor, load_candidate
from ingest.models import FactCandidate, SourceCandidate, StagingRecord
from ingest.normalize import normalize
from ingest.validate import validate
from ingest.knowledge import knowledge_snapshot

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
RAW = ROOT / "artifacts/raw/jpl_de440_ceres_gm.json"


class HarnessTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "test.sqlite3"
        shutil.copy2(DB, self.db)
        self.raw = Path(self.tmp.name) / "raw.json"
        self.conn = sqlite3.connect(self.db)
        self.conn.execute("PRAGMA foreign_keys=ON")
        for table in ("fact_observation", "source_assertion", "preferred_fact", "derived_input", "derived_quantity",
                      "region_model_product", "gravity_model", "orientation_model", "body_model_product", "activity_fact", "material_evidence",
                      "observation", "body_region", "fact", "source", "body"):
            self.conn.execute(f"DELETE FROM {table}")
        self.conn.commit()
        ensure_identity_anchor(self.conn)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def record(self, fact: FactCandidate | None = None) -> StagingRecord:
        artifact = acquire(f"file://{RAW}", self.raw, retrieved_at="2026-09-25T00:00:00Z")
        record = normalize(extract(self.raw, artifact=artifact))
        return StagingRecord(record.source, record.observations, (fact,) if fact else record.facts, extractor_name=record.extractor_name)

    def assertRejects(self, fact: FactCandidate, code: str):
        report = validate(self.conn, self.record(fact))
        self.assertEqual("REJECT", report.decision)
        self.assertIn(code, {finding.code for finding in report.findings})

    def base_fact(self, **changes):
        values = dict(body_id="CERES", source_id="source", property_code="GM", evidence_class="DYNAMICAL_INFERENCE",
                      value_semantics="measured gravitational parameter", reported_value_text="62.62890",
                      reported_unit="km^3/s^2", normalized_value=62.62890, normalized_unit="km^3/s^2")
        values.update(changes)
        return FactCandidate(**values)

    def test_hostile_candidates_reject(self):
        cases = [
            (self.base_fact(normalized_value=-62.0), "NEGATIVE_VALUE"),
            (self.base_fact(property_code="CERES_AWESOMENESS"), "UNKNOWN_PROPERTY_CODE"),
            (self.base_fact(evidence_class="TRUST_ME_BRO"), "UNKNOWN_EVIDENCE_CLASS"),
            (self.base_fact(), "PUBLICATION_AFTER_CUTOFF"),
            (self.base_fact(region_id=999), "UNRESOLVED_REGION"),
            (self.base_fact(preferred_fact_requested=True), "EXTRACTOR_REQUESTED_PREFERRED_FACT"),
        ]
        for fact, expected in cases:
            with self.subTest(expected=expected):
                if expected == "PUBLICATION_AFTER_CUTOFF":
                    record = self.record(fact)
                    record = StagingRecord(SourceCandidate(**{**record.source.__dict__, "publication_date": "2026-01-01"}), record.observations, record.facts)
                    report = validate(self.conn, record)
                    self.assertIn(expected, {finding.code for finding in report.findings})
                elif expected == "NEGATIVE_VALUE":
                    # The frozen DDL protects signed physical quantities through loader validation.
                    self.assertRejects(FactCandidate(**{**fact.__dict__, "value_min": -62.0, "value_max": -63.0}), "MIN_GREATER_THAN_MAX")
                    self.assertRejects(FactCandidate(**{**fact.__dict__, "uncertainty_plus": -1.0}), "NEGATIVE_UNCERTAINTY")
                else:
                    self.assertRejects(fact, expected)

    def test_valid_vertical_slice_and_audit(self):
        artifact = acquire(f"file://{RAW}", self.raw, retrieved_at="2026-09-25T00:00:00Z")
        record = normalize(extract(self.raw, artifact=artifact))
        report = validate(self.conn, record)
        self.assertEqual("PASS", report.decision, report.findings)
        loaded = load_candidate(self.conn, record)
        result = audit(self.conn, record, artifact, loaded)
        self.assertTrue(result["complete"])
        self.assertEqual(("62.62890", "km^3/s^2", 62.62890, "km^3/s^2", "CANDIDATE"), self.conn.execute(
            "SELECT reported_value_text,reported_unit,value_numeric,canonical_unit,fact_status FROM fact").fetchone())
        self.assertEqual(1, self.conn.execute("SELECT count(*) FROM source_assertion").fetchone()[0])
        self.assertEqual(1, self.conn.execute("SELECT count(*) FROM fact_observation").fetchone()[0])
        self.assertEqual([], self.conn.execute("PRAGMA foreign_key_check").fetchall())
        self.assertEqual("ok", self.conn.execute("PRAGMA integrity_check").fetchone()[0])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM preferred_fact").fetchone()[0])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM gravity_model").fetchone()[0])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM material_evidence").fetchone()[0])

    def test_duplicate_and_unknown_are_not_loaded(self):
        artifact = acquire(f"file://{RAW}", self.raw, retrieved_at="2026-09-25T00:00:00Z")
        record = normalize(extract(self.raw, artifact=artifact))
        load_candidate(self.conn, record)
        duplicate = validate(self.conn, record)
        self.assertEqual("REJECT", duplicate.decision)
        self.assertIn("DUPLICATE_ASSERTION", {finding.code for finding in duplicate.findings})
        unknown = self.base_fact(property_code="MASS", reported_value_text="UNKNOWN", reported_unit="kg", normalized_value=None, normalized_unit=None)
        review = validate(self.conn, self.record(unknown))
        self.assertEqual("REVIEW", review.decision)
        self.assertIn("UNKNOWN_VALUE", {finding.code for finding in review.findings})

    def test_all_hcq_cohorts_are_registered_without_payload(self):
        cohorts = json.loads((ROOT / "COHORTS.json").read_text(encoding="utf-8"))
        self.assertEqual(list("ABCDEFGH"), [item["id"] for item in cohorts["cohorts"]])
        self.assertEqual("candidate_only", cohorts["load_policy"])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM preferred_fact").fetchone()[0])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM material_evidence").fetchone()[0])

    def test_jpl_radius_semantics_and_dimensional_mismatch_guard(self):
        html = (ROOT / "artifacts/acquired/01_jpl_physical_parameters.html").read_text(encoding="utf-8")
        self.assertIn("Equatorial Radius", html)
        self.assertIn("Mean Radius", html)
        self.assertIn("Mean<br>Radius", html)
        self.assertIn("Radius of a sphere with the equivalent volume", html)
        valid = self.base_fact(property_code="MEAN_RADIUS", reported_value_text="469.7",
                               reported_unit="km", normalized_value=469.7, normalized_unit="km",
                               source_locator="JPL physical parameters Ceres row: Mean Radius")
        self.assertEqual("PASS", validate(self.conn, self.record(valid)).decision)
        invalid = FactCandidate(**{**valid.__dict__, "source_locator": "JPL physical parameters Ceres row: Polar Radius"})
        report = validate(self.conn, self.record(invalid))
        self.assertEqual("REJECT", report.decision)
        self.assertIn("SEMANTIC_PROPERTY_MISMATCH", {finding.code for finding in report.findings})

    def test_range_value_is_not_replaced_by_fabricated_scalar(self):
        fact = self.base_fact(property_code="SURFACE_TEMPERATURE", reported_value_text="170-180",
                              reported_unit="K", normalized_value=None, normalized_unit="K",
                              value_min=170.0, value_max=180.0)
        self.assertEqual("PASS", validate(self.conn, self.record(fact)).decision)

    def test_frozen_vocabularies_and_statuses_reject_invalid_values(self):
        for field, value, code in (("evidence_class", "ASSERTED", "UNKNOWN_EVIDENCE_CLASS"),
                                   ("confidence_class", "MEDIUM", "UNKNOWN_CONFIDENCE_CLASS"),
                                   ("assertion_role", "ASSERTS", "UNKNOWN_ASSERTION_ROLE"),
                                   ("fact_status", "PREFERRED", "UNKNOWN_FACT_STATUS"),
                                   ("value_semantics", "", "INVALID_VALUE_SEMANTICS")):
            with self.subTest(field=field):
                report = validate(self.conn, self.record(FactCandidate(**{**self.base_fact().__dict__, field: value})))
                self.assertEqual("REJECT", report.decision)
                self.assertIn(code, {finding.code for finding in report.findings})

    def test_cross_body_and_unlinked_region_guards(self):
        fact = self.base_fact(region_ref="OTHER_BODY_REGION")
        report = validate(self.conn, StagingRecord(self.record().source, regions=()))
        self.assertEqual("PASS", report.decision)
        self.assertIn("UNRESOLVED_REGION", {finding.code for finding in validate(self.conn, self.record(fact)).findings})
        from ingest.models import RegionCandidate, ObservationCandidate
        mismatch = StagingRecord(self.record().source,
            observations=(ObservationCandidate(body_id="OTHER", source_id="source", region_ref="CERES_REGION", spatial_context="Ceres region"),),
            regions=(RegionCandidate(body_id="CERES", source_id="source", region_type="TEST", region_ref="CERES_REGION", canonical_name="Ceres region"),))
        findings = {finding.code for finding in validate(self.conn, mismatch).findings}
        self.assertIn("UNRESOLVED_BODY", findings)
        self.assertIn("CROSS_BODY_REGION_MISMATCH", findings)

    def test_round2_actual_semantics_and_regional_links(self):
        actual = sqlite3.connect(DB)
        rows = actual.execute("SELECT evidence_class FROM fact UNION ALL SELECT evidence_class FROM material_evidence UNION ALL SELECT evidence_class FROM activity_fact").fetchall()
        allowed = {"DIRECT_SAMPLE", "IN_SITU_DIRECT", "IN_SITU_REMOTE", "EARTH_REMOTE", "DYNAMICAL_INFERENCE", "ANALOG_INFERENCE", "PHYSICAL_MODEL", "THEORETICAL_EXPECTATION", "DERIVED"}
        self.assertTrue(all(row[0] in allowed for row in rows))
        self.assertEqual("OTHER", actual.execute("SELECT source_type FROM source WHERE title LIKE 'Ahuna Mons:%'").fetchone()[0])
        self.assertEqual("OTHER", actual.execute("SELECT source_type FROM source WHERE url='https://arxiv.org/pdf/2003.11045'").fetchone()[0])
        self.assertGreater(actual.execute("SELECT count(*) FROM region_model_product").fetchone()[0], 0)
        self.assertEqual(0, actual.execute("SELECT count(*) FROM material_evidence WHERE material_family='water_ice' AND areal_extent IS NOT NULL").fetchone()[0])
        actual.close()

    def test_historical_snapshots_ignore_retrieval_time(self):
        actual = sqlite3.connect(DB)
        for cutoff, expected_min in (("2010-12-31T23:59:59Z", 0), ("2016-12-31T23:59:59Z", 1), ("2025-12-31T23:59:59Z", 8)):
            snap = knowledge_snapshot(actual, cutoff)
            self.assertGreaterEqual(len(snap["facts"]), expected_min)
        self.assertEqual(0, len(knowledge_snapshot(actual, "2010-12-31T23:59:59Z")["facts"]))
        self.assertEqual(8, len(knowledge_snapshot(actual, "2025-12-31T23:59:59Z")["facts"]))
        actual.close()

    def test_derived_lineage_is_not_valid_without_input(self):
        actual = sqlite3.connect(DB)
        self.assertEqual(1, actual.execute("SELECT count(*) FROM derived_input di JOIN derived_quantity dq ON dq.derived_id=di.derived_id JOIN fact f ON f.fact_id=di.fact_id WHERE dq.property_code='VOLUME' AND f.property_code='MEAN_RADIUS'").fetchone()[0])
        self.assertEqual(0, actual.execute("SELECT count(*) FROM derived_quantity dq WHERE NOT EXISTS (SELECT 1 FROM derived_input di JOIN fact f ON f.fact_id=di.fact_id WHERE di.derived_id=dq.derived_id AND f.fact_status='CANDIDATE')").fetchone()[0])
        actual.close()

    def test_psr_area_and_forbidden_authority_surfaces_reject(self):
        from ingest.models import MaterialCandidate, ModelProductCandidate
        psr = StagingRecord(self.record().source, materials=(MaterialCandidate(body_id="CERES", source_id="source", material_family="water_ice", evidence_class="PHYSICAL_MODEL", physical_form="potential cold-trap ice", areal_extent=1800.0, areal_extent_unit="km^2", notes="modeled PSR area, not measured ice"),))
        self.assertIn("MODELED_AREA_AS_ICE", {finding.code for finding in validate(self.conn, psr).findings})
        forbidden = StagingRecord(self.record().source, model_products=(ModelProductCandidate(body_id="CERES", source_id="source", model_type="EPHEMERIS_STATE", model_name="forbidden"),))
        self.assertIn("FORBIDDEN_AUTHORITY_SURFACE", {finding.code for finding in validate(self.conn, forbidden).findings})

    def test_resolvable_region_must_be_relationally_linked(self):
        from ingest.models import RegionCandidate, ObservationCandidate
        record = StagingRecord(self.record().source,
            observations=(ObservationCandidate(body_id="CERES", source_id="source", spatial_context="Ceres test region", observation_product_id="REGION_TEST"),),
            regions=(RegionCandidate(body_id="CERES", source_id="source", region_type="TEST", region_ref="TEST_REGION", canonical_name="Ceres test region"),))
        self.assertIn("RESOLVABLE_REGION_UNLINKED", {finding.code for finding in validate(self.conn, record).findings})

    def test_quarantine_invalidates_dependent_derivation(self):
        copy = Path(self.tmp.name) / "quarantine.sqlite3"
        shutil.copy2(DB, copy)
        conn = sqlite3.connect(copy)
        conn.execute("UPDATE fact SET fact_status='RETIRED' WHERE property_code='MEAN_RADIUS'")
        self.assertEqual(0, conn.execute("SELECT count(*) FROM derived_quantity dq WHERE EXISTS (SELECT 1 FROM derived_input di JOIN fact f ON f.fact_id=di.fact_id WHERE di.derived_id=dq.derived_id AND f.fact_status='CANDIDATE')").fetchone()[0])
        conn.close()


if __name__ == "__main__":
    unittest.main()
