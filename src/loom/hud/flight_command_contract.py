from __future__ import annotations

"""Typed command contract shared by human, LLM, NPC and system pilots.

The origin describes who proposed a command. It never changes execution authority.
Only deterministic flight-control / physics code may apply a command to vehicle state.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

CONTRACT = "LOOM_FLIGHT_COMMAND_V1"
PLAN_CONTRACT = "LOOM_MANEUVER_PLAN_V1"


class CommandOrigin(str, Enum):
    MANUAL = "MANUAL"
    LLM = "LLM"
    NPC = "NPC"
    SYSTEM = "SYSTEM"


class CommandKind(str, Enum):
    COAST = "COAST"
    TORCH_BURN = "TORCH_BURN"
    ROTATE_TO_VECTOR = "ROTATE_TO_VECTOR"
    HOLD_ATTITUDE = "HOLD_ATTITUDE"


class PlanExecutionPolicy(str, Enum):
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    EXPLICIT_EXECUTION = "EXPLICIT_EXECUTION"


@dataclass(frozen=True)
class FlightCommand:
    kind: CommandKind
    origin: CommandOrigin
    duration_s: float | None = None
    torch_mode: str | None = None
    target_direction_inertial: tuple[float, float, float] | None = None
    requested_by: str | None = None

    def __post_init__(self) -> None:
        if self.duration_s is not None and self.duration_s < 0:
            raise ValueError("duration_s must be nonnegative")
        if self.kind in {CommandKind.COAST, CommandKind.TORCH_BURN}:
            if self.duration_s is None or self.duration_s <= 0:
                raise ValueError(f"{self.kind.value} requires positive duration_s")
        if self.kind is CommandKind.TORCH_BURN and not self.torch_mode:
            raise ValueError("TORCH_BURN requires torch_mode")
        if self.kind is CommandKind.ROTATE_TO_VECTOR:
            v = self.target_direction_inertial
            if v is None or len(v) != 3 or sum(float(x) * float(x) for x in v) <= 0:
                raise ValueError("ROTATE_TO_VECTOR requires a nonzero 3-vector")

    def payload(self) -> dict[str, Any]:
        return {
            "contract": CONTRACT,
            "kind": self.kind.value,
            "origin": self.origin.value,
            "duration_s": self.duration_s,
            "torch_mode": self.torch_mode,
            "target_direction_inertial": list(self.target_direction_inertial) if self.target_direction_inertial else None,
            "requested_by": self.requested_by,
            "execution_authority": "NONE_UNTIL_DETERMINISTIC_EXECUTOR_ACCEPTS",
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "FlightCommand":
        return cls(
            kind=CommandKind(str(raw["kind"]).upper()),
            origin=CommandOrigin(str(raw["origin"]).upper()),
            duration_s=None if raw.get("duration_s") is None else float(raw["duration_s"]),
            torch_mode=None if raw.get("torch_mode") is None else str(raw["torch_mode"]).upper(),
            target_direction_inertial=None
            if raw.get("target_direction_inertial") is None
            else tuple(float(x) for x in raw["target_direction_inertial"]),
            requested_by=None if raw.get("requested_by") is None else str(raw["requested_by"]),
        )


@dataclass(frozen=True)
class ManeuverPlan:
    commands: tuple[FlightCommand, ...]
    objective: str
    planner: str
    execution_policy: PlanExecutionPolicy = PlanExecutionPolicy.REVIEW_REQUIRED

    def __post_init__(self) -> None:
        if not self.commands:
            raise ValueError("maneuver plan requires at least one command")
        if not self.objective.strip():
            raise ValueError("maneuver plan objective is required")
        if not self.planner.strip():
            raise ValueError("maneuver plan planner is required")

    def payload(self) -> dict[str, Any]:
        return {
            "contract": PLAN_CONTRACT,
            "objective": self.objective,
            "planner": self.planner,
            "execution_policy": self.execution_policy.value,
            "commands": [c.payload() for c in self.commands],
            "execution_authority": "NONE_UNTIL_EXPLICIT_EXECUTION_BOUNDARY",
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ManeuverPlan":
        return cls(
            commands=tuple(FlightCommand.from_mapping(c) for c in raw["commands"]),
            objective=str(raw["objective"]),
            planner=str(raw["planner"]),
            execution_policy=PlanExecutionPolicy(str(raw.get("execution_policy", "REVIEW_REQUIRED")).upper()),
        )
