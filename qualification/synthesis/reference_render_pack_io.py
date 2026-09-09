from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Mapping

from deterministic_reference_renderer import ReferenceRenderPackage


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_reference_render_pack(package: ReferenceRenderPackage, output_dir: Path) -> Mapping[str, str]:
    """Write deterministic SVG reference evidence and a content-addressed manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, str] = {}
    for artifact in package.artifacts:
        path = output_dir / artifact.artifact_id
        path.write_text(artifact.content, encoding="utf-8")
        written[artifact.artifact_id] = artifact.content_sha256

    payload = asdict(package)
    for artifact in payload["artifacts"]:
        artifact.pop("content", None)
    payload["written_artifact_hashes"] = dict(sorted(written.items()))
    manifest_text = json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    manifest_name = "reference_render_manifest.json"
    (output_dir / manifest_name).write_text(manifest_text, encoding="utf-8")
    written[manifest_name] = _sha(manifest_text)
    return dict(sorted(written.items()))
