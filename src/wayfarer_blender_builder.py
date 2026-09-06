#!/usr/bin/env python3
"""Build deterministic LOOM Wayfarer geometry inside Blender.

The builder consumes the same generated ``geometry/wayfarer_geometry.json`` payload
used by the phone Three.js viewer. If the JSON does not yet exist, it will try to
compile it from the repository SQL seed using ``src/wayfarer_geometry.py``.

Run from Blender's Scripting workspace, or from a shell, for example::

    blender --python src/wayfarer_blender_builder.py -- \
      --launch DOCKED --radiators STOWED --save Wayfarer_v0_1.blend

Geometry authority remains the LOOM parameter/SQL -> geometry compiler pipeline;
this script is a deterministic Blender consumer, not a second geometry authority.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

try:  # Importable under normal Python for regression testing of the pure planner.
    import bpy  # type: ignore
except ImportError:  # pragma: no cover - exercised outside Blender by design
    bpy = None

COLLECTION_NAME = "LOOM_WAYFARER"
GROUP_COLORS = {
    "habitat": (0.72, 0.70, 0.62, 1.0),
    "tanks": (0.44, 0.46, 0.48, 1.0),
    "structure": (0.20, 0.23, 0.27, 1.0),
    "launch_bay": (0.34, 0.30, 0.25, 1.0),
    "launch": (0.68, 0.64, 0.52, 1.0),
    "radiators": (0.055, 0.065, 0.075, 1.0),
    "propulsion": (0.28, 0.28, 0.30, 1.0),
    "docking": (0.50, 0.47, 0.40, 1.0),
}


def _repo_root_from(path: Path) -> Optional[Path]:
    path = path.resolve()
    candidates = [path] + list(path.parents)
    for candidate in candidates:
        if (candidate / "geometry" / "wayfarer_geometry_seed.sql").exists() and (candidate / "src" / "wayfarer_geometry.py").exists():
            return candidate
    return None


def find_repo_root() -> Path:
    probes: List[Path] = []
    if "__file__" in globals():
        probes.append(Path(__file__).resolve().parent)
    probes.append(Path.cwd())
    for probe in probes:
        root = _repo_root_from(probe)
        if root:
            return root
    raise RuntimeError("Could not locate LOOM repository root containing geometry/ and src/wayfarer_geometry.py")


def load_or_compile_geometry(root: Path, explicit: Optional[Path] = None) -> Dict[str, Any]:
    geometry_path = explicit.resolve() if explicit else root / "geometry" / "wayfarer_geometry.json"
    if not geometry_path.exists():
        src = root / "src"
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        from wayfarer_geometry import init_db, write_geometry  # type: ignore

        db = root / "data" / "wayfarer_geometry.sqlite3"
        seed = root / "geometry" / "wayfarer_geometry_seed.sql"
        conn = init_db(db, seed)
        try:
            write_geometry(conn, geometry_path)
        finally:
            conn.close()
    return json.loads(geometry_path.read_text(encoding="utf-8"))


def component_visible(component: Mapping[str, Any], launch_state: str, include_open: bool) -> bool:
    if component.get("id") == "planetary_launch" and launch_state == "ABSENT":
        return False
    if component.get("status") == "OPEN" and not include_open and component.get("group") != "radiators":
        return False
    return True


def component_plan(component: Mapping[str, Any], radiator_state: str) -> Dict[str, Any]:
    """Translate one canonical geometry component into a Blender-neutral primitive plan."""
    kind = str(component["kind"])
    dims = dict(component["dimensions"])
    center = [float(v) for v in component["center_m"]]
    rotation = [0.0, 0.0, 0.0]
    primitive: Dict[str, Any]

    if kind == "cylinder_x":
        primitive = {
            "primitive": "cylinder",
            "radius_m": float(dims["diameter_m"]) / 2.0,
            "depth_m": float(dims["length_m"]),
        }
        rotation[1] = math.pi / 2.0
    elif kind == "box":
        primitive = {
            "primitive": "box",
            "size_m": [float(dims["x_m"]), float(dims["y_m"]), float(dims["z_m"])],
        }
    elif kind == "nozzle_x":
        aperture = float(dims["aperture_diameter_m"])
        primitive = {
            "primitive": "cone",
            "radius1_m": aperture * 0.28,
            "radius2_m": aperture / 2.0,
            "depth_m": float(dims["length_m"]),
        }
        rotation[1] = math.pi / 2.0
    elif kind == "collar_z":
        primitive = {
            "primitive": "cylinder",
            "radius_m": float(dims["diameter_m"]) / 2.0,
            "depth_m": float(dims["depth_m"]),
        }
    elif kind == "radiator_placeholder":
        azimuth = math.radians(float(dims["azimuth_deg"]))
        if radiator_state == "DEPLOYED":
            center[1] += math.cos(azimuth) * 8.0
            center[2] += math.sin(azimuth) * 8.0
            size = [float(dims["root_length_m"]), float(dims["panel_chord_m"]), 0.12]
        else:
            size = [float(dims["root_length_m"]), 0.18, 6.5]
        rotation[0] = azimuth
        primitive = {"primitive": "box", "size_m": size, "placeholder": True}
    else:
        raise ValueError(f"Unsupported Wayfarer component kind: {kind}")

    return {
        "id": str(component["id"]),
        "group": str(component.get("group", "other")),
        "status": str(component.get("status", "OPEN")),
        "source": str(component.get("source", "")),
        "center_m": center,
        "rotation_euler_rad": rotation,
        "primitive": primitive,
        "component": dict(component),
    }


def build_plan(payload: Mapping[str, Any], launch_state: str = "DOCKED", radiator_state: str = "STOWED", include_open: bool = False) -> List[Dict[str, Any]]:
    if launch_state not in {"DOCKED", "EXTRACTING", "ABSENT"}:
        raise ValueError(f"Unsupported launch state {launch_state!r}")
    if radiator_state not in {"STOWED", "DEPLOYING", "DEPLOYED"}:
        raise ValueError(f"Unsupported radiator state {radiator_state!r}")
    # DEPLOYING has no frozen physical topology yet, so render the conservative stowed placeholder.
    effective_radiator_state = "DEPLOYED" if radiator_state == "DEPLOYED" else "STOWED"
    return [
        component_plan(component, effective_radiator_state)
        for component in payload["components"]
        if component_visible(component, launch_state, include_open)
    ]


def _material_for(group: str, status_name: str):
    material_name = f"LOOM_{group}_{status_name}"
    material = bpy.data.materials.get(material_name)
    if material:
        return material
    material = bpy.data.materials.new(material_name)
    rgba = GROUP_COLORS.get(group, (0.35, 0.35, 0.35, 1.0))
    alpha = 0.45 if status_name == "OPEN" else rgba[3]
    material.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF") if material.node_tree else None
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
        bsdf.inputs["Metallic"].default_value = 0.45
        bsdf.inputs["Roughness"].default_value = 0.58
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        if hasattr(material, "surface_render_method"):
            try:
                material.surface_render_method = "DITHERED"
            except Exception:
                pass
        elif hasattr(material, "blend_method"):
            try:
                material.blend_method = "BLEND"
            except Exception:
                pass
    return material


def _remove_collection(name: str) -> None:
    collection = bpy.data.collections.get(name)
    if not collection:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for child in list(collection.children):
        for obj in list(child.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(child)
    bpy.data.collections.remove(collection)


def _group_collection(parent, name: str):
    child = bpy.data.collections.get(f"{COLLECTION_NAME}_{name}")
    if child:
        return child
    child = bpy.data.collections.new(f"{COLLECTION_NAME}_{name}")
    parent.children.link(child)
    return child


def _move_object_to_collection(obj, collection) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def _create_object(item: Mapping[str, Any], collection):
    p = item["primitive"]
    loc = tuple(item["center_m"])
    rot = tuple(item["rotation_euler_rad"])
    if p["primitive"] == "box":
        sx, sy, sz = p["size_m"]
        bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot, scale=(sx / 2.0, sy / 2.0, sz / 2.0))
    elif p["primitive"] == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=p["radius_m"], depth=p["depth_m"], location=loc, rotation=rot)
    elif p["primitive"] == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=p["radius1_m"], radius2=p["radius2_m"], depth=p["depth_m"], location=loc, rotation=rot)
    else:
        raise ValueError(f"Unsupported primitive {p['primitive']!r}")
    obj = bpy.context.active_object
    obj.name = item["id"]
    _move_object_to_collection(obj, collection)
    obj.data.materials.append(_material_for(item["group"], item["status"]))
    obj["loom_id"] = item["id"]
    obj["loom_group"] = item["group"]
    obj["loom_status"] = item["status"]
    obj["loom_source"] = item["source"]
    obj["loom_component_json"] = json.dumps(item["component"], sort_keys=True)
    if p.get("placeholder"):
        obj["loom_placeholder_geometry"] = True
    return obj


def build_blender_scene(payload: Mapping[str, Any], launch_state: str, radiator_state: str, include_open: bool = False):
    if bpy is None:
        raise RuntimeError("This function must run inside Blender (bpy is unavailable)")
    if not payload.get("validation", {}).get("overall_pass"):
        raise RuntimeError("Wayfarer geometry validation is not passing; refusing Blender build")

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0

    _remove_collection(COLLECTION_NAME)
    master = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(master)

    datum = bpy.data.objects.new("WAYFARER_DATUM", None)
    master.objects.link(datum)
    datum.empty_display_type = "PLAIN_AXES"
    datum.empty_display_size = 2.0
    datum["loom_schema"] = str(payload.get("schema", ""))
    datum["loom_schema_version"] = str(payload.get("schema_version", ""))
    datum["launch_state"] = launch_state
    datum["radiator_state"] = radiator_state

    groups: Dict[str, Any] = {}
    plan = build_plan(payload, launch_state, radiator_state, include_open)
    for item in plan:
        group_name = item["group"]
        if group_name not in groups:
            groups[group_name] = _group_collection(master, group_name)
        _create_object(item, groups[group_name])

    bpy.context.view_layer.objects.active = datum
    datum.select_set(True)
    return {"collection": master, "datum": datum, "object_count": len(plan), "plan": plan}


def _script_args(argv: Optional[Iterable[str]] = None) -> List[str]:
    args = list(sys.argv if argv is None else argv)
    return args[args.index("--") + 1 :] if "--" in args else []


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic LOOM Wayfarer geometry in Blender")
    parser.add_argument("--geometry", type=Path, default=None, help="Path to generated wayfarer_geometry.json")
    parser.add_argument("--launch", choices=["DOCKED", "EXTRACTING", "ABSENT"], default="DOCKED")
    parser.add_argument("--radiators", choices=["STOWED", "DEPLOYING", "DEPLOYED"], default="STOWED")
    parser.add_argument("--include-open", action="store_true", help="Include OPEN placeholder components such as the docking collar")
    parser.add_argument("--save", type=Path, default=None, help="Optional .blend output path")
    return parser.parse_args(_script_args(argv))


def main() -> None:
    if bpy is None:
        raise SystemExit("wayfarer_blender_builder.py must be executed by Blender; pure planning helpers may be imported under normal Python")
    args = parse_args()
    root = find_repo_root()
    payload = load_or_compile_geometry(root, args.geometry)
    result = build_blender_scene(payload, args.launch, args.radiators, args.include_open)
    validation = payload["validation"]
    print("LOOM WAYFARER BLENDER BUILDER v0.1")
    print("ROOT             ", root)
    print("OBJECTS          ", result["object_count"])
    print("LAUNCH            ", args.launch)
    print("RADIATORS         ", args.radiators)
    print(f"BOUNDARY PROXY    {validation['normal_boundary_proxy_m2']:.1f} m^2 / {validation['normal_boundary_target_m2']:.1f} m^2")
    print("VALIDATION        ", "PASS" if validation["overall_pass"] else "FAIL")
    if args.save:
        save_path = args.save.expanduser().resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print("BLEND             ", save_path)


if __name__ == "__main__":
    main()
