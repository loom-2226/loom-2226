"""Gravity-aware terminal retargeting shadow for LOOM Navigation Physics v2.

D2h is deliberately non-authoritative. It reuses the accepted Sequence-B
ordinary-space reference trajectory as a feed-forward baseline, adds the live
caller-supplied gravity field, and applies a bounded terminal-state correction
that drives shadow position/velocity error toward zero at the final qualified
ordinary-space boundary.

The guidance law is a receding-horizon cubic terminal correction over the
remaining qualified time. For current reference-relative position error e_p and
velocity error e_v with remaining time T, the unconstrained correction is

    a_corr = -6 e_p / T^2 - 4 e_v / T

which is the initial acceleration of the cubic error trajectory satisfying
zero terminal position and velocity error in the gravity-free linearized error
system. The correction is recomputed at every RK4 substep and magnitude-limited.

This module does not mutate a route, campaign state, remass ledger, metric
segment, or Navigator authority. It is a qualification instrument for the next
stage of gravity-aware guidance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import math
from typing import Any, Callable, Iterable, Mapping

from loom.spatial.gravity import GravityEvaluation
from .gravity_shadow import GravityShadowError, OrdinaryTrajectorySample


D2H_GRAVITY_RETARGETING_CONTRACT = "LOOM_NAV_PHYSICS_V2_D2H_GRAVITY_RETARGETING_SHADOW_V1"


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


def _add(a: tuple[float,float,float], b: tuple[float,float,float]) -> tuple[float,float,float]:
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])


def _sub(a: tuple[float,float,float], b: tuple[float,float,float]) -> tuple[float,float,float]:
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])


def _scale(a: tuple[float,float,float], s: float) -> tuple[float,float,float]:
    return (a[0]*s, a[1]*s, a[2]*s)


def _norm(a: tuple[float,float,float]) -> float:
    return math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])


def _limit_magnitude(a: tuple[float,float,float], limit: float) -> tuple[float,float,float]:
    mag = _norm(a)
    if mag <= limit or mag == 0.0:
        return a
    return _scale(a, limit/mag)


@dataclass(frozen=True)
class GuidanceShadowSample:
    epoch_utc: str
    reference_position_km: tuple[float,float,float]
    shadow_position_km: tuple[float,float,float]
    reference_velocity_km_s: tuple[float,float,float]
    shadow_velocity_km_s: tuple[float,float,float]
    position_error_km: float
    velocity_error_km_s: float
    guidance_correction_km_s2: float
    gravity_magnitude_km_s2: float
    dominant_gravity_source: str | None = None


@dataclass(frozen=True)
class GuidanceShadowReport:
    contract: str
    model: str
    reference_authority: str
    start_epoch_utc: str
    end_epoch_utc: str
    sample_count: int
    integration_step_limit_s: float
    guidance_accel_limit_km_s2: float
    terminal_position_error_km: float
    terminal_velocity_error_km_s: float
    max_position_error_km: float
    max_velocity_error_km_s: float
    max_guidance_correction_km_s2: float
    guidance_correction_delta_v_km_s: float
    samples: tuple[GuidanceShadowSample,...]
    qualification: Mapping[str,Any] = field(default_factory=dict)


GravityEvaluator = Callable[[tuple[float,float,float], str], GravityEvaluation]


def _reference_state_between(
    a: OrdinaryTrajectorySample,
    b: OrdinaryTrajectorySample,
    epoch: datetime,
) -> tuple[tuple[float,float,float], tuple[float,float,float]]:
    start = _dt(a.epoch_utc)
    end = _dt(b.epoch_utc)
    span = (end-start).total_seconds()
    if span <= 0.0:
        raise GravityShadowError("non-positive reference interval")
    u = min(1.0, max(0.0, (epoch-start).total_seconds()/span))
    # Cubic Hermite interpolation keeps both reference endpoint states exact.
    u2 = u*u
    u3 = u2*u
    h00 = 2*u3 - 3*u2 + 1
    h10 = u3 - 2*u2 + u
    h01 = -2*u3 + 3*u2
    h11 = u3 - u2
    p = tuple(
        h00*a.position_km[i] + h10*span*a.velocity_km_s[i]
        + h01*b.position_km[i] + h11*span*b.velocity_km_s[i]
        for i in range(3)
    )
    dh00 = 6*u2 - 6*u
    dh10 = 3*u2 - 4*u + 1
    dh01 = -6*u2 + 6*u
    dh11 = 3*u2 - 2*u
    v = tuple(
        (dh00*a.position_km[i] + dh10*span*a.velocity_km_s[i]
         + dh01*b.position_km[i] + dh11*span*b.velocity_km_s[i]) / span
        for i in range(3)
    )
    return p, v


def _feedforward_accel(
    a: OrdinaryTrajectorySample,
    b: OrdinaryTrajectorySample,
    epoch: datetime,
) -> tuple[float,float,float]:
    """Second derivative of the same cubic Hermite reference interpolation."""
    start = _dt(a.epoch_utc)
    end = _dt(b.epoch_utc)
    span = (end-start).total_seconds()
    if span <= 0.0:
        raise GravityShadowError("non-positive reference interval")
    u = min(1.0, max(0.0, (epoch-start).total_seconds()/span))
    d2h00 = 12*u - 6
    d2h10 = 6*u - 4
    d2h01 = -12*u + 6
    d2h11 = 6*u - 2
    return tuple(
        (d2h00*a.position_km[i] + d2h10*span*a.velocity_km_s[i]
         + d2h01*b.position_km[i] + d2h11*span*b.velocity_km_s[i]) / (span*span)
        for i in range(3)
    )


def compare_gravity_guidance_shadow(
    reference_samples: Iterable[OrdinaryTrajectorySample],
    gravity: GravityEvaluator,
    *,
    max_step_s: float = 10.0,
    guidance_accel_limit_km_s2: float = 0.02,
    reference_authority: str = "PYTHON_AUTHORED_SEQUENCE_B",
) -> GuidanceShadowReport:
    """Propagate a bounded gravity-aware terminal retargeting shadow.

    The reference path remains the accepted Sequence-B ordinary trajectory. A
    Hermite feed-forward acceleration exactly reproduces each reference interval
    in the zero-gravity limit. A receding-horizon cubic correction acts on
    reference-relative error and is clipped to ``guidance_accel_limit_km_s2``.
    """
    samples = tuple(reference_samples)
    if len(samples) < 2:
        raise GravityShadowError("at least two reference samples are required")
    for a,b in zip(samples,samples[1:]):
        if _dt(b.epoch_utc) <= _dt(a.epoch_utc):
            raise GravityShadowError("reference sample epochs must be strictly increasing")
    step_limit = float(max_step_s)
    accel_limit = float(guidance_accel_limit_km_s2)
    if not math.isfinite(step_limit) or step_limit <= 0.0:
        raise GravityShadowError("max_step_s must be finite and positive")
    if not math.isfinite(accel_limit) or accel_limit <= 0.0:
        raise GravityShadowError("guidance_accel_limit_km_s2 must be finite and positive")

    final_epoch = _dt(samples[-1].epoch_utc)
    p = samples[0].position_km
    v = samples[0].velocity_km_s
    correction_dv = 0.0
    max_correction = 0.0

    first_g = gravity(p,samples[0].epoch_utc)
    first_dom = first_g.contributions[0].entity_id if first_g.contributions else None
    out: list[GuidanceShadowSample] = [GuidanceShadowSample(
        epoch_utc=samples[0].epoch_utc,
        reference_position_km=samples[0].position_km,
        shadow_position_km=p,
        reference_velocity_km_s=samples[0].velocity_km_s,
        shadow_velocity_km_s=v,
        position_error_km=0.0,
        velocity_error_km_s=0.0,
        guidance_correction_km_s2=0.0,
        gravity_magnitude_km_s2=first_g.total_magnitude_km_s2,
        dominant_gravity_source=first_dom,
    )]

    for a,b in zip(samples,samples[1:]):
        start = _dt(a.epoch_utc)
        end = _dt(b.epoch_utc)
        interval = (end-start).total_seconds()
        n = max(1,int(math.ceil(interval/step_limit)))
        h = interval/n
        t = start
        last_corr_mag = 0.0
        for _ in range(n):
            def deriv(
                pp: tuple[float,float,float],
                vv: tuple[float,float,float],
                tt: datetime,
            ) -> tuple[tuple[float,float,float], tuple[float,float,float], float]:
                ref_p,ref_v = _reference_state_between(a,b,tt)
                feed = _feedforward_accel(a,b,tt)
                remaining = max(h, (final_epoch-tt).total_seconds())
                ep = _sub(pp,ref_p)
                ev = _sub(vv,ref_v)
                raw_corr = _add(_scale(ep,-6.0/(remaining*remaining)), _scale(ev,-4.0/remaining))
                corr = _limit_magnitude(raw_corr,accel_limit)
                ge = gravity(pp,_iso(tt))
                return vv, _add(_add(feed,corr),ge.total_acceleration_km_s2), _norm(corr)

            k1p,k1v,c1 = deriv(p,v,t)
            k2p,k2v,c2 = deriv(_add(p,_scale(k1p,0.5*h)),_add(v,_scale(k1v,0.5*h)),t+timedelta(seconds=0.5*h))
            k3p,k3v,c3 = deriv(_add(p,_scale(k2p,0.5*h)),_add(v,_scale(k2v,0.5*h)),t+timedelta(seconds=0.5*h))
            k4p,k4v,c4 = deriv(_add(p,_scale(k3p,h)),_add(v,_scale(k3v,h)),t+timedelta(seconds=h))
            p = _add(p,_scale(_add(_add(k1p,_scale(k2p,2.0)),_add(_scale(k3p,2.0),k4p)),h/6.0))
            v = _add(v,_scale(_add(_add(k1v,_scale(k2v,2.0)),_add(_scale(k3v,2.0),k4v)),h/6.0))
            corr_mag = (c1+2*c2+2*c3+c4)/6.0
            correction_dv += corr_mag*h
            max_correction = max(max_correction,c1,c2,c3,c4)
            last_corr_mag = c4
            t += timedelta(seconds=h)

        ge = gravity(p,b.epoch_utc)
        pe = _norm(_sub(p,b.position_km))
        ve = _norm(_sub(v,b.velocity_km_s))
        dom = ge.contributions[0].entity_id if ge.contributions else None
        out.append(GuidanceShadowSample(
            epoch_utc=b.epoch_utc,
            reference_position_km=b.position_km,
            shadow_position_km=p,
            reference_velocity_km_s=b.velocity_km_s,
            shadow_velocity_km_s=v,
            position_error_km=pe,
            velocity_error_km_s=ve,
            guidance_correction_km_s2=last_corr_mag,
            gravity_magnitude_km_s2=ge.total_magnitude_km_s2,
            dominant_gravity_source=dom,
        ))

    terminal = out[-1]
    return GuidanceShadowReport(
        contract=D2H_GRAVITY_RETARGETING_CONTRACT,
        model="LOOM_NAV_PHYSICS_V2_GRAVITY_GUIDANCE_SHADOW_RK4_HERMITE_CUBIC_TERMINAL",
        reference_authority=reference_authority,
        start_epoch_utc=samples[0].epoch_utc,
        end_epoch_utc=samples[-1].epoch_utc,
        sample_count=len(samples),
        integration_step_limit_s=step_limit,
        guidance_accel_limit_km_s2=accel_limit,
        terminal_position_error_km=terminal.position_error_km,
        terminal_velocity_error_km_s=terminal.velocity_error_km_s,
        max_position_error_km=max(row.position_error_km for row in out),
        max_velocity_error_km_s=max(row.velocity_error_km_s for row in out),
        max_guidance_correction_km_s2=max_correction,
        guidance_correction_delta_v_km_s=correction_dv,
        samples=tuple(out),
        qualification={
            "authority":"SHADOW_ONLY_NOT_ROUTE_AUTHORITY",
            "reference_path":"PYTHON_AUTHORED_SEQUENCE_B_ORDINARY_SPACE",
            "reference_interpolation":"CUBIC_HERMITE_POSITION_VELOCITY_MATCHED",
            "guidance_law":"RECEDING_HORIZON_CUBIC_TERMINAL_ERROR_CORRECTION",
            "guidance_acceleration_bounded":True,
            "gravity":"CALLER_SUPPLIED_TIME_VARYING_FIELD",
            "integrator":"RK4",
            "route_mutation":False,
            "campaign_mutation":False,
            "remass_reoptimization":False,
            "metric_relational_segment_integrated":False,
        },
    )
