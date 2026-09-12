"""Read-only body radius/GM adapter over existing WORLD authority."""
from __future__ import annotations

from pathlib import Path
import math
import sqlite3
from typing import Any


class SQLiteBodyPropertyCatalogError(RuntimeError):
    pass


class SQLiteBodyPropertyCatalog:
    def __init__(self, db_path: Path | str) -> None:
        self.path = Path(db_path).expanduser().resolve()

    def _connect(self) -> sqlite3.Connection:
        if not self.path.is_file():
            raise SQLiteBodyPropertyCatalogError(f"WORLD database not found: {self.path}")
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def get(self, entity_id: str) -> dict[str, Any]:
        key = str(entity_id).strip()
        if not key:
            raise SQLiteBodyPropertyCatalogError("entity_id is required")
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT entity_id,gm_km3_s2,mean_radius_km,source_id,status
                FROM celestial_properties
                WHERE entity_id=?
                """,
                (key,),
            ).fetchone()
            if row is not None and row["gm_km3_s2"] is not None and row["mean_radius_km"] is not None:
                radius = float(row["mean_radius_km"])
                mu = float(row["gm_km3_s2"])
                source = f"celestial_properties:{row['source_id'] or ''}:{row['status'] or ''}"
            else:
                row = conn.execute(
                    """
                    SELECT entity_id,gm_km3_s2,mean_radius_km,source,metadata_status
                    FROM celestial_dynamics
                    WHERE entity_id=?
                    """,
                    (key,),
                ).fetchone()
                if row is None or row["gm_km3_s2"] is None or row["mean_radius_km"] is None:
                    raise SQLiteBodyPropertyCatalogError(f"body properties incomplete for {key}")
                radius = float(row["mean_radius_km"])
                mu = float(row["gm_km3_s2"])
                source = f"celestial_dynamics:{row['source'] or ''}:{row['metadata_status'] or ''}"
        if not math.isfinite(radius) or radius <= 0.0 or not math.isfinite(mu) or mu <= 0.0:
            raise SQLiteBodyPropertyCatalogError(f"invalid body properties for {key}")
        return {
            "entity_id": key,
            "radius_km": radius,
            "mu_km3_s2": mu,
            "source": source,
        }
