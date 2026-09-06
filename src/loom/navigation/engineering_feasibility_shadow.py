"""D2i engineering feasibility shadow for gravity-aware Navigator guidance.

D2i remains non-authoritative. It consumes the already-computed D2h guidance
shadow plus the accepted NAV-V1-A terminal-burn engineering payload and asks a
narrow engineering question: does the sampled guidance correction fit inside the
selected torch mode's thrust-magnitude envelope, and what remass/vectoring demand
would that imply?

The baseline thrust direction is the NAV-V1-A terminal burn ``dv_hat`` and the
baseline thrust magnitude at each qualified ordinary sample comes from the
Sequence-B ``ordinary_accel_g`` telemetry. D2i adds a reconstructed D2h guidance
correction vector at those same sample epochs. It does not invent a certified
thrust-vector/gimbal envelope or thermal margin: those remain explicit OPEN
qualification items.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any, Mapping, Sequence


D2I_ENGINEERING_FEASIBILITY_CONTRACT = "LOOM_NAV_PHYSICS_V2_D2I_ENGINEERING_FEASIBILITY_SHADOW_V1"
G0_KM_S2 = 0.00980665


class EngineeringFeasibilityError(RuntimeError):
    pass


def _dt(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        out = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise EngineeringFeasibilityError(f"invalid epoch: {value!r}") from exc
    if out.tzinfo is None:
        raise EngineeringFeasibilityError("epoch must include timezone")
    return out.astimezone(timezone.utc)


def _vec3(value: Sequence[Any], name: str) -> tuple[float, float, float]:
    try:
        out = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise EngineeringFeasibilityError(f"{name} must contain three numeric values") from exc
    if len(out) != 3 or not all(math.isfinite(v) for v in out):
        raise EngineeringFeasibilityError(f"{name} must contain exactly three finite values")
    return out  # type: ignore[return-value]


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _norm(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _unit(a, name: str):
    n = _norm(a)
    if n <= 0.0:
        raise EngineeringFeasibilityError(f"{name} must be non-zero")
    return _scale(a, 1.0 / n)


def _limit(a, limit: float):
    n = _norm(a)
    if n <= limit or n == 0.0:
        return a
    return _scale(a, limit / n)


def _angle_deg(a, b) -> float:
    na = _norm(a)
    nb = _norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    c = max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))
    return math.degrees(math.acos(c))


def _terminal_burn(route_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    leg = route_payload.get("leg")
    if isinstance(leg, Mapping) and isinstance(leg.get("terminal_burn"), Mapping):
        return leg["terminal_burn"]
    if isinstance(route_payload.get("terminal_burn"), Mapping):
        return route_payload["terminal_burn"]
    raise EngineeringFeasibilityError("route payload has no terminal_burn engineering block")


def _required_number(mapping: Mapping[str, Any], key: str) -> float:
    value = mapping.get(key)
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise EngineeringFeasibilityError(f"terminal_burn.{key} is required") from exc
    if not math.isfinite(out) or out <= 0.0:
        raise EngineeringFeasibilityError(f"terminal_burn.{key} must be finite and positive")
    return out


def _trajectory_rows_by_epoch(trajectory: Mapping[str, Any]) -> dict[datetime, Mapping[str, Any]]:
    rows = trajectory.get("samples")
    if not isinstance(rows, (list, tuple)):
        raise EngineeringFeasibilityError("trajectory.samples is required")
    out: dict[datetime, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping) or row.get("epoch_utc") is None:
            continue
        if row.get("ordinary_pos_x_km") is None:
            continue
        key = _dt(str(row["epoch_utc"]))
        prev = out.get(key)
        if prev is None or float(row.get("sample_index", -1)) >= float(prev.get("sample_index", -1)):
            out[key] = row
    return out


def _guidance_correction_vector(
    sample: Mapping[str, Any],
    final_epoch: datetime,
    limit: float,
) -> tuple[float, float, float]:
    epoch = _dt(str(sample["epoch_utc"]))
    remaining = (final_epoch - epoch).total_seconds()
    if remaining <= 0.0:
        return (0.0, 0.0, 0.0)
    rp = _vec3(sample["reference_position_km"], "reference_position_km")
    sp = _vec3(sample["shadow_position_km"], "shadow_position_km")
    rv = _vec3(sample["reference_velocity_km_s"], "reference_velocity_km_s")
    sv = _vec3(sample["shadow_velocity_km_s"], "shadow_velocity_km_s")
    ep = _sub(sp, rp)
    ev = _sub(sv, rv)
    raw = _add(_scale(ep, -6.0 / (remaining * remaining)), _scale(ev, -4.0 / remaining))
    return _limit(raw, limit)


def evaluate_engineering_feasibility_shadow(
    trajectory: Mapping[str, Any],
    route_payload: Mapping[str, Any],
    guidance_shadow: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate sampled D2h correction demand against NAV-V1-A engineering data.

    This is deliberately a qualification shadow, not a route solver. A PASS is
    not emitted because certified vectoring/gimbal and numeric thermal envelopes
    are not present in the current NAV-V1-A payload.
    """
    report = guidance_shadow.get("report")
    if not isinstance(report, Mapping):
        raise EngineeringFeasibilityError("guidance shadow report is required")
    guidance_samples = report.get("samples")
    if not isinstance(guidance_samples, (list, tuple)) or len(guidance_samples) < 2:
        raise EngineeringFeasibilityError("guidance shadow requires at least two samples")

    burn = _terminal_burn(route_payload)
    thrust_n = burn.get("thrust_N")
    if thrust_n is None and burn.get("thrust_MN") is not None:
        thrust_n = float(burn["thrust_MN"]) * 1e6
    try:
        thrust_n = float(thrust_n)
    except (TypeError, ValueError) as exc:
        raise EngineeringFeasibilityError("terminal_burn thrust is required") from exc
    if not math.isfinite(thrust_n) or thrust_n <= 0.0:
        raise EngineeringFeasibilityError("terminal_burn thrust must be finite and positive")
    ve_km_s = _required_number(burn, "ve_km_s")
    baseline_mdot = _required_number(burn, "mdot_kg_s")
    dv_hat = _unit(_vec3(burn.get("dv_hat"), "terminal_burn.dv_hat"), "terminal_burn.dv_hat")

    limit = float(report.get("guidance_accel_limit_km_s2", 0.0))
    if not math.isfinite(limit) or limit <= 0.0:
        raise EngineeringFeasibilityError("guidance acceleration limit is required")
    final_epoch = _dt(str(guidance_samples[-1]["epoch_utc"]))
    raw_rows = _trajectory_rows_by_epoch(trajectory)

    samples_out: list[dict[str, Any]] = []
    previous_corr = (0.0, 0.0, 0.0)
    max_reconstructed_correction = 0.0
    for index, sample in enumerate(guidance_samples):
        if not isinstance(sample, Mapping):
            raise EngineeringFeasibilityError("guidance sample must be a mapping")
        epoch = _dt(str(sample["epoch_utc"]))
        row = raw_rows.get(epoch)
        if row is None:
            raise EngineeringFeasibilityError(f"no Sequence-B ordinary row for guidance epoch {sample['epoch_utc']}")
        try:
            wet_mass_t = float(row["wet_mass_t"])
            ordinary_accel_g = float(row["ordinary_accel_g"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EngineeringFeasibilityError("Sequence-B wet_mass_t and ordinary_accel_g are required") from exc
        if wet_mass_t <= 0.0 or ordinary_accel_g < 0.0:
            raise EngineeringFeasibilityError("invalid Sequence-B mass/acceleration telemetry")

        corr = _guidance_correction_vector(sample, final_epoch, limit)
        if index == len(guidance_samples) - 1:
            terminal_corr_mag = float(sample.get("guidance_correction_km_s2", 0.0) or 0.0)
            if terminal_corr_mag > 0.0 and _norm(previous_corr) > 0.0:
                corr = _scale(_unit(previous_corr, "previous guidance correction"), terminal_corr_mag)
        if _norm(corr) > 0.0:
            previous_corr = corr
        max_reconstructed_correction = max(max_reconstructed_correction, _norm(corr))

        baseline_accel = _scale(dv_hat, ordinary_accel_g * G0_KM_S2)
        required_accel = _add(baseline_accel, corr)
        required_mag = _norm(required_accel)
        available_accel = thrust_n / (wet_mass_t * 1e6) / 1000.0
        margin = available_accel - required_mag
        required_thrust_n = required_mag * wet_mass_t * 1e6 * 1000.0
        required_mdot = required_thrust_n / (ve_km_s * 1000.0)
        samples_out.append({
            "epoch_utc": str(sample["epoch_utc"]),
            "sample_index": row.get("sample_index"),
            "wet_mass_t": wet_mass_t,
            "reference_accel_g": ordinary_accel_g,
            "reference_thrust_accel_vector_km_s2": baseline_accel,
            "guidance_correction_vector_km_s2": corr,
            "guidance_correction_km_s2": _norm(corr),
            "required_thrust_accel_vector_km_s2": required_accel,
            "required_thrust_accel_km_s2": required_mag,
            "available_thrust_accel_km_s2": available_accel,
            "thrust_accel_margin_km_s2": margin,
            "required_thrust_N": required_thrust_n,
            "required_mdot_kg_s": required_mdot,
            "steering_angle_deg_from_nav_v1_burn_axis": _angle_deg(baseline_accel, required_accel),
            "within_sampled_thrust_magnitude_envelope": margin >= -1e-12,
        })

    required_remass_kg = 0.0
    baseline_interval_remass_kg = 0.0
    for a, b in zip(samples_out, samples_out[1:]):
        dt_s = (_dt(b["epoch_utc"]) - _dt(a["epoch_utc"])).total_seconds()
        required_remass_kg += 0.5 * (a["required_mdot_kg_s"] + b["required_mdot_kg_s"]) * dt_s
        baseline_interval_remass_kg += baseline_mdot * dt_s

    sampled_pass = all(row["within_sampled_thrust_magnitude_envelope"] for row in samples_out)
    min_margin = min(row["thrust_accel_margin_km_s2"] for row in samples_out)
    max_required = max(row["required_thrust_accel_km_s2"] for row in samples_out)
    max_steering = max(row["steering_angle_deg_from_nav_v1_burn_axis"] for row in samples_out)
    d2h_peak_corr = float(report.get("max_guidance_correction_km_s2", 0.0) or 0.0)
    max_reference = max(row["reference_accel_g"] * G0_KM_S2 for row in samples_out)
    min_available = min(row["available_thrust_accel_km_s2"] for row in samples_out)
    conservative_peak_upper = max_reference + d2h_peak_corr

    thermal_numeric_margin = burn.get("thermal_numeric_margin")
    thermal_status = "NUMERIC_MARGIN_AVAILABLE" if thermal_numeric_margin is not None else "OPEN_NO_NUMERIC_THERMAL_MARGIN"
    vectoring_status = "OPEN_NO_CERTIFIED_THRUST_VECTOR_OR_GIMBAL_ENVELOPE"
    if not sampled_pass:
        overall = "FAIL_SAMPLED_THRUST_MAGNITUDE"
    else:
        overall = "OPEN_VECTORING_AND_THERMAL_QUALIFICATION"

    return {
        "contract": D2I_ENGINEERING_FEASIBILITY_CONTRACT,
        "authority": "DIAGNOSTIC_ENGINEERING_SHADOW_ONLY_NOT_ROUTE_AUTHORITY",
        "status": overall,
        "torch_mode": route_payload.get("torch") or burn.get("torch_mode"),
        "thermal_posture": route_payload.get("thermal") or burn.get("thermal_posture"),
        "available_thrust_N": thrust_n,
        "exhaust_velocity_km_s": ve_km_s,
        "baseline_mdot_kg_s": baseline_mdot,
        "qualified_sample_count": len(samples_out),
        "sampled_thrust_magnitude_within_mode_envelope": sampled_pass,
        "minimum_sampled_thrust_accel_margin_km_s2": min_margin,
        "maximum_sampled_required_thrust_accel_km_s2": max_required,
        "maximum_sampled_steering_angle_deg": max_steering,
        "d2h_peak_guidance_correction_km_s2": d2h_peak_corr,
        "maximum_reconstructed_sample_guidance_correction_km_s2": max_reconstructed_correction,
        "between_sample_peak_correction_open": d2h_peak_corr > max_reconstructed_correction + 1e-12,
        "minimum_available_thrust_accel_km_s2": min_available,
        "conservative_peak_required_accel_upper_bound_km_s2": conservative_peak_upper,
        "conservative_peak_upper_bound_within_mode_envelope": conservative_peak_upper <= min_available + 1e-12,
        "estimated_required_remass_t_over_qualified_interval": required_remass_kg / 1000.0,
        "baseline_constant_mdot_remass_t_over_qualified_interval": baseline_interval_remass_kg / 1000.0,
        "estimated_remass_delta_t_over_qualified_interval": (required_remass_kg - baseline_interval_remass_kg) / 1000.0,
        "vectoring_qualification": vectoring_status,
        "thermal_qualification": thermal_status,
        "thermal_numeric_margin": thermal_numeric_margin,
        "samples": samples_out,
        "qualification": {
            "route_mutation": False,
            "campaign_mutation": False,
            "remass_reoptimization": False,
            "guidance_reoptimization": False,
            "reference_thrust_axis": "NAV_V1_A_TERMINAL_BURN_DV_HAT",
            "reference_acceleration_magnitude": "SEQUENCE_B_ORDINARY_ACCEL_G",
            "guidance_vector_reconstruction": "D2H_CUBIC_ERROR_LAW_AT_QUALIFIED_SAMPLE_EPOCHS",
            "terminal_guidance_vector_direction": "PREVIOUS_SAMPLE_DIRECTION_WITH_D2H_TERMINAL_MAGNITUDE",
            "remass_estimate": "FIXED_EXHAUST_VE_TRAPEZOIDAL_REQUIRED_THRUST_MAGNITUDE",
            "between_sample_vector_envelope": "OPEN_D2H_REPORT_ONLY_EXPOSES_PEAK_MAGNITUDE",
            "certified_vectoring_envelope": False,
            "certified_numeric_thermal_margin": thermal_numeric_margin is not None,
        },
    }
