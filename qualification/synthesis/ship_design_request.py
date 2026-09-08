from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from design_requirements import (
    LinearDerivationRule,
    RequirementsError,
    canonical_json,
    compile_requirements,
)
from ship_requirements import (
    ShipMissionRequest,
    direct_requirements_from_ship_request,
    doctrine_profile,
)


SHIP_DESIGN_REQUEST_SCHEMA = "LOOM_2226_SHIP_DESIGN_REQUEST"
SHIP_DESIGN_REQUEST_SCHEMA_VERSION = "0.1"


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RequirementsError(f"{label} must be an object")
    return value


def _sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, (list, tuple)):
        raise RequirementsError(f"{label} must be an array")
    return value


def compile_ship_design_request(payload: Mapping[str, Any]):
    schema = payload.get("schema")
    version = payload.get("schema_version")
    if schema != SHIP_DESIGN_REQUEST_SCHEMA or version != SHIP_DESIGN_REQUEST_SCHEMA_VERSION:
        raise RequirementsError(
            f"Unsupported ship request schema/version: {schema!r} {version!r}"
        )

    doctrine_data = _mapping(payload.get("ship_class"), "ship_class")
    doctrine = doctrine_profile(
        str(doctrine_data.get("id", "")),
        objective_priority=tuple(
            str(v) for v in _sequence(doctrine_data.get("objective_priority"), "ship_class.objective_priority")
        ),
        required_capabilities=tuple(
            str(v) for v in doctrine_data.get("required_capabilities", ())
        ),
        authority_status=str(doctrine_data.get("authority_status", "QUALIFICATION_ONLY")),
        provenance=str(doctrine_data.get("provenance", "SHIP_DESIGN_REQUEST")),
    )

    functional = _mapping(payload.get("functional_requirements"), "functional_requirements")
    allowed_fields = set(ShipMissionRequest.__dataclass_fields__)
    unknown = sorted(set(functional) - allowed_fields)
    if unknown:
        raise RequirementsError(f"Unknown functional requirement field(s): {', '.join(unknown)}")
    request = ShipMissionRequest(**dict(functional))
    direct = direct_requirements_from_ship_request(
        request,
        provenance=str(payload.get("requirements_provenance", "SHIP_DESIGN_REQUEST")),
    )

    rules = []
    for raw in payload.get("derivation_rules", ()):
        row = _mapping(raw, "derivation_rule")
        required = (
            "rule_id",
            "input_requirement_id",
            "output_requirement_id",
            "coefficient",
            "offset",
            "output_unit",
            "output_relation",
            "authority_status",
            "provenance",
        )
        missing = [key for key in required if key not in row]
        if missing:
            raise RequirementsError(
                f"Derivation rule missing field(s): {', '.join(missing)}"
            )
        rules.append(
            LinearDerivationRule(
                rule_id=str(row["rule_id"]),
                input_requirement_id=str(row["input_requirement_id"]),
                output_requirement_id=str(row["output_requirement_id"]),
                coefficient=float(row["coefficient"]),
                offset=float(row["offset"]),
                output_unit=str(row["output_unit"]),
                output_relation=str(row["output_relation"]),
                authority_status=str(row["authority_status"]),
                provenance=str(row["provenance"]),
            )
        )

    expected_outputs = tuple(
        str(v) for v in payload.get("expected_derived_requirements", ())
    )
    return compile_requirements(
        direct,
        doctrine=doctrine,
        rules=tuple(rules),
        expected_outputs=expected_outputs,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile a LOOM ship class + functional requirement request into canonical engineering requirements"
    )
    parser.add_argument("request_json", type=Path)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.request_json.read_text(encoding="utf-8"))
        compiled = compile_ship_design_request(_mapping(payload, "request root"))
        print(json.dumps(json.loads(canonical_json(compiled)), indent=2, sort_keys=True, allow_nan=False))
        return 0
    except Exception as exc:
        print("SHIP_DESIGN_REQUIREMENTS_COMPILATION = FAIL")
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
