"""Deterministic local repair from the preserved v0.3 candidate."""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
from pathlib import Path


V3_SHA256 = "310c35491e3768adcfc1607c4542603613d8d28ad00df883755537805037ed74"


def _rebuild_knowledge_event(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE knowledge_event_r1(
            knowledge_event_id INTEGER PRIMARY KEY,
            event_key TEXT NOT NULL UNIQUE CHECK(length(trim(event_key))>0),
            event_type TEXT NOT NULL CHECK(event_type IN(
                'OBSERVED','PUBLISHED','RELEASED','REVISED','SUPERSEDED','RETRACTED','INGESTED')),
            event_time TEXT NOT NULL CHECK(
                (length(event_time)=10 AND event_time GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]') OR
                (length(event_time)=20 AND event_time GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z')),
            target_fact_id INTEGER REFERENCES fact(fact_id),
            target_observation_id INTEGER REFERENCES observation(observation_id),
            target_model_product_id INTEGER REFERENCES body_model_product(model_product_id),
            target_source_id INTEGER REFERENCES source(source_id),
            source_id INTEGER REFERENCES source(source_id),
            notes TEXT,
            CHECK((target_fact_id IS NOT NULL) + (target_observation_id IS NOT NULL) +
                  (target_model_product_id IS NOT NULL) + (target_source_id IS NOT NULL) = 1)
        )
        """
    )
    conn.execute(
        """INSERT INTO knowledge_event_r1(
            knowledge_event_id,event_key,event_type,event_time,target_fact_id,
            target_observation_id,target_model_product_id,target_source_id,source_id,notes)
            SELECT knowledge_event_id,event_key,event_type,event_time,target_fact_id,
            target_observation_id,target_model_product_id,target_source_id,source_id,notes
            FROM knowledge_event ORDER BY knowledge_event_id"""
    )
    conn.execute("DROP TABLE knowledge_event")
    conn.execute("ALTER TABLE knowledge_event_r1 RENAME TO knowledge_event")
    conn.execute("CREATE INDEX idx_knowledge_event_time ON knowledge_event(event_time)")
    conn.execute("CREATE INDEX idx_knowledge_event_type ON knowledge_event(event_type)")


def _same_body_triggers(conn: sqlite3.Connection) -> None:
    statements = (
        # Endpoint-node protection for the relationships already present in v0.3.
        """
        CREATE TRIGGER trg_r1_fact_body_update BEFORE UPDATE OF body_id ON fact
        WHEN EXISTS(SELECT 1 FROM fact_observation fo JOIN observation o ON o.observation_id=fo.observation_id
                    WHERE fo.fact_id=NEW.fact_id AND o.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM fact_input fi JOIN fact i ON i.fact_id=fi.input_fact_id
                    WHERE fi.fact_id=NEW.fact_id AND fi.input_fact_id IS NOT NULL AND i.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM fact_input fi JOIN fact output_fact ON output_fact.fact_id=fi.fact_id
                    WHERE fi.input_fact_id=NEW.fact_id AND output_fact.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM fact_input fi JOIN observation o ON o.observation_id=fi.input_observation_id
                    WHERE fi.fact_id=NEW.fact_id AND fi.input_observation_id IS NOT NULL AND o.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM fact_input fi JOIN body_model_product m ON m.model_product_id=fi.input_model_product_id
                    WHERE fi.fact_id=NEW.fact_id AND fi.input_model_product_id IS NOT NULL AND m.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM derived_input di JOIN derived_quantity d ON d.derived_id=di.derived_id
                    WHERE di.fact_id=NEW.fact_id AND d.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM preferred_fact p WHERE p.fact_id=NEW.fact_id AND p.body_id<>NEW.body_id)
          OR (NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id))
          OR EXISTS(SELECT 1 FROM fact s WHERE s.supersedes_fact_id=NEW.fact_id AND s.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'fact body update breaks same-body relationship'); END
        """,
        """
        CREATE TRIGGER trg_r1_observation_body_update BEFORE UPDATE OF body_id ON observation
        WHEN EXISTS(SELECT 1 FROM fact_observation fo JOIN fact f ON f.fact_id=fo.fact_id
                    WHERE fo.observation_id=NEW.observation_id AND f.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM fact_input fi JOIN fact f ON f.fact_id=fi.fact_id
                    WHERE fi.input_observation_id=NEW.observation_id AND f.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM material_evidence m WHERE m.observation_id=NEW.observation_id AND m.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM activity_fact a WHERE a.observation_id=NEW.observation_id AND a.body_id<>NEW.body_id)
          OR (NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id))
        BEGIN SELECT RAISE(ABORT,'observation body update breaks same-body relationship'); END
        """,
        """
        CREATE TRIGGER trg_r1_model_body_update BEFORE UPDATE OF body_id ON body_model_product
        WHEN EXISTS(SELECT 1 FROM region_model_product rm JOIN body_region r ON r.region_id=rm.region_id
                    WHERE rm.model_product_id=NEW.model_product_id AND r.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM fact_input fi JOIN fact f ON f.fact_id=fi.fact_id
                    WHERE fi.input_model_product_id=NEW.model_product_id AND f.body_id<>NEW.body_id)
          OR (NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id))
        BEGIN SELECT RAISE(ABORT,'model body update breaks same-body relationship'); END
        """,
        """
        CREATE TRIGGER trg_r1_region_body_update BEFORE UPDATE OF body_id ON body_region
        WHEN EXISTS(SELECT 1 FROM observation o WHERE o.region_id=NEW.region_id AND o.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM fact f WHERE f.region_id=NEW.region_id AND f.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM material_evidence m WHERE m.region_id=NEW.region_id AND m.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM activity_fact a WHERE a.region_id=NEW.region_id AND a.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM body_model_product m WHERE m.region_id=NEW.region_id AND m.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM derived_quantity d WHERE d.region_id=NEW.region_id AND d.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM preferred_fact p WHERE p.region_id=NEW.region_id AND p.body_id<>NEW.body_id)
          OR EXISTS(SELECT 1 FROM region_model_product rm JOIN body_model_product m ON m.model_product_id=rm.model_product_id
                    WHERE rm.region_id=NEW.region_id AND m.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'region body update breaks same-body relationship'); END
        """,
        # Relationships not protected by the original v0.3 implementation.
        """
        CREATE TRIGGER trg_r1_material_observation_insert BEFORE INSERT ON material_evidence
        WHEN NEW.observation_id IS NOT NULL AND EXISTS(SELECT 1 FROM observation o WHERE o.observation_id=NEW.observation_id AND o.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'material/observation belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_material_observation_update BEFORE UPDATE OF body_id,observation_id ON material_evidence
        WHEN NEW.observation_id IS NOT NULL AND EXISTS(SELECT 1 FROM observation o WHERE o.observation_id=NEW.observation_id AND o.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'material/observation belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_activity_observation_insert BEFORE INSERT ON activity_fact
        WHEN NEW.observation_id IS NOT NULL AND EXISTS(SELECT 1 FROM observation o WHERE o.observation_id=NEW.observation_id AND o.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'activity/observation belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_activity_observation_update BEFORE UPDATE OF body_id,observation_id ON activity_fact
        WHEN NEW.observation_id IS NOT NULL AND EXISTS(SELECT 1 FROM observation o WHERE o.observation_id=NEW.observation_id AND o.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'activity/observation belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_derived_input_insert BEFORE INSERT ON derived_input
        WHEN EXISTS(SELECT 1 FROM derived_quantity d JOIN fact f ON f.fact_id=NEW.fact_id
                    WHERE d.derived_id=NEW.derived_id AND d.body_id<>f.body_id)
        BEGIN SELECT RAISE(ABORT,'derived quantity/input fact belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_derived_input_update BEFORE UPDATE OF derived_id,fact_id ON derived_input
        WHEN EXISTS(SELECT 1 FROM derived_quantity d JOIN fact f ON f.fact_id=NEW.fact_id
                    WHERE d.derived_id=NEW.derived_id AND d.body_id<>f.body_id)
        BEGIN SELECT RAISE(ABORT,'derived quantity/input fact belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_derived_body_update BEFORE UPDATE OF body_id ON derived_quantity
        WHEN EXISTS(SELECT 1 FROM derived_input di JOIN fact f ON f.fact_id=di.fact_id
                    WHERE di.derived_id=NEW.derived_id AND f.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'derived quantity body update breaks lineage'); END
        """,
        """
        CREATE TRIGGER trg_r1_derived_region_update BEFORE UPDATE OF body_id,region_id ON derived_quantity
        WHEN NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'derived quantity/region belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_preferred_insert BEFORE INSERT ON preferred_fact
        WHEN EXISTS(SELECT 1 FROM fact f WHERE f.fact_id=NEW.fact_id AND f.body_id<>NEW.body_id)
          OR (NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id))
        BEGIN SELECT RAISE(ABORT,'preferred fact relationships belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_preferred_update BEFORE UPDATE OF body_id,region_id,fact_id ON preferred_fact
        WHEN EXISTS(SELECT 1 FROM fact f WHERE f.fact_id=NEW.fact_id AND f.body_id<>NEW.body_id)
          OR (NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id))
        BEGIN SELECT RAISE(ABORT,'preferred fact update breaks same-body relationship'); END
        """,
        """
        CREATE TRIGGER trg_r1_fact_supersession_insert BEFORE INSERT ON fact
        WHEN NEW.supersedes_fact_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f WHERE f.fact_id=NEW.supersedes_fact_id AND f.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'superseded facts belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_r1_fact_supersession_update BEFORE UPDATE OF body_id,supersedes_fact_id ON fact
        WHEN (NEW.supersedes_fact_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f WHERE f.fact_id=NEW.supersedes_fact_id AND f.body_id<>NEW.body_id))
          OR EXISTS(SELECT 1 FROM fact f WHERE f.supersedes_fact_id=NEW.fact_id AND f.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'fact supersession update breaks same-body relationship'); END
        """,
    )
    for statement in statements:
        conn.execute(statement)


def migrate_connection(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        conn.execute("BEGIN IMMEDIATE")
        _rebuild_knowledge_event(conn)
        _same_body_triggers(conn)
        conn.execute("UPDATE meta SET value='LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3-R1' WHERE key='schema_name'")
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version','v0.3-R1')")
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('repair_parent','LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3')")
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('repair_policy','HOSTILE_REVIEW_REMEDIATION')")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys=ON")


def migrate_file(source: Path, destination: Path) -> None:
    source = Path(source); destination = Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("refusing to repair v0.3 in place")
    if hashlib.sha256(source.read_bytes()).hexdigest() != V3_SHA256:
        raise ValueError("source is not the preserved v0.3 candidate")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    conn = sqlite3.connect(destination)
    try:
        migrate_connection(conn)
    finally:
        conn.close()
