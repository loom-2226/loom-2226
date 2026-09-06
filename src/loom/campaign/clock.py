"""Canonical campaign clock service for LOOM 2226.

Stage B deliberately keeps JSON/history as campaign authority. This service is
an adapter over that authority: it exposes a typed CampaignClockState, validates
monotonic advancement, and provides campaign/revision/epoch stamps for downstream
systems without allowing presentation/playback code to mutate campaign time.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
import json

from loom.application.contracts import CampaignClockState

CAMPAIGN_CLOCK_CONTRACT = "LOOM_CAMPAIGN_CLOCK_V1"
LEGACY_CAMPAIGN_ID = "LOOM_CAMPAIGN_V1"


class CampaignClockError(RuntimeError):
    """Raised when campaign clock authority is missing, invalid, or stale."""


def _parse_utc(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise CampaignClockError(f"invalid campaign epoch_utc: {value!r}") from exc
    if parsed.tzinfo is None:
        raise CampaignClockError("campaign epoch_utc must include timezone")
    return parsed.astimezone(timezone.utc)


def _campaign_id(state: Mapping[str, Any]) -> str:
    value = str(state.get("campaign_id") or "").strip()
    return value or LEGACY_CAMPAIGN_ID


def clock_from_state(state: Mapping[str, Any]) -> CampaignClockState:
    """Build the canonical typed clock snapshot from one campaign state object."""
    try:
        revision = int(state["revision"])
        epoch_utc = str(state["epoch_utc"])
    except Exception as exc:
        raise CampaignClockError("campaign state is missing revision/epoch_utc") from exc
    _parse_utc(epoch_utc)
    last = state.get("last_flight") or {}
    if not isinstance(last, Mapping):
        last = {}
    transition_id = (
        last.get("flight_id")
        or state.get("last_transition_id")
        or state.get("state_id")
    )
    return CampaignClockState(
        campaign_id=_campaign_id(state),
        revision=revision,
        epoch_utc=epoch_utc,
        last_transition_id=str(transition_id) if transition_id is not None else None,
        payload={
            "contract": CAMPAIGN_CLOCK_CONTRACT,
            "authority": "CAMPAIGN_JSON_HISTORY",
            "state_id": state.get("state_id"),
        },
    )


def validate_clock_advance(before: CampaignClockState, after: CampaignClockState) -> None:
    """Validate one authorized campaign transition's clock movement.

    Stage-B canonical transitions advance exactly one campaign revision and may
    preserve or advance time, but may never move it backwards.
    """
    if before.campaign_id != after.campaign_id:
        raise CampaignClockError("campaign identity changed across transition")
    if after.revision != before.revision + 1:
        raise CampaignClockError("campaign revision must advance exactly one step")
    if _parse_utc(after.epoch_utc) < _parse_utc(before.epoch_utc):
        raise CampaignClockError("campaign time cannot move backward")


def is_stamp_current(
    clock: CampaignClockState,
    *,
    campaign_revision: int,
    solution_epoch: str,
) -> bool:
    """Return whether a solved/planned object is current for this campaign clock."""
    return int(campaign_revision) == clock.revision and _parse_utc(solution_epoch) == _parse_utc(clock.epoch_utc)


class LegacyCampaignClockService:
    """Read-only clock adapter over current JSON/history campaign authority."""

    def __init__(self, campaign_root: Path | str, core: Any | None = None):
        self.root = Path(campaign_root).expanduser().resolve()
        self.core = core

    @property
    def state_path(self) -> Path:
        filename = str(getattr(self.core, "STATE_FILE", "LOOM_STATE_V1.json"))
        return self.root / filename

    def _read_state(self) -> dict[str, Any]:
        try:
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise CampaignClockError(f"cannot read canonical campaign state: {self.state_path}") from exc
        if not isinstance(value, dict):
            raise CampaignClockError("canonical campaign state must be a JSON object")
        validate = getattr(self.core, "_validate_state", None)
        if callable(validate):
            validate(value)
        return value

    def now(self) -> CampaignClockState:
        """Return the current authoritative campaign clock snapshot."""
        return clock_from_state(self._read_state())

    def stamp(self) -> dict[str, Any]:
        """Return a serialization-friendly authority stamp for plans/solutions."""
        return asdict(self.now())

    def assert_current(self, expected: CampaignClockState) -> CampaignClockState:
        """Fail if campaign revision or epoch changed since an earlier snapshot."""
        current = self.now()
        if current.campaign_id != expected.campaign_id:
            raise CampaignClockError("campaign identity changed")
        if current.revision != expected.revision or _parse_utc(current.epoch_utc) != _parse_utc(expected.epoch_utc):
            raise CampaignClockError("campaign clock changed; re-resolve/replan against current state")
        return current
