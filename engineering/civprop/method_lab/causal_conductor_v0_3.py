"""Event-driven master conductor for CIVPROP V0.3 migration qualification.

NON-CANON / UNPROMOTED.  This module owns simulation time for migrated lanes.
Annual models are adapters scheduled onto the same queue as causal events; there
is deliberately no global annual heartbeat and no call to HybridEngineV1.run().
"""
from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import heapq
import json
from typing import Callable, Mapping, Sequence


QUALIFICATION_CLASS = "CAUSAL_CONDUCTOR_V0_3_NON_CANON_UNPROMOTED"


@dataclass(frozen=True)
class ConductorEventV03:
    event_id: str
    year: int
    phase: int
    event_type: str
    lane_id: str
    status: str
    parent_event_ids: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    payload: Mapping[str, object]


@dataclass(frozen=True)
class ConductorRunV03:
    qualification_class: str
    events: tuple[ConductorEventV03, ...]
    processed_years: tuple[int, ...]
    annual_lane_invocations: Mapping[str, int]
    global_annual_heartbeat_count: int
    final_state: Mapping[str, object]
    canonical_sha256: str


Lane = Callable[[int, Mapping[str, object], Mapping[str, object]], tuple[Mapping[str, object], Sequence[Mapping[str, object]]]]


def _event_id(kind: str, lane: str, year: int, parents, payload) -> str:
    raw = json.dumps([kind, lane, year, list(parents), payload], sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode()
    return "conductor-" + hashlib.sha256(raw).hexdigest()[:20]


def run_conductor(*, start_year: int, end_year: int,
                  initial_state: Mapping[str, object],
                  seed_events: Sequence[Mapping[str, object]],
                  lanes: Mapping[str, Lane]) -> ConductorRunV03:
    """Own time and dispatch typed events to registered lanes.

    Lanes return a state patch and zero or more child events.  A genuinely annual
    lane schedules its own next boundary event.  The conductor itself never
    iterates across the year horizon.
    """
    state = copy.deepcopy(dict(initial_state))
    queue = []
    serial = 0
    events = []
    years = []
    annual_counts: dict[str, int] = {}

    def push(raw):
        nonlocal serial
        year = int(raw["year"])
        if year < start_year or year > end_year:
            return
        serial += 1
        heapq.heappush(queue, (
            year, int(raw.get("phase", 50)), serial,
            str(raw["event_type"]), str(raw["lane_id"]),
            tuple(raw.get("parent_event_ids", ())),
            tuple(raw.get("provenance_refs", ())),
            dict(raw.get("payload", {})),
        ))

    for raw in seed_events:
        push(raw)

    while queue:
        year, phase, _, kind, lane_id, parents, refs, payload = heapq.heappop(queue)
        if not years or years[-1] != year:
            years.append(year)
        eid = _event_id(kind, lane_id, year, parents, payload)
        lane = lanes.get(lane_id)
        if lane is None:
            events.append(ConductorEventV03(
                eid, year, phase, kind, lane_id, "BLOCKED_UNKNOWN_LANE",
                parents, refs, payload,
            ))
            continue
        patch, children = lane(year, state, payload)
        for key, value in dict(patch).items():
            state[key] = copy.deepcopy(value)
        if kind == "ANNUAL_LANE_BOUNDARY":
            annual_counts[lane_id] = annual_counts.get(lane_id, 0) + 1
        events.append(ConductorEventV03(
            eid, year, phase, kind, lane_id, "PROCESSED",
            parents, refs, payload,
        ))
        for child in children:
            c = dict(child)
            c.setdefault("parent_event_ids", (eid,))
            push(c)

    plain = {
        "events": [x.__dict__ for x in events],
        "processed_years": years,
        "annual_lane_invocations": annual_counts,
        "global_annual_heartbeat_count": 0,
        "final_state": state,
    }
    # Stream canonical JSON into the digest.  This preserves the exact canonical
    # byte contract while avoiding a second giant in-memory JSON string at run end.
    digest = hashlib.sha256()
    encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"), allow_nan=False)
    for chunk in encoder.iterencode(plain):
        digest.update(chunk.encode())
    sha = digest.hexdigest()
    return ConductorRunV03(
        QUALIFICATION_CLASS, tuple(events), tuple(years),
        dict(sorted(annual_counts.items())), 0, state, sha,
    )


def annual_authority_lane(*, lane_id: str, values_by_year: Mapping[int, object],
                          state_key: str, provenance_ref: str) -> Lane:
    """Adapt a true annual authority/model to the event queue without a heartbeat."""
    values = {int(k): copy.deepcopy(v) for k, v in values_by_year.items()}

    def lane(year, state, payload):
        if year not in values:
            raise ValueError(f"{lane_id}: annual authority missing year {year}")
        patch = {state_key: copy.deepcopy(values[year])}
        children = []
        next_year = year + 1
        if next_year in values:
            children.append({
                "year": next_year,
                "phase": 10,
                "event_type": "ANNUAL_LANE_BOUNDARY",
                "lane_id": lane_id,
                "provenance_refs": (provenance_ref,),
                "payload": {},
            })
        return patch, children
    return lane


def project_lifecycle_lane(*, project_id: str, activation_lag_years: int = 1) -> Lane:
    """Small causal lifecycle adapter proving nonannual descendants share the clock."""
    def lane(year, state, payload):
        projects = copy.deepcopy(state.get("projects", {}))
        project = copy.deepcopy(projects.get(project_id, {}))
        kind = str(payload.get("action"))
        children = []
        if kind == "REVIEW":
            if project.get("status") != "COMMITTED":
                raise ValueError("PROJECT_NOT_COMMITTED")
            project["status"] = "ACTIVATION_AUTHORIZED"
            children.append({
                "year": year + activation_lag_years,
                "phase": 40,
                "event_type": "PROJECT_LIFECYCLE_EVENT",
                "lane_id": "PROJECT_LIFECYCLE",
                "provenance_refs": tuple(payload.get("provenance_refs", ())),
                "payload": {"action": "ACTIVATE"},
            })
        elif kind == "ACTIVATE":
            if project.get("status") != "ACTIVATION_AUTHORIZED":
                raise ValueError("ACTIVATION_NOT_AUTHORIZED")
            project["status"] = "ACTIVE"
        else:
            raise ValueError("UNKNOWN_PROJECT_LIFECYCLE_ACTION")
        projects[project_id] = project
        return {"projects": projects}, children
    return lane


def run_earth_project_conductor(*, earth_population_rows: Sequence[Mapping[str, object]],
                                committed_state: Mapping[str, object],
                                project_id: str,
                                review_year: int,
                                timeline_events: Sequence[Mapping[str, object]] = (),
                                timeline_lane_handler: Lane | None = None,
                                start_year: int = 2026,
                                end_year: int = 2226) -> ConductorRunV03:
    """Qualified migration seam: real Earth annual authority + causal project events.

    The committed state is expected to come from Gate-G atomic transaction logic.
    This function does not create projects or debit budgets itself.
    """
    values = {int(r["year"]): float(r["biological_population"])
              for r in earth_population_rows}
    expected = set(range(start_year, end_year + 1))
    if set(values) != expected:
        raise ValueError("EARTH_AUTHORITY_HORIZON_NOT_EXACT")
    project = committed_state.get("projects", {}).get(project_id)
    if project is None or project.get("status") != "COMMITTED":
        raise ValueError("CONDUCTOR_REQUIRES_COMMITTED_PROJECT")
    refs = tuple(project.get("provenance_refs", ()))
    if not refs:
        raise ValueError("CONDUCTOR_PROJECT_PROVENANCE_REQUIRED")

    earth_lane = annual_authority_lane(
        lane_id="EARTH_DEMOGRAPHY",
        values_by_year=values,
        state_key="earth_biological_population",
        provenance_ref="GAP014_PROMOTED_EARTH_AUTHORITY",
    )
    project_lane = project_lifecycle_lane(project_id=project_id)
    seeds = [
        {
            "year": start_year, "phase": 10,
            "event_type": "ANNUAL_LANE_BOUNDARY",
            "lane_id": "EARTH_DEMOGRAPHY",
            "provenance_refs": ("GAP014_PROMOTED_EARTH_AUTHORITY",),
            "payload": {},
        },
        {
            "year": int(review_year), "phase": 30,
            "event_type": "PROJECT_LIFECYCLE_EVENT",
            "lane_id": "PROJECT_LIFECYCLE",
            "provenance_refs": refs,
            "payload": {"action": "REVIEW", "provenance_refs": refs},
        },
    ]
    seeds.extend(dict(x) for x in timeline_events)
    lanes = {
        "EARTH_DEMOGRAPHY": earth_lane,
        "PROJECT_LIFECYCLE": project_lane,
    }
    if timeline_events:
        if timeline_lane_handler is None:
            raise ValueError("TIMELINE_EVENTS_REQUIRE_TIMELINE_LANE")
        lanes["TIMELINE"] = timeline_lane_handler
    return run_conductor(
        start_year=start_year, end_year=end_year,
        initial_state=committed_state, seed_events=seeds, lanes=lanes,
    )
