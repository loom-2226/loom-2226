"""Behavior-preserving adapter from canonical navigation services to Navigator RC6.1.

No physics is implemented here. This module validates service boundaries,
normalizes canonical requests and delegates to the frozen legacy Navigator
functions that remain authoritative while exposing typed downstream contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import hashlib
import json

from .contracts import (
    EphemerisSnapshot,
    FlightExecutionResult,
    FlightPlan,
    NavigationContext,
    NavigationRequest,
    RouteCandidate,
)
from .ephemeris import LegacySequenceHEphemerisProvider
from .execution import LegacyFlightExecutionAdapter
from .route_layer import LegacyRouteLayerAdapter, LoomRouteLayerV1


class NavigationServiceError(RuntimeError):
    """Raised for missing legacy capabilities or invalid adapter state."""


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    body = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(body).hexdigest()[:16]}"


@dataclass
class LegacyNavigationService:
    """Canonical service facade over the frozen outer Navigator module."""

    core: Any

    def _sequence_h(self, context: NavigationContext) -> Any:
        loader = getattr(self.core, "_load_core", None)
        if not callable(loader):
            raise NavigationServiceError("legacy Navigator core does not expose _load_core")
        root = Path(context.runtime_root) if context.runtime_root is not None else Path.cwd()
        return loader(root / "LOOM_Navigator_Internal_SequenceH")

    @staticmethod
    def _require(value: Any, name: str) -> Any:
        if value is None:
            raise NavigationServiceError(f"{name} is required for this legacy operation")
        return value

    def discover_routes(self, request: NavigationRequest, context: NavigationContext) -> tuple[RouteCandidate, ...]:
        nav = self._sequence_h(context)
        normalize = getattr(nav, "validate_and_normalize_mission", None)
        discover = getattr(self.core, "_candidate_plans", None)
        if not callable(normalize) or not callable(discover):
            raise NavigationServiceError("legacy route-discovery capability is unavailable")
        acq = self._require(context.acquisition, "acquisition")
        cache = self._require(context.cache_dir, "cache_dir")
        normalized = normalize(request.to_legacy_mission())
        rows = discover(nav, normalized, acq, cache, dict(context.campaign_state), request.priority)
        out: list[RouteCandidate] = []
        for index, row in enumerate(rows):
            payload = dict(row)
            rid = str(payload.get("route_id") or payload.get("candidate_id") or _stable_id(f"route{index+1}", payload))
            modes = "/".join(str(payload.get(k)) for k in ("metric", "torch") if payload.get(k)) or None
            out.append(RouteCandidate(
                route_id=rid,
                origin=request.origin,
                destination=request.destination,
                departure_epoch=payload.get("departure_epoch_utc") or context.campaign_state.get("epoch_utc"),
                arrival_epoch=payload.get("arrival_epoch_utc"),
                strategy=modes,
                payload=payload,
            ))
        return tuple(out)

    def compile_flight(self, request: NavigationRequest, candidate: RouteCandidate, context: NavigationContext) -> FlightPlan:
        nav = self._sequence_h(context)
        normalize = getattr(nav, "validate_and_normalize_mission", None)
        gate = getattr(nav, "target_determinism_gate", None)
        if not callable(normalize) or not callable(gate):
            raise NavigationServiceError("legacy deterministic-flight capability is unavailable")
        acq = self._require(context.acquisition, "acquisition")
        cache = self._require(context.cache_dir, "cache_dir")
        b1 = self._require(context.b1_package, "b1_package")
        mission = request.to_legacy_mission()
        cp = dict(candidate.payload)
        mission["requested_modes"] = {"metric": cp.get("metric"), "torch": cp.get("torch")}
        normalized = normalize(mission)
        state = dict(context.campaign_state)
        if state:
            normalized["_campaign_initial_state"] = {
                "state_id": state.get("state_id"),
                "state_sha256": state.get("state_sha256"),
                "wet_mass_t": (state.get("ship") or {}).get("wet_mass_t"),
                "remass_t": (state.get("ship") or {}).get("remass_t"),
            }
        runtime, payloads, html, validation, determinism = gate(normalized, acq, cache, b1)

        plan_summary = None
        plan_sha = None
        summarize = getattr(self.core, "_plan_summary", None)
        canon = getattr(self.core, "_canon", None)
        sha_bytes = getattr(self.core, "_sha_bytes", None)
        if (
            callable(summarize)
            and callable(canon)
            and callable(sha_bytes)
            and state
            and isinstance(cp.get("leg"), Mapping)
        ):
            plan_summary = summarize(nav, state, cp, request.origin, request.destination, request.priority)
            plan_sha = sha_bytes(canon(plan_summary))

        packed = {
            "runtime": runtime,
            "payloads": payloads,
            "html": html,
            "validation": validation,
            "determinism": determinism,
            "plan_summary": plan_summary,
            "plan_sha256": plan_sha,
            "request": request.to_legacy_mission(),
        }
        flight = (runtime or {}).get("flight", {})
        fid = str(flight.get("flight_id") or _stable_id("flight", {"candidate": candidate.route_id, "runtime": runtime}))
        return FlightPlan(flight_id=fid, candidate=candidate, payload=packed)

    def plan_flight(self, request: NavigationRequest, context: NavigationContext, candidate_index: int = 0) -> FlightPlan:
        candidates = self.discover_routes(request, context)
        if not candidates:
            raise NavigationServiceError("legacy Navigator returned no route candidates")
        try:
            candidate = candidates[candidate_index]
        except IndexError as exc:
            raise NavigationServiceError(f"candidate_index out of range: {candidate_index}") from exc
        return self.compile_flight(request, candidate, context)

    def execute_flight(self, plan: FlightPlan, context: NavigationContext) -> FlightExecutionResult:
        """Return the authoritative arrival transition without persisting campaign state."""
        try:
            return LegacyFlightExecutionAdapter(self.core).execute(plan, context)
        except RuntimeError as exc:
            raise NavigationServiceError(str(exc)) from exc

    def get_ephemeris(self, context: NavigationContext, epoch: str | None = None) -> EphemerisSnapshot:
        nav = self._sequence_h(context)
        provider = LegacySequenceHEphemerisProvider(nav)
        try:
            return provider.snapshot(context, epoch=epoch)
        except RuntimeError as exc:
            raise NavigationServiceError(str(exc)) from exc

    def get_flight_geometry(self, plan: FlightPlan) -> Mapping[str, Any]:
        runtime = dict(plan.payload).get("runtime") or {}
        return dict((runtime or {}).get("flight") or {})

    def get_route_layer(self, plan: FlightPlan, context: NavigationContext | None = None) -> LoomRouteLayerV1:
        """Expose solved Navigator truth through the display-agnostic GIS V1 contract."""
        return LegacyRouteLayerAdapter().build(plan, context)
