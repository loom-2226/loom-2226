from __future__ import annotations

import sqlite3


def knowledge_snapshot(conn: sqlite3.Connection, cutoff: str) -> dict[str, list[dict]]:
    """Return evidence available by cutoff without using retrieval time."""
    def rows(sql: str, args: tuple = ()) -> list[dict]:
        cur = conn.execute(sql, args)
        names = [d[0] for d in cur.description]
        return [dict(zip(names, row)) for row in cur.fetchall()]

    return {
        "sources": rows("SELECT * FROM source WHERE publication_date<=? ORDER BY source_id", (cutoff,)),
        "facts": rows("SELECT f.* FROM fact f JOIN source_assertion sa ON sa.fact_id=f.fact_id JOIN source s ON s.source_id=sa.source_id WHERE f.fact_status='CANDIDATE' AND f.knowledge_valid_from<=? AND s.publication_date<=? ORDER BY f.fact_id", (cutoff, cutoff)),
        "observations": rows("SELECT o.* FROM observation o JOIN source s ON s.source_id=o.source_id WHERE s.publication_date<=? ORDER BY o.observation_id", (cutoff,)),
        "materials": rows("SELECT m.* FROM material_evidence m JOIN source s ON s.source_id=m.source_id WHERE s.publication_date<=? ORDER BY m.material_evidence_id", (cutoff,)),
        "models": rows("SELECT m.* FROM body_model_product m JOIN source s ON s.source_id=m.source_id WHERE s.publication_date<=? ORDER BY m.model_product_id", (cutoff,)),
    }
