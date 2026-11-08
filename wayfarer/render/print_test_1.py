#!/usr/bin/env python3
"""PRINT TEST 1: one 1:100 deployable hotfin prototype. Print-only trial, no canon credit."""
import hashlib
import json
from pathlib import Path
from build123d import Align, Box, Cylinder, Pos, Rot, export_stl

ROOT = Path(__file__).resolve().parents[1]
GEOMETRY = ROOT / "results/out/wayfarer_v05_geometry.json"
DEST = ROOT / "render/print_test_1"
SHA = "88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"


def plate(x0, x1, y0, y1, thickness):
    return Pos(x0, y0, -thickness / 2) * Box(
        x1 - x0, y1 - y0, thickness,
        align=(Align.MIN, Align.MIN, Align.MIN))


def knuckle(x0, x1):
    # 2.0 mm metal axle with 0.4 mm diametral clearance; 1.2 mm barrel wall.
    pose = Pos(x0, 0, 2) * Rot(Y=90)
    outer = pose * Cylinder(
        radius=2.4, height=x1 - x0,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    hole = (Pos(x0 - 0.2, 0, 2) * Rot(Y=90) *
            Cylinder(radius=1.2, height=x1 - x0 + 0.4,
                     align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return outer - hole


def main():
    assert hashlib.sha256(GEOMETRY.read_bytes()).hexdigest() == SHA
    G = json.loads(GEOMETRY.read_text())
    p = {v["id"]: v["shape"] for v in G["parts"]}
    fin, root = p["hotfin_40"], p["hotfin_root_40"]
    assert fin["k"] == root["k"] == "panel"
    for actual, expected in (
        (fin["x1"] - fin["x0"], 19), (root["x1"] - root["x0"], 14),
        (fin["span"], 2), (root["span"], 1.75),
        (fin["t"], 0.6), (root["t"], 0.3),
    ):
        assert abs(actual - expected) < 1e-8, (actual, expected)

    # Sourced panel sizes in metres: 19x2x0.6m, 14x1.75x0.3m.
    # 1:100 print sizes: 190x20x6mm, 140x17.5x3mm.
    # Hinge mounts are *print additions*; the source has no governed hinge.
    stationary = plate(50, 190, -17.5, -0.2, 3)
    moving = plate(0, 190, 0.2, 20, 6)
    for a, b in ((55, 84.8), (155.2, 185)):
        stationary = stationary + knuckle(a, b)
    moving = moving + knuckle(85.2, 154.8)
    assert stationary.is_valid and moving.is_valid
    assert stationary.volume > 0 and moving.volume > 0

    DEST.mkdir(parents=True, exist_ok=True)
    outputs = [
        ("hotfin_root_40_1to100.stl", stationary),
        ("hotfin_40_1to100.stl", moving),
    ]
    for name, shape in outputs:
        export_stl(shape, DEST / name)
    manifest = [
        "# PRINT TEST 1, print-only functional hinge trial. No canon or CAD credit.",
        "source_tag: canon-v2.5",
        "geometry_sha256: " + SHA,
        "test: 1",
        "source_part_ids: ['hotfin_root_40', 'hotfin_40']",
        "scale: '1:100'",
        "unit: millimetre",
        "printer: Bambu A2L",
        "nozzle_diameter_mm: 0.4",
        "panel_print_dimensions_mm: ['190 x 20 x 6', '140 x 17.5 x 3']",
        "metal_hinge_pin_diameter_mm: 2.0",
        "pin_hole_diameter_mm: 2.4",
        "hinge_diametral_clearance_mm: 0.4",
        "hinge_radial_wall_mm: 1.2",
        "panel_edge_gap_mm: 0.4",
        "source_exactness: 'panel envelope only; hinge added for print test'",
        "physical_print_result: NOT_YET_TESTED",
        "deployment_mechanism_qualification: OPEN",
        "parts:",
    ]
    for name, _ in outputs:
        data = (DEST / name).read_bytes()
        manifest += [
            "  - path: wayfarer/render/print_test_1/" + name,
            "    bytes: " + str(len(data)),
            "    sha256: " + hashlib.sha256(data).hexdigest(),
        ]
    (DEST / "PRINT_TEST_1.yml").write_text("\n".join(manifest) + "\n")
    print("PRINT_TEST_1_SOURCE_SIZES_PASS")
    print("PRINT_TEST_1_STL_PASS", [(n, (DEST / n).stat().st_size) for n, _ in outputs])


if __name__ == "__main__":
    main()
