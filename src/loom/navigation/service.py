"""Behavior-preserving adapter from canonical navigation services to Navigator RC6.1.

No physics is implemented here. This module only validates the service boundary,
normalizes canonical requests and delegates to the frozen legacy Navigator
functions that remain authoritative during Phase 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import hashlib
import json

from .contracts import FlightPlan, NavigationContext, NavigationRequest, RouteCandidate


class NavigationServiceError(RuntimeError):
    """Raised for missing legacy capabilities or invalid adapter state."""


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    body = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(body).hexdigest()[:16]}"


@dataclass
class LegacyNavigationService:
    """Canonical service facade over the frozen outer Navigator module.

    The outer module is ``loom_navigator_core.py``. Its embedded Sequence-H
    module is loaded through the outer module's own ``_load_core`` routine, so
    its existing hash check and authoritative implementation are preserved.
    """

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
        """Delegate authoritative route discovery to RC6.1 ``_candidate_plans``."""
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

    def compile_flight(
        self,
        request: NavigationRequest,
        candidate: RouteCandidate,
        context: NavigationContext,
    ) -> FlightPlan:
        """Run the existing deterministic final solve for a selected candidate."""
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
        packed = {
            "runtime": runtime,
            "payloads": payloads,
            "html": html,
            "validation": validation,
            "determinism": determinism,
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

    def execute_flight(self, *_: Any, **__: Any) -> None:
        raise NavigationServiceError(
            "campaign execution remains in the legacy outer Navigator during Phase 2; "
            "it is not duplicated in the service layer"
        )

    def get_ephemeris(self, *_: Any, **__: Any) -> None:
        raise NavigationServiceError(
            "ephemeris extraction is pending; the legacy Sequence-H provider remains authoritative"
        )

    def get_flight_geometry(self, plan: FlightPlan) -> Mapping[str, Any]:
        runtime = dict(plan.payload).get("runtime") or {}
        return dict((runtime or {}).get("flight") or {})
