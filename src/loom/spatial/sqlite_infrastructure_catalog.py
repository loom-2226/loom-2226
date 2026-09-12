"""Read-only WORLD adapter for named infrastructure spatial state.

WORLD owns facility identity and declared placement/orbit models. This adapter
promotes only supported conventional Keplerian infrastructure models into the
shared :class:`SpatialState` contract. It does not copy those models into a
second authority store, invent body orientation, or reinterpret CR3BP/surface
models as ordinary two-body orbits.

The quantitative WORLD orbit rows used here explicitly declare
``output_track_frame=ECLIPJ2000_PARENT_CENTERED``. Those parent-centric states
are composed with an injected shared parent-body state resolver in
``J2000/ECLIPTIC``.
"""
from __future__ import annotations

from pathlib import Path
import json
import math
import sqlite3
from typing import Any, Callable, Mapping

from loom.application.contracts import SpatialState
from .celestial_state import CANONICAL_FRAME, ParentCentricOrbitModel, propagate_parent_centric


class SQLiteInfrastructureCatalogError(RuntimeError):
    """Raised when WORLD infrastructure state cannot be resolved safely."""


BodyStateResolver = Callable[[str, str], SpatialState]


class SQLiteInfrastructureCatalog:
    """Resolve WORLD-backed conventional orbital facilities read-only."""

    def __init__(self, db_path: Path | str, body_state_resolver: BodyStateResolver):
        self.path = Path(db_path).expanduser().resolve()
        self._body_state_resolver = body_state_resolver

    def _connect(self) -> sqlite3.Connection:
        if not self.path.is_file():
            raise SQLiteInfrastructureCatalogError(f"WORLD database not found: {self.path}")
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    @staticmethod
    def _json_object(value: Any, label: str) -> dict[str, Any]:
        if value in (None, ""):
            return {}
        try:
            parsed = json.loads(str(value))
        except json.JSONDecodeError as exc:
            raise SQLiteInfrastructureCatalogError(f"invalid {label} JSON") from exc
        if not isinstance(parsed, dict):
            raise SQLiteInfrastructureCatalogError(f"{label} must be a JSON object")
        return parsed

    def _facility_row(self, target_id: str) -> sqlite3.Row:
        key = str(target_id).strip()
        if not key:
            raise SQLiteInfrastructureCatalogError("target_id is required")
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT e.entity_id,e.name,e.parent_entity_id,
                       n.facility_type,n.system,n.traffic,
                       n.civil_authority,n.administrative_authority,n.security_authority,
                       l.model_id AS location_model_id,l.center_entity_id,l.frame_family,
                       l.geometry_kind,l.precision_class,l.position_authority,
                       l.navigation_grade AS location_navigation_grade,
                       o.orbit_family,o.parent_entity_id AS orbit_parent_entity_id,
                       o.reference_frame,o.reference_plane,o.epoch_utc,
                       o.semi_major_axis_km,o.eccentricity,o.inclination_deg,
                       o.raan_deg,o.arg_periapsis_deg,o.mean_anomaly_deg,o.period_s,
                       o.parameter_json AS orbit_parameter_json,
                       o.assumption_json AS orbit_assumption_json,
                       o.navigation_grade AS orbit_navigation_grade,
                       o.epistemic_status,o.source_id,o.derivation_model_id,o.notes AS orbit_notes
                FROM entities e
                JOIN infrastructure_nodes n ON n.entity_id=e.entity_id
                LEFT JOIN entity_location_models l ON l.entity_id=e.entity_id
                LEFT JOIN orbit_geometry_models o ON o.entity_id=e.entity_id
                WHERE e.entity_id=?
                """,
                (key,),
            ).fetchone()
        if row is None:
            raise SQLiteInfrastructureCatalogError(f"unknown WORLD infrastructure target: {key}")
        return row

    def _parent_mu(self, parent_entity_id: str) -> tuple[float, str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT gm_km3_s2,source_id,status FROM celestial_properties WHERE entity_id=?",
                (parent_entity_id,),
            ).fetchone()
            if row is not None and row["gm_km3_s2"] is not None:
                mu = float(row["gm_km3_s2"])
                source = f"celestial_properties:{row['source_id'] or ''}:{row['status'] or ''}"
            else:
                row = conn.execute(
                    "SELECT gm_km3_s2,source,metadata_status FROM celestial_dynamics WHERE entity_id=?",
                    (parent_entity_id,),
                ).fetchone()
                if row is None or row["gm_km3_s2"] is None:
                    raise SQLiteInfrastructureCatalogError(f"no parent GM for {parent_entity_id}")
                mu = float(row["gm_km3_s2"])
                source = f"celestial_dynamics:{row['source'] or ''}:{row['metadata_status'] or ''}"
        if not math.isfinite(mu) or mu <= 0.0:
            raise SQLiteInfrastructureCatalogError(f"invalid parent GM for {parent_entity_id}")
        return mu, source

    def describe_target(self, target_id: str) -> dict[str, Any]:
        row = self._facility_row(target_id)
        return {
            "contract": "LOOM_SPATIAL_TARGET_V1",
            "target_id": row["entity_id"],
            "target_type": "INFRASTRUCTURE",
            "display_name": row["name"],
            "parent_body": row["parent_entity_id"],
            "facility_type": row["facility_type"],
            "location_model_id": row["location_model_id"],
            "frame_family": row["frame_family"],
            "precision_class": row["precision_class"],
            "position_authority": row["position_authority"],
            "orbit_family": row["orbit_family"],
            "reference_frame": row["reference_frame"],
            "reference_plane": row["reference_plane"],
            "navigation_grade": bool(row["orbit_navigation_grade"]) if row["orbit_navigation_grade"] is not None else None,
            "epistemic_status": row["epistemic_status"],
            "source_id": row["source_id"],
            "derivation_model_id": row["derivation_model_id"],
            "operational_metadata": {
                "system": row["system"],
                "traffic": row["traffic"],
                "civil_authority": row["civil_authority"],
                "administrative_authority": row["administrative_authority"],
                "security_authority": row["security_authority"],
            },
        }

    def _kepler_model(self, row: sqlite3.Row) -> tuple[ParentCentricOrbitModel, dict[str, Any], str]:
        family = str(row["orbit_family"] or "")
        if not family.startswith("KEPLERIAN_"):
            raise SQLiteInfrastructureCatalogError(
                f"{row['entity_id']} orbit family is not supported by conventional Kepler resolver: {family or 'MISSING'}"
            )
        parent = str(row["orbit_parent_entity_id"] or row["parent_entity_id"] or "").strip()
        if not parent:
            raise SQLiteInfrastructureCatalogError(f"{row['entity_id']} has no orbit parent")
        params = self._json_object(row["orbit_parameter_json"], "orbit parameter")
        if params.get("output_track_frame") != "ECLIPJ2000_PARENT_CENTERED":
            raise SQLiteInfrastructureCatalogError(
                f"{row['entity_id']} lacks qualified ECLIPJ2000 parent-centered output declaration"
            )
        required = (
            "epoch_utc", "semi_major_axis_km", "eccentricity", "inclination_deg",
            "raan_deg", "arg_periapsis_deg", "mean_anomaly_deg",
        )
        missing = [name for name in required if row[name] is None]
        if missing:
            raise SQLiteInfrastructureCatalogError(
                f"{row['entity_id']} incomplete Kepler geometry: {', '.join(missing)}"
            )
        mu, mu_source = self._parent_mu(parent)
        model = ParentCentricOrbitModel(
            entity_id=row["entity_id"],
            parent_entity_id=parent,
            element_epoch_utc=row["epoch_utc"],
            semi_major_axis_km=float(row["semi_major_axis_km"]),
            eccentricity=float(row["eccentricity"]),
            inclination_deg=float(row["inclination_deg"]),
            raan_deg=float(row["raan_deg"]),
            arg_periapsis_deg=float(row["arg_periapsis_deg"]),
            mean_anomaly_deg=float(row["mean_anomaly_deg"]),
            parent_mu_km3_s2=mu,
            model_id=f"WORLD_ORBIT_GEOMETRY:{row['entity_id']}:{row['derivation_model_id'] or family}",
            provenance={
                "store": str(self.path),
                "table": "orbit_geometry_models",
                "source_id": row["source_id"],
                "derivation_model_id": row["derivation_model_id"],
                "epistemic_status": row["epistemic_status"],
                "orbit_family": family,
                "declared_reference_frame": row["reference_frame"],
                "declared_reference_plane": row["reference_plane"],
                "output_track_frame": params.get("output_track_frame"),
                "orientation_model_id": params.get("orientation_model_id"),
                "parent_mu_source": mu_source,
            },
            uncertainty={
                "model_class": "WORLD_ENGINEERING_REFERENCE_KEPLER",
                "navigation_qualification": "REFERENCE_NOT_NAVIGATION_GRADE",
                "unmodeled_perturbations": True,
                "position_authority": row["position_authority"],
                "precision_class": row["precision_class"],
            },
        )
        return model, params, mu_source

    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState:
        row = self._facility_row(target_id)
        model, params, mu_source = self._kepler_model(row)
        parent = self._body_state_resolver(model.parent_entity_id, epoch_utc)
        if parent.entity_id != model.parent_entity_id:
            raise SQLiteInfrastructureCatalogError("parent resolver returned wrong entity_id")
        if parent.epoch_utc != epoch_utc:
            raise SQLiteInfrastructureCatalogError("parent resolver returned wrong epoch")
        if parent.reference_frame != CANONICAL_FRAME:
            raise SQLiteInfrastructureCatalogError("parent resolver returned non-canonical frame")
        rel_p, rel_v = propagate_parent_centric(model, epoch_utc)
        position = tuple(parent.position_km[i] + rel_p[i] for i in range(3))
        velocity = tuple(parent.velocity_km_s[i] + rel_v[i] for i in range(3))
        assumptions = self._json_object(row["orbit_assumption_json"], "orbit assumption")
        return SpatialState(
            entity_id=row["entity_id"],
            epoch_utc=epoch_utc,
            reference_frame=CANONICAL_FRAME,
            position_km=position,
            velocity_km_s=velocity,
            provenance={
                "state_source": "WORLD_ORBIT_GEOMETRY_PARENT_CENTRIC_KEPLER",
                "world_store": str(self.path),
                "location_model_id": row["location_model_id"],
                "orbit_family": row["orbit_family"],
                "orbit_source_id": row["source_id"],
                "derivation_model_id": row["derivation_model_id"],
                "element_epoch_utc": row["epoch_utc"],
                "parent_entity_id": model.parent_entity_id,
                "parent_state_source": parent.provenance.get("state_source"),
                "parent_mu_source": mu_source,
                "output_track_frame": params.get("output_track_frame"),
                "orientation_model_id": params.get("orientation_model_id"),
            },
            navigation_grade=False,
            uncertainty={
                "epistemic_status": row["epistemic_status"],
                "position_authority": row["position_authority"],
                "precision_class": row["precision_class"],
                "navigation_qualification": "REFERENCE_NOT_NAVIGATION_GRADE",
                "do_not_promote_to_canon": bool(assumptions.get("do_not_promote_to_canon", False)),
                "unmodeled_perturbations": True,
            },
            payload={
                "state_class": "INFRASTRUCTURE",
                "facility_type": row["facility_type"],
                "system": row["system"],
                "traffic": row["traffic"],
                "orbit_family": row["orbit_family"],
                "location_frame_family": row["frame_family"],
                "location_geometry_kind": row["geometry_kind"],
                "world_reference_frame": row["reference_frame"],
                "world_reference_plane": row["reference_plane"],
                "propagation_model": "TWO_BODY_WORLD_ENGINEERING_REFERENCE",
            },
        )
