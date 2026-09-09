from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from shipyard_glb_viewer import parse_glb
from shipyard_visual_library import VisualLibraryAsset
from shipyard_visual_grammar import GRAMMARS, grammar_hash, validate_grammar

HANDOFF_VERSION = "LOOM_SHIPYARD_REALIZATION_HANDOFF_v0.1"
HANDOFF_AUTHORITY = "NON_AUTHORITATIVE_VISUAL_REALIZATION_HANDOFF_ONLY"

REFERENCE_VIEWS = (
    {"view_id": "REF_3Q_FORE_PORT", "azimuth_deg": 35.0, "elevation_deg": 24.0, "projection": "PERSPECTIVE", "fov_deg": 41.25},
    {"view_id": "REF_3Q_AFT_STARBOARD", "azimuth_deg": 215.0, "elevation_deg": 24.0, "projection": "PERSPECTIVE", "fov_deg": 41.25},
    {"view_id": "REF_PORT", "azimuth_deg": 90.0, "elevation_deg": 0.0, "projection": "PERSPECTIVE", "fov_deg": 41.25},
    {"view_id": "REF_STARBOARD", "azimuth_deg": 270.0, "elevation_deg": 0.0, "projection": "PERSPECTIVE", "fov_deg": 41.25},
    {"view_id": "REF_TOP", "azimuth_deg": 0.0, "elevation_deg": 89.0, "projection": "PERSPECTIVE", "fov_deg": 41.25},
    {"view_id": "REF_FORE", "azimuth_deg": 0.0, "elevation_deg": 0.0, "projection": "PERSPECTIVE", "fov_deg": 41.25},
    {"view_id": "REF_AFT", "azimuth_deg": 180.0, "elevation_deg": 0.0, "projection": "PERSPECTIVE", "fov_deg": 41.25},
)


def _sha(payload: Any) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _infer_class(name: str, extras: dict[str, Any]) -> str:
    explicit = extras.get("semantic_class") or extras.get("component_class")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip().upper()
    n = name.lower()
    rules = (
        (("pressure", "hab", "hull"), "PRESSURE_VOLUME"),
        (("tank", "propellant", "remass"), "PROPELLANT"),
        (("radiator",), "RADIATOR"),
        (("reactor",), "REACTOR"),
        (("nozzle",), "NOZZLE"),
        (("dock", "collar"), "DOCK"),
        (("shield",), "SHIELD"),
        (("longeron", "truss", "structure", "frame"), "STRUCTURE"),
        (("cargo",), "CARGO"),
        (("launch",), "OTHER"),
        (("core", "power"), "POWER"),
        (("drive", "torch"), "DRIVE"),
    )
    for needles, cls in rules:
        if any(token in n for token in needles):
            return cls
    return "OTHER"


def component_map(asset: VisualLibraryAsset) -> list[dict[str, Any]]:
    doc, _ = parse_glb(asset.payload)
    out: list[dict[str, Any]] = []
    for index, node in enumerate(doc.get("nodes", [])):
        if "mesh" not in node:
            continue
        extras = node.get("extras") if isinstance(node.get("extras"), dict) else {}
        name = str(node.get("name") or f"node_{index}")
        out.append({
            "node_index": index,
            "node_name": name,
            "mesh_index": int(node["mesh"]),
            "semantic_object_id": extras.get("semantic_object_id"),
            "component_id": extras.get("component_id") or extras.get("source_component_id"),
            "inferred_component_class": _infer_class(name, extras),
            "classification_basis": "EXPLICIT_SEMANTIC_EXTRAS" if (extras.get("semantic_class") or extras.get("component_class")) else "NAME_HEURISTIC_VISUAL_ONLY",
        })
    return out


def build_library_realization_packet(asset: VisualLibraryAsset, yard_id: str) -> dict[str, Any]:
    yard = yard_id.upper()
    if yard not in GRAMMARS:
        raise ValueError(f"unknown yard_id {yard_id}")
    grammar = GRAMMARS[yard]
    validate_grammar(grammar)
    cmap = component_map(asset)
    packet: dict[str, Any] = {
        "version": HANDOFF_VERSION,
        "authority_status": HANDOFF_AUTHORITY,
        "visual_realization_authoritative": False,
        "may_backpropagate_engineering_claims": False,
        "source_asset": {
            "asset_id": asset.asset_id,
            "display_name": asset.display_name,
            "ship_name": asset.ship_name,
            "artifact_class": asset.artifact_class,
            "asset_authority_status": asset.authority_status,
            "glb_sha256": asset.sha256,
            "generator": asset.generator,
            "mesh_count": asset.mesh_count,
            "node_count": asset.node_count,
            "semantic_node_count": asset.semantic_node_count,
            "source_candidate_id": asset.source_candidate_id,
            "source_candidate_hash": asset.source_candidate_hash,
        },
        "yard": {
            "yard_id": yard,
            "grammar_version": grammar.version,
            "grammar_hash": grammar_hash(grammar),
            "fabrication_context": list(grammar.fabrication_context),
            "structural_doctrine": list(grammar.structural_doctrine),
            "module_doctrine": list(grammar.module_doctrine),
            "maintenance_doctrine": list(grammar.maintenance_doctrine),
            "redundancy_doctrine": list(grammar.redundancy_doctrine),
            "geometric_complexity_doctrine": list(grammar.geometric_complexity_doctrine),
            "visual_consequences": list(grammar.visual_consequences),
            "prohibited_interpretations": list(grammar.prohibited_interpretations),
        },
        "component_map": cmap,
        "reference_views": list(REFERENCE_VIEWS),
        "realization_rules": [
            "Treat the selected GLB and deterministic reference views as the spatial source constraint.",
            "Preserve recognizable component count, placement, orientation, scale relationships, and function where supplied or inferable.",
            "For NAME_HEURISTIC_VISUAL_ONLY mappings, preserve visual identity but do not promote the inferred class to engineering truth.",
            "Apply the selected yard grammar only in geometric/material/detail freedoms not fixed by the source artifact.",
            "Generated members, materials, pipes, conduits, surface details, and topology remain non-authoritative visualization unless separately admitted by engineering.",
        ],
    }
    packet["packet_hash"] = _sha(packet)
    return packet


def canonical_packet_json(packet: dict[str, Any]) -> str:
    if packet.get("authority_status") != HANDOFF_AUTHORITY:
        raise ValueError("realization handoff authority mismatch")
    if packet.get("visual_realization_authoritative") or packet.get("may_backpropagate_engineering_claims"):
        raise ValueError("realization handoff authority escalation")
    return json.dumps(packet, sort_keys=True, separators=(",", ":"), allow_nan=False)
