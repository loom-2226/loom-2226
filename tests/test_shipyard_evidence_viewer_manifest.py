import json
from pathlib import Path


def test_phase7_manifest_preserves_authority():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "manifests" / "shipyard_overlay_manifest.json").read_text())
    assert manifest["release_id"].startswith("shipyard-phase7-visual-evidence")
    assert manifest["authority"]["canon_changed"] is False
    assert manifest["authority"]["production_shipclasses_changed"] is False
    assert manifest["authority"]["flight_dynamics_authority"] is False
