"""Gravity-aware shadow propagation for LOOM Navigation Physics v2 qualification.

This module does not replace NAV-V1-A and does not alter campaign or route
authority. It replays the ordinary-space kinematic control history authored by
Sequence-B while adding a caller-supplied time-varying gravity field, then
reports divergence from the frozen V1 trajectory.

The intended qualification question is deliberately narrow:
    "If the accepted V1 ordinary-space control history were flown in the
     accepted gravitational field, how far would the vehicle diverge?"

Retargeting, guidance optimization, gravity assists, remass re-optimization and
route promotion are later stages. This module is a deterministic comparison
instrument only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import math
from typing import Any, Callable, Iterable, Mapping, Sequence

from loom.spatial.gravity import GravityEvaluation


class GravityShadowError(RuntimeError):
    pass


def _dt(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        out = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise GravityShadowError(f"invalid epoch: {value!r}") from exc
    if out.tzinfo is None:
        raise GravityShadowError("epoch must include timezone")
    return out.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _vec3(value: Sequence[float], name: str) -> tuple[float, float, float]:
    try:
        out = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise GravityShadowError(f"{name} must contain three numeric values") from exc
    if len(out) != 3 or not all(math.isfinite(v) for v in out):
        raise GravityShadowError(f"{name} must contain exactly three finite values")
    return out  # type: ignore[return-value]


def _add(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(a: tuple[float, float, float], s: float) -> tuple[float, float, float]:
    return (a[0] * s, a[1] * s, a[2] * s)


def _norm(a: tuple[float, float, float]) -> float:
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


@dataclass(frozen=True)
class OrdinaryTrajectorySample:
    epoch_utc: str
    position_km: tuple[float, float, float]
    velocity_km_s: tuple[float, float, float]
    sample_index: int | None = None
    phase_code: Any = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _dt(self.epoch_utc)
        object.__setattr__(self, "position_km", _vec3(self.position_km, "position_km"))
        object.__setattr__(self, "velocity_km_s", _vec3(self.velocity_km_s, "velocity_km_s"))
        object.__setattr__(self, "payload", dict(self.payload))


@dataclass(frozen=True)
class GravityShadowSample:
    epoch_utc: str
    reference_position_km: tuple[float, float, float]
    shadow_position_km: tuple[float, float, float]
    reference_velocity_km_s: tuple[float, float, float]
    shadow_velocity_km_s: tuple[float, float, float]
    position_error_km: float
    velocity_error_km_s: float
    gravity_magnitude_km_s2: float
    dominant_gravity_source: str | None = None


@dataclass(frozen=True)
class GravityShadowReport:
    model: str
    reference_authority: str
    start_epoch_utc: str
    end_epoch_utc: str
    sample_count: int
    integration_step_limit_s: float
    terminal_position_error_km: float
    terminal_velocity_error_km_s: float
    max_position_error_km: float
    max_velocity_error_km_s: float
    samples: tuple[GravityShadowSample, ...]
    qualification: Mapping[str, Any] = field(default_factory=dict)


GravityEvaluator = Callable[[tuple[float, float, float], str], GravityEvaluation]


def _same_state(a: OrdinaryTrajectorySample, b: OrdinaryTrajectorySample, *, abs_tol: float = 1e-9) -> bool:
    return (
        all(math.isclose(x, y, rel_tol=0.0, abs_tol=abs_tol) for x, y in zip(a.position_km, b.position_km))
        and all(math.isclose(x, y, rel_tol=0.0, abs_tol=abs_tol) for x, y in zip(a.velocity_km_s, b.velocity_km_s))
    )


def _normalize_duplicate_epochs(samples: list[OrdinaryTrajectorySample]) -> list[OrdinaryTrajectorySample]:
    """Collapse duplicate-epoch samples only when their ordinary state agrees.

    Sequence-B may emit a repeated terminal arrival sample at the same epoch.
    That is harmless for shadow integration if position and velocity are the
    same. Any same-epoch state disagreement remains ambiguous and fails closed.
    The later duplicate is retained so terminal sample provenance/index wins.
    """
    if not samples:
        return []
    normalized: list[OrdinaryTrajectorySample] = [samples[0]]
    for sample in samples[1:]:
        previous = normalized[-1]
        if _dt(sample.epoch_utc) != _dt(previous.epoch_utc):
            normalized.append(sample)
            continue
        if not _same_state(previous, sample):
            raise GravityShadowError(
                "duplicate ordinary-space sample epoch has conflicting position/velocity state"
            )
        normalized[-1] = sample
    return normalized


def ordinary_samples_from_route_trajectory(trajectory: Mapping[str, Any]) -> tuple[OrdinaryTrajectorySample, ...]:
    """Extract only Sequence-B samples with complete ordinary-space state.

    Metric/relational samples with no ordinary occupancy are ignored. No position
    or velocity is inferred for them. Exact duplicate-epoch ordinary states are
    collapsed; conflicting duplicate epochs are rejected.
    """
    rows = trajectory.get("samples")
    if not isinstance(rows, (list, tuple)):
        raise GravityShadowError("trajectory.samples is required")
    out: list[OrdinaryTrajectorySample] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        epoch = row.get("epoch_utc")
        xyz = (row.get("ordinary_pos_x_km"), row.get("ordinary_pos_y_km"), row.get("ordinary_pos_z_km"))
        vel = (row.get("ordinary_vel_x_km_s"), row.get("ordinary_vel_y_km_s"), row.get("ordinary_vel_z_km_s"))
        if epoch is None or any(v is None for v in xyz) or any(v is None for v in vel):
            continue
        out.append(OrdinaryTrajectorySample(
            epoch_utc=str(epoch),
            position_km=_vec3(xyz, "ordinary position"),
            velocity_km_s=_vec3(vel, "ordinary velocity"),
            sample_index=int(row["sample_index"]) if row.get("sample_index") is not None else None,
            phase_code=row.get("phase_code"),
            payload={"ordinary_accel_g": row.get("ordinary_accel_g"), "torch_state_code": row.get("torch_state_code")},
        ))
    out.sort(key=lambda s: (_dt(s.epoch_utc), s.sample_index if s.sample_index is not None else -1))
    out = _normalize_duplicate_epochs(out)
    if len(out) < 2:
        raise GravityShadowError("at least two complete ordinary-space samples are required")
    for a, b in zip(out, out[1:]):
        if _dt(b.epoch_utc) <= _dt(a.epoch_utc):
            raise GravityShadowError("ordinary-space sample epochs must be strictly increasing")
    return tuple(out)


def _command_acceleration(a: OrdinaryTrajectorySample, b: OrdinaryTrajectorySample) -> tuple[float, float, float]:
    dt_s = (_dt(b.epoch_utc) - _dt(a.epoch_utc)).total_seconds()
    if dt_s <= 0.0:
        raise GravityShadowError("non-positive control interval")
    return _scale(_sub(b.velocity_km_s, a.velocity_km_s), 1.0 / dt_s)


def _rk4_step(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float],
    epoch: datetime,
    dt_s: float,
    commanded_accel: tuple[float, float, float],
    gravity: GravityEvaluator,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    def deriv(p: tuple[float, float, float], v: tuple[float, float, float], t: datetime):
        ge = gravity(p, _iso(t))
        return v, _add(commanded_accel, ge.total_acceleration_km_s2)

    k1p, k1v = deriv(position, velocity, epoch)
    k2p, k2v = deriv(_add(position, _scale(k1p, 0.5 * dt_s)), _add(velocity, _scale(k1v, 0.5 * dt_s)), epoch + timedelta(seconds=0.5 * dt_s))
    k3p, k3v = deriv(_add(position, _scale(k2p, 0.5 * dt_s)), _add(velocity, _scale(k2v, 0.5 * dt_s)), epoch + timedelta(seconds=0.5 * dt_s))
    k4p, k4v = deriv(_add(position, _scale(k3p, dt_s)), _add(velocity, _scale(k3v, dt_s)), epoch + timedelta(seconds=dt_s))
    weighted_p = _scale(_add(_add(k1p, _scale(k2p, 2.0)), _add(_scale(k3p, 2.0), k4p)), dt_s / 6.0)
    weighted_v = _scale(_add(_add(k1v, _scale(k2v, 2.0)), _add(_scale(k3v, 2.0), k4v)), dt_s / 6.0)
    return _add(position, weighted_p), _add(velocity, weighted_v)


def compare_gravity_shadow(
    reference_samples: Iterable[OrdinaryTrajectorySample],
    gravity: GravityEvaluator,
    *,
    max_step_s: float = 30.0,
    reference_authority: str = "PYTHON_AUTHORED_SEQUENCE_B",
) -> GravityShadowReport:
    """Replay V1 control acceleration with gravity and report divergence.

    Command acceleration is the interval-average vector required to reproduce
    each V1 velocity change in the gravity-free model. Within an interval it is
    held constant; gravity is evaluated at every RK4 substage using the shadow
    state and substage epoch.
    """
    samples = tuple(reference_samples)
    if len(samples) < 2:
        raise GravityShadowError("at least two reference samples are required")
    step_limit = float(max_step_s)
    if not math.isfinite(step_limit) or step_limit <= 0.0:
        raise GravityShadowError("max_step_s must be finite and positive")

    p = samples[0].position_km
    v = samples[0].velocity_km_s
    first_g = gravity(p, samples[0].epoch_utc)
    first_dom = first_g.contributions[0].entity_id if first_g.contributions else None
    out = [GravityShadowSample(
        epoch_utc=samples[0].epoch_utc,
        reference_position_km=samples[0].position_km,
        shadow_position_km=p,
        reference_velocity_km_s=samples[0].velocity_km_s,
        shadow_velocity_km_s=v,
        position_error_km=0.0,
        velocity_error_km_s=0.0,
        gravity_magnitude_km_s2=first_g.total_magnitude_km_s2,
        dominant_gravity_source=first_dom,
    )]

    for a, b in zip(samples, samples[1:]):
        start = _dt(a.epoch_utc)
        end = _dt(b.epoch_utc)
        interval = (end - start).total_seconds()
        commanded = _command_acceleration(a, b)
        n = max(1, int(math.ceil(interval / step_limit)))
        h = interval / n
        t = start
        for _ in range(n):
            p, v = _rk4_step(p, v, t, h, commanded, gravity)
            t += timedelta(seconds=h)
        ge = gravity(p, b.epoch_utc)
        pe = _norm(_sub(p, b.position_km))
        ve = _norm(_sub(v, b.velocity_km_s))
        dom = ge.contributions[0].entity_id if ge.contributions else None
        out.append(GravityShadowSample(
            epoch_utc=b.epoch_utc,
            reference_position_km=b.position_km,
            shadow_position_km=p,
            reference_velocity_km_s=b.velocity_km_s,
            shadow_velocity_km_s=v,
            position_error_km=pe,
            velocity_error_km_s=ve,
            gravity_magnitude_km_s2=ge.total_magnitude_km_s2,
            dominant_gravity_source=dom,
        ))

    terminal = out[-1]
    return GravityShadowReport(
        model="LOOM_NAV_PHYSICS_V2_GRAVITY_SHADOW_RK4",
        reference_authority=reference_authority,
        start_epoch_utc=samples[0].epoch_utc,
        end_epoch_utc=samples[-1].epoch_utc,
        sample_count=len(samples),
        integration_step_limit_s=step_limit,
        terminal_position_error_km=terminal.position_error_km,
        terminal_velocity_error_km_s=terminal.velocity_error_km_s,
        max_position_error_km=max(s.position_error_km for s in out),
        max_velocity_error_km_s=max(s.velocity_error_km_s for s in out),
        samples=tuple(out),
        qualification={
            "authority": "SHADOW_ONLY_NOT_ROUTE_AUTHORITY",
            "control_replay": "INTERVAL_AVERAGE_V1_VELOCITY_DELTA",
            "gravity": "CALLER_SUPPLIED_TIME_VARYING_FIELD",
            "integrator": "RK4",
            "retargeting": False,
            "guidance_optimization": False,
            "remass_reoptimization": False,
        },
    )
