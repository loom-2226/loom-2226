"""HUD/GIS-ready Earth-Luna scene projection over governed spatial services.

This adapter is presentation assembly only. It does not calculate orbital state,
body-fixed transforms, CR3BP state, or station geometry. It joins the existing
HUD facility object adapter and unified target router into one read-only scene
payload suitable for HUD/GIS consumption.
"""
from __future__ import annotations

from typing import Any, Protocol

from loom.application.contracts import SpatialState


class TargetRouterProtocol(Protocol):
    def list_targets(self) -> tuple[dict[str, Any], ...]: ...
    def describe_target(self, target_id: str) -> dict[str, Any]: ...
    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState: ...


class HUDObjectAdapterProtocol(Protocol):
    def describe_object(self, target_id: str) -> dict[str, Any]: ...
    def resolve_object(self, target_id: str, epoch_utc: str) -> dict[str, Any]: ...


class EarthLunaHUDSceneAdapter:
    """Assemble a single-epoch Earth-Luna target scene without alternate physics."""

    def __init__(self, target_router: TargetRouterProtocol, facility_hud_adapter: HUDObjectAdapterProtocol) -> None:
        self._router = target_router
        self._hud = facility_hud_adapter

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

    def _facility(self, target_id: str, epoch_utc: str) -> dict[str, Any]:
        obj = self._hud.describe_object(target_id)
        if obj.get("state", {}).get("availability") == "RESOLVABLE_SHARED_CONVENTIONAL":
            return self._hud.resolve_object(target_id, epoch_utc)
        return obj

    def _standard_orbit(self, target_id: str, epoch_utc: str) -> dict[str, Any]:
        desc = self._router.describe_target(target_id)
        state = self._router.resolve_target_state(target_id, epoch_utc)
        return {
            **desc,
            "presentation": {
                "geometry_role": "ORBIT_RING",
                "render_authority": "HUD_GIS_PRESENTATION",
                "state_source": "SHARED_SPATIAL_NAVIGATION_SERVICES",
            },
            "state": {
                "authority": "SHARED_SPATIAL_NAVIGATION_SERVICES",
                "availability": "RESOLVED",
            },
            "spatial_state": self._state_dict(state),
        }

    def build_scene(self, epoch_utc: str) -> dict[str, Any]:
        index = self._router.list_targets()
        facilities: list[dict[str, Any]] = []
        standard_orbits: list[dict[str, Any]] = []
        for row in index:
            if row["target_type"] == "FACILITY":
                facilities.append(self._facility(row["target_id"], epoch_utc))
            elif row["target_type"] == "STANDARD_ORBIT":
                standard_orbits.append(self._standard_orbit(row["target_id"], epoch_utc))
        return {
            "contract": "LOOM_EARTH_LUNA_SCENE_V1",
            "epoch_utc": epoch_utc,
            "target_count": len(index),
            "state_authority": "SHARED_SPATIAL_NAVIGATION_SERVICES",
            "geometry_authority": "VISUALIZATION_ONLY_FOR_PROXIES",
            "station_detail_policy": "STATION_COMPLEXITY_DEFERRED",
            "facilities": facilities,
            "standard_orbits": standard_orbits,
        }
