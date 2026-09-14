#!/usr/bin/env python3
from __future__ import annotations

"""Typed authored runtime-configuration input for E1.

Three configuration states are scenario inputs. Domain membership is deliberately
not authorable here: it must be derived by a later governed certification step.
Unknown defaults preserve epistemic honesty until the scenario explicitly supplies
values.
"""

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

SCHEMA = "LOOM_E1_RUNTIME_CONFIGURATION_INPUT_V1"
CONFIGURATION_IDENTITY = "WAYFARER_REFERENCE_SCHEMATIC_V2_4A"


class LaunchAttachmentState(str, Enum):
    UNKNOWN = "UNKNOWN"
    DOCKED = "DOCKED"
    EXTRACTING = "EXTRACTING"
    ABSENT = "ABSENT"


class ExternalAttachmentState(str, Enum):
    UNKNOWN = "UNKNOWN"
    FREE = "FREE"
    APPROACH = "APPROACH"
    SOFT_CAPTURE = "SOFT_CAPTURE"
    HARD_DOCKED = "HARD_DOCKED"


class DeployableStructureState(str, Enum):
    UNKNOWN = "UNKNOWN"
    STOWED = "STOWED"
    DEPLOYING = "DEPLOYING"
    DEPLOYED = "DEPLOYED"


@dataclass(frozen=True)
class RuntimeConfigurationInput:
    configuration_identity: str = CONFIGURATION_IDENTITY
    launch_attachment_state: LaunchAttachmentState = LaunchAttachmentState.UNKNOWN
    external_attachment_state: ExternalAttachmentState = ExternalAttachmentState.UNKNOWN
    deployable_structure_state: DeployableStructureState = DeployableStructureState.UNKNOWN

    def to_evidence(self) -> dict[str, Any]:
        authored = asdict(self)
        authored.pop("configuration_identity")
        authored = {
            name: value.value if isinstance(value, Enum) else value
            for name, value in authored.items()
        }
        missing = sorted(name for name, value in authored.items() if value == "UNKNOWN")
        return {
            "schema": SCHEMA,
            "status": "PASS",
            "configuration_identity": self.configuration_identity,
            "authored_state": authored,
            "derived_state": {"domain_membership_state": "UNKNOWN"},
            "missing_authored_scenario_inputs": missing,
            "disposition": "AUTHORED_RUNTIME_INPUT_PRESENT" if not missing else "RUNTIME_INPUT_INCOMPLETE",
            "policy": {
                "unknown_default_is_governed": True,
                "infer_unknown_values": False,
                "domain_membership_is_derived_only": True,
                "manual_domain_membership_override_allowed": False,
                "configuration_identity_implies_domain_membership": False,
            },
            "authority": {
                "certifies_runtime_input_contract": True,
                "certifies_domain_membership": False,
                "certifies_domain_geometry": False,
                "certifies_domain_size": False,
                "certifies_lattice_coherence": False,
                "certifies_overall_ga": False,
                "campaign_state_mutation": "ZERO",
                "runtime_policy_mutation": "ZERO",
                "llm_calculation_authority": "ZERO",
            },
        }


def build_default_e1_runtime_configuration() -> RuntimeConfigurationInput:
    return RuntimeConfigurationInput()


def main() -> int:
    result = build_default_e1_runtime_configuration().to_evidence()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=runtime_configuration_input")
    print(f"QUALIFICATION_DISPOSITION={result['disposition']}")
    missing = ",".join(result["missing_authored_scenario_inputs"]) or "NONE"
    print(f"QUALIFICATION_MISSING_REQUIRED_EVIDENCE={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
