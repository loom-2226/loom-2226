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


def _legacy_test_id(payload: Mapping[str, Any]) -> str:
    """Use the frozen campaign's accepted H-F###### Sequence-H identifier shape."""
    body = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    n = int(hashlib.sha256(body).hexdigest()[:12], 16) % 1_000_000
    return f"H-F{n:06d}"


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

    def _legacy_mission(self, request: NavigationRequest, context: NavigationContext, nav: Any) -> dict[str, Any]:
        """Adapt a canonical request to the frozen RC6.1 mission envelope.

        Existing replay/import payloads retain their supplied envelope fields.
        New GIS-originated requests receive the exact defaults used by the
        frozen campaign workflow; GIS itself never knows this legacy grammar.
        """
        mission = request.to_legacy_mission()
        state = dict(context.campaign_state)
        mission.setdefault("schema", "LOOM_NAV_REQUEST_v1")
        mission.setdefault("test_id", _legacy_test_id({
            "state_id": state.get("state_id"),
            "origin": request.origin,
            "destination": request.destination,
            "priority": request.priority,
        }))
        if "epoch" not in mission:
            epoch_utc = state.get("epoch_utc")
            if not epoch_utc:
                raise NavigationServiceError("campaign epoch_utc is required to build a Navigator mission")
            local_for_utc = getattr(self.core, "_melbourne_local_for_utc", None)
            if not callable(local_for_utc):
                raise NavigationServiceError("legacy Navigator local-epoch adapter is unavailable")
            mission["epoch"] = {
                "local": local_for_utc(nav, epoch_utc),
                "timezone": "Australia/Melbourne",
            }
        mission.setdefault("ship", "WAYFARER_BASELINE")
        if not mission.get("requested_modes"):
            mission["requested_modes"] = {"metric": "FAST", "torch": "CRUISE"}
        mission.setdefault(
            "notes",
            "GIS Phase 5 planning request; persistent campaign state inherited from LOOM_STATE_V1.",
        )
        return mission

    def prepare_context(
        self,
        request: NavigationRequest,
        context: NavigationContext,
        *,
        offline: bool = False,
        refresh: bool = False,
    ) -> NavigationContext:
        """Prepare Sequence-H acquisition for planning without leaking provider logic into GIS."""
        nav = self._sequence_h(context)
        normalize = getattr(nav, "validate_and_normalize_mission", None)
        acquire = getattr(nav, "run_acquisition", None)
        if not callable(normalize) or not callable(acquire):
            raise NavigationServiceError("legacy acquisition capability is unavailable")
        cache = self._require(context.cache_dir, "cache_dir")
        mission = self._legacy_mission(request, context, nav)
        normalized = normalize(mission)
        acquisition = acquire(normalized, cache, offline=offline, refresh=refresh)
        return NavigationContext(
            campaign_state=context.campaign_state,
            acquisition=acquisition,
            cache_dir=context.cache_dir,
            b1_package=context.b1_package,
            runtime_root=context.runtime_root,
            payload=context.payload,
        )

    def discover_routes(self, request: NavigationRequest, context: NavigationContext) -> tuple[RouteCandidate, ...]:
        nav = self._sequence_h(context)
        normalize = getattr(nav, "validate_and_normalize_mission", None)
        discover = getattr(self.core, "_candidate_plans", None)
        if not callable(normalize) or not callable(discover):
            raise NavigationServiceError("legacy route-discovery capability is unavailable")
        acq = self._require(context.acquisition, "acquisition")
        cache = self._require(context.cache_dir, "cache_dir")
        normalized = normalize(self._legacy_mission(request, context, nav))
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
        mission = self._legacy_mission(request, context, nav)
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
            "request": mission,
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
