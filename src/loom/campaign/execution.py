"""Canonical campaign persistence boundary for Phase 6.

Navigator computes authoritative flight results. This module alone converts a
validated FlightExecutionResult into persistent campaign state/history using the
existing RC6.1 state and history machinery. It performs no navigation physics.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
import copy
import json
import os

from loom.navigation import FlightExecutionResult, FlightPlan, NavigationContext
from loom.navigation.execution import canonical_runtime_sha256, normalize_legacy_determinism
from loom.runtime import resolve_runtime_roots
from .clock import CampaignClockError, clock_from_state, validate_clock_advance

CAMPAIGN_EXECUTION_VERSION = "LOOM_CAMPAIGN_EXECUTION_V1"


class CampaignExecutionError(RuntimeError):
    """Raised when a flight cannot be safely committed to campaign authority."""


@dataclass(frozen=True)
class CampaignFlightCommitV1:
    flight_id: str
    state_before_id: str | None
    state_after_id: str | None
    revision_before: int
    revision_after: int
    origin: str
    destination: str
    departure_epoch_utc: str
    arrival_epoch_utc: str
    remass_before_t: float
    remass_after_t: float
    state_path: str
    history_path: str
    history_record_number: int
    history_record_sha256: str
    final_state: Mapping[str, Any]
    contract: str = CAMPAIGN_EXECUTION_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CampaignExecutionError(f"cannot read canonical campaign state: {path}") from exc
    if not isinstance(data, dict):
        raise CampaignExecutionError("canonical campaign state must be a JSON object")
    return data


def _restore_bytes(path: Path, before: bytes | None) -> None:
    if before is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return
    tmp = path.with_name(path.name + ".phase6-rollback")
    tmp.write_bytes(before)
    os.replace(tmp, path)


class LegacyCampaignExecutionService:
    """Campaign-authority adapter over the frozen RC6.1 persistence machinery."""

    def __init__(self, core: Any):
        self.core = core

    def _require(self, name: str) -> Any:
        value = getattr(self.core, name, None)
        if value is None:
            raise CampaignExecutionError(f"legacy campaign capability unavailable: {name}")
        return value

    def commit_flight(
        self,
        plan: FlightPlan,
        execution: FlightExecutionResult,
        context: NavigationContext,
    ) -> CampaignFlightCommitV1:
        # Split-root runtime contract: Navigator code lives under APP while
        # canonical campaign state/history live under CAMPAIGN.  The legacy
        # single-root assumption is invalid after runtime cutover.
        roots = resolve_runtime_roots(app_root=context.runtime_root or None)
        app_root = Path(roots.app_root).expanduser().resolve()
        campaign_root = Path(roots.campaign_root).expanduser().resolve()
        if not app_root.exists():
            raise CampaignExecutionError("application root is required for persistent execution")
        if not campaign_root.exists():
            raise CampaignExecutionError("campaign root is required for persistent execution")

        state_file = str(getattr(self.core, "STATE_FILE", "LOOM_STATE_V1.json"))
        backup_file = str(getattr(self.core, "BACKUP_FILE", "LOOM_STATE_V1.bak"))
        history_file = str(getattr(self.core, "HISTORY_FILE", "LOOM_CAMPAIGN_HISTORY.jsonl.gz"))
        state_path = campaign_root / state_file
        backup_path = campaign_root / backup_file
        history_path = campaign_root / history_file
        if not state_path.is_file():
            raise CampaignExecutionError(f"canonical campaign state not found: {state_path}")

        expected = copy.deepcopy(dict(context.campaign_state))
        current = _read_json(state_path)
        validate = self._require("_validate_state")
        validate(current)
        validate(expected)

        if current != expected:
            raise CampaignExecutionError(
                "campaign state changed after planning; rediscover and recommit the flight"
            )

        if execution.flight_id != plan.flight_id:
            raise CampaignExecutionError("execution flight_id differs from committed plan")
        payload = dict(execution.payload or {})
        if payload.get("persistence_owner") != "CAMPAIGN":
            raise CampaignExecutionError("Navigator execution did not delegate persistence to CAMPAIGN")
        if execution.status != "ARRIVED_HOLD":
            raise CampaignExecutionError(f"unsupported Phase-6 terminal status: {execution.status}")

        arrival = copy.deepcopy(dict(execution.final_state))
        validate(arrival)
        try:
            before_clock = clock_from_state(current)
            after_clock = clock_from_state(arrival)
            validate_clock_advance(before_clock, after_clock)
        except CampaignClockError as exc:
            raise CampaignExecutionError(f"invalid campaign clock transition: {exc}") from exc

        try:
            revision_before = int(current["revision"])
            revision_after = int(arrival["revision"])
            last = dict(arrival["last_flight"])
            ship_before = dict(current["ship"])
            ship_after = dict(arrival["ship"])
        except Exception as exc:
            raise CampaignExecutionError("arrival state is missing campaign transition fields") from exc
        if revision_after != revision_before + 1:
            raise CampaignExecutionError("arrival revision is not exactly one campaign step")
        if last.get("flight_id") != plan.flight_id:
            raise CampaignExecutionError("arrival state does not identify the committed flight")
        if last.get("departure_state_id") != current.get("state_id"):
            raise CampaignExecutionError("arrival state does not descend from the current campaign state")

        packed = dict(plan.payload)
        runtime = packed.get("runtime") or {}
        determinism = packed.get("determinism") or {}
        html = packed.get("html") or ""
        plan_sha = packed.get("plan_sha256")
        runtime_sha = canonical_runtime_sha256(determinism)
        if last.get("runtime_sha256") != runtime_sha or last.get("committed_plan_sha256") != plan_sha:
            raise CampaignExecutionError("arrival provenance differs from the committed Navigator plan")

        load_core = self._require("_load_core")
        outcome_summary = self._require("_outcome_summary")
        ledger_type = self._require("HistoryLedger")
        atomic_save = self._require("_atomic_save")
        nav = load_core(app_root / "LOOM_Navigator_Internal_SequenceH")
        legacy_determinism = normalize_legacy_determinism(determinism)
        outcome = outcome_summary(
            nav, runtime, legacy_determinism, html, current, arrival, plan.flight_id, plan_sha
        )

        state_before_bytes = state_path.read_bytes()
        history_before_bytes = history_path.read_bytes() if history_path.exists() else None
        record = None
        try:
            ledger = ledger_type(campaign_root, current)
            record = ledger.append(
                "FLIGHT_ARRIVED",
                current,
                arrival,
                outcome,
                flight_id=plan.flight_id,
                event_epoch_utc=arrival["epoch_utc"],
                state_after_snapshot=arrival,
            )
            atomic_save(state_path, backup_path, arrival)
            ledger.state = arrival
            persisted = _read_json(state_path)
            validate(persisted)
            if persisted != arrival:
                raise CampaignExecutionError("campaign state read-back differs from committed arrival")
        except Exception as exc:
            _restore_bytes(state_path, state_before_bytes)
            _restore_bytes(history_path, history_before_bytes)
            if isinstance(exc, CampaignExecutionError):
                raise
            raise CampaignExecutionError(f"campaign flight commit failed: {type(exc).__name__}: {exc}") from exc

        assert record is not None
        return CampaignFlightCommitV1(
            flight_id=plan.flight_id,
            state_before_id=current.get("state_id"),
            state_after_id=arrival.get("state_id"),
            revision_before=revision_before,
            revision_after=revision_after,
            origin=str(current.get("location_token") or plan.candidate.origin),
            destination=str(arrival.get("location_token") or plan.candidate.destination),
            departure_epoch_utc=str(current.get("epoch_utc")),
            arrival_epoch_utc=str(arrival.get("epoch_utc")),
            remass_before_t=float(ship_before["remass_t"]),
            remass_after_t=float(ship_after["remass_t"]),
            state_path=str(state_path),
            history_path=str(history_path),
            history_record_number=int(record["record_number"]),
            history_record_sha256=str(record["record_sha256"]),
            final_state=arrival,
        )
