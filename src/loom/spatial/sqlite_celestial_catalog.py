"""SQLite adapter from LOOM celestial ephemeris/catalog data to Physics v2 states.

This module bridges the existing CORE/WORLD astronomical tables into the shared
HybridCelestialStateService without promoting renderer-only fallbacks to physics.

Rules:
- exact J2000/ECLIPTIC navigation-grade states may be used directly;
- a moon without direct coverage may be propagated only from a stored genuine
  navigation-grade parent-centric ephemeris anchor;
- parent GM comes from the existing celestial-properties/dynamics catalog;
- display-only circular-period fallbacks are never converted into physics
  authority here;
- the database is opened read-only/query-only and is never modified.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import math
import sqlite3
from typing import Iterable

from loom.application.contracts import SpatialState
from .celestial_state import (
    CANONICAL_FRAME,
    CelestialStateError,
    HybridCelestialStateService,
    ParentCentricOrbitModel,
)

AU_KM = 149_597_870.7
DAY_S = 86_400.0


class SQLiteCelestialCatalogError(CelestialStateError):
    pass


def _epoch(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise SQLiteCelestialCatalogError(f"invalid epoch_utc: {value!r}") from exc
    if dt.tzinfo is None:
        raise SQLiteCelestialCatalogError("epoch_utc must include timezone")
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm(v: tuple[float, float, float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(a[i] * b[i] for i in range(3))


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _clamp(value: float) -> float:
    return max(-1.0, min(1.0, value))


def osculating_elements_from_state(
    position_km: tuple[float, float, float],
    velocity_km_s: tuple[float, float, float],
    mu_km3_s2: float,
) -> dict[str, float]:
    """Convert one bound Cartesian parent-centric state into elliptic elements.

    Returned angles are degrees in the same inertial frame as the input state.
    Degenerate circular/equatorial cases use conventional zero-valued undefined
    angles while preserving the physical longitude in mean anomaly.
    """
    r = tuple(float(x) for x in position_km)
    v = tuple(float(x) for x in velocity_km_s)
    mu = float(mu_km3_s2)
    if not math.isfinite(mu) or mu <= 0.0:
        raise SQLiteCelestialCatalogError("parent GM must be finite and positive")
    if not all(math.isfinite(x) for x in (*r, *v)):
        raise SQLiteCelestialCatalogError("state vector must contain finite values")
    rmag = _norm(r)
    vmag = _norm(v)
    if rmag <= 0.0:
        raise SQLiteCelestialCatalogError("zero-radius ephemeris anchor")

    h = _cross(r, v)
    hmag = _norm(h)
    if hmag <= 0.0:
        raise SQLiteCelestialCatalogError("degenerate radial ephemeris anchor")
    n = (-h[1], h[0], 0.0)
    nmag = _norm(n)

    vxh = _cross(v, h)
    evec = tuple(vxh[i] / mu - r[i] / rmag for i in range(3))
    ecc = _norm(evec)
    if not (0.0 <= ecc < 1.0):
        raise SQLiteCelestialCatalogError(f"only bound elliptic moon anchors are supported; e={ecc}")

    energy = 0.5 * vmag * vmag - mu / rmag
    if energy >= 0.0:
        raise SQLiteCelestialCatalogError("ephemeris anchor is not a bound elliptic state")
    a = -mu / (2.0 * energy)
    inc = math.acos(_clamp(h[2] / hmag))

    eps = 1e-12
    if nmag > eps:
        raan = math.atan2(n[1], n[0]) % (2.0 * math.pi)
    else:
        raan = 0.0

    if ecc > eps and nmag > eps:
        argp = math.acos(_clamp(_dot(n, evec) / (nmag * ecc)))
        if evec[2] < 0.0:
            argp = 2.0 * math.pi - argp
    elif ecc > eps:
        argp = math.atan2(evec[1], evec[0]) % (2.0 * math.pi)
    else:
        argp = 0.0

    if ecc > eps:
        nu = math.acos(_clamp(_dot(evec, r) / (ecc * rmag)))
        if _dot(r, v) < 0.0:
            nu = 2.0 * math.pi - nu
        e_anom = 2.0 * math.atan2(
            math.sqrt(1.0 - ecc) * math.sin(nu / 2.0),
            math.sqrt(1.0 + ecc) * math.cos(nu / 2.0),
        )
        mean = (e_anom - ecc * math.sin(e_anom)) % (2.0 * math.pi)
    else:
        # For circular orbits periapsis is undefined. Preserve orbital phase as
        # argument of latitude (or true longitude for equatorial circular).
        if nmag > eps:
            phase = math.acos(_clamp(_dot(n, r) / (nmag * rmag)))
            if r[2] < 0.0:
                phase = 2.0 * math.pi - phase
        else:
            phase = math.atan2(r[1], r[0]) % (2.0 * math.pi)
        mean = phase

    return {
        "semi_major_axis_km": a,
        "eccentricity": ecc,
        "inclination_deg": math.degrees(inc),
        "raan_deg": math.degrees(raan),
        "arg_periapsis_deg": math.degrees(argp),
        "mean_anomaly_deg": math.degrees(mean),
    }


class SQLiteCelestialCatalog:
    """Read-only provider of direct states and propagated moon models."""

    def __init__(self, db_path: Path | str):
        self.path = Path(db_path).expanduser().resolve()

    def _connect(self) -> sqlite3.Connection:
        if not self.path.is_file():
            raise SQLiteCelestialCatalogError(f"celestial database not found: {self.path}")
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def direct_state(self, entity_id: str, epoch_utc: str) -> SpatialState | None:
        """Return only an exact navigation-grade heliocentric state."""
        epoch = _iso(_epoch(epoch_utc))
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT s.entity_id,s.x_au,s.y_au,s.z_au,
                       s.vx_au_d,s.vy_au_d,s.vz_au_d,s.source,s.navigation_grade
                FROM states s
                WHERE s.entity_id=? AND s.epoch_utc=?
                  AND s.reference_frame='J2000' AND s.reference_plane='ECLIPTIC'
                  AND s.navigation_grade=1
                """,
                (entity_id, epoch),
            ).fetchone()
        if row is None:
            return None
        return SpatialState(
            entity_id=row["entity_id"],
            epoch_utc=epoch,
            reference_frame=CANONICAL_FRAME,
            position_km=(row["x_au"] * AU_KM, row["y_au"] * AU_KM, row["z_au"] * AU_KM),
            velocity_km_s=(row["vx_au_d"] * AU_KM / DAY_S, row["vy_au_d"] * AU_KM / DAY_S, row["vz_au_d"] * AU_KM / DAY_S),
            provenance={"state_source": row["source"], "store": "states", "qualification": "DIRECT_NAVIGATION_GRADE"},
            navigation_grade=True,
            payload={"state_class": "CELESTIAL"},
        )

    def _parent_mu(self, conn: sqlite3.Connection, parent_entity_id: str) -> tuple[float, str]:
        row = conn.execute(
            "SELECT gm_km3_s2,source_id,status FROM celestial_properties WHERE entity_id=?",
            (parent_entity_id,),
        ).fetchone()
        if row is not None and row["gm_km3_s2"] is not None:
            return float(row["gm_km3_s2"]), f"celestial_properties:{row['source_id'] or ''}:{row['status']}"
        row = conn.execute(
            "SELECT gm_km3_s2,source,metadata_status FROM celestial_dynamics WHERE entity_id=?",
            (parent_entity_id,),
        ).fetchone()
        if row is not None and row["gm_km3_s2"] is not None:
            return float(row["gm_km3_s2"]), f"celestial_dynamics:{row['source']}:{row['metadata_status']}"
        raise SQLiteCelestialCatalogError(f"no parent GM available for {parent_entity_id}")

    def orbit_model_from_direct_anchor(self, entity_id: str, requested_epoch_utc: str) -> ParentCentricOrbitModel:
        """Derive a propagator from the latest genuine local JPL/nav-grade anchor."""
        requested = _iso(_epoch(requested_epoch_utc))
        with self._connect() as conn:
            dyn = conn.execute(
                "SELECT primary_gravity_parent_id,source FROM celestial_dynamics WHERE entity_id=?",
                (entity_id,),
            ).fetchone()
            if dyn is None or not dyn["primary_gravity_parent_id"]:
                raise SQLiteCelestialCatalogError(f"no declared gravity parent for {entity_id}")
            parent = str(dyn["primary_gravity_parent_id"])
            mu, mu_source = self._parent_mu(conn, parent)
            anchor = conn.execute(
                """
                SELECT * FROM ephemeris_states
                WHERE entity_id=? AND center_entity_id=?
                  AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
                  AND navigation_grade=1 AND epoch_utc<=?
                ORDER BY epoch_utc DESC LIMIT 1
                """,
                (entity_id, parent, requested),
            ).fetchone()
            if anchor is None:
                # Future/historical queries before the first local sample may still
                # use the nearest genuine anchor. Never use a display-only sample.
                anchor = conn.execute(
                    """
                    SELECT * FROM ephemeris_states
                    WHERE entity_id=? AND center_entity_id=?
                      AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
                      AND navigation_grade=1
                    ORDER BY ABS(julianday(epoch_utc)-julianday(?)) ASC LIMIT 1
                    """,
                    (entity_id, parent, requested),
                ).fetchone()
            if anchor is None:
                raise SQLiteCelestialCatalogError(
                    f"no genuine navigation-grade parent-centric ephemeris anchor for {entity_id}"
                )

        units = str(anchor["units"] or "").upper().replace(" ", "")
        if units not in {"AU/AU-DAY", "AU/AU-DAY".replace(" ", "")}:
            raise SQLiteCelestialCatalogError(f"unsupported local ephemeris units for {entity_id}: {anchor['units']}")
        r = (anchor["x"] * AU_KM, anchor["y"] * AU_KM, anchor["z"] * AU_KM)
        v = (anchor["vx"] * AU_KM / DAY_S, anchor["vy"] * AU_KM / DAY_S, anchor["vz"] * AU_KM / DAY_S)
        elements = osculating_elements_from_state(r, v, mu)
        anchor_epoch = _iso(_epoch(anchor["epoch_utc"]))
        age_days = abs((_epoch(requested) - _epoch(anchor_epoch)).total_seconds()) / DAY_S
        return ParentCentricOrbitModel(
            entity_id=entity_id,
            parent_entity_id=parent,
            element_epoch_utc=anchor_epoch,
            parent_mu_km3_s2=mu,
            model_id=f"SQLITE_DIRECT_ANCHOR_OSCULATING:{entity_id}:{anchor_epoch}",
            provenance={
                "catalog": str(self.path),
                "anchor_source": anchor["source"],
                "anchor_status": anchor["ephemeris_status"],
                "anchor_navigation_grade": True,
                "parent_mu_source": mu_source,
                "dynamics_source": dyn["source"],
                "derivation": "CARTESIAN_TO_OSCULATING_ELEMENTS",
            },
            uncertainty={
                "anchor_age_days": age_days,
                "model_class": "TWO_BODY_OSCULATING_FROM_DIRECT_STATE",
                "unmodeled_perturbations": True,
                "navigation_qualification": "PROPAGATED_NOT_DIRECT",
            },
            **elements,
        )

    def build_service(self, entity_ids: Iterable[str], epoch_utc: str) -> HybridCelestialStateService:
        """Build a service with propagation models only where direct state is absent."""
        epoch = _iso(_epoch(epoch_utc))
        models: dict[str, ParentCentricOrbitModel] = {}
        for entity_id in sorted({str(v).strip() for v in entity_ids if str(v).strip()}):
            if self.direct_state(entity_id, epoch) is not None:
                continue
            try:
                models[entity_id] = self.orbit_model_from_direct_anchor(entity_id, epoch)
            except SQLiteCelestialCatalogError:
                # Parents and major bodies may intentionally have no parent-centric
                # model; they still resolve through direct_state. Missing required
                # children fail later at resolve(), preserving fail-closed behavior.
                pass
        return HybridCelestialStateService(self.direct_state, models)
