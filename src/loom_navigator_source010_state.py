"""Adapt Navigator SOURCE-010 route rows into shared celestial-state authority.

E1-bounded seam. Navigator remains ephemeris authority. This module only samples
already-acquired, axis-qualified route rows and exposes position/velocity in the
shared canonical frame for metric-domain hydration.

It does not acquire ephemeris, choose routes, choose domain radii, mutate campaign
state, or grant Mara/LLM numerical authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Mapping, Sequence

from src.loom_spatial_state_authority import CANONICAL_FRAME, SpatialState

AU_KM = 149_597_870.7
DAY_S = 86_400.0


class NavigatorSource010StateError(RuntimeError):
    pass


def _epoch(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise NavigatorSource010StateError(f"invalid epoch: {value!r}") from exc
    if dt.tzinfo is None:
        raise NavigatorSource010StateError("epoch must include timezone")
    return dt.astimezone(timezone.utc)


def _row(value: Sequence[float]) -> tuple[float, float, float, float, float, float, float]:
    try:
        out = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise NavigatorSource010StateError("Navigator route row must be numeric") from exc
    if len(out) < 7 or not all(math.isfinite(v) for v in out[:7]):
        raise NavigatorSource010StateError("Navigator route row must contain seven finite values")
    return out[:7]  # type: ignore[return-value]


def _hermite(
    p0: float,
    p1: float,
    v0_per_s: float,
    v1_per_s: float,
    u: float,
    dt_s: float,
) -> tuple[float, float]:
    u2 = u * u
    u3 = u2 * u
    h00 = 2 * u3 - 3 * u2 + 1
    h10 = u3 - 2 * u2 + u
    h01 = -2 * u3 + 3 * u2
    h11 = u3 - u2
    p = h00 * p0 + h10 * dt_s * v0_per_s + h01 * p1 + h11 * dt_s * v1_per_s

    dh00 = 6 * u2 - 6 * u
    dh10 = 3 * u2 - 4 * u + 1
    dh01 = -6 * u2 + 6 * u
    dh11 = 3 * u2 - 2 * u
    v = (dh00 * p0 + dh10 * dt_s * v0_per_s + dh01 * p1 + dh11 * dt_s * v1_per_s) / dt_s
    return p, v


class NavigatorSource010StateResolver:
    """Resolve body states from Navigator's qualified SOURCE-010 route rows.

    `route_rows` values must use Navigator's documented row shape:
    `[source_time, x_AU, y_AU, z_AU, vx_AU_day, vy_AU_day, vz_AU_day]`.
    The canonical time axis controls sampling; the row source-time field is
    preserved as provenance only and is not reinterpreted here.
    """

    def __init__(
        self,
        *,
        route_rows: Mapping[str, Sequence[Sequence[float]]],
        time_axis: Mapping[str, object],
        axis_qualification: str,
        source_authority: str,
    ) -> None:
        if str(source_authority).strip() != "SOURCE-010":
            raise NavigatorSource010StateError("only Navigator SOURCE-010 rows may be promoted")
        if str(axis_qualification).strip().upper() != "PASS":
            raise NavigatorSource010StateError("Navigator time axis must be qualified PASS")
        try:
            start = _epoch(str(time_axis["start_utc"]))
            step = float(time_axis["step_seconds"])
        except (KeyError, TypeError, ValueError) as exc:
            raise NavigatorSource010StateError("invalid Navigator time axis") from exc
        if not math.isfinite(step) or step <= 0.0:
            raise NavigatorSource010StateError("Navigator time-axis step_seconds must be positive")

        normalized = {}
        for entity_id, rows in route_rows.items():
            key = str(entity_id).strip()
            if not key:
                raise NavigatorSource010StateError("route-row entity id is required")
            parsed = tuple(_row(r) for r in rows)
            if len(parsed) < 2:
                raise NavigatorSource010StateError(f"{key} requires at least two route rows")
            normalized[key] = parsed

        self._rows = normalized
        self._start = start
        self._step_s = step
        self._axis = dict(time_axis)

    def resolve(self, entity_id: str, epoch_utc: str) -> SpatialState:
        key = str(entity_id).strip()
        rows = self._rows.get(key)
        if rows is None:
            raise NavigatorSource010StateError(f"no SOURCE-010 route rows for {key}")

        requested = _epoch(epoch_utc)
        offset_s = (requested - self._start).total_seconds()
        max_s = self._step_s * (len(rows) - 1)
        eps = 1e-9
        if offset_s < -eps or offset_s > max_s + eps:
            raise NavigatorSource010StateError(
                f"requested epoch outside acquired SOURCE-010 axis for {key}"
            )
        offset_s = min(max(offset_s, 0.0), max_s)

        q = offset_s / self._step_s
        lo = min(int(math.floor(q + eps)), len(rows) - 1)
        if lo == len(rows) - 1 or abs(q - round(q)) < 1e-12:
            r = rows[int(round(q))]
            pos = tuple(r[i] * AU_KM for i in (1, 2, 3))
            vel = tuple(r[i] * AU_KM / DAY_S for i in (4, 5, 6))
            interpolation = "EXACT_NAVIGATOR_ROW"
            bracket = (int(round(q)), int(round(q)))
        else:
            hi = lo + 1
            u = q - lo
            r0, r1 = rows[lo], rows[hi]
            pos_values = []
            vel_values = []
            for p_idx, v_idx in ((1, 4), (2, 5), (3, 6)):
                p, v = _hermite(
                    r0[p_idx] * AU_KM,
                    r1[p_idx] * AU_KM,
                    r0[v_idx] * AU_KM / DAY_S,
                    r1[v_idx] * AU_KM / DAY_S,
                    u,
                    self._step_s,
                )
                pos_values.append(p)
                vel_values.append(v)
            pos = tuple(pos_values)
            vel = tuple(vel_values)
            interpolation = "CUBIC_HERMITE_FROM_NAVIGATOR_ROWS"
            bracket = (lo, hi)

        requested_iso = requested.isoformat().replace("+00:00", "Z")
        return SpatialState(
            entity_id=key,
            epoch_utc=requested_iso,
            reference_frame=CANONICAL_FRAME,
            position_km=pos,
            velocity_km_s=vel,
            provenance={
                "state_source": "NAVIGATOR_SOURCE_010_ROUTE_ROWS",
                "source_authority": "SOURCE-010",
                "axis_qualification": "PASS",
                "interpolation": interpolation,
                "bracket_row_indexes": list(bracket),
                "row_source_time_before": rows[bracket[0]][0],
                "row_source_time_after": rows[bracket[1]][0],
            },
            navigation_grade=True,
            uncertainty={
                "qualification": "INHERITS_NAVIGATOR_SOURCE_010_AND_AXIS_QUALIFICATION",
                "additional_ephemeris_model": False,
            },
        )
