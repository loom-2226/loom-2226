#!/usr/bin/env python3
"""Build or verify a deterministic derived Solar basemap publication."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loom_solar_basemap_compile import compile_product
from src.loom_solar_basemap_contract import validate_product


def tree_files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in Path(root).rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database")
    parser.add_argument("--asset-root")
    parser.add_argument("--epoch", default="2226-01-01T00:00:00 TDB")
    parser.add_argument("--output")
    parser.add_argument("--verify-identical", nargs=2, metavar=("A", "B"))
    parser.add_argument("--validate")
    args = parser.parse_args()
    if args.verify_identical:
        a, b = map(Path, args.verify_identical)
        aa, bb = tree_files(a), tree_files(b)
        if aa.keys() != bb.keys(): raise SystemExit("product file inventories differ")
        diff = [k for k in aa if aa[k] != bb[k]]
        if diff: raise SystemExit("product bytes differ: " + ", ".join(diff[:10]))
        ma, _ = validate_product(a); mb, _ = validate_product(b)
        print(json.dumps({"identical": True, "build_id": ma["build_id"], "files": len(aa)})); return
    if args.validate:
        manifest, root = validate_product(args.validate)
        print(json.dumps({"valid": True, "build_id": manifest["build_id"], "features": len(root["features"])})); return
    if not all((args.database, args.asset_root, args.output)):
        parser.error("--database, --asset-root, and --output are required for a build")
    manifest, report = compile_product(args.database, args.asset_root, args.output, args.epoch)
    print(json.dumps({"manifest": manifest, "report": report}, sort_keys=True))


if __name__ == "__main__": main()
