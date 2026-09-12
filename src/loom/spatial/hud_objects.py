"""Thin HUD-facing object adapter over WORLD, shared spatial state and geometry metadata.

This module deliberately does not model detailed station topology. It exposes the
minimum governed object surface needed for HUD/GIS selection and inspection:
identity, classification, authority summary, engineering/transport summary,
approved HERO media, visualization-only geometry references, and (when
requested) the exact shared SpatialState returned by the injected resolver.

WORLD remains world-fact authority. Shared spatial/navigation services remain
physical-state authority. The generated spatial-geometry database remains a
non-state definition/render-support layer.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any, Protocol

from loom.application.contracts import SpatialState
from .procedural_proxies import decode_proxy_row


class HUDSpatialObjectError(RuntimeError):
    """Raised when a HUD object cannot be described without inventing data."""


class SpatialStateResolverProtocol(Protocol):
    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState: ...


class HUDInfrastructureObjectAdapter:
    """Join governed WORLD presentation facts to the shared spatial-state seam."""

    def __init__(
        self,
        world_db_path: Path | str,
        state_resolver: SpatialStateResolverProtocol,
        *,
        geometry_db_path: Path | str | None = None,
    ) -> None:
        self.world_path = Path(world_db_path).expanduser().resolve()
        self.geometry_path = (
            Path(geometry_db_path).expanduser().resolve()
            if geometry_db_path is not None
            else None
        )
        self._state_resolver = state_resolver

    @staticmethod
    def _connect_readonly(path: Path, label: str) -> sqlite3.Connection:
        if not path.is_file():
            raise HUDSpatialObjectError(f"{label} database not found: {path}")
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def _world_row(self, target_id: str) -> sqlite3.Row:
        key = str(target_id).strip()
        if not key:
            raise HUDSpatialObjectError("target_id is required")
        with self._connect_readonly(self.world_path, "WORLD") as conn:
            row = conn.execute(
                """
                SELECT e.entity_id,e.name,e.parent_entity_id,
                       n.facility_type,n.system,n.traffic,n.region_entity_id,
                       n.commercial_1,n.commercial_2,n.commercial_regime,
                       n.civil_authority,n.administrative_authority,n.security_authority,
                       n.institutional_morphology,n.synthetic_constituency_1,
                       l.model_id AS location_model_id,l.frame_family,l.geometry_kind,
                       l.precision_class,l.position_authority,
                       o.orbit_family,o.navigation_grade AS orbit_navigation_grade,
                       o.epistemic_status AS orbit_epistemic_status
                FROM entities e
                JOIN infrastructure_nodes n ON n.entity_id=e.entity_id
                LEFT JOIN entity_location_models l ON l.entity_id=e.entity_id
                LEFT JOIN orbit_geometry_models o ON o.entity_id=e.entity_id
                WHERE e.entity_id=?
                """,
                (key,),
            ).fetchone()
        if row is None:
            raise HUDSpatialObjectError(f"unknown WORLD infrastructure object: {key}")
        return row

    def _engineering(self, target_id: str) -> dict[str, Any]:
        with self._connect_readonly(self.world_path, "WORLD") as conn:
            row = conn.execute(
                "SELECT * FROM infrastructure_engineering_profiles WHERE entity_id=?",
                (target_id,),
            ).fetchone()
        return dict(row) if row else {}

    def _transport(self, target_id: str) -> dict[str, Any]:
        with self._connect_readonly(self.world_path, "WORLD") as conn:
            row = conn.execute(
                "SELECT * FROM entity_transport_profiles WHERE entity_id=?",
                (target_id,),
            ).fetchone()
        return dict(row) if row else {}

    def _hero_media(self, target_id: str) -> dict[str, Any] | None:
        with self._connect_readonly(self.world_path, "WORLD") as conn:
            row = conn.execute(
                """
                SELECT ke.noun_id,ke.canonical_name,ke.display_name_short,
                       ke.quick_description,ke.boundary_note,ke.canon_status,
                       ia.asset_id,ia.asset_role,ia.review_status,ia.media_key,
                       ia.mime_type,ia.width_px,ia.height_px,ia.content_hash,
                       ia.thumbnail_hash,ia.is_current
                FROM knowledge_entities ke
                JOIN image_assets ia ON ia.entity_id=ke.noun_id
                WHERE ke.spatial_entity_id=?
                  AND ia.asset_role='HERO'
                  AND ia.is_current=1
                  AND ia.review_status='APPROVED_REFERENCE'
                ORDER BY ia.media_key
                LIMIT 1
                """,
                (target_id,),
            ).fetchone()
        return dict(row) if row else None

    def _geometry(self, target_id: str) -> dict[str, Any]:
        result: dict[str, Any] = {
            "object_id": target_id,
            "database_role": "DEFINITION_AND_OPERATIONAL_GEOMETRY",
            "available_roles": [],
            "default_symbol": None,
            "orbit_render_style": None,
            "visual_proxy": None,
            "status": "UNAVAILABLE",
        }
        if self.geometry_path is None or not self.geometry_path.is_file():
            return result
        with self._connect_readonly(self.geometry_path, "SPATIAL_GEOMETRY") as conn:
            obj = conn.execute(
                "SELECT object_id,object_kind,status FROM spatial_objects WHERE object_id=?",
                (target_id,),
            ).fetchone()
            if obj is None:
                return result
            assets = conn.execute(
                """
                SELECT asset_id,geometry_role,mime_type,asset_uri,asset_sha256,
                       lod_level,scale_m_per_unit,navigation_authority,status
                FROM geometry_assets
                WHERE object_id=?
                ORDER BY geometry_role,asset_id
                """,
                (target_id,),
            ).fetchall()
            visual = conn.execute(
                "SELECT * FROM visual_profiles WHERE object_id=?",
                (target_id,),
            ).fetchone()
            proxy = conn.execute(
                "SELECT * FROM procedural_visual_proxies WHERE object_id=?",
                (target_id,),
            ).fetchone()
        result.update(
            {
                "object_kind": obj["object_kind"],
                "status": obj["status"],
                "available_roles": sorted({r["geometry_role"] for r in assets}),
                "assets": [dict(r) for r in assets],
                "visual_proxy": decode_proxy_row(proxy) if proxy is not None else None,
            }
        )
        if visual is not None:
            result.update(
                {
                    "default_symbol": visual["default_symbol"],
                    "orbit_render_style": visual["orbit_render_style"],
                    "label_priority": visual["label_priority"],
                    "visual_status": visual["status"],
                }
            )
        return result

    @staticmethod
    def _state_dict(state: SpatialState) -> dict[str, Any]:
        return {
            "entity_id": state.entity_id,
            "epoch_utc": state.epoch_utc,
            "reference_frame": state.reference_frame,
            "position_km": list(state.position_km),
            "velocity_km_s": list(state.velocity_km_s),
            "orientation": dict(state.orientation),
            "provenance": dict(state.provenance),
            "navigation_grade": state.navigation_grade,
            "uncertainty": dict(state.uncertainty),
            "payload": dict(state.payload),
        }

    def describe_object(self, target_id: str) -> dict[str, Any]:
        row = self._world_row(target_id)
        engineering = self._engineering(row["entity_id"])
        transport = self._transport(row["entity_id"])
        media = self._hero_media(row["entity_id"])
        orbit_family = str(row["orbit_family"] or "")
        state_availability = (
            "RESOLVABLE_SHARED_CONVENTIONAL"
            if orbit_family.startswith("KEPLERIAN_")
            else "REQUIRES_SHARED_RESOLVER"
        )
        return {
            "contract": "LOOM_HUD_SPATIAL_OBJECT_V1",
            "detail_scope": "THIN_WORLD_BACKED_V1",
            "detail_policy": "STATION_COMPLEXITY_DEFERRED",
            "entity_id": row["entity_id"],
            "display_name": row["name"],
            "parent_body_id": row["parent_entity_id"],
            "facility_type": row["facility_type"],
            "system": row["system"],
            "region_entity_id": row["region_entity_id"],
            "traffic": row["traffic"],
            "authorities": {
                "civil": row["civil_authority"],
                "administrative": row["administrative_authority"],
                "security": row["security_authority"],
            },
            "commercial": {
                "primary": row["commercial_1"],
                "secondary": row["commercial_2"],
                "regime": row["commercial_regime"],
            },
            "institutional": {
                "morphology": row["institutional_morphology"],
                "synthetic_constituency": row["synthetic_constituency_1"],
            },
            "placement": {
                "location_model_id": row["location_model_id"],
                "frame_family": row["frame_family"],
                "geometry_kind": row["geometry_kind"],
                "precision_class": row["precision_class"],
                "position_authority": row["position_authority"],
                "orbit_family": row["orbit_family"],
                "orbit_navigation_grade": (
                    bool(row["orbit_navigation_grade"])
                    if row["orbit_navigation_grade"] is not None
                    else None
                ),
                "orbit_epistemic_status": row["orbit_epistemic_status"],
            },
            "engineering": engineering,
            "transport": transport,
            "media": media,
            "geometry": self._geometry(row["entity_id"]),
            "state": {
                "authority": "SHARED_SPATIAL_NAVIGATION_SERVICES",
                "availability": state_availability,
                "embedded_in_object_record": False,
            },
        }

    def resolve_object(self, target_id: str, epoch_utc: str) -> dict[str, Any]:
        obj = self.describe_object(target_id)
        state = self._state_resolver.resolve_target_state(target_id, epoch_utc)
        if state.entity_id != obj["entity_id"]:
            raise HUDSpatialObjectError("shared state resolver returned wrong entity_id")
        if state.epoch_utc != epoch_utc:
            raise HUDSpatialObjectError("shared state resolver returned wrong epoch")
        obj["spatial_state"] = self._state_dict(state)
        obj["state"] = {
            "authority": "SHARED_SPATIAL_NAVIGATION_SERVICES",
            "availability": "RESOLVED",
            "embedded_in_object_record": False,
        }
        return obj
