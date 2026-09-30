"""Typed actor-state and spendable-budget contract for CIVPROP Engine V1."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


FORMAT = "CIVPROP_ACTOR_STATE_V1"
CONTRACT_VERSION = "1.0.0"
FACT_SET_STATUS = {"KNOWN_RECORDS", "KNOWN_NONE", "UNKNOWN"}
BUDGET_STATUS = {"KNOWN", "UNKNOWN"}
CAPABILITY_STATUS = {"USABLE", "CONDITIONAL", "UNUSABLE", "UNKNOWN"}
EVENT_TYPES = {"BUDGET_ALLOCATION_SET", "CAPABILITY_SET"}


@dataclass(frozen=True)
class ActorIdentity:
    display_name: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ActorFact:
    record_id: str
    subject_id: Optional[str]
    status: str
    scope: str
    counterparty_id: Optional[str]
    provider_id: Optional[str]
    capability_id: Optional[str]
    valid_from: Optional[int]
    valid_to: Optional[int]
    provenance_refs: tuple[str, ...]
    details: Mapping[str, Any]


@dataclass(frozen=True)
class ActorFactSet:
    status: str
    records: tuple[ActorFact, ...]


@dataclass(frozen=True)
class SpendableAllocation:
    status: str
    amount: Optional[float]
    unit: Optional[str]
    scope: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class CommittedFund:
    commitment_id: str
    status: str
    amount: float
    unit: str
    scope: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ActorBudget:
    spendable_allocation: SpendableAllocation
    committed_funds: tuple[CommittedFund, ...]


@dataclass(frozen=True)
class ActorState:
    actor_id: str
    actor_type: str
    identity: ActorIdentity
    budget: ActorBudget
    ownership: ActorFactSet
    operation: ActorFactSet
    access_rights: ActorFactSet
    contracts: ActorFactSet
    provider_service_access: ActorFactSet
    installed_capability: ActorFactSet
    acquired_capability: ActorFactSet
    experience: ActorFactSet
    owned_infrastructure: ActorFactSet
    relationships: ActorFactSet


@dataclass(frozen=True)
class ActorStateEvent:
    event_id: str
    year: int
    actor_id: str
    event_type: str
    payload: Mapping[str, Any]
    provenance_class: str
    provenance_ref: str


@dataclass(frozen=True)
class ActorStatePackage:
    format: str
    contract_version: str
    as_of_year: int
    actors: tuple[ActorState, ...]
    events: tuple[ActorStateEvent, ...]


def _fact(record: Mapping[str, Any]) -> ActorFact:
    known = {
        "record_id", "subject_id", "status", "scope", "counterparty_id",
        "provider_id", "capability_id", "valid_from", "valid_to",
        "provenance_refs",
    }
    return ActorFact(
        record_id=str(record["record_id"]),
        subject_id=record.get("subject_id"),
        status=str(record["status"]),
        scope=str(record["scope"]),
        counterparty_id=record.get("counterparty_id"),
        provider_id=record.get("provider_id"),
        capability_id=record.get("capability_id"),
        valid_from=None if record.get("valid_from") is None else int(record["valid_from"]),
        valid_to=None if record.get("valid_to") is None else int(record["valid_to"]),
        provenance_refs=tuple(record.get("provenance_refs", ())),
        details={k: v for k, v in record.items() if k not in known},
    )


def _fact_set(data: Mapping[str, Any]) -> ActorFactSet:
    status = str(data["status"])
    if status not in FACT_SET_STATUS:
        raise ValueError("invalid actor fact-set status")
    records = tuple(_fact(x) for x in data.get("records", ()))
    if status == "KNOWN_NONE" and records:
        raise ValueError("KNOWN_NONE fact set cannot contain records")
    if status == "UNKNOWN" and records:
        raise ValueError("UNKNOWN fact set cannot contain asserted records")
    ids = [x.record_id for x in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate actor fact record id")
    for record in records:
        if record.valid_to is not None and record.valid_from is not None:
            if record.valid_to < record.valid_from:
                raise ValueError("invalid actor fact validity")
    return ActorFactSet(status=status, records=records)


def _spendable(data: Mapping[str, Any]) -> SpendableAllocation:
    status = str(data["status"])
    if status not in BUDGET_STATUS:
        raise ValueError("invalid spendable-allocation status")
    amount = None if data.get("amount") is None else float(data["amount"])
    unit = data.get("unit")
    if status == "UNKNOWN":
        if amount is not None or unit is not None:
            raise ValueError("UNKNOWN spendable allocation cannot invent amount or unit")
    else:
        if amount is None or amount < 0 or not unit:
            raise ValueError("KNOWN spendable allocation requires nonnegative amount and unit")
    return SpendableAllocation(
        status=status,
        amount=amount,
        unit=unit,
        scope=str(data["scope"]),
        provenance_refs=tuple(data.get("provenance_refs", ())),
    )


def _committed(data: Mapping[str, Any]) -> CommittedFund:
    amount = float(data["amount"])
    if amount < 0 or not data.get("unit"):
        raise ValueError("invalid committed fund")
    return CommittedFund(
        commitment_id=str(data["commitment_id"]),
        status=str(data["status"]),
        amount=amount,
        unit=str(data["unit"]),
        scope=str(data["scope"]),
        provenance_refs=tuple(data.get("provenance_refs", ())),
    )


def _actor(data: Mapping[str, Any]) -> ActorState:
    identity = data["identity"]
    budget = data["budget"]
    collections = (
        "ownership", "operation", "access_rights", "contracts",
        "provider_service_access", "installed_capability",
        "acquired_capability", "experience", "owned_infrastructure",
        "relationships",
    )
    parsed = {name: _fact_set(data[name]) for name in collections}
    return ActorState(
        actor_id=str(data["actor_id"]),
        actor_type=str(data["actor_type"]),
        identity=ActorIdentity(
            display_name=str(identity["display_name"]),
            provenance_refs=tuple(identity.get("provenance_refs", ())),
        ),
        budget=ActorBudget(
            spendable_allocation=_spendable(budget["spendable_allocation"]),
            committed_funds=tuple(_committed(x) for x in budget.get("committed_funds", ())),
        ),
        **parsed,
    )


def _event(data: Mapping[str, Any], as_of_year: int) -> ActorStateEvent:
    event_type = str(data["event_type"])
    if event_type not in EVENT_TYPES:
        raise ValueError("invalid actor-state event type")
    year = int(data["year"])
    if year < as_of_year:
        raise ValueError("actor-state event predates boundary")
    provenance = data["provenance"]
    payload = dict(data["payload"])
    if event_type == "BUDGET_ALLOCATION_SET":
        if float(payload["amount"]) < 0 or not payload.get("unit") or not payload.get("scope"):
            raise ValueError("invalid budget allocation event")
    if event_type == "CAPABILITY_SET":
        if payload.get("status") not in CAPABILITY_STATUS or not payload.get("capability_id"):
            raise ValueError("invalid capability event")
    return ActorStateEvent(
        event_id=str(data["event_id"]),
        year=year,
        actor_id=str(data["actor_id"]),
        event_type=event_type,
        payload=payload,
        provenance_class=str(provenance["class"]),
        provenance_ref=str(provenance["ref"]),
    )


def load_actor_state_package(data: Mapping[str, Any]) -> ActorStatePackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected actor-state contract")
    as_of_year = int(data["as_of_year"])
    actors = tuple(_actor(x) for x in data.get("actors", ()))
    actor_ids = [x.actor_id for x in actors]
    if not actor_ids or len(actor_ids) != len(set(actor_ids)):
        raise ValueError("actor-state actors must be nonempty and unique")
    events = tuple(_event(x, as_of_year) for x in data.get("events", ()))
    event_ids = [x.event_id for x in events]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError("duplicate actor-state event id")
    unknown_actors = {x.actor_id for x in events} - set(actor_ids)
    if unknown_actors:
        raise ValueError("actor-state event references unknown actor")
    return ActorStatePackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        as_of_year=as_of_year,
        actors=actors,
        events=tuple(sorted(events, key=lambda x: (x.year, x.event_id))),
    )


class ActorStateRuntime:
    """Pure replay view. No state change exists unless represented by a versioned event."""

    def __init__(self, package: ActorStatePackage):
        self.package = package
        self._actors = {x.actor_id: x for x in package.actors}

    def actor(self, actor_id: str) -> ActorState:
        try:
            return self._actors[actor_id]
        except KeyError as exc:
            raise KeyError(f"unknown actor {actor_id}") from exc

    def committed_funds(self, actor_id: str) -> tuple[CommittedFund, ...]:
        return self.actor(actor_id).budget.committed_funds

    def budget(self, actor_id: str, year: int) -> SpendableAllocation:
        actor = self.actor(actor_id)
        current = actor.budget.spendable_allocation
        for event in self.package.events:
            if event.actor_id != actor_id or event.year > year:
                continue
            if event.event_type == "BUDGET_ALLOCATION_SET":
                current = SpendableAllocation(
                    status="KNOWN",
                    amount=float(event.payload["amount"]),
                    unit=str(event.payload["unit"]),
                    scope=str(event.payload["scope"]),
                    provenance_refs=(event.provenance_ref,),
                )
        return current

    def capability_status(self, actor_id: str, capability_id: str, year: int) -> str:
        actor = self.actor(actor_id)
        status = "UNKNOWN"
        for fact_set in (actor.installed_capability, actor.acquired_capability):
            for record in fact_set.records:
                if record.capability_id != capability_id:
                    continue
                if record.valid_from is not None and year < record.valid_from:
                    continue
                if record.valid_to is not None and year > record.valid_to:
                    continue
                if record.status in CAPABILITY_STATUS:
                    status = record.status
        for event in self.package.events:
            if event.actor_id != actor_id or event.year > year:
                continue
            if event.event_type == "CAPABILITY_SET":
                if event.payload["capability_id"] == capability_id:
                    status = str(event.payload["status"])
        return status
