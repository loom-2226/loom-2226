"""Read-only resolver for standard-orbit target definitions in SPATIAL_GEOMETRY.

The geometry registry owns only the named orbit definition. Body radius/GM and
parent-body state are injected from existing shared authority services, and the
existing parent-centric propagator performs the actual orbital calculation.
"""
from __future__ import annotations

from pathlib import Path
import math
import sqlite3
from typing import Any, Callable, Mapping

from loom.application.contracts import SpatialState
from .celestial_state import CANONICAL_FRAME, ParentCentricOrbitModel, propagate_parent_centric


class SQLiteStandardOrbitResolverError(RuntimeError):
    pass


BodyStateResolver = Callable[[str, str], SpatialState]
BodyPropertyResolver = Callable[[str], Mapping[str, Any]]


class SQLiteStandardOrbitResolver:
    def __init__(
        self,
        geometry_db_path: Path | str,
        body_state_resolver: BodyStateResolver,
        body_property_resolver: BodyPropertyResolver,
    ) -> None:
        self.path = Path(geometry_db_path).expanduser().resolve()
        self._body_state_resolver = body_state_resolver
        self._body_property_resolver = body_property_resolver

    def _connect(self) -> sqlite3.Connection:
        if not self.path.is_file():
            raise SQLiteStandardOrbitResolverError(f"SPATIAL_GEOMETRY database not found: {self.path}")
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def _row(self, target_id: str) -> sqlite3.Row:
        key = str(target_id).strip()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT s.object_id,s.display_name,s.parent_body_id,s.operational_role,s.status,
                       o.representation,o.element_epoch_utc,o.semi_major_axis_km,o.altitude_km,
                       o.eccentricity,o.inclination_deg,o.raan_deg,o.arg_periapsis_deg,
                       o.mean_anomaly_deg,o.reference_frame,o.navigation_grade,
                       o.epistemic_status,o.derivation_note
                FROM spatial_objects s
                JOIN standard_orbits o ON o.object_id=s.object_id
                WHERE s.object_kind='STANDARD_ORBIT' AND s.object_id=?
                """,
                (key,),
            ).fetchone()
        if row is None:
            raise SQLiteStandardOrbitResolverError(f"unknown standard orbit target: {key}")
        return row

    def list_targets(self) -> tuple[dict[str, Any], ...]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.object_id,s.display_name,s.parent_body_id,s.operational_role,s.status,
                       o.altitude_km,o.inclination_deg,o.reference_frame,o.navigation_grade,
                       o.epistemic_status
                FROM spatial_objects s
                JOIN standard_orbits o ON o.object_id=s.object_id
                WHERE s.object_kind='STANDARD_ORBIT'
                ORDER BY s.object_id
                """
            ).fetchall()
        return tuple(
            {
                "contract": "LOOM_SPATIAL_TARGET_V1",
                "target_id": row["object_id"],
                "target_type": "STANDARD_ORBIT",
                "display_name": row["display_name"],
                "parent_body": row["parent_body_id"],
                "operational_role": row["operational_role"],
                "status": row["status"],
                "altitude_km": row["altitude_km"],
                "inclination_deg": row["inclination_deg"],
                "reference_frame": row["reference_frame"],
                "navigation_grade": bool(row["navigation_grade"]),
                "epistemic_status": row["epistemic_status"],
            }
            for row in rows
        )

    def describe_target(self, target_id: str) -> dict[str, Any]:
        row = self._row(target_id)
        return {
            "contract": "LOOM_SPATIAL_TARGET_V1",
            "target_id": row["object_id"],
            "target_type": "STANDARD_ORBIT",
            "display_name": row["display_name"],
            "parent_body": row["parent_body_id"],
            "operational_role": row["operational_role"],
            "status": row["status"],
            "state_availability": "RESOLVABLE_SHARED_CONVENTIONAL",
            "state_method": "SPATIAL_GEOMETRY_DEFINITION_SHARED_KEPLER_PROPAGATOR",
            "reference_frame": row["reference_frame"],
            "navigation_grade": bool(row["navigation_grade"]),
            "epistemic_status": row["epistemic_status"],
            "orbit": {
                "representation": row["representation"],
                "element_epoch_utc": row["element_epoch_utc"],
                "semi_major_axis_km": row["semi_major_axis_km"],
                "altitude_km": row["altitude_km"],
                "eccentricity": row["eccentricity"],
                "inclination_deg": row["inclination_deg"],
                "raan_deg": row["raan_deg"],
                "arg_periapsis_deg": row["arg_periapsis_deg"],
                "mean_anomaly_deg": row["mean_anomaly_deg"],
            },
            "provenance": {
                "store": str(self.path),
                "table": "standard_orbits",
                "derivation_note": row["derivation_note"],
            },
        }

    def _model(self, row: sqlite3.Row) -> ParentCentricOrbitModel:
        if row["reference_frame"] != CANONICAL_FRAME:
            raise SQLiteStandardOrbitResolverError(
                f"unsupported standard-orbit frame: {row['reference_frame']}"
            )
        props = dict(self._body_property_resolver(str(row["parent_body_id"])))
        try:
            radius = float(props["radius_km"])
            mu = float(props["mu_km3_s2"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SQLiteStandardOrbitResolverError("body radius/GM authority is incomplete") from exc
        if not math.isfinite(radius) or radius <= 0.0 or not math.isfinite(mu) or mu <= 0.0:
            raise SQLiteStandardOrbitResolverError("body radius/GM authority is invalid")
        representation = str(row["representation"])
        if representation != "CIRCULAR_ALTITUDE":
            raise SQLiteStandardOrbitResolverError(
                f"unsupported standard-orbit representation: {representation}"
            )
        if row["altitude_km"] is None:
            raise SQLiteStandardOrbitResolverError("circular-altitude target lacks altitude")
        semi_major = radius + float(row["altitude_km"])
        return ParentCentricOrbitModel(
            entity_id=row["object_id"],
            parent_entity_id=row["parent_body_id"],
            element_epoch_utc=row["element_epoch_utc"],
            semi_major_axis_km=semi_major,
            eccentricity=float(row["eccentricity"]),
            inclination_deg=float(row["inclination_deg"]),
            raan_deg=float(row["raan_deg"]),
            arg_periapsis_deg=float(row["arg_periapsis_deg"]),
            mean_anomaly_deg=float(row["mean_anomaly_deg"]),
            parent_mu_km3_s2=mu,
            model_id=f"SPATIAL_GEOMETRY_STANDARD_ORBIT:{row['object_id']}",
            provenance={
                "definition_store": str(self.path),
                "definition_table": "standard_orbits",
                "body_property_source": props.get("source", "SHARED_BODY_PROPERTY_RESOLVER"),
                "epistemic_status": row["epistemic_status"],
            },
            uncertainty={
                "model_class": "STANDARD_ORBIT_ENGINEERING_REFERENCE",
                "navigation_qualification": "REFERENCE_NOT_NAVIGATION_GRADE",
                "unmodeled_perturbations": True,
            },
        )

    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState:
        row = self._row(target_id)
        model = self._model(row)
        parent = self._body_state_resolver(str(row["parent_body_id"]), epoch_utc)
        if parent.entity_id != row["parent_body_id"] or parent.epoch_utc != epoch_utc:
            raise SQLiteStandardOrbitResolverError("parent state resolver returned mismatched state")
        if parent.reference_frame != CANONICAL_FRAME:
            raise SQLiteStandardOrbitResolverError("parent state resolver returned non-canonical frame")
        rel_p, rel_v = propagate_parent_centric(model, epoch_utc)
        return SpatialState(
            entity_id=row["object_id"],
            epoch_utc=epoch_utc,
            reference_frame=CANONICAL_FRAME,
            position_km=tuple(parent.position_km[i] + rel_p[i] for i in range(3)),
            velocity_km_s=tuple(parent.velocity_km_s[i] + rel_v[i] for i in range(3)),
            provenance={
                "state_source": "SPATIAL_GEOMETRY_STANDARD_ORBIT_SHARED_KEPLER",
                "definition_store": str(self.path),
                "definition_table": "standard_orbits",
                "element_epoch_utc": row["element_epoch_utc"],
                "parent_entity_id": row["parent_body_id"],
                "parent_state_source": parent.provenance.get("state_source"),
            },
            navigation_grade=False,
            uncertainty={
                "epistemic_status": row["epistemic_status"],
                "navigation_qualification": "REFERENCE_NOT_NAVIGATION_GRADE",
                "unmodeled_perturbations": True,
            },
            payload={
                "state_class": "STANDARD_ORBIT",
                "operational_role": row["operational_role"],
                "representation": row["representation"],
                "definition_status": row["status"],
            },
        )
