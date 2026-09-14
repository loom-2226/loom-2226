"""Read-only exact-or-interpolated celestial resolver for E1.

Exact navigation-grade SQLite state remains preferred. When an exact row is not
available, the resolver requires two bracketing navigation-grade J2000/ECLIPTIC
rows for the same entity and applies the qualified cubic-Hermite interpolation
helper. No extrapolation, display-only fallback, route solve, radius policy,
campaign mutation, or LLM authority is introduced here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from src.loom_ephemeris_interpolation import EphemerisAnchor, hermite_state
from src.loom_sqlite_celestial_provider import AU_KM, DAY_S, SQLiteCelestialCatalog
from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError, SpatialState


class SQLiteInterpolatedCelestialError(CelestialStateError):
    pass


def _epoch(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise SQLiteInterpolatedCelestialError(f"invalid epoch_utc: {value!r}") from exc
    if dt.tzinfo is None:
        raise SQLiteInterpolatedCelestialError("epoch_utc must include timezone")
    return dt.astimezone(timezone.utc)


def _iso_preserve(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _anchor(row: sqlite3.Row) -> EphemerisAnchor:
    return EphemerisAnchor(
        epoch_utc=str(row["epoch_utc"]),
        position_km=(float(row["x_au"]) * AU_KM, float(row["y_au"]) * AU_KM, float(row["z_au"]) * AU_KM),
        velocity_km_s=(
            float(row["vx_au_d"]) * AU_KM / DAY_S,
            float(row["vy_au_d"]) * AU_KM / DAY_S,
            float(row["vz_au_d"]) * AU_KM / DAY_S,
        ),
    )


class SQLiteInterpolatedCelestialResolver:
    """Resolve exact direct state first, otherwise qualified bracket interpolation."""

    def __init__(self, db_path: Path | str):
        self.path = Path(db_path).expanduser().resolve()
        self.catalog = SQLiteCelestialCatalog(self.path)

    def _connect(self) -> sqlite3.Connection:
        if not self.path.is_file():
            raise SQLiteInterpolatedCelestialError(f"celestial database not found: {self.path}")
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def resolve(self, entity_id: str, epoch_utc: str) -> SpatialState:
        entity = str(entity_id).strip()
        if not entity:
            raise SQLiteInterpolatedCelestialError("entity_id is required")
        requested_dt = _epoch(epoch_utc)
        requested = _iso_preserve(requested_dt)

        direct = self.catalog.direct_state(entity, requested)
        if direct is not None and _epoch(direct.epoch_utc) == requested_dt:
            return direct

        # SQLite timestamps in LOOM are canonical ISO UTC strings. Compare with
        # julianday so sub-second request epochs bracket correctly even when
        # stored anchors are whole-second samples.
        with self._connect() as conn:
            before = conn.execute(
                """
                SELECT entity_id,epoch_utc,x_au,y_au,z_au,vx_au_d,vy_au_d,vz_au_d,source
                FROM states
                WHERE entity_id=?
                  AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
                  AND navigation_grade=1
                  AND julianday(epoch_utc) < julianday(?)
                ORDER BY julianday(epoch_utc) DESC LIMIT 1
                """,
                (entity, requested),
            ).fetchone()
            after = conn.execute(
                """
                SELECT entity_id,epoch_utc,x_au,y_au,z_au,vx_au_d,vy_au_d,vz_au_d,source
                FROM states
                WHERE entity_id=?
                  AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
                  AND navigation_grade=1
                  AND julianday(epoch_utc) > julianday(?)
                ORDER BY julianday(epoch_utc) ASC LIMIT 1
                """,
                (entity, requested),
            ).fetchone()

        if before is None or after is None:
            raise SQLiteInterpolatedCelestialError(
                f"no navigation-grade bracketing states for {entity} at {requested}"
            )

        a, b = _anchor(before), _anchor(after)
        try:
            position, velocity = hermite_state(a, b, requested)
        except ValueError as exc:
            raise SQLiteInterpolatedCelestialError(str(exc)) from exc

        return SpatialState(
            entity_id=entity,
            epoch_utc=requested,
            reference_frame=CANONICAL_FRAME,
            position_km=position,
            velocity_km_s=velocity,
            provenance={
                "state_source": "INTERPOLATED_NAVIGATION_GRADE",
                "interpolation_method": "CUBIC_HERMITE_POSITION_VELOCITY",
                "store": "states",
                "before_epoch_utc": str(before["epoch_utc"]),
                "after_epoch_utc": str(after["epoch_utc"]),
                "before_source": before["source"],
                "after_source": after["source"],
                "qualification": "INTERPOLATED_FROM_NAVIGATION_GRADE_BRACKET",
            },
            navigation_grade=True,
            uncertainty={
                "state_class": "INTERPOLATED_BETWEEN_NAVIGATION_GRADE_ANCHORS",
                "extrapolation": False,
            },
            payload={"state_class": "CELESTIAL"},
        )
