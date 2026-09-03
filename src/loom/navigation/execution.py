"""Flight execution boundary for LOOM navigation Phase 2.

This module extracts the authoritative arrival-state transition from the legacy
Navigator CLI without taking campaign persistence authority. It does not write
state files, append history, award jobs, or advance any independent clock.
Those campaign responsibilities remain in the outer Navigator until Phase 6.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import FlightExecutionResult, FlightPlan, NavigationContext


@dataclass
class LegacyFlightExecutionAdapter:
    """Pure adapter for the legacy Navigator's post-solve arrival transition."""

    core: Any

    def execute(self, plan: FlightPlan, context: NavigationContext) -> FlightExecutionResult:
        state = dict(context.campaign_state)
        validate = getattr(self.core, "_validate_state", None)
        deep_copy = getattr(self.core, "_deepcopy", None)
        stamp = getattr(self.core, "_stamp_state", None)
        if not callable(deep_copy) or not callable(stamp):
            raise RuntimeError("legacy Navigator arrival-state helpers are unavailable")
        if callable(validate):
            validate(state)

        packed = dict(plan.payload)
        runtime = packed.get("runtime") or {}
        determinism = packed.get("determinism") or {}
        flight = runtime.get("flight") or {}
        mass_ledger = flight.get("mass_ledger") or {}
        legs = flight.get("legs") or []
        if not legs:
            raise RuntimeError("compiled flight contains no authoritative legs")
        leg = legs[-1]
        arrival_leg = leg.get("arrival") or {}

        try:
            final_epoch = flight["final_epoch_utc"]
            final_remass = float(mass_ledger["final_remass_t"])
            final_wet = float(mass_ledger["final_wet_mass_t"])
            total_remass = float(mass_ledger["total_remass_used_t"])
            state_units = arrival_leg["target_state_source_units"]
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("compiled flight is missing authoritative arrival fields") from exc

        origin = state.get("location_token") or plan.candidate.origin
        destination = plan.candidate.destination
        candidate = dict(plan.candidate.payload)
        metric = candidate.get("metric")
        torch = candidate.get("torch")
        plan_sha = packed.get("plan_sha256")
        runtime_sha = determinism.get("canonical_runtime_sha256")

        arrival = deep_copy(state)
        arrival["epoch_utc"] = final_epoch
        arrival["location_token"] = destination
        arrival["status"] = "ARRIVED_HOLD"
        arrival["ship"]["remass_t"] = final_remass
        arrival["ship"]["wet_mass_t"] = final_wet
        arrival["kinematic_boundary"] = {
            "status": "BODY_RENDEZVOUS",
            "source": "PYTHON_NAV_V1_A_TERMINAL_BOUNDARY",
            "state_source_units": state_units,
        }
        arrival["last_flight"] = {
            "flight_id": plan.flight_id,
            "route": f"{origin}>{destination}",
            "strategy": "DIRECT_NAVIGATION",
            "metric": metric,
            "torch": torch,
            "departure_epoch_utc": state.get("epoch_utc"),
            "arrival_epoch_utc": final_epoch,
            "departure_state_id": state.get("state_id"),
            "committed_plan_sha256": plan_sha,
            "runtime_sha256": runtime_sha,
            "remass_used_t": total_remass,
        }
        arrival = stamp(arrival, int(state["revision"]) + 1)

        return FlightExecutionResult(
            flight_id=plan.flight_id,
            status="ARRIVED_HOLD",
            final_state=arrival,
            payload={
                "runtime_sha256": runtime_sha,
                "plan_sha256": plan_sha,
                "persistence_required": True,
                "persistence_owner": "CAMPAIGN",
            },
        )
