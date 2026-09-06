"""Read-only SQLite adapter for canonical LOOM spatial state.

Stage C promotes the already-populated CORE/WORLD state vectors into the shared
SpatialState application contract. This module never performs orbital mechanics
and never writes the world database: it only reads state that the existing GIS
runtime has already acquired/derived for a resolved scene epoch.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import sqlite3

from loom.application.contracts import SpatialState

AU_KM = 149_597_870.7
DAY_S = 86_400.0
SPATIAL_SNAPSHOT_CONTRACT = "LOOM_SPATIAL_STATE_SNAPSHOT_V1"
CANONICAL_FRAME = "J2000/ECLIPTIC"


class SpatialSQLiteError(RuntimeError):
    pass


def normalize_epoch_seconds(value: str) -> str:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise SpatialSQLiteError(f"invalid spatial epoch: {value!r}") from exc
    if dt.tzinfo is None:
        raise SpatialSQLiteError("spatial epoch must include timezone")
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SQLiteSpatialStateSource:
    """Read canonical celestial + derived infrastructure state for one epoch."""

    def __init__(self, db_path: Path | str):
        self.path = Path(db_path).expanduser().resolve()

    def _connect(self) -> sqlite3.Connection:
        if not self.path.is_file():
            raise SpatialSQLiteError(f"spatial database not found: {self.path}")
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def states_at(self, epoch_utc: str) -> tuple[SpatialState, ...]:
        epoch = normalize_epoch_seconds(epoch_utc)
        out: list[SpatialState] = []
        with self._connect() as conn:
            # `states` is the legacy scene/cache table and may contain derived
            # infrastructure copies as well as celestial ephemeris rows. A
            # first-class `spatial_states` row at the same epoch therefore takes
            # precedence for classification and provenance. Do not infer entity
            # role from identifiers or from which renderer table happens to contain
            # a copy.
            celestial = conn.execute(
                """
                SELECT s.entity_id,e.name,s.x_au,s.y_au,s.z_au,
                       s.vx_au_d,s.vy_au_d,s.vz_au_d,s.source,s.navigation_grade
                FROM states s
                JOIN entities e ON e.entity_id=s.entity_id
                WHERE s.epoch_utc=? AND s.reference_frame='J2000' AND s.reference_plane='ECLIPTIC'
                  AND NOT EXISTS (
                      SELECT 1 FROM spatial_states p
                      WHERE p.entity_id=s.entity_id AND p.epoch_utc=s.epoch_utc
                  )
                ORDER BY s.entity_id
                """,
                (epoch,),
            ).fetchall()
            for row in celestial:
                out.append(SpatialState(
                    entity_id=row["entity_id"],
                    epoch_utc=epoch,
                    reference_frame=CANONICAL_FRAME,
                    position_km=(row["x_au"] * AU_KM, row["y_au"] * AU_KM, row["z_au"] * AU_KM),
                    velocity_km_s=(row["vx_au_d"] * AU_KM / DAY_S, row["vy_au_d"] * AU_KM / DAY_S, row["vz_au_d"] * AU_KM / DAY_S),
                    provenance={"state_source": row["source"], "store": "states"},
                    navigation_grade=bool(row["navigation_grade"]),
                    payload={"name": row["name"], "state_class": "CELESTIAL"},
                ))

            infrastructure = conn.execute(
                """
                SELECT s.entity_id,e.name,s.x_km,s.y_km,s.z_km,
                       s.vx_km_s,s.vy_km_s,s.vz_km_s,s.state_source,s.model_id,
                       s.navigation_grade,s.validity_status,s.center_entity_id,s.reference_frame
                FROM spatial_states s
                JOIN entities e ON e.entity_id=s.entity_id
                WHERE s.epoch_utc=?
                ORDER BY s.entity_id
                """,
                (epoch,),
            ).fetchall()
            for row in infrastructure:
                out.append(SpatialState(
                    entity_id=row["entity_id"],
                    epoch_utc=epoch,
                    reference_frame=str(row["reference_frame"] or CANONICAL_FRAME),
                    position_km=(row["x_km"], row["y_km"], row["z_km"]),
                    velocity_km_s=(row["vx_km_s"], row["vy_km_s"], row["vz_km_s"]),
                    provenance={
                        "state_source": row["state_source"],
                        "model_id": row["model_id"],
                        "store": "spatial_states",
                    },
                    navigation_grade=bool(row["navigation_grade"]),
                    payload={
                        "name": row["name"],
                        "state_class": "INFRASTRUCTURE",
                        "center_entity_id": row["center_entity_id"],
                        "validity_status": row["validity_status"],
                    },
                ))
        return tuple(sorted(out, key=lambda state: state.entity_id))

    def snapshot(
        self,
        epoch_utc: str,
        *,
        campaign_revision: int | None = None,
        campaign_epoch_utc: str | None = None,
        epoch_source: str | None = None,
    ) -> dict[str, Any]:
        resolved = normalize_epoch_seconds(epoch_utc)
        states = self.states_at(resolved)
        counts = {
            "total": len(states),
            "navigation_grade": sum(state.navigation_grade is True for state in states),
            "non_navigation_grade": sum(state.navigation_grade is not True for state in states),
            "celestial": sum(state.payload.get("state_class") == "CELESTIAL" for state in states),
            "infrastructure": sum(state.payload.get("state_class") == "INFRASTRUCTURE" for state in states),
        }
        return {
            "contract": SPATIAL_SNAPSHOT_CONTRACT,
            "epoch_utc": resolved,
            "reference_frame": CANONICAL_FRAME,
            "epoch_source": epoch_source,
            "campaign_stamp": {
                "revision": campaign_revision,
                "epoch_utc": campaign_epoch_utc,
            },
            "source": {
                "database": str(self.path),
                "mode": "READ_ONLY",
            },
            "counts": counts,
            "states": [asdict(state) for state in states],
        }
