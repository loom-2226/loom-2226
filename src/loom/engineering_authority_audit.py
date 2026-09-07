"""Read-only Stage F-PA-6 audit of vehicle/engineering authority.

This audit is intentionally documentary and structural. It reads governed
Git-tracked sources, records their content hash, and classifies which
simulator-facing engineering domains are presently locked, partially
represented, or still open. It does not change canon, physics, vehicle state,
route state, or campaign authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

ENGINEERING_AUTHORITY_AUDIT_VERSION = "LOOM_F_PA_ENGINEERING_AUTHORITY_AUDIT_V1"
ENGINEERING_CANON_REL = Path("canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md")
ENGINEERING_SHADOW_REL = Path("src/loom/navigation/engineering_feasibility_shadow.py")
ENGINEERING_CANON_GIT_BLOB = "618ee985f395414e0acbb583fa82e1b297745aba"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise RuntimeError(f"governed engineering source missing required marker: {label}")


def engineering_authority_audit(repo_root: Path | str) -> dict[str, Any]:
    root = Path(repo_root).expanduser().resolve()
    canon_path = root / ENGINEERING_CANON_REL
    shadow_path = root / ENGINEERING_SHADOW_REL
    if not canon_path.is_file():
        raise FileNotFoundError(canon_path)
    if not shadow_path.is_file():
        raise FileNotFoundError(shadow_path)

    canon_sha = _sha256(canon_path)
    canon = canon_path.read_text(encoding="utf-8")
    shadow = shadow_path.read_text(encoding="utf-8")

    required_canon = {
        "governing_status": "GOVERNING TECHNICAL / OPERATING CANON",
        "machine_constants": "CERTIFIED MACHINE CONSTANTS",
        "mass_remass": "MASS / REMASS STATE",
        "torch_regime": "**TORCH** — ordinary momentum exchange",
        "metric_regime": "**METRIC** — continuous subluminal relational/metric transport",
        "loom_regime": "**LOOM** — discontinuous interstellar relational re-embedding",
        "plant_mass": "Plant mass | **~88 t**",
        "mc_inventory": "Mc-299m | **10.0 kg**",
        "bank": "Shared bank | **2 GJ reversible field bank**",
        "cryoplant": "Cryoplant | **150 kW-class, 20 K**",
        "high_drive_reject": "High-drive reject | **900 K interface**",
        "frame_rule": "A local three-velocity without a frame is incomplete.",
        "conservation": "Finite ledgers must close ordinary, relational/wake, bank/reactor, radiation/heat and external-environment exchanges consistently.",
        "metric_not_spice": "JPL/SPICE does not supply it.",
    }
    for label, marker in required_canon.items():
        _require(canon, marker, label)

    required_shadow = {
        "non_authoritative": "D2i remains non-authoritative",
        "thrust_magnitude": "thrust-magnitude envelope",
        "sample_accel": "ordinary_accel_g",
        "no_vectoring": "thrust-vector/gimbal envelope",
        "thermal_open": "OPEN_NO_NUMERIC_THERMAL_MARGIN",
        "mdot": "mdot_kg_s",
        "wet_mass": "wet_mass_t",
        "remass_estimate": "estimated_required_remass_t_over_qualified_interval",
    }
    for label, marker in required_shadow.items():
        _require(shadow, marker, label)

    domains = {
        "PROPULSION_REGIME_SEPARATION": "GOVERNING_CANON",
        "RELATIONAL_PLANT_BASELINE": "GOVERNING_CANON",
        "MC_INVENTORY_AND_ARRAY_BASELINE": "GOVERNING_CANON",
        "METRIC_SPEED_RAMP_CARD": "GOVERNING_CANON",
        "METRIC_ENVIRONMENT_CERTIFICATION_ARCHITECTURE": "GOVERNING_CANON_WITH_OPEN_NUMERICAL_CLOSURE",
        "CONSERVATION_LEDGER_REQUIREMENT": "GOVERNING_CANON",
        "FRAME_DISCIPLINE": "GOVERNING_CANON",
        "TORCH_THRUST_MAGNITUDE_RUNTIME_CHECK": "DIAGNOSTIC_SHADOW_ONLY",
        "TORCH_MASS_FLOW_RUNTIME_ESTIMATE": "DIAGNOSTIC_SHADOW_ONLY",
        "VEHICLE_TRUE_6DOF_DYNAMICS": "MISSING",
        "CERTIFIED_THRUST_VECTOR_GIMBAL_ENVELOPE": "MISSING",
        "ATTITUDE_RCS_ACTUATOR_MODEL": "MISSING",
        "MASS_PROPERTIES_INERTIA_TENSOR_CG_EVOLUTION": "MISSING",
        "QUANTITATIVE_THERMAL_STATE_AND_MARGIN": "MISSING",
        "RUNTIME_POWER_BUS_AND_LOAD_STATE": "MISSING",
        "STRUCTURAL_LOAD_ENVELOPE_RUNTIME_MODEL": "MISSING",
        "SENSOR_SUITE_MEASUREMENT_MODELS": "MISSING",
        "COMMUNICATIONS_LINK_BUDGET_LATENCY_MODEL": "MISSING",
        "FAULT_DAMAGE_DEGRADATION_DYNAMICS": "MISSING",
    }

    return {
        "contract": ENGINEERING_AUTHORITY_AUDIT_VERSION,
        "engineering_canon": str(ENGINEERING_CANON_REL),
        "engineering_canon_git_blob": ENGINEERING_CANON_GIT_BLOB,
        "engineering_canon_content_sha256": canon_sha,
        "engineering_shadow": str(ENGINEERING_SHADOW_REL),
        "authority_domains": domains,
        "locked_or_governing_count": sum(1 for v in domains.values() if v.startswith("GOVERNING")),
        "diagnostic_shadow_count": sum(1 for v in domains.values() if v == "DIAGNOSTIC_SHADOW_ONLY"),
        "missing_runtime_domain_count": sum(1 for v in domains.values() if v == "MISSING"),
        "hard_boundaries": [
            "No retired flight result may be promoted to machine constant.",
            "Metric ordinary-state propagation is not supplied by JPL/SPICE.",
            "Diagnostic D2i thrust/remass calculations are not route or campaign authority.",
            "A sampled thrust-magnitude PASS does not establish certified vectoring or thermal closure.",
            "Missing 6DOF, attitude/RCS, power, thermal, sensor, communications and fault models remain missing.",
        ],
    }
