from __future__ import annotations

import hashlib
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from migration_r1 import V3_SHA256, migrate_file
from temporal import validate_event_time


ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "v0_3/LOOM_SOLAR_HCQ01_CERES_v0_3.sqlite3"
V2 = ROOT / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
V2_SHA256 = "91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d"


class R1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.v3_copy = Path(self.tmp.name) / "v3.sqlite3"
        self.r1 = Path(self.tmp.name) / "r1.sqlite3"
        shutil.copy2(V3, self.v3_copy)
        migrate_file(self.v3_copy, self.r1)
        self.conn = sqlite3.connect(self.r1)
        self.conn.execute("PRAGMA foreign_keys=ON")

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def fresh_v3(self) -> sqlite3.Connection:
        p = Path(self.tmp.name) / f"v3-{len(list(Path(self.tmp.name).glob('v3-*.sqlite3')))}.sqlite3"
        shutil.copy2(V3, p)
        c = sqlite3.connect(p); c.execute("PRAGMA foreign_keys=ON"); return c

    def add_other_body(self, conn: sqlite3.Connection, body_id: str = "OTHER") -> None:
        conn.execute("INSERT INTO body(body_id,canonical_name,body_class,status) VALUES(?,?,?,?)",
                     (body_id, body_id, "TEST", "ACTIVE"))
        conn.commit()

    def assert_rejects(self, sql: str, conn: sqlite3.Connection | None = None) -> None:
        conn = conn or self.conn
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(sql)
        conn.rollback()

    def test_baseline_hashes_and_preservation(self) -> None:
        self.assertEqual(V2_SHA256, hashlib.sha256(V2.read_bytes()).hexdigest())
        self.assertEqual(V3_SHA256, hashlib.sha256(V3.read_bytes()).hexdigest())
        self.assertEqual(8, self.conn.execute("SELECT count(*) FROM fact").fetchone()[0])
        self.assertEqual(8, self.conn.execute("SELECT count(*) FROM fact WHERE fact_status='CANDIDATE'").fetchone()[0])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM preferred_fact").fetchone()[0])
        self.assertEqual(2, self.conn.execute("SELECT count(*) FROM fact_input").fetchone()[0])
        self.assertEqual(4, self.conn.execute("SELECT count(*) FROM knowledge_event").fetchone()[0])
        self.assertEqual("PREPRINT", self.conn.execute(
            "SELECT source_type FROM source WHERE persistent_identifier='arXiv:2003.11045'").fetchone()[0])
        self.assertEqual(0, self.conn.execute(
            "SELECT count(*) FROM observation WHERE spatial_resolution_value IS NOT NULL OR vertical_sensitivity_min IS NOT NULL OR vertical_sensitivity_max IS NOT NULL").fetchone()[0])

    def test_reproduces_known_v3_node_and_temporal_attacks(self) -> None:
        attacks = [
            ("fact endpoint", "UPDATE fact SET body_id='OTHER' WHERE fact_id=7"),
            ("observation endpoint", "UPDATE observation SET body_id='OTHER' WHERE observation_id=3"),
            ("derived output endpoint", "UPDATE fact SET body_id='OTHER' WHERE fact_id=4"),
            ("input fact endpoint", "UPDATE fact SET body_id='OTHER' WHERE fact_id=1"),
        ]
        for name, sql in attacks:
            with self.subTest(name=name):
                c = self.fresh_v3(); self.add_other_body(c)
                c.execute(sql); c.commit()
                c.close()

        c = self.fresh_v3(); self.add_other_body(c)
        c.execute("INSERT INTO body_model_product(model_product_id,body_id,model_type,model_name) VALUES(99,'CERES','TEST','M')")
        c.execute("INSERT INTO region_model_product(region_id,model_product_id,relationship) VALUES(1,99,'TEST')")
        c.commit(); c.execute("UPDATE body_model_product SET body_id='OTHER' WHERE model_product_id=99"); c.commit(); c.close()

        c = self.fresh_v3(); self.add_other_body(c)
        c.execute("INSERT INTO body_model_product(model_product_id,body_id,model_type,model_name) VALUES(99,'CERES','TEST','M')")
        c.execute("INSERT INTO fact_input(fact_id,input_model_product_id,input_role) VALUES(7,99,'MODEL_TEST')")
        c.commit(); c.execute("UPDATE body_model_product SET body_id='OTHER' WHERE model_product_id=99"); c.commit(); c.close()

        c = self.fresh_v3(); self.add_other_body(c)
        c.execute("INSERT INTO knowledge_event(event_key,event_type,event_time,target_observation_id) VALUES('banana','OBSERVED','banana',3)")
        c.commit(); c.close()

    def test_r1_rejects_fact_and_observation_endpoint_corruption(self) -> None:
        self.add_other_body(self.conn)
        self.assert_rejects("UPDATE fact SET body_id='OTHER' WHERE fact_id=7")
        self.assert_rejects("UPDATE observation SET body_id='OTHER' WHERE observation_id=3")
        self.assert_rejects("UPDATE fact SET body_id='OTHER' WHERE fact_id=4")
        self.assert_rejects("UPDATE fact SET body_id='OTHER' WHERE fact_id=1")

    def test_r1_rejects_input_observation_and_model_endpoint_corruption(self) -> None:
        self.add_other_body(self.conn)
        self.conn.execute("INSERT INTO fact_input(fact_id,input_observation_id,input_role) VALUES(7,3,'OBS_TEST')")
        self.conn.execute("INSERT INTO body_model_product(model_product_id,body_id,model_type,model_name) VALUES(99,'CERES','TEST','M')")
        self.conn.execute("INSERT INTO fact_input(fact_id,input_model_product_id,input_role) VALUES(7,99,'MODEL_TEST')")
        self.conn.execute("INSERT INTO region_model_product(region_id,model_product_id,relationship) VALUES(1,99,'TEST')")
        self.conn.execute("INSERT INTO body_region(region_id,body_id,region_type,canonical_name) VALUES(99,'OTHER','TEST','Other')")
        self.conn.commit()
        self.assert_rejects("UPDATE observation SET body_id='OTHER' WHERE observation_id=3")
        self.assert_rejects("UPDATE body_model_product SET body_id='OTHER' WHERE model_product_id=99")
        self.assert_rejects("UPDATE region_model_product SET region_id=99 WHERE region_id=1 AND model_product_id=99")

    def test_r1_rejects_region_material_activity_and_derived_endpoint_corruption(self) -> None:
        self.add_other_body(self.conn)
        self.assert_rejects("UPDATE material_evidence SET body_id='OTHER' WHERE material_evidence_id=1")
        self.assert_rejects("UPDATE activity_fact SET body_id='OTHER' WHERE activity_id=1")
        self.assert_rejects("UPDATE body_region SET body_id='OTHER' WHERE region_id=1")
        self.assert_rejects("UPDATE derived_quantity SET body_id='OTHER' WHERE derived_id=1")

    def test_valid_isolated_body_mutations_remain_allowed(self) -> None:
        self.add_other_body(self.conn)
        self.conn.execute("UPDATE fact SET body_id='OTHER' WHERE fact_id=2")
        self.conn.execute("UPDATE observation SET body_id='OTHER' WHERE observation_id=1")
        self.conn.execute("UPDATE body_model_product SET body_id='OTHER' WHERE model_product_id=2")
        self.conn.commit()
        self.assertEqual("OTHER", self.conn.execute("SELECT body_id FROM fact WHERE fact_id=2").fetchone()[0])

    def test_edge_insert_and_update_guards_remain_active(self) -> None:
        self.add_other_body(self.conn)
        self.conn.execute("INSERT INTO observation(observation_id,body_id) VALUES(99,'OTHER')")
        self.conn.execute("UPDATE fact SET body_id='OTHER' WHERE fact_id=2")
        self.conn.commit()
        self.assert_rejects("INSERT INTO fact_observation(fact_id,observation_id) VALUES(7,99)")
        self.assert_rejects("INSERT INTO fact_input(fact_id,input_fact_id,input_role) VALUES(4,2,'BAD')")
        self.conn.execute("UPDATE observation SET body_id='OTHER' WHERE observation_id=1")
        self.conn.commit()
        self.assert_rejects("UPDATE fact_observation SET observation_id=1 WHERE fact_id=7 AND observation_id=3")

    def test_temporal_database_contract_and_application_calendar_validation(self) -> None:
        for value in ("banana", "yesterday-ish", "2025-1-1", "2226-WALTER-SCOFFLES"):
            c = sqlite3.connect(self.r1)
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute(
                    "INSERT INTO knowledge_event(event_key,event_type,event_time,target_observation_id) VALUES(?,?,?,?)",
                    ("bad-" + value.replace('-', '_'), "OBSERVED", value, 3))
            c.rollback(); c.close()
        # The database intentionally enforces canonical syntax; the application
        # layer owns actual calendar validity for syntactically valid dates.
        self.assertEqual("DATE", validate_event_time("2025-02-28"))
        self.assertEqual("DATE", validate_event_time("2024-02-29"))
        self.assertEqual("SECOND", validate_event_time("2025-02-28T12:30:45Z"))
        for value in ("banana", "yesterday-ish", "2025-13-01", "2025-02-30", "2023-02-29", "2025-02-28T12:30:45+00:00"):
            with self.assertRaises(ValueError):
                validate_event_time(value)
        for value in self.conn.execute("SELECT event_time FROM knowledge_event"):
            self.assertEqual("DATE", validate_event_time(value[0]))

    def test_valid_timestamp_and_event_vocabulary(self) -> None:
        self.conn.execute("INSERT INTO knowledge_event(event_key,event_type,event_time,target_observation_id) VALUES('timestamp','OBSERVED','2025-02-28T12:30:45Z',3)")
        for event_type in ("PUBLISHED", "RELEASED", "REVISED", "SUPERSEDED", "RETRACTED", "INGESTED"):
            self.conn.execute("INSERT INTO knowledge_event(event_key,event_type,event_time,target_source_id) VALUES(?,?,?,9)",
                              ("event-" + event_type.lower(), event_type, "2025-02-28"))
        self.conn.commit()
        self.assert_rejects("INSERT INTO knowledge_event(event_key,event_type,event_time,target_observation_id) VALUES('bad-type','NOPE','2025-02-28',3)")

    def test_r1_rebuild_is_deterministic_and_integrity_clean(self) -> None:
        second = Path(self.tmp.name) / "second.sqlite3"
        migrate_file(self.v3_copy, second)
        self.assertEqual(self.r1.read_bytes(), second.read_bytes())
        self.assertEqual("ok", self.conn.execute("PRAGMA integrity_check").fetchone()[0])
        self.assertEqual([], self.conn.execute("PRAGMA foreign_key_check").fetchall())


if __name__ == "__main__":
    unittest.main()
