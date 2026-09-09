from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "qualification" / "synthesis"
if str(SYN) not in sys.path:
    sys.path.insert(0, str(SYN))

from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb, canonical_manifest_json


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    out_dir = Path(args[0] if args else "out/wayfarer-semantic-glb").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    source = build_wayfarer_governed_synthesis()
    semantic = build_semantic_geometry(source)
    glb, manifest = build_semantic_glb(source, semantic)

    glb_path = out_dir / "wayfarer_semantic.glb"
    manifest_path = out_dir / "wayfarer_semantic_glb_manifest.json"
    glb_path.write_bytes(glb)
    manifest_path.write_text(canonical_manifest_json(manifest) + "\n", encoding="utf-8")

    print(json.dumps({
        "glb": str(glb_path),
        "manifest": str(manifest_path),
        "glb_sha256": manifest["glb_sha256"],
        "object_count": manifest["object_count"],
        "authority_status": manifest["authority_status"],
        "flight_dynamics_authority": manifest["flight_dynamics_authority"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
