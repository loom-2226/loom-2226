from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Dict, Tuple

GRAMMAR_VERSION = "LOOM_SHIPYARD_VISUAL_GRAMMAR_v0.1"
GRAMMAR_AUTHORITY = "NON_AUTHORITATIVE_VISUAL_REALIZATION_INSTRUCTIONS_ONLY"
PACKET_AUTHORITY = "NON_AUTHORITATIVE_VISUAL_REALIZATION_PACKET_ONLY"


class ShipyardVisualGrammarError(ValueError):
    pass


def _sha(payload: object) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ShipyardVisualGrammar:
    version: str
    yard_id: str
    fabrication_context: Tuple[str, ...]
    structural_doctrine: Tuple[str, ...]
    module_doctrine: Tuple[str, ...]
    maintenance_doctrine: Tuple[str, ...]
    redundancy_doctrine: Tuple[str, ...]
    geometric_complexity_doctrine: Tuple[str, ...]
    visual_consequences: Tuple[str, ...]
    prohibited_interpretations: Tuple[str, ...]
    authority_status: str = GRAMMAR_AUTHORITY


@dataclass(frozen=True)
class ShipyardRealizationPacket:
    version: str
    yard_id: str
    source_design_candidate_id: str
    source_governed_package_hash: str
    source_semantic_package_hash: str
    source_glb_sha256: str
    grammar_hash: str
    realization_instruction: str
    packet_hash: str
    authority_status: str = PACKET_AUTHORITY
    visual_realization_authoritative: bool = False
    may_backpropagate_engineering_claims: bool = False


def _grammar(yard_id, fabrication_context, structural_doctrine, module_doctrine, maintenance_doctrine, redundancy_doctrine, geometric_complexity_doctrine, visual_consequences):
    return ShipyardVisualGrammar(
        version=GRAMMAR_VERSION,
        yard_id=yard_id,
        fabrication_context=fabrication_context,
        structural_doctrine=structural_doctrine,
        module_doctrine=module_doctrine,
        maintenance_doctrine=maintenance_doctrine,
        redundancy_doctrine=redundancy_doctrine,
        geometric_complexity_doctrine=geometric_complexity_doctrine,
        visual_consequences=visual_consequences,
        prohibited_interpretations=(
            "Do not alter the governed placement or envelope of constrained engineering objects.",
            "Do not reinterpret a semantic component as another subsystem because its primitive shape is ambiguous.",
            "Do not imply that generated structural members are qualified load paths.",
            "Do not invent propulsion, radiator, docking, shielding, or pressure-volume capabilities absent from the engineering state.",
            "Do not treat generated material, pipework, cabling, surface detail, or topology as engineering evidence.",
        ),
    )


GRAMMARS: Dict[str, ShipyardVisualGrammar] = {
    "ASTERIA": _grammar("ASTERIA", ("high robotic fabrication freedom", "additive and computationally planned assembly", "high tolerance for part-specific geometry"), ("minimum unnecessary structural material", "branching topology-like transitions where unconstrained", "integrated support around major envelopes"), ("modules subordinate to whole-vehicle optimization where service constraints permit",), ("robotic inspection and local repair preferred over broad human access", "access preserved where explicitly required"), ("redundancy concentrated in critical paths rather than uniform duplicated framing",), ("variable cross-sections and non-stock geometry acceptable", "geometric complexity is cheap when it reduces mass or integration burden"), ("branching structural language", "smooth structural transitions", "integrated tank/equipment cradles", "visually sparse minimum-mass framing")),
    "KELDRIN": _grammar("KELDRIN", ("standardized industrial fabrication", "repeatable stock sections and modules", "rugged robotic and human assembly"), ("rectilinear trusses", "standard section families", "clear load-transfer hierarchy"), ("replaceable standardized equipment modules", "interfaces remain visually explicit"), ("human and robotic service access prioritized", "machinery should be easy to reach and isolate"), ("selective duplication of critical members and utilities",), ("low geometric novelty preferred", "repeatability and field comprehension outweigh minimum-part geometry"), ("rectilinear framing", "obvious modular bays", "visible service corridors", "rugged industrial construction")),
    "SHIKARI": _grammar("SHIKARI", ("high-precision integrated fabrication", "advanced composite and consolidated assemblies", "tight dimensional control"), ("few large structural elements", "load-bearing and enclosure functions consolidated where admissible", "mass/performance optimized integration"), ("module count minimized", "interfaces consolidated and protected"), ("planned replacement at major assembly level", "routine access accepted only where lifecycle analysis requires it"), ("redundancy implemented through integrated alternate paths rather than visible duplicate framing",), ("complex integrated forms acceptable when they reduce part count or mass", "precision is expensive but deliberately purchased"), ("highly consolidated structure", "low visible part count", "integrated composite expression", "tight clean transitions around engineering volumes")),
    "TASCHEN": _grammar("TASCHEN", ("expeditionary construction and repair", "mixed robotic/human intervention", "parts must tolerate imperfect field conditions"), ("multiple accessible load paths", "local reinforcement easy to inspect and replace", "avoid single elegant elements whose failure immobilizes the vehicle"), ("replaceable modules with generous interfaces", "local improvisation and substitution anticipated"), ("human access, remote-manipulator access, and in-situ repair strongly favored", "machinery remains exposed enough for diagnosis"), ("visible structural and utility redundancy", "fault isolation valued over minimum part count"), ("moderate complexity allowed only when repairability remains obvious", "robust interfaces preferred to delicate integration"), ("redundant framing", "accessible machinery", "modular replacement zones", "expedition/field-repair appearance")),
}


def validate_grammar(grammar: ShipyardVisualGrammar) -> None:
    if grammar.version != GRAMMAR_VERSION or grammar.authority_status != GRAMMAR_AUTHORITY:
        raise ShipyardVisualGrammarError("grammar authority/version mismatch")
    if grammar.yard_id not in GRAMMARS:
        raise ShipyardVisualGrammarError("unknown yard grammar")
    for field in (grammar.fabrication_context, grammar.structural_doctrine, grammar.module_doctrine, grammar.maintenance_doctrine, grammar.redundancy_doctrine, grammar.geometric_complexity_doctrine, grammar.visual_consequences, grammar.prohibited_interpretations):
        if not field or any(not isinstance(v, str) or not v.strip() for v in field):
            raise ShipyardVisualGrammarError("grammar fields must be non-empty strings")


def grammar_hash(grammar: ShipyardVisualGrammar) -> str:
    validate_grammar(grammar)
    return _sha(asdict(grammar))


def _instruction(grammar: ShipyardVisualGrammar) -> str:
    sections = (("FABRICATION CONTEXT", grammar.fabrication_context), ("STRUCTURAL DOCTRINE", grammar.structural_doctrine), ("MODULE DOCTRINE", grammar.module_doctrine), ("MAINTENANCE DOCTRINE", grammar.maintenance_doctrine), ("REDUNDANCY DOCTRINE", grammar.redundancy_doctrine), ("GEOMETRIC COMPLEXITY", grammar.geometric_complexity_doctrine), ("ALLOWED VISUAL CONSEQUENCES", grammar.visual_consequences), ("PROHIBITED INTERPRETATIONS", grammar.prohibited_interpretations))
    lines = [f"LOOM SHIPYARD REALIZATION — {grammar.yard_id}", "Treat the supplied semantic GLB/reference views as the spatial engineering constraint.", "Preserve constrained component identity, placement, scale, and envelope.", "Add only plausible visual elaboration in freedoms not fixed by the engineering model.", "Generated detail is visualization, not engineering evidence."]
    for title, values in sections:
        lines.append(title + ":")
        lines.extend("- " + value for value in values)
    return "\n".join(lines)


def build_realization_packet(glb_manifest: dict, yard_id: str) -> ShipyardRealizationPacket:
    if yard_id not in GRAMMARS:
        raise ShipyardVisualGrammarError(f"unknown yard_id {yard_id}")
    grammar = GRAMMARS[yard_id]
    validate_grammar(grammar)
    required = ("source_design_candidate_id", "source_governed_package_hash", "source_semantic_package_hash", "glb_sha256")
    if any(not isinstance(glb_manifest.get(k), str) or not glb_manifest[k] for k in required):
        raise ShipyardVisualGrammarError("GLB manifest missing required provenance")
    if glb_manifest.get("flight_dynamics_authority") or glb_manifest.get("canon_changed") or glb_manifest.get("production_shipclasses_changed"):
        raise ShipyardVisualGrammarError("realization packet refuses authority-escalated GLB")
    provisional = ShipyardRealizationPacket(version=GRAMMAR_VERSION, yard_id=yard_id, source_design_candidate_id=glb_manifest["source_design_candidate_id"], source_governed_package_hash=glb_manifest["source_governed_package_hash"], source_semantic_package_hash=glb_manifest["source_semantic_package_hash"], source_glb_sha256=glb_manifest["glb_sha256"], grammar_hash=grammar_hash(grammar), realization_instruction=_instruction(grammar), packet_hash="")
    payload = asdict(provisional)
    payload["packet_hash"] = ""
    return ShipyardRealizationPacket(**{**payload, "packet_hash": _sha(payload)})


def canonical_packet_json(packet: ShipyardRealizationPacket) -> str:
    if packet.authority_status != PACKET_AUTHORITY or packet.visual_realization_authoritative or packet.may_backpropagate_engineering_claims:
        raise ShipyardVisualGrammarError("realization packet authority escalation")
    return json.dumps(asdict(packet), sort_keys=True, separators=(",", ":"), allow_nan=False)
