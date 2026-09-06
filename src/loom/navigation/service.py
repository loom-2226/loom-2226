"""Behavior-preserving adapter from canonical navigation services to Navigator RC6.1.

No physics is implemented here. This module validates service boundaries,
normalizes canonical requests and delegates to the frozen legacy Navigator
functions that remain authoritative while exposing typed downstream contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo
import hashlib
import json
import math
import re

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


def _melbourne_local_fallback(epoch_utc: str) -> str:
    """Standards-only fallback when legacy CLI glue is unavailable.

    Real RC6.1 continues to use its own helper. This exists so extracted domain
    services and tests do not depend on unrelated outer-CLI formatting code.
    """
    text = str(epoch_utc).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise NavigationServiceError(f"invalid campaign epoch_utc: {epoch_utc}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    local = dt.astimezone(ZoneInfo("Australia/Melbourne"))
    return local.isoformat(timespec="seconds")


_DIRECT_COVERAGE_PATTERNS = (
    re.compile(r"No ephemeris for target .* after A\.D\.", re.IGNORECASE),
    re.compile(r"No ephemeris for target .* before A\.D\.", re.IGNORECASE),
)
_SEQUENCE_B_GLOBAL_LOCAL_PREFIX = "Sequence B requires direct B1-supported local ephemeris; missing "


def _looks_like_direct_coverage_unavailable(exc: BaseException) -> bool:
    """Recognize only an explicit provider no-vector coverage statement.

    Sequence-H already distinguishes genuine direct-vector coverage gaps from
    network, HTTP, parsing, cache, and configuration failures. Some Horizons
    responses currently escape as a generic WorkflowError containing the exact
    no-ephemeris message instead of DirectCoverageUnavailable. This predicate is
    intentionally narrow so transport/cache failures still fail closed.
    """
    text = str(exc)
    return any(pattern.search(text) for pattern in _DIRECT_COVERAGE_PATTERNS)


def _is_global_sequence_b_local_completeness_error(exc: BaseException) -> bool:
    """Identify only the frozen all-local-systems presentation completeness gate."""
    return str(exc).startswith(_SEQUENCE_B_GLOBAL_LOCAL_PREFIX)


def _run_acquisition_with_coverage_normalization(
    nav: Any,
    normalized: Mapping[str, Any],
    cache: Path,
    *,
    offline: bool,
    refresh: bool,
) -> dict[str, Any]:
    """Run the frozen acquisition policy while repairing one exception mismatch.

    The embedded core's run_acquisition already parks DirectCoverageUnavailable
    for LOCAL dependencies and re-raises it for BASE dependencies. We therefore
    do not change dependency scope or authority policy here. We only translate a
    provider exception carrying the exact Horizons no-coverage message into the
    exception type the frozen policy already handles, then restore the module
    function immediately after the acquisition call.
    """
    acquire = getattr(nav, "run_acquisition", None)
    fetch = getattr(nav, "fetch_or_cache", None)
    direct_exc = getattr(nav, "DirectCoverageUnavailable", None)
    if not callable(acquire) or not callable(fetch) or not isinstance(direct_exc, type):
        if not callable(acquire):
            raise NavigationServiceError("legacy acquisition capability is unavailable")
        return acquire(dict(normalized), cache, offline=offline, refresh=refresh)

    def normalized_fetch(*args: Any, **kwargs: Any):
        try:
            return fetch(*args, **kwargs)
        except direct_exc:
            raise
        except Exception as exc:
            if _looks_like_direct_coverage_unavailable(exc):
                raise direct_exc(str(exc)) from exc
            raise

    setattr(nav, "fetch_or_cache", normalized_fetch)
    try:
        return acquire(dict(normalized), cache, offline=offline, refresh=refresh)
    finally:
        setattr(nav, "fetch_or_cache", fetch)


def _route_scoped_dependency_rows(nav: Any, runtime: Mapping[str, Any], cache: Path) -> tuple[dict[str, Any], dict[tuple[str, str], Any]]:
    """Load direct rows without imposing the obsolete all-local-systems display gate.

    BASE ephemeris remains complete/fail-closed. LOCAL rows are admitted only
    when Sequence-H acquired real rows. Missing local rows remain absent and can
    therefore never be silently promoted to navigation truth.
    """
    load_rows = getattr(nav, "_load_rows", None)
    base_objects = getattr(nav, "BASE_MAP_OBJECTS", None)
    if not callable(load_rows) or not isinstance(base_objects, Mapping):
        raise NavigationServiceError("legacy route-scoped dependency capabilities are unavailable")

    base: dict[str, Any] = {}
    local: dict[tuple[str, str], Any] = {}
    dependencies = ((runtime.get("ephemeris") or {}).get("dependencies") or [])
    for dep in dependencies:
        if not isinstance(dep, Mapping) or not dep.get("row_count"):
            continue
        scope = dep.get("scope")
        if scope == "BASE":
            base[str(dep["id"])] = load_rows(dep, cache)
        elif scope == "LOCAL":
            local[(str(dep["system_id"]), str(dep["id"]))] = load_rows(dep, cache)

    required_base = set(base_objects) - {"SOL"}
    missing_base = sorted(required_base - set(base))
    if missing_base:
        raise NavigationServiceError(f"route-scoped Sequence B requires complete base ephemeris; missing {missing_base}")
    return base, local


def _route_scoped_local_models(nav: Any, runtime: Mapping[str, Any], local_rows: Mapping[tuple[str, str], Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    """Build presentation scales only for parent systems touched by this route.

    The formulas are the frozen Sequence-B formulas; the only change is that an
    unrelated missing moon is skipped instead of dereferenced. This helper does
    not create state vectors and does not change navigation-grade status.
    """
    route_parent = getattr(nav, "_route_parent_system_id", None)
    local_systems = getattr(nav, "LOCAL_SYSTEMS", None)
    median = getattr(nav, "_median", None)
    local_scale = getattr(nav, "_local_scale", None)
    if not all(callable(x) for x in (route_parent, median, local_scale)) or not isinstance(local_systems, Mapping):
        raise NavigationServiceError("legacy local-model capabilities are unavailable")

    route = ((runtime.get("mission") or {}).get("route") or [])
    systems = list(dict.fromkeys(str(route_parent(token)) for token in route))
    out: dict[str, Any] = {}
    max_radius_px = float(contract["canvas"]["local"]["max_orbit_radius_px"])
    for sid in systems:
        moons = ((local_systems.get(sid) or {}).get("moons") or {})
        refs: dict[str, float] = {}
        tracks: dict[str, Any] = {}
        for mid in moons:
            rows = local_rows.get((sid, str(mid)))
            if not rows:
                continue
            radii = [math.sqrt(row[1] * row[1] + row[2] * row[2] + row[3] * row[3]) for row in rows]
            ref = float(median(radii))
            refs[str(mid)] = ref
            tracks[str(mid)] = rows
        scale = local_scale(list(refs.values()), contract)
        max_phys = max(refs.values()) if refs else None
        px_per = (max_radius_px / max_phys) if max_phys else None
        out[sid] = {
            "refs": refs,
            "tracks": tracks,
            "scale": scale,
            "px_per_km": px_per,
            "max_physical_radius_km": max_phys,
        }
    return out


def _canonical_runtime_bytes(nav: Any, runtime: Mapping[str, Any]) -> bytes:
    canon = getattr(nav, "canonical_json_bytes", None)
    if callable(canon):
        return bytes(canon(runtime))
    return json.dumps(runtime, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _route_scoped_sequence_b_flight_gate(
    nav: Any,
    normalized: Mapping[str, Any],
    acquisition: Mapping[str, Any],
    cache: Path,
    b1_package: Path,
) -> tuple[dict[str, Any], dict[str, bytes], str, dict[str, Any], dict[str, Any]]:
    """Compile only the route-scoped authoritative Sequence-B flight payload.

    This fallback exists solely because the frozen Sequence-B presentation
    compiler requires direct moon tracks for every supported local system. The
    actual Sequence-A solver is already route-scoped. We therefore preserve its
    authoritative runtime and call the frozen flight-payload compiler directly,
    twice, using only real acquired rows. No flight math is reimplemented here.
    """
    solve = getattr(nav, "solve_sequence_a", None)
    load_ref = getattr(nav, "load_locked_b1_reference", None)
    compile_flight = getattr(nav, "compile_flight_payload", None)
    if not all(callable(x) for x in (solve, load_ref, compile_flight)):
        raise NavigationServiceError("route-scoped Sequence-B compiler capabilities are unavailable")

    ref = load_ref(b1_package)
    contract = ref["contract"]

    def once() -> tuple[dict[str, Any], bytes, dict[str, Any]]:
        runtime, sequence_a = solve(dict(normalized), dict(acquisition), cache)
        if sequence_a.get("status") != "PASS":
            raise NavigationServiceError("Sequence A failed inside route-scoped Sequence B")
        base, local = _route_scoped_dependency_rows(nav, runtime, cache)
        local_models = _route_scoped_local_models(nav, runtime, local, contract)
        ep_meta = {
            "frame_count": int(runtime["ephemeris"]["time_axis"]["row_count"]),
            "t0_index": 0,
            "solar_view_modes": {"cameras": ref["reference_ephemeris_meta"]["solar_view_modes"]["cameras"]},
            "local_view_modes": {"cameras": ref["reference_ephemeris_meta"]["local_view_modes"]["cameras"]},
        }
        ep_aux = {"base_rows": base, "local_rows": local, "local_models": local_models}
        raw, _flight_object, audit, _decoded = compile_flight(runtime, ep_meta, ep_aux, ref)
        if audit.get("status") != "PASS":
            raise NavigationServiceError("route-scoped Sequence-B flight payload validation failed")
        return runtime, bytes(raw), audit

    runtime1, raw1, audit1 = once()
    runtime2, raw2, audit2 = once()
    runtime_bytes1 = _canonical_runtime_bytes(nav, runtime1)
    runtime_bytes2 = _canonical_runtime_bytes(nav, runtime2)
    if runtime_bytes1 != runtime_bytes2:
        raise NavigationServiceError("route-scoped Sequence-B determinism failed: runtime mismatch")
    if raw1 != raw2:
        raise NavigationServiceError("route-scoped Sequence-B determinism failed: flight payload mismatch")

    runtime_sha = hashlib.sha256(runtime_bytes1).hexdigest()
    payload_sha = hashlib.sha256(raw1).hexdigest()
    validation = {
        "schema": "LOOM_NAV_ROUTE_SCOPED_SEQUENCE_B_VALIDATION_V1",
        "status": "PASS",
        "scope": "ROUTE_SCOPED_FLIGHT_PAYLOAD_ONLY",
        "physics_authority": "FROZEN_SEQUENCE_A_AND_SEQUENCE_B_FLIGHT_COMPILER",
        "all_systems_legacy_presentation": "NOT_COMPILED_DUE_UNRELATED_LOCAL_COVERAGE_GAPS",
        "flight_payload_audit": audit1,
    }
    determinism = {
        "schema": "LOOM_NAV_ROUTE_SCOPED_DETERMINISM_V1",
        "status": "PASS",
        "runtime_sha256": runtime_sha,
        "flight_payload_sha256": payload_sha,
        "second_run_audit_status": audit2.get("status"),
    }
    return runtime1, {"flightSolutionsPayload": raw1}, "", validation, determinism


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
            local_text = local_for_utc(nav, epoch_utc) if callable(local_for_utc) else _melbourne_local_fallback(epoch_utc)
            mission["epoch"] = {
                "local": local_text,
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
        acquisition = _run_acquisition_with_coverage_normalization(
            nav,
            normalized,
            cache,
            offline=offline,
            refresh=refresh,
        )
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
        try:
            runtime, payloads, html, validation, determinism = gate(normalized, acq, cache, b1)
        except Exception as exc:
            if not _is_global_sequence_b_local_completeness_error(exc):
                raise
            runtime, payloads, html, validation, determinism = _route_scoped_sequence_b_flight_gate(
                nav, normalized, acq, cache, b1
            )

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
