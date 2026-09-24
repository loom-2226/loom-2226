"""Invoke hash-pinned inherited bridge code with isolated candidate paths.

The inherited algorithms are unchanged. Path injection keeps all writes inside
the candidate root; the source modules are read-only dependencies.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

INHERITED = Path("/home/ubuntu/loom_earth_2026_2035/earth_repair_successor_2026_09_22")
EXPECTED = {"stage_bridge.py": "50fc8d9b38bf0336e34cd9214158120a3177df207fa3bcd977adf5eeea96b0a7",
            "stage_mid.py": "fb944c8d29e35bcd010d39e149604010dfdd89ab832764f87560844ef19947da"}


def load_pinned(name):
    path = INHERITED / name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED[name]:
        raise ValueError(f"inherited code hash mismatch: {name}")
    spec = importlib.util.spec_from_file_location("candidate_" + name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_seed(root):
    manifest = json.loads((root / "SEED_MANIFEST.json").read_text())
    for name, record in manifest["files"].items():
        path = Path(name)
        if not path.is_file() or path.stat().st_size != record["bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"seed dependency mismatch: {path}")


def run_bridge(root):
    verify_seed(root)
    module = load_pinned("stage_bridge.py")
    module.QUALIFIED = root / "qualified_inputs"
    module.MACRO_COUNTRIES = module.QUALIFIED / "countries_2026_2031.ndjson"
    module.MACRO_SECTORS = module.QUALIFIED / "country_sectors_2026_2031.ndjson"
    module.ASSET_SEED = root / "seed_assets_2026.ndjson"
    module.OUTDIR = root / "stage_2026_2031"
    module.COUNTRIES_ALL = module.OUTDIR / "countries_2026_2031.ndjson"
    module.SECTORS_ALL = module.OUTDIR / "country_sectors_2026_2031.ndjson"
    module.ASSETS_ALL = module.OUTDIR / "country_sector_assets_2026_2031.ndjson"
    module.COUNTRIES_2031 = module.OUTDIR / "countries_2031.ndjson"
    module.SECTORS_2031 = module.OUTDIR / "country_sectors_2031.ndjson"
    module.ASSETS_2031 = module.OUTDIR / "country_sector_assets_2031.ndjson"
    module.REPORT = module.OUTDIR / "report.json"
    module.main()


def run_mid(root):
    if not (root / "stage_2026_2031/report.json").is_file():
        raise ValueError("candidate 2026-2031 stage absent")
    module = load_pinned("stage_mid.py")
    module.ASSET_BRIDGE = root / "stage_2026_2031"
    module.COUNTRIES_2031_SRC = module.ASSET_BRIDGE / "countries_2031.ndjson"
    module.COUNTRIES_2026_2031_SRC = module.ASSET_BRIDGE / "countries_2026_2031.ndjson"
    module.SECTORS_2031_SRC = module.ASSET_BRIDGE / "country_sectors_2031.ndjson"
    module.ASSETS_2031_SRC = module.ASSET_BRIDGE / "country_sector_assets_2031.ndjson"
    module.OUTDIR = root / "stage_2031_2060"
    module.COUNTRIES_ALL = module.OUTDIR / "countries_2031_2060.ndjson"
    module.SECTORS_ALL = module.OUTDIR / "country_sectors_2031_2060.ndjson"
    module.ASSETS_ALL = module.OUTDIR / "country_sector_assets_2031_2060.ndjson"
    module.COUNTRIES_2060 = module.OUTDIR / "countries_2060.ndjson"
    module.SECTORS_2060 = module.OUTDIR / "country_sectors_2060.ndjson"
    module.ASSETS_2060 = module.OUTDIR / "country_sector_assets_2060.ndjson"
    module.REPORT = module.OUTDIR / "report.json"
    module.main()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--stage", choices=("bridge", "mid"), required=True)
    args = parser.parse_args()
    (run_bridge if args.stage == "bridge" else run_mid)(args.candidate_root)


if __name__ == "__main__":
    main()
