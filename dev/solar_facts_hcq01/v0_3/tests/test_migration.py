from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from migration import migrate_file


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
V2_SHA = "91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d"


class V03MigrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.original = Path(self.tmp.name) / "original.sqlite3"
        self.migrated = Path(self.tmp.name) / "migrated.sqlite3"
        shutil.copy2(V2, self.original)
        migrate_file(self.original, self.migrated)
        self.conn = sqlite3.connect(self.migrated)
        self.conn.execute("PRAGMA foreign_keys=ON")

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def assert_sql_rejects(self, sql: str, args: tuple = ()) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(sql, args)
        self.conn.rollback()

    def test_frozen_source_and_integrity(self) -> None:
        self.assertEqual(V2_SHA, hashlib.sha256(V2.read_bytes()).hexdigest())
        self.assertEqual(V2_SHA, hashlib.sha256(self.original.read_bytes()).hexdigest())
        self.assertEqual("ok", self.conn.execute("PRAGMA integrity_check").fetchone()[0])
        self.assertEqual([], self.conn.execute("PRAGMA foreign_key_check").fetchall())
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM preferred_fact").fetchone()[0])

    def test_legacy_rows_and_values_survive(self) -> None:
        for table in ("body", "property_definition", "source", "body_region", "observation", "fact",
                      "fact_observation", "source_assertion", "material_evidence", "activity_fact",
                      "body_model_product", "region_model_product", "gravity_model", "orientation_model",
                      "derived_quantity", "derived_input", "preferred_fact"):
            old = sqlite3.connect(self.original)
            self.assertEqual(old.execute(f"SELECT count(*) FROM {table}").fetchone()[0],
                             self.conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0], table)
            old.close()
        self.assertEqual(("BULK_DENSITY", "2.162", "g/cm^3"), self.conn.execute(
            "SELECT property_code,reported_value_text,reported_unit FROM fact WHERE fact_id=4").fetchone())
        self.assertEqual("lineage: JPL total mass and equivalent-volume mean radius",
                         self.conn.execute("SELECT notes FROM fact WHERE fact_id=4").fetchone()[0])
        self.assertEqual(8, self.conn.execute("SELECT count(*) FROM fact WHERE fact_status='CANDIDATE'").fetchone()[0])

    def test_observation_scale_defaults_and_validation(self) -> None:
        fields = self.conn.execute("PRAGMA table_info(observation)").fetchall()
        names = {row[1] for row in fields}
        self.assertTrue({"spatial_resolution_value", "spatial_resolution_unit", "spatial_resolution_semantics",
                         "vertical_sensitivity_min", "vertical_sensitivity_max", "vertical_sensitivity_unit"} <= names)
        self.assertEqual((None, None, None, None, None, None), self.conn.execute(
            "SELECT spatial_resolution_value,spatial_resolution_unit,spatial_resolution_semantics,"
            "vertical_sensitivity_min,vertical_sensitivity_max,vertical_sensitivity_unit FROM observation WHERE observation_id=1"
        ).fetchone())
        base = "INSERT INTO observation(body_id,observation_product_id,spatial_resolution_value,spatial_resolution_unit,spatial_resolution_semantics) VALUES('CERES',?,?,?,?)"
        self.conn.execute(base, ("V03_VALID", 10.0, "km", "instrument footprint"))
        self.assert_sql_rejects(base, ("V03_NEGATIVE", -1.0, "km", "instrument footprint"))
        vertical = "INSERT INTO observation(body_id,observation_product_id,vertical_sensitivity_min,vertical_sensitivity_max,vertical_sensitivity_unit) VALUES('CERES',?,?,?,?)"
        self.conn.execute(vertical, ("V03_VERTICAL_VALID", 0.0, 3.0, "km"))
        self.assert_sql_rejects(vertical, ("V03_VERTICAL_NEGATIVE", -1.0, 3.0, "km"))
        self.assert_sql_rejects(vertical, ("V03_VERTICAL_REVERSED", 4.0, 3.0, "km"))
        self.conn.commit()

    def test_fact_lineage_is_typed_and_constrained(self) -> None:
        self.assertEqual([(1, "MASS"), (3, "MEAN_RADIUS")], self.conn.execute(
            "SELECT fi.input_fact_id,f.property_code FROM fact_input fi JOIN fact f ON f.fact_id=fi.input_fact_id "
            "WHERE fi.fact_id=4 ORDER BY fi.input_fact_id").fetchall())
        self.assert_sql_rejects(
            "INSERT INTO fact_input(fact_id,input_fact_id,input_role) VALUES(4,999,'missing')")
        self.assert_sql_rejects(
            "INSERT INTO fact_input(fact_id,input_fact_id,input_role) VALUES(4,4,'self')")
        self.conn.execute("INSERT INTO body(body_id,canonical_name,body_class,status) VALUES('OTHER','Other','TEST','ACTIVE')")
        self.conn.execute("INSERT INTO fact(fact_id,body_id,property_code,value_semantics,evidence_class,fact_status,created_at) "
                          "VALUES(99,'OTHER','MASS','test','DYNAMICAL_INFERENCE','CANDIDATE','2026-01-01')")
        self.conn.commit()
        self.assert_sql_rejects(
            "INSERT INTO fact_input(fact_id,input_fact_id,input_role) VALUES(4,99,'cross-body')")
        self.conn.execute("INSERT INTO fact_input(fact_id,input_observation_id,input_role) VALUES(7,3,'OBSERVATION_INPUT')")
        self.conn.execute("INSERT INTO fact_input(fact_id,input_model_product_id,input_role) VALUES(7,5,'MODEL_INPUT')")
        self.conn.commit()

    def test_knowledge_events_and_preprint(self) -> None:
        self.assertEqual("PREPRINT", self.conn.execute(
            "SELECT source_type FROM source WHERE persistent_identifier='arXiv:2003.11045'").fetchone()[0])
        self.assertGreaterEqual(self.conn.execute("SELECT count(*) FROM knowledge_event").fetchone()[0], 1)
        self.conn.execute("INSERT INTO knowledge_event(event_key,event_type,event_time,target_observation_id,notes) "
                          "VALUES('test-observed','OBSERVED','2020-01-01',3,'test')")
        self.conn.execute("INSERT INTO knowledge_event(event_key,event_type,event_time,target_source_id,source_id) "
                          "VALUES('test-ingested','INGESTED','2026-01-01',9,9)")
        self.assert_sql_rejects("INSERT INTO knowledge_event(event_key,event_type,event_time,target_observation_id) "
                               "VALUES('bad-event','NOT_A_REAL_EVENT','2020-01-01',3)")
        self.assert_sql_rejects("INSERT INTO knowledge_event(event_key,event_type,event_time) "
                               "VALUES('no-target','PUBLISHED','2020-01-01')")
        self.conn.rollback()

    def test_legacy_source_types_and_invalid_source_type(self) -> None:
        values = {row[0] for row in self.conn.execute("SELECT DISTINCT source_type FROM source")}
        self.assertTrue({"DATA_PRODUCT", "OFFICIAL_REFERENCE", "PEER_REVIEWED", "OTHER"} <= values)
        self.assert_sql_rejects(
            "INSERT INTO source(source_type,title,retrieved_at) VALUES('NOT_A_SOURCE_TYPE','bad','2026-01-01')")

    def test_update_safe_cross_body_guards(self) -> None:
        self.conn.execute("INSERT INTO body(body_id,canonical_name,body_class,status) VALUES('OTHER2','Other 2','TEST','ACTIVE')")
        self.conn.execute("INSERT INTO body_region(region_id,body_id,region_type,canonical_name) VALUES(99,'OTHER2','TEST','Other region')")
        self.conn.commit()
        self.assert_sql_rejects("UPDATE observation SET body_id='OTHER2' WHERE observation_id=2")
        self.assert_sql_rejects("UPDATE observation SET region_id=99 WHERE observation_id=2")
        self.conn.execute("UPDATE fact SET region_id=1 WHERE fact_id=1")
        self.conn.commit()
        self.assert_sql_rejects("UPDATE fact SET body_id='OTHER2' WHERE fact_id=1")
        self.assert_sql_rejects("UPDATE fact SET region_id=99 WHERE fact_id=1")
        self.assert_sql_rejects("UPDATE body_model_product SET body_id='OTHER2' WHERE model_product_id=5")
        self.assert_sql_rejects("UPDATE body_model_product SET region_id=99 WHERE model_product_id=5")
        self.assert_sql_rejects("UPDATE material_evidence SET body_id='OTHER2' WHERE material_evidence_id=1")
        self.assert_sql_rejects("UPDATE activity_fact SET body_id='OTHER2' WHERE activity_id=1")
        self.assert_sql_rejects("UPDATE region_model_product SET region_id=99 WHERE region_id=1 AND model_product_id=5")
        self.assert_sql_rejects("UPDATE body_region SET body_id='OTHER2' WHERE region_id=1")

    def test_update_safe_lineage_and_fact_observation_guards(self) -> None:
        self.conn.execute("INSERT INTO body(body_id,canonical_name,body_class,status) VALUES('OTHER3','Other 3','TEST','ACTIVE')")
        self.conn.execute("INSERT INTO observation(observation_id,body_id,observation_product_id) VALUES(99,'OTHER3','OTHER_OBS')")
        self.conn.execute("INSERT INTO fact(fact_id,body_id,property_code,value_semantics,evidence_class,fact_status,created_at) "
                          "VALUES(99,'OTHER3','MASS','test','DYNAMICAL_INFERENCE','CANDIDATE','2026-01-01')")
        self.conn.commit()
        self.assert_sql_rejects("UPDATE fact_observation SET observation_id=99 WHERE fact_id=7 AND observation_id=3")
        self.assert_sql_rejects("UPDATE fact_input SET input_fact_id=99 WHERE fact_id=4 AND input_fact_id=1")

    def test_migration_is_deterministic(self) -> None:
        second = Path(self.tmp.name) / "migrated-second.sqlite3"
        migrate_file(self.original, second)
        a = sqlite3.connect(self.migrated)
        b = sqlite3.connect(second)
        for table in ("source", "observation", "fact", "fact_input", "knowledge_event"):
            self.assertEqual(a.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall(),
                             b.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall(), table)
        self.assertEqual(hashlib.sha256(self.migrated.read_bytes()).hexdigest(), hashlib.sha256(second.read_bytes()).hexdigest())
        a.close(); b.close()


if __name__ == "__main__":
    unittest.main()
