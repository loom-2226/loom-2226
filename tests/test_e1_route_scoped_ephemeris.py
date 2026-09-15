from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "engineering" / "experience_one" / "qualification" / "e1_route_scoped_ephemeris.py"
spec = importlib.util.spec_from_file_location("e1_route_scoped_ephemeris_tested", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fake_core():
    route_objects = {
        "CERES": {"kind": "base", "base_id": "CE"},
        "NEPTUNE_SYSTEM": {"kind": "base", "base_id": "NE"},
        "EARTH": {"kind": "base", "base_id": "EA"},
        "LUNA": {"kind": "local_direct_parent", "base_id": "EA", "local_id": "LU"},
    }
    full_plan = [
        {"scope": "BASE", "id": "CE", "name": "Ceres"},
        {"scope": "BASE", "id": "EA", "name": "Earth"},
        {"scope": "BASE", "id": "JU", "name": "Jupiter"},
        {"scope": "BASE", "id": "NE", "name": "Neptune"},
        {"scope": "LOCAL", "system_id": "EA", "id": "LU", "name": "Luna"},
        {"scope": "LOCAL", "system_id": "JU", "id": "IO", "name": "Io"},
    ]
    return SimpleNamespace(
        ROUTE_OBJECTS=route_objects,
        build_acquisition_plan=lambda normalized: list(full_plan),
    )


def test_ceres_neptune_excludes_irrelevant_io_and_other_bases():
    core = fake_core()
    mod.install_route_scoped_acquisition(core)
    plan = core.build_acquisition_plan({"route": ["CERES", "NEPTUNE_SYSTEM"]})
    assert [(x["scope"], x.get("system_id"), x["id"]) for x in plan] == [
        ("BASE", None, "CE"),
        ("BASE", None, "NE"),
    ]


def test_local_route_keeps_parent_and_required_local_object():
    core = fake_core()
    mod.install_route_scoped_acquisition(core)
    plan = core.build_acquisition_plan({"route": ["EARTH", "LUNA"]})
    assert [(x["scope"], x.get("system_id"), x["id"]) for x in plan] == [
        ("BASE", None, "EA"),
        ("LOCAL", "EA", "LU"),
    ]


def test_install_is_idempotent():
    core = fake_core()
    mod.install_route_scoped_acquisition(core)
    first = core.build_acquisition_plan
    mod.install_route_scoped_acquisition(core)
    assert core.build_acquisition_plan is first
