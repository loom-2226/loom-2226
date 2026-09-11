"""One-call wiring for the Earth-Luna HUD/Navigator spatial slice."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from loom.application.contracts import SpatialState
from .earth_luna_router import EarthLunaTargetRouter
from .earth_luna_scene import EarthLunaHUDSceneAdapter
from .hud_objects import HUDInfrastructureObjectAdapter
from .sqlite_body_properties import SQLiteBodyPropertyCatalog
from .sqlite_infrastructure_catalog import SQLiteInfrastructureCatalog
from .sqlite_standard_orbit_resolver import SQLiteStandardOrbitResolver


BodyStateResolver = Callable[[str, str], SpatialState]


@dataclass(frozen=True)
class EarthLunaRuntimeBundle:
    body_properties: SQLiteBodyPropertyCatalog
    facilities: SQLiteInfrastructureCatalog
    standard_orbits: SQLiteStandardOrbitResolver
    router: EarthLunaTargetRouter
    hud_objects: HUDInfrastructureObjectAdapter
    scene: EarthLunaHUDSceneAdapter


def build_earth_luna_runtime(
    world_db_path: Path | str,
    geometry_db_path: Path | str,
    body_state_resolver: BodyStateResolver,
) -> EarthLunaRuntimeBundle:
    """Wire the shared Earth-Luna spatial consumers around one body-state service.

    The caller supplies the existing shared body-state resolver. WORLD supplies
    body radius/GM and facility definitions. SPATIAL_GEOMETRY supplies standard
    orbit definitions and visualization-only proxies. No new state authority is
    created here.
    """
    body_properties = SQLiteBodyPropertyCatalog(world_db_path)
    facilities = SQLiteInfrastructureCatalog(world_db_path, body_state_resolver)
    standard_orbits = SQLiteStandardOrbitResolver(
        geometry_db_path,
        body_state_resolver,
        body_properties.get,
    )
    router = EarthLunaTargetRouter(geometry_db_path, facilities, standard_orbits)
    hud_objects = HUDInfrastructureObjectAdapter(
        world_db_path,
        facilities,
        geometry_db_path=geometry_db_path,
    )
    scene = EarthLunaHUDSceneAdapter(router, hud_objects)
    return EarthLunaRuntimeBundle(
        body_properties=body_properties,
        facilities=facilities,
        standard_orbits=standard_orbits,
        router=router,
        hud_objects=hud_objects,
        scene=scene,
    )
