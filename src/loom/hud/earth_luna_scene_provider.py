"""Live HUD provider for the governed Earth-Luna spatial scene.

This module is deliberately thin. It resolves runtime paths, materializes the
reviewable SPATIAL_GEOMETRY cache when needed, and wires the existing shared
celestial-state service into the Earth-Luna runtime bundle. It owns no orbital
math, no facility truth, and no propagated-state authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable
import os

from loom.application.contracts import SpatialState
from loom.runtime import resolve_runtime_roots
from loom.spatial.earth_luna_runtime import build_earth_luna_runtime
from loom.spatial.geometry_catalog import build_earth_luna_geometry_db
from loom.spatial.sqlite_celestial_catalog import SQLiteCelestialCatalog

CONTRACT = "LOOM_EARTH_LUNA_SCENE_V1"
DEFAULT_EPOCH = "2226-08-29T05:00:00Z"
WORLD_FILENAME = "LOOM_2226.sqlite3"
GEOMETRY_FILENAME = "LOOM_2226_SPATIAL_GEOMETRY.sqlite3"
SEED_RELATIVE = Path("geometry/earth_luna_spatial_geometry_seed.sql")
BODY_IDS = ("EA", "LU")

BodyStateResolver = Callable[[str, str], SpatialState]


def build_earth_luna_hud_scene(
    *,
    epoch_utc: str = DEFAULT_EPOCH,
    app_root: Path | str | None = None,
    data_root: Path | str | None = None,
    body_state_resolver: BodyStateResolver | None = None,
    rebuild_geometry: bool = False,
) -> dict:
    """Build the live HUD Earth-Luna scene from governed runtime authority.

    Production callers normally leave ``body_state_resolver`` unset. In that
    path the resolver comes from ``SQLiteCelestialCatalog.build_service`` over
    the authoritative WORLD database. Injection exists only to make the seam
    independently testable; the Earth-Luna runtime itself still consumes the
    exact same ``SpatialState`` contract.

    The generated geometry SQLite is a disposable definition/presentation
    cache. It is rebuilt from WORLD + committed seed only when absent or when
    explicitly requested; propagated state is never stored there.
    """
    roots = resolve_runtime_roots(app_root=app_root, data_root=data_root)
    world_path = Path(os.environ.get("LOOM_SPATIAL_DB") or (roots.data_root / WORLD_FILENAME))
    geometry_path = Path(
        os.environ.get("LOOM_SPATIAL_GEOMETRY_DB")
        or (roots.data_root / GEOMETRY_FILENAME)
    )
    seed_path = roots.app_root / SEED_RELATIVE

    if not world_path.is_file():
        raise FileNotFoundError(f"Earth-Luna WORLD database missing: {world_path}")
    if not seed_path.is_file():
        raise FileNotFoundError(f"Earth-Luna geometry seed missing: {seed_path}")

    if rebuild_geometry or not geometry_path.is_file():
        build_earth_luna_geometry_db(world_path, seed_path, geometry_path)

    resolver = body_state_resolver
    if resolver is None:
        catalog = SQLiteCelestialCatalog(world_path)
        celestial = catalog.build_service(BODY_IDS, epoch_utc)
        resolver = celestial.resolve

    runtime = build_earth_luna_runtime(world_path, geometry_path, resolver)
    scene = runtime.scene.build_scene(epoch_utc)
    if scene.get("contract") != CONTRACT:
        raise RuntimeError(f"unexpected Earth-Luna scene contract: {scene.get('contract')!r}")
    return scene
