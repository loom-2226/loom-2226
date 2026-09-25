"""Deterministic, lossless migration from the frozen HCQ-01 v0.2 SQLite copy."""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
from pathlib import Path


V2_SHA256 = "91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d"
PREPRINT_IDENTIFIER = "arXiv:2003.11045"

SOURCE_COLUMNS = (
    "source_id,source_type,provider,title,authors,journal,doi,url,publication_date,"
    "product_name,product_version,persistent_identifier,retrieved_at,citation_text,notes"
)


def _source_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE source_v03(
            source_id INTEGER PRIMARY KEY,
            source_type TEXT NOT NULL CHECK(source_type IN(
                'MISSION_PRODUCT','DATA_PRODUCT','PEER_REVIEWED','OFFICIAL_REFERENCE',
                'REFERENCE_COMPILATION','HISTORICAL_PRIMARY','OTHER','PREPRINT')),
            provider TEXT,
            title TEXT NOT NULL,
            authors TEXT,
            journal TEXT,
            doi TEXT,
            url TEXT,
            publication_date TEXT,
            product_name TEXT,
            product_version TEXT,
            persistent_identifier TEXT,
            retrieved_at TEXT NOT NULL,
            citation_text TEXT,
            notes TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO source_v03(" + SOURCE_COLUMNS + ") SELECT source_id,"
        "CASE WHEN persistent_identifier=? AND source_type='OTHER' THEN 'PREPRINT' ELSE source_type END,"
        "provider,title,authors,journal,doi,url,publication_date,product_name,product_version,"
        "persistent_identifier,retrieved_at,citation_text,notes FROM source ORDER BY source_id",
        (PREPRINT_IDENTIFIER,),
    )
    if conn.execute("SELECT count(*) FROM source_v03 WHERE persistent_identifier=? AND source_type='PREPRINT'",
                    (PREPRINT_IDENTIFIER,)).fetchone()[0] != 1:
        raise ValueError("preserved preprint identity is not unique and unambiguous")
    conn.execute("DROP TABLE source")
    conn.execute("ALTER TABLE source_v03 RENAME TO source")
    conn.execute("CREATE UNIQUE INDEX uq_source_doi ON source(doi) WHERE doi IS NOT NULL")


def _observation_scale(conn: sqlite3.Connection) -> None:
    for column in (
        "spatial_resolution_value REAL",
        "spatial_resolution_unit TEXT",
        "spatial_resolution_semantics TEXT",
        "vertical_sensitivity_min REAL",
        "vertical_sensitivity_max REAL",
        "vertical_sensitivity_unit TEXT",
    ):
        conn.execute(f"ALTER TABLE observation ADD COLUMN {column}")


def _new_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE fact_input(
            fact_input_id INTEGER PRIMARY KEY,
            fact_id INTEGER NOT NULL REFERENCES fact(fact_id) ON DELETE CASCADE,
            input_fact_id INTEGER REFERENCES fact(fact_id),
            input_observation_id INTEGER REFERENCES observation(observation_id),
            input_model_product_id INTEGER REFERENCES body_model_product(model_product_id),
            input_role TEXT NOT NULL,
            notes TEXT,
            CHECK((input_fact_id IS NOT NULL) + (input_observation_id IS NOT NULL) +
                  (input_model_product_id IS NOT NULL) = 1),
            CHECK(length(trim(input_role))>0),
            CHECK(input_fact_id IS NULL OR input_fact_id<>fact_id)
        )
        """
    )
    conn.execute("CREATE UNIQUE INDEX uq_fact_input_fact ON fact_input(fact_id,input_fact_id,input_role) WHERE input_fact_id IS NOT NULL")
    conn.execute("CREATE UNIQUE INDEX uq_fact_input_observation ON fact_input(fact_id,input_observation_id,input_role) WHERE input_observation_id IS NOT NULL")
    conn.execute("CREATE UNIQUE INDEX uq_fact_input_model ON fact_input(fact_id,input_model_product_id,input_role) WHERE input_model_product_id IS NOT NULL")
    conn.execute(
        """
        CREATE TABLE knowledge_event(
            knowledge_event_id INTEGER PRIMARY KEY,
            event_key TEXT NOT NULL UNIQUE,
            event_type TEXT NOT NULL CHECK(event_type IN(
                'OBSERVED','PUBLISHED','RELEASED','REVISED','SUPERSEDED','RETRACTED','INGESTED')),
            event_time TEXT NOT NULL CHECK(length(trim(event_time))>0),
            target_fact_id INTEGER REFERENCES fact(fact_id),
            target_observation_id INTEGER REFERENCES observation(observation_id),
            target_model_product_id INTEGER REFERENCES body_model_product(model_product_id),
            target_source_id INTEGER REFERENCES source(source_id),
            source_id INTEGER REFERENCES source(source_id),
            notes TEXT,
            CHECK(length(trim(event_key))>0),
            CHECK((target_fact_id IS NOT NULL) + (target_observation_id IS NOT NULL) +
                  (target_model_product_id IS NOT NULL) + (target_source_id IS NOT NULL) = 1)
        )
        """
    )
    conn.execute("CREATE INDEX idx_knowledge_event_time ON knowledge_event(event_time)")
    conn.execute("CREATE INDEX idx_knowledge_event_type ON knowledge_event(event_type)")


def _migrate_unambiguous_lineage_and_events(conn: sqlite3.Connection) -> None:
    mass = conn.execute("SELECT fact_id FROM fact WHERE body_id='CERES' AND property_code='MASS'").fetchall()
    radius = conn.execute("SELECT fact_id FROM fact WHERE body_id='CERES' AND property_code='MEAN_RADIUS'").fetchall()
    density = conn.execute("SELECT fact_id FROM fact WHERE body_id='CERES' AND property_code='BULK_DENSITY'").fetchall()
    if len(mass) != 1 or len(radius) != 1 or len(density) != 1:
        raise ValueError("BULK_DENSITY lineage is not unambiguous in the v0.2 specimen")
    conn.executemany(
        "INSERT INTO fact_input(fact_id,input_fact_id,input_role,notes) VALUES(?,?,?,?)",
        [
            (density[0][0], mass[0][0], "MASS_INPUT", "Existing fact.notes identifies JPL total mass."),
            (density[0][0], radius[0][0], "MEAN_RADIUS_INPUT", "Existing fact.notes identifies equivalent-volume mean radius."),
        ],
    )

    # Only explicit observation-time starts are migrated. Publication/release
    # dates are intentionally not guessed into knowledge events.
    observations = conn.execute(
        "SELECT observation_id,observation_time_start FROM observation "
        "WHERE observation_time_start IS NOT NULL ORDER BY observation_id"
    ).fetchall()
    conn.executemany(
        "INSERT INTO knowledge_event(event_key,event_type,event_time,target_observation_id,notes) VALUES(?,?,?,?,?)",
        [
            (f"observation:{oid}:observed", "OBSERVED", event_time, oid,
             "Migrated only from the explicit observation_time_start field; no publication-time inference.")
            for oid, event_time in observations
        ],
    )


def _triggers(conn: sqlite3.Connection) -> None:
    statements = (
        """
        CREATE TRIGGER trg_v03_observation_scale_insert
        BEFORE INSERT ON observation
        WHEN (NEW.spatial_resolution_value IS NOT NULL AND
              (NEW.spatial_resolution_value<0 OR NEW.spatial_resolution_unit IS NULL OR trim(NEW.spatial_resolution_unit)='' OR
               NEW.spatial_resolution_semantics IS NULL OR trim(NEW.spatial_resolution_semantics)=''))
          OR (NEW.vertical_sensitivity_min IS NOT NULL AND
              (NEW.vertical_sensitivity_min<0 OR NEW.vertical_sensitivity_unit IS NULL OR trim(NEW.vertical_sensitivity_unit)=''))
          OR (NEW.vertical_sensitivity_max IS NOT NULL AND
              (NEW.vertical_sensitivity_max<0 OR NEW.vertical_sensitivity_unit IS NULL OR trim(NEW.vertical_sensitivity_unit)=''))
          OR (NEW.vertical_sensitivity_min IS NOT NULL AND NEW.vertical_sensitivity_max IS NOT NULL AND
              NEW.vertical_sensitivity_min>NEW.vertical_sensitivity_max)
        BEGIN SELECT RAISE(ABORT,'invalid observational scale'); END
        """,
        """
        CREATE TRIGGER trg_v03_observation_scale_update
        BEFORE UPDATE OF spatial_resolution_value,spatial_resolution_unit,spatial_resolution_semantics,
                         vertical_sensitivity_min,vertical_sensitivity_max,vertical_sensitivity_unit ON observation
        WHEN (NEW.spatial_resolution_value IS NOT NULL AND
              (NEW.spatial_resolution_value<0 OR NEW.spatial_resolution_unit IS NULL OR trim(NEW.spatial_resolution_unit)='' OR
               NEW.spatial_resolution_semantics IS NULL OR trim(NEW.spatial_resolution_semantics)=''))
          OR (NEW.vertical_sensitivity_min IS NOT NULL AND
              (NEW.vertical_sensitivity_min<0 OR NEW.vertical_sensitivity_unit IS NULL OR trim(NEW.vertical_sensitivity_unit)=''))
          OR (NEW.vertical_sensitivity_max IS NOT NULL AND
              (NEW.vertical_sensitivity_max<0 OR NEW.vertical_sensitivity_unit IS NULL OR trim(NEW.vertical_sensitivity_unit)=''))
          OR (NEW.vertical_sensitivity_min IS NOT NULL AND NEW.vertical_sensitivity_max IS NOT NULL AND
              NEW.vertical_sensitivity_min>NEW.vertical_sensitivity_max)
        BEGIN SELECT RAISE(ABORT,'invalid observational scale'); END
        """,

        """
        CREATE TRIGGER trg_v03_observation_region_update BEFORE UPDATE OF body_id,region_id ON observation
        WHEN NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'observation region belongs to another body'); END
        """,
        """
        CREATE TRIGGER trg_v03_fact_region_update BEFORE UPDATE OF body_id,region_id ON fact
        WHEN NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'fact region belongs to another body'); END
        """,
        """
        CREATE TRIGGER trg_v03_material_region_update BEFORE UPDATE OF body_id,region_id ON material_evidence
        WHEN NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'material region belongs to another body'); END
        """,
        """
        CREATE TRIGGER trg_v03_activity_region_update BEFORE UPDATE OF body_id,region_id ON activity_fact
        WHEN NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'activity region belongs to another body'); END
        """,
        """
        CREATE TRIGGER trg_v03_model_region_update BEFORE UPDATE OF body_id,region_id ON body_model_product
        WHEN NEW.region_id IS NOT NULL AND EXISTS(SELECT 1 FROM body_region r WHERE r.region_id=NEW.region_id AND r.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'model region belongs to another body'); END
        """,
        """
        CREATE TRIGGER trg_v03_region_model_update BEFORE UPDATE OF region_id,model_product_id ON region_model_product
        WHEN EXISTS(SELECT 1 FROM body_region r JOIN body_model_product m ON m.model_product_id=NEW.model_product_id
                    WHERE r.region_id=NEW.region_id AND r.body_id<>m.body_id)
        BEGIN SELECT RAISE(ABORT,'region/model belong to different bodies'); END
        """,
        """
        CREATE TRIGGER trg_v03_fact_observation_update BEFORE UPDATE OF fact_id,observation_id ON fact_observation
        WHEN EXISTS(SELECT 1 FROM fact f JOIN observation o ON o.observation_id=NEW.observation_id
                    WHERE f.fact_id=NEW.fact_id AND f.body_id<>o.body_id)
        BEGIN SELECT RAISE(ABORT,'fact/observation belong to different bodies'); END
        """,

        """
        CREATE TRIGGER trg_v03_region_body_update BEFORE UPDATE OF body_id ON body_region
        WHEN EXISTS(SELECT 1 FROM observation o WHERE o.region_id=NEW.region_id AND o.body_id<>NEW.body_id)
           OR EXISTS(SELECT 1 FROM fact f WHERE f.region_id=NEW.region_id AND f.body_id<>NEW.body_id)
           OR EXISTS(SELECT 1 FROM material_evidence m WHERE m.region_id=NEW.region_id AND m.body_id<>NEW.body_id)
           OR EXISTS(SELECT 1 FROM activity_fact a WHERE a.region_id=NEW.region_id AND a.body_id<>NEW.body_id)
           OR EXISTS(SELECT 1 FROM body_model_product m WHERE m.region_id=NEW.region_id AND m.body_id<>NEW.body_id)
        BEGIN SELECT RAISE(ABORT,'region body would invalidate references'); END
        """,

        """
        CREATE TRIGGER trg_v03_fact_input_insert BEFORE INSERT ON fact_input
        WHEN (NEW.input_fact_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f JOIN fact i ON i.fact_id=NEW.input_fact_id
                    WHERE f.fact_id=NEW.fact_id AND f.body_id<>i.body_id))
          OR (NEW.input_observation_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f JOIN observation o ON o.observation_id=NEW.input_observation_id
                    WHERE f.fact_id=NEW.fact_id AND f.body_id<>o.body_id))
          OR (NEW.input_model_product_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f JOIN body_model_product m ON m.model_product_id=NEW.input_model_product_id
                    WHERE f.fact_id=NEW.fact_id AND f.body_id<>m.body_id))
        BEGIN SELECT RAISE(ABORT,'fact lineage input belongs to another body'); END
        """,
        """
        CREATE TRIGGER trg_v03_fact_input_update BEFORE UPDATE OF fact_id,input_fact_id,input_observation_id,input_model_product_id ON fact_input
        WHEN (NEW.input_fact_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f JOIN fact i ON i.fact_id=NEW.input_fact_id
                    WHERE f.fact_id=NEW.fact_id AND f.body_id<>i.body_id))
          OR (NEW.input_observation_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f JOIN observation o ON o.observation_id=NEW.input_observation_id
                    WHERE f.fact_id=NEW.fact_id AND f.body_id<>o.body_id))
          OR (NEW.input_model_product_id IS NOT NULL AND EXISTS(SELECT 1 FROM fact f JOIN body_model_product m ON m.model_product_id=NEW.input_model_product_id
                    WHERE f.fact_id=NEW.fact_id AND f.body_id<>m.body_id))
        BEGIN SELECT RAISE(ABORT,'fact lineage input belongs to another body'); END
        """,
    )
    for statement in statements:
        conn.execute(statement)


def migrate_connection(conn: sqlite3.Connection) -> dict[str, object]:
    """Migrate an open pristine v0.2 connection in one transaction."""
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        conn.execute("BEGIN IMMEDIATE")
        _source_table(conn)
        _observation_scale(conn)
        _new_tables(conn)
        _migrate_unambiguous_lineage_and_events(conn)
        _triggers(conn)
        conn.execute("UPDATE meta SET value='LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3' WHERE key='schema_name'")
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version','v0.3')")
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('migration_parent','LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.2')")
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('migration_policy','LOSSLESS_LOCAL_QUALIFICATION')")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys=ON")
    return {
        "schema": "LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3",
        "authorized_source_metadata_change": f"OTHER -> PREPRINT for {PREPRINT_IDENTIFIER}",
        "fact_input_rows_migrated": conn.execute("SELECT count(*) FROM fact_input").fetchone()[0],
        "knowledge_event_rows_migrated": conn.execute("SELECT count(*) FROM knowledge_event").fetchone()[0],
    }


def migrate_file(source: Path, destination: Path) -> dict[str, object]:
    source = Path(source)
    destination = Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("refusing to migrate the frozen v0.2 file in place")
    if hashlib.sha256(source.read_bytes()).hexdigest() != V2_SHA256:
        raise ValueError("source is not the trusted frozen HCQ-01 v0.2 specimen")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    conn = sqlite3.connect(destination)
    try:
        return migrate_connection(conn)
    finally:
        conn.close()
