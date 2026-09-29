from __future__ import annotations

from typing import Any, Mapping


REQUIRED_TOP_LEVEL = (
    "identity",
    "mass_states",
    "torch",
    "endurance",
    "rcs",
    "attitude",
    "metric_interface",
    "power_thermal",
    "configuration_states",
    "failure_modes",
    "provenance",
    "qualification_status",
)

ALLOWED_DISPOSITIONS = {"BASELINE", "CANDIDATE", "QUALIFIED", "REJECTED", "OPEN"}


def validate_flight_standard(payload: Mapping[str, Any]) -> dict:
    missing = [key for key in REQUIRED_TOP_LEVEL if key not in payload]
    if missing:
        return {"pass": False, "errors": [f"missing top-level field: {key}" for key in missing]}

    errors: list[str] = []
    status = payload.get("qualification_status")
    if not isinstance(status, Mapping):
        errors.append("qualification_status must be a mapping")
        return {"pass": False, "errors": errors}

    gates = status.get("gates")
    if not isinstance(gates, Mapping):
        errors.append("qualification_status.gates must be a mapping")
        return {"pass": False, "errors": errors}

    for name, disposition in gates.items():
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"invalid disposition for {name}: {disposition}")

    final_label = status.get("overall")
    if final_label == "QUALIFIED" and any(v != "QUALIFIED" for v in gates.values()):
        errors.append("overall QUALIFIED requires every gate to be QUALIFIED")

    torch = payload.get("torch")
    if not isinstance(torch, Mapping):
        errors.append("torch must be a mapping")
    else:
        if torch.get("momentum_exchange") != "ORDINARY_REACTION_MASS":
            errors.append("torch momentum_exchange must remain ORDINARY_REACTION_MASS")

    metric = payload.get("metric_interface")
    if not isinstance(metric, Mapping):
        errors.append("metric_interface must be a mapping")
    else:
        if metric.get("ordinary_velocity_reset_allowed") is not False:
            errors.append("metric interface must prohibit free ordinary-velocity reset")

    return {"pass": not errors, "errors": errors}


def promotable(payload: Mapping[str, Any]) -> bool:
    result = validate_flight_standard(payload)
    if not result["pass"]:
        return False
    status = payload["qualification_status"]
    return status.get("overall") == "QUALIFIED" and all(
        value == "QUALIFIED" for value in status.get("gates", {}).values()
    )
