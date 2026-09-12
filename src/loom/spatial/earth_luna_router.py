"""Unified Earth-Luna target router for HUD/GIS and Navigator consumers.

This module owns no physics. It dispatches canonical facility IDs and standard
orbit IDs from the generated spatial registry to already-qualified resolvers.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any, Protocol

from loom.application.contracts import SpatialState


class TargetResolverProtocol(Protocol):
    def describe_target(self, target_id: str) -> dict[str, Any]: ...
    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState: ...


class EarthLunaTargetRouterError(RuntimeError):
    """Raised when a registry target cannot be routed without inventing authority."""


class EarthLunaTargetRouter:
    """Route Earth-Luna registry targets to shared facility/orbit resolvers."""

    def __init__(
        self,
        geometry_db_path: Path | str,
        facility_resolver: TargetResolverProtocol,
        standard_orbit_resolver: TargetResolverProtocol,
    ) -> None:
        self.path = Path(geometry_db_path).expanduser().resolve()
        self._facility_resolver = facility_resolver
        self._standard_orbit_resolver = standard_orbit_resolver

    def _connect(self) -> sqlite3.Connection:
        if not self.path.is_file():
            raise EarthLunaTargetRouterError(f"SPATIAL_GEOMETRY database not found: {self.path}")
        conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn

    def _registry_row(self, target_id: str) -> sqlite3.Row:
        key = str(target_id).strip()
        if not key:
            raise EarthLunaTargetRouterError("target_id is required")
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM spatial_objects WHERE object_id=?",
                (key,),
            ).fetchone()
        if row is None:
            raise EarthLunaTargetRouterError(f"unknown Earth-Luna spatial target: {key}")
        return row

    def _resolver_for(self, row: sqlite3.Row) -> TargetResolverProtocol:
        kind = str(row["object_kind"])
        if kind == "FACILITY":
            return self._facility_resolver
        if kind == "STANDARD_ORBIT":
            return self._standard_orbit_resolver
        raise EarthLunaTargetRouterError(f"unsupported registry object_kind: {kind}")

    def describe_target(self, target_id: str) -> dict[str, Any]:
        row = self._registry_row(target_id)
        resolver = self._resolver_for(row)
        described = resolver.describe_target(str(row["object_id"]))
        if str(described.get("target_id") or "") != str(row["object_id"]):
            raise EarthLunaTargetRouterError("resolver described a different target_id")
        return described

    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState:
        row = self._registry_row(target_id)
        state = self._resolver_for(row).resolve_target_state(str(row["object_id"]), epoch_utc)
        if state.entity_id != str(row["object_id"]):
            raise EarthLunaTargetRouterError("resolver returned a different entity_id")
        if state.epoch_utc != epoch_utc:
            raise EarthLunaTargetRouterError("resolver returned a different epoch")
        return state

    def list_targets(self) -> tuple[dict[str, Any], ...]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT object_id,object_kind,display_name,parent_body_id,operational_role,status
                FROM spatial_objects
                ORDER BY object_kind,object_id
                """
            ).fetchall()
        return tuple(
            {
                "contract": "LOOM_EARTH_LUNA_TARGET_INDEX_V1",
                "target_id": row["object_id"],
                "target_type": row["object_kind"],
                "display_name": row["display_name"],
                "parent_body_id": row["parent_body_id"],
                "operational_role": row["operational_role"],
                "status": row["status"],
                "state_authority": "SHARED_SPATIAL_NAVIGATION_SERVICES",
            }
            for row in rows
        )
