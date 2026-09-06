"""Live CORE-backed gravity qualification for a previewed Sequence-B route.

D2e connects the D2c celestial catalog and D2d shadow propagator without changing
Navigator route authority. Major bodies are propagated from the nearest genuine
heliocentric navigation-grade state as Sun-centric osculating two-body models;
moons are propagated from genuine parent-centric navigation-grade anchors.

D2f adds characterization only: elapsed-time error profiles, simple growth
summaries, dominant-source counts, and body-radius cutoff penetration depth. It
does not alter the shadow integrator, route choice, guidance, campaign state, or
Navigator authority.

The comparison is intentionally fail-closed. Renderer/display fallbacks are not
accepted as physics. Reference samples that enter a gravitating body's recorded
mean radius are excluded from the shadow interval because a point-mass field is
not a collision/surface model and Sequence-B endpoints may represent abstract
body-centre capture states.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import math
import sqlite3
from typing import Any, Mapping

from loom.application.contracts import SpatialState
from loom.spatial.celestial_state import CANONICAL_FRAME, ParentCentricOrbitModel, propagate_parent_centric
from loom.spatial.gravity import GravityEvaluation, GravitySource, evaluate_gravity
from loom.spatial.sqlite_celestial_catalog import (
    AU_KM,
    DAY_S,
    SQLiteCelestialCatalog,
    SQLiteCelestialCatalogError,
    osculating_elements_from_state,
)
from .gravity_shadow import (
    GravityShadowError,
    OrdinaryTrajectorySample,
    compare_gravity_shadow,
    ordinary_samples_from_route_trajectory,
)

LIVE_GRAVITY_COMPARE_CONTRACT = "LOOM_NAV_PHYSICS_V2_LIVE_GRAVITY_COMPARE_V1"


class LiveGravityCompareError(RuntimeError):
    pass


def _epoch(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise LiveGravityCompareError(f"invalid epoch: {value!r}") from exc
    if dt.tzinfo is None:
        raise LiveGravityCompareError("epoch must include timezone")
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm(v: tuple[float, float, float]) -> float:
    return math.sqrt(sum(x * x for x in v))


class SQLiteDynamicGravityField:
    """Resolve moving gravitating bodies from CORE for D2e shadow integration."""

    def __init__(self, db_path: Path | str, anchor_epoch_utc: str):
        self.path = Path(db_path).expanduser().resolve()
        if not self.path.is_file():
            raise LiveGravityCompareError(f"CORE database not found: {self.path}")
        self.anchor_epoch_utc = _iso(_epoch(anchor_epoch_utc))
        self.catalog = SQLiteCelestialCatalog(self.path)
        self._mu: dict[str, float] = {}
        self._radius: dict[str, float] = {}
        self._parent: dict[str, str | None] = {}
        self._models: dict[str, ParentCentricOrbitModel] = {}
        self._model_errors: dict[str, str] = {}
        self._load_catalog()
        self._build_models()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def _load_catalog(self) -> None:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT e.entity_id,d.primary_gravity_parent_id,
                       COALESCE(p.gm_km3_s2,d.gm_km3_s2) AS gm,
                       COALESCE(p.mean_radius_km,d.mean_radius_km) AS radius
                FROM entities e
                LEFT JOIN celestial_dynamics d ON d.entity_id=e.entity_id
                LEFT JOIN celestial_properties p ON p.entity_id=e.entity_id
                WHERE e.entity_class IN ('STAR','PLANET','MOON','DWARF_PLANET','ASTEROID')
                ORDER BY e.entity_id
                """
            ).fetchall()
        for row in rows:
            eid = str(row["entity_id"])
            self._parent[eid] = str(row["primary_gravity_parent_id"]) if row["primary_gravity_parent_id"] else None
            if row["gm"] is not None and float(row["gm"]) > 0.0:
                self._mu[eid] = float(row["gm"])
            if row["radius"] is not None and float(row["radius"]) > 0.0:
                self._radius[eid] = float(row["radius"])

    def _nearest_heliocentric_anchor(self, entity_id: str) -> tuple[str, tuple[float,float,float], tuple[float,float,float], str]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT entity_id,epoch_utc,x_au,y_au,z_au,vx_au_d,vy_au_d,vz_au_d,source
                FROM states
                WHERE entity_id=? AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
                  AND navigation_grade=1
                ORDER BY ABS(julianday(epoch_utc)-julianday(?)) ASC LIMIT 1
                """,
                (entity_id, self.anchor_epoch_utc),
            ).fetchone()
        if row is None:
            raise LiveGravityCompareError(f"no genuine heliocentric anchor for {entity_id}")
        return (
            _iso(_epoch(row["epoch_utc"])),
            (row["x_au"]*AU_KM,row["y_au"]*AU_KM,row["z_au"]*AU_KM),
            (row["vx_au_d"]*AU_KM/DAY_S,row["vy_au_d"]*AU_KM/DAY_S,row["vz_au_d"]*AU_KM/DAY_S),
            str(row["source"]),
        )

    def _build_models(self) -> None:
        solar_mu = self._mu.get("SOL")
        for eid, parent in sorted(self._parent.items()):
            if eid == "SOL":
                continue
            try:
                if parent in (None, "SOL"):
                    if solar_mu is None:
                        raise LiveGravityCompareError("Sun GM unavailable")
                    ep, p, v, source = self._nearest_heliocentric_anchor(eid)
                    elements = osculating_elements_from_state(p, v, solar_mu)
                    self._models[eid] = ParentCentricOrbitModel(
                        entity_id=eid,
                        parent_entity_id="SOL",
                        element_epoch_utc=ep,
                        parent_mu_km3_s2=solar_mu,
                        model_id=f"CORE_HELIOCENTRIC_OSCULATING:{eid}:{ep}",
                        provenance={"anchor_source": source, "derivation": "CORE_NAV_GRADE_HELIOCENTRIC_STATE"},
                        uncertainty={"model_class": "SUN_CENTRIC_TWO_BODY", "unmodeled_perturbations": True},
                        **elements,
                    )
                else:
                    self._models[eid] = self.catalog.orbit_model_from_direct_anchor(eid, self.anchor_epoch_utc)
            except (LiveGravityCompareError, SQLiteCelestialCatalogError) as exc:
                self._model_errors[eid] = str(exc)

    def resolve_state(self, entity_id: str, epoch_utc: str, _stack: tuple[str,...]=()) -> SpatialState:
        epoch = _iso(_epoch(epoch_utc))
        if entity_id == "SOL":
            return SpatialState(
                entity_id="SOL", epoch_utc=epoch, reference_frame=CANONICAL_FRAME,
                position_km=(0.0,0.0,0.0), velocity_km_s=(0.0,0.0,0.0),
                provenance={"state_source":"HELIOCENTRIC_ORIGIN"}, navigation_grade=True,
                payload={"state_class":"CELESTIAL"},
            )
        if entity_id in _stack:
            raise LiveGravityCompareError("gravity parent cycle")
        model = self._models.get(entity_id)
        if model is None:
            raise LiveGravityCompareError(self._model_errors.get(entity_id, f"no propagation model for {entity_id}"))
        parent = self.resolve_state(model.parent_entity_id, epoch, _stack + (entity_id,))
        rp, rv = propagate_parent_centric(model, epoch)
        return SpatialState(
            entity_id=entity_id, epoch_utc=epoch, reference_frame=CANONICAL_FRAME,
            position_km=tuple(parent.position_km[i]+rp[i] for i in range(3)),
            velocity_km_s=tuple(parent.velocity_km_s[i]+rv[i] for i in range(3)),
            provenance={"state_source":"PROPAGATED_OSCULATING_FOR_D2E","model_id":model.model_id,"parent_entity_id":model.parent_entity_id,"model_provenance":dict(model.provenance)},
            navigation_grade=False, uncertainty=dict(model.uncertainty), payload={"state_class":"CELESTIAL"},
        )

    def evaluator(self, position_km: tuple[float,float,float], epoch_utc: str, *, minimum_acceleration_km_s2: float=1e-12) -> GravityEvaluation:
        sources: list[GravitySource] = []
        for eid, mu in sorted(self._mu.items()):
            try:
                state = self.resolve_state(eid, epoch_utc)
            except LiveGravityCompareError:
                continue
            sources.append(GravitySource(eid,state,mu,provenance={"gm_source":"CORE celestial catalog"},uncertainty=state.uncertainty))
        if not sources:
            raise LiveGravityCompareError("no resolvable gravity sources")
        return evaluate_gravity(position_km,sources,epoch_utc=_iso(_epoch(epoch_utc)),minimum_acceleration_km_s2=minimum_acceleration_km_s2)

    def physically_valid_reference(self, samples: tuple[OrdinaryTrajectorySample,...]) -> tuple[tuple[OrdinaryTrajectorySample,...], dict[str,Any]]:
        kept: list[OrdinaryTrajectorySample] = []
        cutoff: dict[str,Any] = {"applied":False}
        for sample in samples:
            violation = None
            for eid, radius in self._radius.items():
                try:
                    state = self.resolve_state(eid,sample.epoch_utc)
                except LiveGravityCompareError:
                    continue
                sep = _norm(tuple(sample.position_km[i]-state.position_km[i] for i in range(3)))
                if sep <= radius:
                    violation = (eid,radius,sep)
                    break
            if violation:
                cutoff={"applied":True,"body_id":violation[0],"mean_radius_km":violation[1],"reference_separation_km":violation[2],"excluded_from_sample_index":sample.sample_index,"reason":"REFERENCE_ENTERED_BODY_RADIUS_POINT_MASS_MODEL_INVALID"}
                break
            kept.append(sample)
        if len(kept) < 2:
            raise LiveGravityCompareError("fewer than two physically valid ordinary samples remain")
        cutoff["original_sample_count"] = len(samples)
        cutoff["qualified_sample_count"] = len(kept)
        return tuple(kept), cutoff

    def diagnostics(self) -> dict[str,Any]:
        return {
            "database": str(self.path),
            "gravity_parameter_count": len(self._mu),
            "radius_count": len(self._radius),
            "propagation_model_count": len(self._models),
            "unresolved_model_count": len(self._model_errors),
            "unresolved_models": dict(sorted(self._model_errors.items())),
        }


def _characterize_report(report: Any, cutoff: Mapping[str,Any]) -> dict[str,Any]:
    """Produce D2f comparison diagnostics without changing the D2e solution."""
    rows = tuple(report.samples)
    t0 = _epoch(report.start_epoch_utc)
    profile: list[dict[str,Any]] = []
    dominant_counts: dict[str,int] = {}
    pos_non_decreasing = 0
    vel_non_decreasing = 0
    for i, row in enumerate(rows):
        elapsed_s = (_epoch(row.epoch_utc) - t0).total_seconds()
        profile.append({
            "elapsed_s": elapsed_s,
            "epoch_utc": row.epoch_utc,
            "position_error_km": row.position_error_km,
            "velocity_error_km_s": row.velocity_error_km_s,
            "gravity_magnitude_km_s2": row.gravity_magnitude_km_s2,
            "dominant_gravity_source": row.dominant_gravity_source,
        })
        if row.dominant_gravity_source:
            dominant_counts[row.dominant_gravity_source] = dominant_counts.get(row.dominant_gravity_source, 0) + 1
        if i:
            if row.position_error_km + 1e-12 >= rows[i-1].position_error_km:
                pos_non_decreasing += 1
            if row.velocity_error_km_s + 1e-15 >= rows[i-1].velocity_error_km_s:
                vel_non_decreasing += 1
    duration_s = (_epoch(report.end_epoch_utc) - t0).total_seconds()
    intervals = max(0, len(rows)-1)
    duration_min = duration_s / 60.0
    out: dict[str,Any] = {
        "contract": "LOOM_NAV_PHYSICS_V2_D2F_CHARACTERIZATION_V1",
        "duration_s": duration_s,
        "position_error_growth_km_per_min": report.terminal_position_error_km / duration_min if duration_min > 0.0 else None,
        "velocity_error_growth_m_s_per_min": report.terminal_velocity_error_km_s * 1000.0 / duration_min if duration_min > 0.0 else None,
        "position_error_non_decreasing_fraction": pos_non_decreasing / intervals if intervals else None,
        "velocity_error_non_decreasing_fraction": vel_non_decreasing / intervals if intervals else None,
        "dominant_gravity_source_counts": dict(sorted(dominant_counts.items())),
        "error_profile": profile,
    }
    if cutoff.get("applied"):
        radius = float(cutoff["mean_radius_km"])
        separation = float(cutoff["reference_separation_km"])
        out["reference_cutoff_penetration_km"] = max(0.0, radius-separation)
    else:
        out["reference_cutoff_penetration_km"] = None
    return out


def compare_live_route_trajectory(
    trajectory: Mapping[str,Any], db_path: Path | str, *, max_step_s: float=30.0,
    minimum_acceleration_km_s2: float=1e-12,
) -> dict[str,Any]:
    samples = ordinary_samples_from_route_trajectory(trajectory)
    field = SQLiteDynamicGravityField(db_path,samples[0].epoch_utc)
    qualified, cutoff = field.physically_valid_reference(samples)

    def gravity(position: tuple[float,float,float], epoch: str) -> GravityEvaluation:
        return field.evaluator(position,epoch,minimum_acceleration_km_s2=minimum_acceleration_km_s2)

    try:
        report = compare_gravity_shadow(qualified,gravity,max_step_s=max_step_s)
    except (GravityShadowError, LiveGravityCompareError) as exc:
        raise LiveGravityCompareError(str(exc)) from exc
    return {
        "contract": LIVE_GRAVITY_COMPARE_CONTRACT,
        "authority": "DIAGNOSTIC_SHADOW_ONLY_NOT_ROUTE_AUTHORITY",
        "trajectory_authority": trajectory.get("authority"),
        "route_plan_id": trajectory.get("route_plan_id"),
        "solution_key": trajectory.get("solution_key"),
        "coordinate_frame": trajectory.get("coordinate_frame"),
        "reference_cutoff": cutoff,
        "field": field.diagnostics(),
        "report": asdict(report),
        "characterization": _characterize_report(report, cutoff),
        "qualification": {
            "campaign_mutation": False,
            "route_mutation": False,
            "metric_relational_segment_integrated": False,
            "major_body_states": "CORE_NAV_GRADE_HELIOCENTRIC_ANCHOR_TO_SUN_CENTRIC_OSCULATING",
            "moon_states": "CORE_NAV_GRADE_PARENT_CENTRIC_ANCHOR_TO_PARENT_CENTRIC_OSCULATING",
            "display_fallbacks": "REJECTED",
            "unmodeled_perturbations": True,
        },
    }
