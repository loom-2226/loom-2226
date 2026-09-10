"""Interpolation helpers for dense, externally sourced ephemeris samples.

This module performs presentation/consumer-side state reconstruction between two
stored ephemeris anchors. It does not generate orbital dynamics. Cubic Hermite
uses position and velocity at both bracketing epochs so interpolated position and
velocity remain continuous. Interpolated states must retain explicit provenance
and must not be silently promoted to direct navigation-grade measurements.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Sequence

Vector3 = tuple[float, float, float]


def _epoch(value: str) -> datetime:
    probe = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(probe)
    if dt.tzinfo is None:
        raise ValueError("ephemeris epoch must include timezone")
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class EphemerisAnchor:
    epoch_utc: str
    position_km: Vector3
    velocity_km_s: Vector3

    def __post_init__(self) -> None:
        _epoch(self.epoch_utc)
        if len(self.position_km) != 3 or len(self.velocity_km_s) != 3:
            raise ValueError("ephemeris anchor vectors must have length 3")
        if not all(math.isfinite(float(v)) for v in (*self.position_km, *self.velocity_km_s)):
            raise ValueError("ephemeris anchor contains non-finite value")


def hermite_state(a: EphemerisAnchor, b: EphemerisAnchor, epoch_utc: str) -> tuple[Vector3, Vector3]:
    """Interpolate one state between two bracketing position+velocity anchors."""
    ta, tb, t = _epoch(a.epoch_utc), _epoch(b.epoch_utc), _epoch(epoch_utc)
    dt = (tb - ta).total_seconds()
    if dt <= 0.0:
        raise ValueError("ephemeris anchors must be strictly increasing")
    u = (t - ta).total_seconds() / dt
    if not 0.0 <= u <= 1.0:
        raise ValueError("requested epoch is outside anchor bracket")

    u2, u3 = u * u, u * u * u
    h00 = 2.0 * u3 - 3.0 * u2 + 1.0
    h10 = u3 - 2.0 * u2 + u
    h01 = -2.0 * u3 + 3.0 * u2
    h11 = u3 - u2

    dh00 = (6.0 * u2 - 6.0 * u) / dt
    dh10 = 3.0 * u2 - 4.0 * u + 1.0
    dh01 = (-6.0 * u2 + 6.0 * u) / dt
    dh11 = 3.0 * u2 - 2.0 * u

    p = tuple(
        h00 * a.position_km[i]
        + h10 * dt * a.velocity_km_s[i]
        + h01 * b.position_km[i]
        + h11 * dt * b.velocity_km_s[i]
        for i in range(3)
    )
    v = tuple(
        dh00 * a.position_km[i]
        + dh10 * a.velocity_km_s[i]
        + dh01 * b.position_km[i]
        + dh11 * b.velocity_km_s[i]
        for i in range(3)
    )
    return p, v


def validate_uniform_anchors(anchors: Sequence[EphemerisAnchor], *, expected_step_s: float | None = None) -> None:
    if len(anchors) < 2:
        raise ValueError("at least two ephemeris anchors are required")
    previous = _epoch(anchors[0].epoch_utc)
    for anchor in anchors[1:]:
        current = _epoch(anchor.epoch_utc)
        step = (current - previous).total_seconds()
        if step <= 0.0:
            raise ValueError("ephemeris anchors are not strictly increasing")
        if expected_step_s is not None and abs(step - expected_step_s) > 1e-6:
            raise ValueError(f"unexpected ephemeris step {step}s; expected {expected_step_s}s")
        previous = current
