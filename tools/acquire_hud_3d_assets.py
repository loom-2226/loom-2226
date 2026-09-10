#!/usr/bin/env python3
"""Acquire external 3D assets for the HUD qualification scene.

Assets are cached under LOOM data/qualification and are not written into canon,
campaign state, or the authoritative spatial SQLite database. SHA-256 digests
are recorded after acquisition; upstream files currently have no repository-
local qualification hash to compare against.

Three r147 is intentional: r148 removed the classic examples/js addon tree. The
existing Pixel Geometry Lab uses the classic global THREE runtime, so this HUD
qualification slice stays on the last loader-compatible classic release rather
than silently introducing a second module/runtime architecture.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import urllib.request

NASA_MOON_URL = "https://svs.gsfc.nasa.gov/vis/a010000/a014900/a014959/Moon_NASA_LRO_8k_Topo_Small.glb"
THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"
GLTF_LOADER_URL = "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/loaders/GLTFLoader.js"


def _download(url: str, target: Path, minimum_bytes: int) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_size >= minimum_bytes:
        data = target.read_bytes()
        status = "CACHED"
    else:
        tmp = target.with_suffix(target.suffix + ".part")
        print(f"DOWNLOADING      {url}")
        with urllib.request.urlopen(url, timeout=120) as response, tmp.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        if tmp.stat().st_size < minimum_bytes:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"download unexpectedly small: {target.name}")
        tmp.replace(target)
        data = target.read_bytes()
        status = "DOWNLOADED"
    return {
        "name": target.name,
        "path": str(target),
        "url": url,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "status": status,
    }


def main() -> int:
    data_root = Path(os.environ.get("LOOM_DATA_ROOT") or "/storage/emulated/0/Documents/LOOM/data").expanduser().resolve()
    root = data_root / "qualification" / "hud_assets"
    assets = [
        _download(THREE_URL, root / "three.min.js", 100_000),
        _download(GLTF_LOADER_URL, root / "GLTFLoader.js", 20_000),
        _download(NASA_MOON_URL, root / "Moon_NASA_LRO_8k_Topo_Small.glb", 50_000_000),
    ]
    manifest = {
        "contract": "LOOM_HUD_EXTERNAL_3D_ASSET_CACHE_V1",
        "status": "QUALIFICATION_ONLY",
        "data_access": "LOCAL_EXTERNAL_CACHE",
        "three_version": "0.147.0",
        "three_version_reason": "last classic examples/js addon release; matches Pixel global-THREE architecture",
        "moon_radius_km_for_scene_scale": 1737.4,
        "moon_orientation_authority": "MODEL_NATIVE_NOT_SPICE_QUALIFIED",
        "nasa_credit": "NASA's Goddard Space Flight Center",
        "assets": assets,
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("\nLOOM HUD 3D ASSETS")
    for asset in assets:
        print(f"{asset['status']:<16} {asset['name']:<38} {asset['bytes']/1024/1024:8.1f} MiB")
        print(f"SHA-256          {asset['sha256']}")
    print("MANIFEST         ", manifest_path)
    print("AUTHORITY         QUALIFICATION_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
