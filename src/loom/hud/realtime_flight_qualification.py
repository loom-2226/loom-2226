from __future__ import annotations

"""In-memory Earth-Moon local-flight qualification session.

This is deliberately NOT campaign authority. It starts from wall-clock UTC,
uses the local JPL Horizons qualification cache for lunar state, reuses LOOM's
shared gravity primitive, and consumes the pinned Wayfarer engineering handoff
for working torch cards and baseline mass state.

No campaign file or canonical SQLite database is written. Attitude is fixed for
this slice: the ship is initially pointed at the Moon and no rotational dynamics
are invented here. The separate rendezvous qualification consumes the Q4 finite
attitude envelope.
"""

from datetime import datetime, timezone
from pathlib import Path
import math
import os
import sqlite3
import threading
import time
from typing import Any

from loom.application.contracts import SpatialState
from loom.hud.earth_moon_qualification import CACHE_RELATIVE, _load_jpl_cache, _state_from_jpl
from loom.hud.wayfarer_engineering_state import (
    ENGINEERING_SOURCE_COMMIT,
    load_wayfarer_engineering_state,
)
from loom.runtime import resolve_runtime_roots
from loom.spatial.gravity import GravitySource, evaluate_gravity

CONTRACT = "LOOM_HUD_REALTIME_FLIGHT_QUALIFICATION_V1"
PREVIEW_CONTRACT = "LOOM_HUD_TRAJECTORY_PREVIEW_QUALIFICATION_V1"
FRAME = "J2000/ECLIPTIC"
G0_M_S2 = 9.80665
MOON_RADIUS_KM = 1737.4
WAYFARER_LENGTH_KM = 0.057

_ENGINEERING = load_wayfarer_engineering_state()
INITIAL_REMASS_T = float(_ENGINEERING["mass"]["normal_remass_allowance_t"])
INITIAL_WET_MASS_T = float(_ENGINEERING["mass"]["reference_wet_mass_t"])
PROTECTED_WATER_RESERVE_T = float(_ENGINEERING["mass"]["protected_water_reserve_t"])
TORCH_CARDS: dict[str, dict[str, float]] = {
    mode: {
        "acceleration_g": float(card["acceleration_g"]),
        "exhaust_velocity_km_s": float(card["exhaust_velocity_km_s"]),
    }
    for mode, card in _ENGINEERING["torch"]["mode_cards"].items()
}
ALLOWED_TIME_SCALES = (0.0, 1.0, 10.0, 100.0, 1000.0, 10000.0)
MAX_INTEGRATION_STEP_S = 10.0


def _parse_utc(value: str) -> datetime:
    probe = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(probe)
    if dt.tzinfo is None:
        raise ValueError("epoch must include timezone")
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _unit(v: tuple[float, float, float]) -> tuple[float, float, float]:
    mag = math.sqrt(sum(x * x for x in v))
    if mag <= 0.0:
        raise ValueError("zero vector cannot define Wayfarer fixed attitude")
    return tuple(x / mag for x in v)  # type: ignore[return-value]


def _vadd(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def _vscale(a, s: float):
    return tuple(x * s for x in a)


def _load_mu(db_path: Path, entity_id: str) -> tuple[float, str]:
    if not db_path.is_file():
        raise FileNotFoundError(f"celestial database not found: {db_path}")
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA query_only=ON")
        row = conn.execute("SELECT gm_km3_s2,source_id,status FROM celestial_properties WHERE entity_id=?", (entity_id,)).fetchone()
        if row is not None and row["gm_km3_s2"] is not None:
            return float(row["gm_km3_s2"]), f"celestial_properties:{row['source_id'] or ''}:{row['status']}"
        row = conn.execute("SELECT gm_km3_s2,source,metadata_status FROM celestial_dynamics WHERE entity_id=?", (entity_id,)).fetchone()
        if row is not None and row["gm_km3_s2"] is not None:
            return float(row["gm_km3_s2"]), f"celestial_dynamics:{row['source']}:{row['metadata_status']}"
    finally:
        conn.close()
    raise ValueError(f"no GM available for {entity_id}")


class RealtimeFlightQualification:
    """Disposable server-side qualification state; never campaign persistence."""

    def __init__(self, *, data_root: Path | str | None = None):
        roots = resolve_runtime_roots(data_root=data_root)
        self.data_root = roots.data_root
        cache_path = self.data_root / CACHE_RELATIVE
        cached = _load_jpl_cache(cache_path)
        if cached is None:
            raise FileNotFoundError(f"JPL qualification cache missing: {cache_path}; run tools/acquire_earth_moon_ephemeris_2026.py")
        self.anchors, self.cache_doc = cached
        self.coverage_start = _parse_utc(self.anchors[0].epoch_utc)
        self.coverage_end = _parse_utc(self.anchors[-1].epoch_utc)
        db_path = Path(os.environ.get("LOOM_SPATIAL_DB") or (self.data_root / "LOOM_2226.sqlite3"))
        self.earth_mu, self.earth_mu_source = _load_mu(db_path, "EA")
        self.moon_mu, self.moon_mu_source = _load_mu(db_path, "LU")
        self.lock = threading.RLock()
        self.time_scale = 1.0
        self.torch_mode = "CRUISE"
        self.torch_active = False
        self.status = "RUNNING"
        self.last_wall = time.monotonic()
        self._reset_to_wall_utc()

    def _reset_to_wall_utc(self) -> None:
        now = datetime.now(timezone.utc)
        if not (self.coverage_start <= now <= self.coverage_end):
            raise ValueError(f"wall UTC {_iso(now)} outside JPL cache coverage {_iso(self.coverage_start)} .. {_iso(self.coverage_end)}")
        moon_p, _moon_v, _ = _state_from_jpl(self.anchors, now)
        self.sim_epoch = now
        self.ship_position = tuple(0.5 * x for x in moon_p)
        self.ship_velocity = (0.0, 0.0, 0.0)
        self.nose_direction = _unit(tuple(moon_p[i] - self.ship_position[i] for i in range(3)))
        self.remass_t = INITIAL_REMASS_T
        self.wet_mass_t = INITIAL_WET_MASS_T
        self.torch_active = False
        self.status = "RUNNING"
        self.last_wall = time.monotonic()

    def reset(self) -> dict[str, Any]:
        with self.lock:
            self._reset_to_wall_utc()
            return self.snapshot(advance=False)

    def set_time_scale(self, value: float) -> dict[str, Any]:
        value = float(value)
        if value not in ALLOWED_TIME_SCALES:
            raise ValueError(f"time scale must be one of {ALLOWED_TIME_SCALES}")
        with self.lock:
            self._advance_locked()
            self.time_scale = value
            self.last_wall = time.monotonic()
            return self.snapshot(advance=False)

    def set_torch(self, *, active: bool, mode: str | None = None) -> dict[str, Any]:
        with self.lock:
            self._advance_locked()
            if mode is not None:
                mode = str(mode).upper()
                if mode not in TORCH_CARDS:
                    raise ValueError(f"unknown torch mode: {mode}")
                self.torch_mode = mode
            if active and self.remass_t <= 0.0:
                raise ValueError("normal remass exhausted")
            self.torch_active = bool(active)
            self.last_wall = time.monotonic()
            return self.snapshot(advance=False)

    def _gravity(self, epoch: datetime, ship_position) -> tuple[float, float, float]:
        epoch_text = _iso(epoch)
        moon_p, moon_v, state_source = _state_from_jpl(self.anchors, epoch)
        earth = SpatialState(entity_id="EA", epoch_utc=epoch_text, reference_frame=FRAME, position_km=(0.0, 0.0, 0.0), velocity_km_s=(0.0, 0.0, 0.0), provenance={"state_source": "EARTH_CENTERED_FRAME_ORIGIN"}, navigation_grade=False)
        moon = SpatialState(entity_id="LU", epoch_utc=epoch_text, reference_frame=FRAME, position_km=moon_p, velocity_km_s=moon_v, provenance={"state_source": state_source, "cache": "JPL_HORIZONS_DIRECT_HOURLY_PLUS_HERMITE"}, navigation_grade=False)
        evaluation = evaluate_gravity(ship_position, (GravitySource("EA", earth, self.earth_mu, provenance={"source": self.earth_mu_source}), GravitySource("LU", moon, self.moon_mu, provenance={"source": self.moon_mu_source})), epoch_utc=epoch_text)
        return evaluation.total_acceleration_km_s2

    def _thrust_acceleration(self) -> tuple[tuple[float, float, float], float, float]:
        if not self.torch_active or self.remass_t <= 0.0:
            return (0.0, 0.0, 0.0), 0.0, 0.0
        card = TORCH_CARDS[self.torch_mode]
        acceleration_km_s2 = card["acceleration_g"] * G0_M_S2 / 1000.0
        thrust_n = self.wet_mass_t * 1000.0 * acceleration_km_s2 * 1000.0
        exhaust_m_s = card["exhaust_velocity_km_s"] * 1000.0
        mass_flow_kg_s = thrust_n / exhaust_m_s
        return _vscale(self.nose_direction, acceleration_km_s2), thrust_n, mass_flow_kg_s

    def _step(self, dt: float) -> None:
        if dt <= 0.0:
            return
        gravity = self._gravity(self.sim_epoch, self.ship_position)
        thrust_acc, _thrust_n, mass_flow_kg_s = self._thrust_acceleration()
        acc = _vadd(gravity, thrust_acc)
        self.ship_velocity = _vadd(self.ship_velocity, _vscale(acc, dt))
        self.ship_position = _vadd(self.ship_position, _vscale(self.ship_velocity, dt))
        if self.torch_active and mass_flow_kg_s > 0.0:
            used_t = min(self.remass_t, mass_flow_kg_s * dt / 1000.0)
            self.remass_t -= used_t
            self.wet_mass_t -= used_t
            if self.remass_t <= 1e-12:
                self.remass_t = 0.0
                self.torch_active = False
        self.sim_epoch = self.sim_epoch.fromtimestamp(self.sim_epoch.timestamp() + dt, tz=timezone.utc)

    def _advance_locked(self) -> None:
        wall_now = time.monotonic()
        sim_dt = max(0.0, wall_now - self.last_wall) * self.time_scale
        self.last_wall = wall_now
        if sim_dt <= 0.0 or self.status != "RUNNING":
            return
        remaining_coverage = (self.coverage_end - self.sim_epoch).total_seconds()
        if sim_dt > remaining_coverage:
            sim_dt = max(0.0, remaining_coverage)
            self.status = "EPHEMERIS_LIMIT"
            self.time_scale = 0.0
            self.torch_active = False
        remaining = sim_dt
        while remaining > 1e-9:
            step = min(MAX_INTEGRATION_STEP_S, remaining)
            self._step(step)
            remaining -= step

    def trajectory_preview(self, *, burn_s: float, coast_s: float, mode: str, sample_s: float = 60.0) -> dict[str, Any]:
        """Preview a fixed-attitude burn+coast without changing the live session.

        This deliberately uses the same qualification integrator and JPL cache as
        live flight. It is GMAT-like visualization scaffolding, NOT a Navigator
        solution and NOT a targeting solver.
        """
        burn_s, coast_s, sample_s = float(burn_s), float(coast_s), float(sample_s)
        mode = str(mode).upper()
        if mode not in TORCH_CARDS:
            raise ValueError(f"unknown torch mode: {mode}")
        if burn_s < 0 or coast_s < 0 or burn_s + coast_s <= 0:
            raise ValueError("preview duration must be positive")
        if burn_s + coast_s > 7 * 86400:
            raise ValueError("preview limited to seven simulated days")
        if not (10.0 <= sample_s <= 3600.0):
            raise ValueError("sample_s must be in 10..3600")
        with self.lock:
            self._advance_locked()
            saved = (self.sim_epoch, self.ship_position, self.ship_velocity, self.remass_t, self.wet_mass_t, self.torch_active, self.torch_mode, self.status, self.time_scale, self.last_wall)
            start_epoch = self.sim_epoch
            start_position = self.ship_position
            points: list[dict[str, Any]] = []
            try:
                self.torch_mode = mode
                self.torch_active = burn_s > 0 and self.remass_t > 0
                elapsed = 0.0
                total = burn_s + coast_s
                next_sample = 0.0
                while elapsed < total - 1e-9:
                    if elapsed >= burn_s:
                        self.torch_active = False
                    dt = min(MAX_INTEGRATION_STEP_S, total - elapsed)
                    if elapsed < burn_s < elapsed + dt:
                        dt = burn_s - elapsed
                    self._step(dt)
                    elapsed += dt
                    if elapsed + 1e-9 >= next_sample or elapsed >= total - 1e-9:
                        moon_p, _moon_v, moon_source = _state_from_jpl(self.anchors, self.sim_epoch)
                        points.append({"elapsed_s": elapsed, "epoch_utc": _iso(self.sim_epoch), "phase": "BURN" if elapsed <= burn_s and self.remass_t > 0 else "COAST", "wayfarer_position_earth_centered_km": list(self.ship_position), "wayfarer_velocity_earth_centered_km_s": list(self.ship_velocity), "moon_position_earth_centered_km": list(moon_p), "moon_relative_to_wayfarer_km": [moon_p[i] - self.ship_position[i] for i in range(3)], "remass_t": self.remass_t, "state_source": moon_source})
                        next_sample += sample_s
                final_speed = math.sqrt(sum(x*x for x in self.ship_velocity))
                final_moon_range = math.sqrt(sum(x*x for x in points[-1]["moon_relative_to_wayfarer_km"])) if points else None
                return {"contract": PREVIEW_CONTRACT, "status": "QUALIFICATION_ONLY", "navigation_grade": False, "mutates_live_state": False, "solver": "NONE_FIXED_ATTITUDE_FORWARD_PROPAGATION", "frame": FRAME, "start_epoch_utc": _iso(start_epoch), "start_position_earth_centered_km": list(start_position), "mode": mode, "burn_s": burn_s, "coast_s": coast_s, "sample_s": sample_s, "engineering_source_commit": ENGINEERING_SOURCE_COMMIT, "torch_card_status": _ENGINEERING["torch"]["mode_cards"][mode]["status"], "integration": {"method": "SEMI_IMPLICIT_EULER", "max_step_s": MAX_INTEGRATION_STEP_S, "gravity": "LOOM_SHARED_EARTH_PLUS_MOON_POINT_MASS"}, "points": points, "final": {"speed_km_s": final_speed, "moon_range_km": final_moon_range, "remass_t": self.remass_t}}
            finally:
                (self.sim_epoch, self.ship_position, self.ship_velocity, self.remass_t, self.wet_mass_t, self.torch_active, self.torch_mode, self.status, self.time_scale, self.last_wall) = saved

    def snapshot(self, *, advance: bool = True) -> dict[str, Any]:
        with self.lock:
            if advance:
                self._advance_locked()
            moon_p, moon_v, moon_source = _state_from_jpl(self.anchors, self.sim_epoch)
            card = TORCH_CARDS[self.torch_mode]
            thrust_acc, thrust_n, mass_flow_kg_s = self._thrust_acceleration()
            moon_rel = tuple(moon_p[i] - self.ship_position[i] for i in range(3))
            earth_rel = tuple(-self.ship_position[i] for i in range(3))
            engineering = {
                "contract": _ENGINEERING["contract"],
                "source": _ENGINEERING["source"],
                "authority": _ENGINEERING["authority"],
                "mass": _ENGINEERING["mass"],
                "dispatch": _ENGINEERING["dispatch"],
                "power_thermal": _ENGINEERING["power_thermal"],
                "feedstock": _ENGINEERING["feedstock"],
                "mobility_firewall": _ENGINEERING["mobility_firewall"],
            }
            return {"contract": CONTRACT, "status": self.status, "authority": "QUALIFICATION_ONLY", "navigation_grade": False, "campaign_mutation": False, "frame": FRAME, "sim_epoch_utc": _iso(self.sim_epoch), "wall_epoch_utc": _iso(datetime.now(timezone.utc)), "time_scale": self.time_scale, "allowed_time_scales": list(ALLOWED_TIME_SCALES), "ephemeris": {"moon_source": moon_source, "mode": "JPL_HORIZONS_HOURLY_PLUS_CUBIC_HERMITE", "coverage_start_utc": _iso(self.coverage_start), "coverage_end_utc": _iso(self.coverage_end)}, "earth": {"position_km": [0.0, 0.0, 0.0], "relative_to_wayfarer_km": list(earth_rel)}, "moon": {"position_earth_centered_km": list(moon_p), "velocity_earth_centered_km_s": list(moon_v), "relative_to_wayfarer_km": list(moon_rel), "radius_km": MOON_RADIUS_KM, "visual_orientation_authority": "MODEL_NATIVE_NOT_SPICE_QUALIFIED"}, "wayfarer": {"position_earth_centered_km": list(self.ship_position), "velocity_earth_centered_km_s": list(self.ship_velocity), "fixed_nose_direction_inertial": list(self.nose_direction), "attitude_authority": "FIXED_QUALIFICATION_ATTITUDE_NO_ROTATIONAL_DYNAMICS", "length_km": WAYFARER_LENGTH_KM, "wet_mass_t": self.wet_mass_t, "remass_t": self.remass_t, "protected_water_reserve_t": PROTECTED_WATER_RESERVE_T, "geometry_authority": "DETERMINISTIC_WAYFARER_ENGINEERING_GEOMETRY_NON_CANON_VISUAL"}, "torch": {"active": self.torch_active, "mode": self.torch_mode, "acceleration_g": card["acceleration_g"], "exhaust_velocity_km_s": card["exhaust_velocity_km_s"], "card_status": _ENGINEERING["torch"]["mode_cards"][self.torch_mode]["status"], "mode_authorization": _ENGINEERING["dispatch"]["torch_mode_authorization"][self.torch_mode], "thrust_n": thrust_n, "mass_flow_kg_s": mass_flow_kg_s, "acceleration_vector_km_s2": list(thrust_acc), "authority": "PINNED_PR96_WORKING_ENGINEERING_CARD_QUALIFICATION", "jet_power_is_electrical_bus_power": _ENGINEERING["torch"]["jet_power_is_electrical_bus_power"]}, "engineering": engineering, "integration": {"owner": "PYTHON_SERVER_QUALIFICATION_SESSION", "method": "SEMI_IMPLICIT_EULER", "max_step_s": MAX_INTEGRATION_STEP_S, "gravity": "LOOM_SHARED_EARTH_PLUS_MOON_POINT_MASS", "attitude_dynamics": "NOT_IMPLEMENTED"}}
