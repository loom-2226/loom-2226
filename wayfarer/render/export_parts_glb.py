#!/usr/bin/env python3
"""Per-solid viewer GLB from the tagged v2.5 D9 installed BReps (no canon mutation)."""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
import d9_sharded as S
from build123d import Compound, Color, Unit, export_gltf

SHA = "88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
GLB = ROOT / "render/out/wayfarer_parts_88ce19fc.glb"
REGISTER = ROOT / "render/PARTS_REGISTER.yml"


def named_mesh_nodes(path):
    blob = path.read_bytes()
    assert len(blob) >= 28
    magic, version, length = struct.unpack_from("<III", blob)
    assert magic == 0x46546C67 and version == 2 and length == len(blob)
    chunk_length, chunk_type = struct.unpack_from("<II", blob, 12)
    assert chunk_type == 0x4E4F534A
    doc = json.loads(blob[20:20 + chunk_length])
    nodes = [n.get("name", "") for n in doc["nodes"] if "mesh" in n]
    return nodes


def main():
    G, I, C, R, rebuilt, geo_sha, step_sha = S.context()
    assert geo_sha == SHA and rebuilt["candidate_pass"] is True
    rows, shapes, installed, factor = S.imported(G)
    assert len(installed) == 194 and len(set(rows) - set(installed)) == 122
    ratio = I["states"]["S1"]["remass_t"] / R["masses"]["core_R_t"]
    assert 0 < ratio < 1
    solids = []
    for name in installed:
        shape = shapes[name]
        if name.startswith("S1:water_"):
            shape = S.D.trim_liquid_forward(shape, ratio)
        shape.label = name
        shape.color = Color("#7E9BAF" if name.startswith("S1:") else "#A8A8A8")
        solids.append(shape)
    GLB.parent.mkdir(parents=True, exist_ok=True)
    export_gltf(Compound(children=solids), GLB, unit=Unit.M, binary=True,
                linear_deflection=.05, angular_deflection=.3)
    names = named_mesh_nodes(GLB)
    assert len(names) == len(installed), (len(names), len(installed), names[:12])
    assert len(set(names)) == len(names)
    assert set(names) == set(installed), {
        "missing": sorted(set(installed) - set(names))[:30],
        "extra": sorted(set(names) - set(installed))[:30],
    }
    assert all(n.startswith(("dry:", "S1:")) for n in names)
    digest = hashlib.sha256(GLB.read_bytes()).hexdigest()
    record = [
        "# Viewer/print-only derivatives. No new canon, mechanical or CAD qualification.",
        "source_tag: canon-v2.5",
        "source_commit: bfa7dcfb12358b119d5e63773f30ed9d251a43fc",
        "geometry_sha256: " + geo_sha,
        "source_step_gz_sha256: " + step_sha,
        "glb:",
        "  path: wayfarer/render/out/wayfarer_parts_88ce19fc.glb",
        "  sha256: " + digest,
        "  format: glTF-2.0-binary",
        "  node_convention: 'dry:<id>, S1:<id>:<index>'",
        "  installed_mesh_nodes: 194",
        "  dry_mesh_nodes: " + str(sum(n.startswith("dry:") for n in names)),
        "  S1_mesh_nodes: " + str(sum(n.startswith("S1:") for n in names)),
        "  excluded_no_render_placeholders: 122",
        "  source_numeric_unit: metre",
        "  method: 'build123d==0.13.0; same current-G3 D9 STEP and liquid debit'",
        "  classification: VIEWER_ONLY_NON_CANON",
        "  nodes:",
    ]
    record += ["    - '" + n.replace("'", "''") + "'" for n in sorted(names)]
    record += [
        "print_test_1:",
        "  manifest: wayfarer/render/print_test_1/PRINT_TEST_1.yml",
        "  root: wayfarer/render/print_test_1/hotfin_root_40_1to100.stl",
        "  fin: wayfarer/render/print_test_1/hotfin_40_1to100.stl",
        "  status: PROTOTYPE_ONLY",
    ]
    REGISTER.write_text("\n".join(record) + "\n")
    print("VIEWER_PART_GLB_PASS nodes", len(names), "dry",
          sum(n.startswith("dry:") for n in names),
          "S1", sum(n.startswith("S1:") for n in names),
          "bytes", GLB.stat().st_size, "sha256", digest)


if __name__ == "__main__":
    main()
