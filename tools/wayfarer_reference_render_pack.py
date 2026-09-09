from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from deterministic_reference_renderer import build_reference_render_package  # noqa: E402
from governed_ship_synthesis import build_wayfarer_governed_synthesis  # noqa: E402
from minimum_spatial_validation import build_minimum_spatial_validation  # noqa: E402
from reference_render_pack_io import write_reference_render_pack  # noqa: E402
from semantic_geometry import build_semantic_geometry  # noqa: E402
from spatial_rule_contract import build_wayfarer_spatial_rule_contract  # noqa: E402
from spatial_validation_with_rules import build_spatial_validation_with_rules  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic Wayfarer R3 SVG reference evidence.")
    parser.add_argument("--seed", type=int, default=2226)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "wayfarer_reference_r3")
    args = parser.parse_args()

    source = build_wayfarer_governed_synthesis(args.seed)
    semantic = build_semantic_geometry(source)
    r2 = build_minimum_spatial_validation(source, semantic)
    rules = build_wayfarer_spatial_rule_contract(source, semantic)
    r2a = build_spatial_validation_with_rules(source, semantic, r2=r2, rules=rules)
    r3 = build_reference_render_package(source, semantic, r2, rules, r2a)
    written = write_reference_render_pack(r3, args.output)

    print("WAYFARER R3 REFERENCE PACK")
    print("OUTPUT:", args.output)
    print("CANDIDATE:", r3.source_design_candidate_id)
    print("PACKAGE SHA256:", r3.package_hash)
    print("AI HANDOFF:", r3.visual_realization_handoff_status)
    print("REFERENCE RENDERS:", len(r3.artifacts))
    for name, digest in written.items():
        print(f"{name}  {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
