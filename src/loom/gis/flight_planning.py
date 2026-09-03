"""GIS flight planning and Phase-6 campaign execution orchestration.

GIS owns interaction and comparison. Navigator remains sole authority for route
planning and flight calculations. Campaign services remain sole persistence
authority. A planning COMMIT locks a choice; EXECUTE performs the separate,
explicit campaign transition.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping
import copy
import hashlib
import json

from loom.navigation import NavigationContext, NavigationRequest, RouteCandidate
from .navigation_overlay import build_navigation_overlay

GIS_FLIGHT_PLANNING_VERSION = "LOOM_GIS_FLIGHT_PLANNING_V1"


class GISFlightPlanningError(RuntimeError):
    pass


def _stable_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _first(payload: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def _candidate_summary(candidate: RouteCandidate) -> dict[str, Any]:
    p = dict(candidate.payload)
    leg = p.get("leg") if isinstance(p.get("leg"), Mapping) else {}
    source = dict(p)
    for k, v in dict(leg).items():
        source.setdefault(k, v)
    return {
        "route_id": candidate.route_id,
        "origin": candidate.origin,
        "destination": candidate.destination,
        "departure_epoch": candidate.departure_epoch,
        "arrival_epoch": candidate.arrival_epoch,
        "strategy": candidate.strategy,
        "duration_minutes": _first(source, "total_minutes", "duration_minutes", "elapsed_minutes", "flight_minutes"),
        "remass_t": _first(source, "stage_remass_t", "remass_t", "remass_used_t", "total_remass_t"),
        "holonomy": _first(source, "holonomy", "H", "holonomy_cost"),
        "confidence": _first(source, "confidence", "C_M", "mission_confidence"),
        "metric_mode": _first(source, "metric", "metric_mode"),
        "torch_mode": _first(source, "torch", "torch_mode"),
        "selectable": bool(source.get("selectable", True)),
    }


@dataclass(frozen=True)
class GISPlanningCandidateV1:
    route_id: str
    summary: Mapping[str, Any]
    source_payload: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GISPlanningStateV1:
    session_id: str
    origin: str
    destination: str | None
    priority: str
    candidates: tuple[GISPlanningCandidateV1, ...] = ()
    preview_route_id: str | None = None
    committed_route_id: str | None = None
    preview_overlay: Mapping[str, Any] | None = None
    campaign_state_sha256: str | None = None
    execution_available: bool = False
    last_execution: Mapping[str, Any] | None = None
    contract: str = GIS_FLIGHT_PLANNING_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GISFlightPlanningSession:
    """Planning session bound to one canonical campaign snapshot at a time."""

    def __init__(
        self,
        navigation_service: Any,
        context: NavigationContext,
        *,
        offline: bool = False,
        campaign_execution_service: Any | None = None,
    ):
        self.service = navigation_service
        self.campaign_execution_service = campaign_execution_service
        self.offline = bool(offline)
        self.last_execution: Mapping[str, Any] | None = None
        self._bind_context(context)

    def _bind_context(self, context: NavigationContext) -> None:
        self.context = context
        self._campaign_before = copy.deepcopy(dict(context.campaign_state))
        origin = str(self._campaign_before.get("location_token") or "").strip()
        if not origin:
            raise GISFlightPlanningError("campaign state has no location_token")
        self.origin = origin
        self.destination: str | None = None
        self.priority = "BALANCED"
        self._request: NavigationRequest | None = None
        self._candidates: dict[str, RouteCandidate] = {}
        self._plans: dict[str, Any] = {}
        self.preview_route_id: str | None = None
        self.committed_route_id: str | None = None
        self.preview_overlay: Mapping[str, Any] | None = None
        seed = {
            "state": self._campaign_before.get("state_id"),
            "revision": self._campaign_before.get("revision"),
            "origin": origin,
        }
        self.session_id = "plan-" + hashlib.sha256(_stable_json(seed)).hexdigest()[:16]
        self.campaign_state_sha256 = hashlib.sha256(_stable_json(self._campaign_before)).hexdigest()

    def _assert_read_only(self) -> None:
        if dict(self.context.campaign_state) != self._campaign_before:
            raise GISFlightPlanningError("planning mutated canonical campaign state")

    def state(self) -> GISPlanningStateV1:
        return GISPlanningStateV1(
            session_id=self.session_id,
            origin=self.origin,
            destination=self.destination,
            priority=self.priority,
            candidates=tuple(
                GISPlanningCandidateV1(c.route_id, _candidate_summary(c), dict(c.payload))
                for c in self._candidates.values()
            ),
            preview_route_id=self.preview_route_id,
            committed_route_id=self.committed_route_id,
            preview_overlay=self.preview_overlay,
            campaign_state_sha256=self.campaign_state_sha256,
            execution_available=self.campaign_execution_service is not None,
            last_execution=self.last_execution,
        )

    def discover(self, destination: str, priority: str = "BALANCED") -> GISPlanningStateV1:
        destination = str(destination or "").strip()
        if not destination:
            raise GISFlightPlanningError("destination is required")
        if destination == self.origin:
            raise GISFlightPlanningError("destination must differ from origin")
        self.destination = destination
        self.priority = str(priority or "BALANCED").upper()
        self._request = NavigationRequest(origin=self.origin, destination=destination, priority=self.priority)
        self.context = self.service.prepare_context(self._request, self.context, offline=self.offline, refresh=False)
        rows = self.service.discover_routes(self._request, self.context)
        self._candidates = {c.route_id: c for c in rows}
        self._plans.clear()
        self.preview_route_id = None
        self.committed_route_id = None
        self.preview_overlay = None
        self.last_execution = None
        self._assert_read_only()
        return self.state()

    def preview(self, route_id: str) -> GISPlanningStateV1:
        if self._request is None:
            raise GISFlightPlanningError("discover routes before preview")
        candidate = self._candidates.get(str(route_id))
        if candidate is None:
            raise GISFlightPlanningError(f"unknown route_id: {route_id}")
        if not _candidate_summary(candidate)["selectable"]:
            raise GISFlightPlanningError(f"route is not selectable: {route_id}")
        plan = self._plans.get(candidate.route_id)
        if plan is None:
            plan = self.service.compile_flight(self._request, candidate, self.context)
            self._plans[candidate.route_id] = plan
        layer = self.service.get_route_layer(plan, self.context)
        self.preview_route_id = candidate.route_id
        self.preview_overlay = build_navigation_overlay(layer).to_dict()
        self._assert_read_only()
        return self.state()

    def commit(self, route_id: str | None = None) -> GISPlanningStateV1:
        selected = str(route_id or self.preview_route_id or "")
        if not selected or selected not in self._candidates:
            raise GISFlightPlanningError("preview/select a valid route before commit")
        if self.preview_route_id != selected:
            self.preview(selected)
        self.committed_route_id = selected
        self._assert_read_only()
        return self.state()

    def execute(self) -> GISPlanningStateV1:
        if self.campaign_execution_service is None:
            raise GISFlightPlanningError("campaign execution is unavailable in this runtime")
        plan = self.committed_plan()
        if plan is None or self.committed_route_id is None:
            raise GISFlightPlanningError("commit a route before execute")
        # Navigator calculates; campaign service persists. GIS does neither.
        execution = self.service.execute_flight(plan, self.context)
        layer = self.service.get_route_layer(plan, self.context)
        committed = self.campaign_execution_service.commit_flight(plan, execution, self.context)
        history_overlay = build_navigation_overlay(historical_routes=(layer,)).to_dict()
        summary = committed.to_dict()
        summary["navigation_status"] = execution.status
        summary["historical_overlay"] = history_overlay
        new_context = NavigationContext(
            campaign_state=copy.deepcopy(dict(committed.final_state)),
            acquisition=None,
            cache_dir=self.context.cache_dir,
            b1_package=self.context.b1_package,
            runtime_root=self.context.runtime_root,
            payload=self.context.payload,
        )
        self._bind_context(new_context)
        self.last_execution = summary
        return self.state()

    def cancel(self) -> GISPlanningStateV1:
        self.preview_route_id = None
        self.committed_route_id = None
        self.preview_overlay = None
        self._assert_read_only()
        return self.state()

    def committed_plan(self) -> Any | None:
        return self._plans.get(self.committed_route_id) if self.committed_route_id else None
