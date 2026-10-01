"""Pressure Observability V1 adapter for Hybrid.

Read-only instrumentation. It mirrors internal pressure transitions and
qualification arithmetic, verifies equivalence, and emits immutable audit records.
"""
from __future__ import annotations

from dataclasses import replace
import math

from engineering.civprop.contracts.pressure_observability_v1 import (
    CAUSAL_SEMANTICS,
    LEGACY_SEMANTICS,
    PressureObservabilityRuntime,
)


class PressureLaneV1:
    def __init__(self, scenario, recorder):
        if scenario.pressure_observability_v1 is None:
            raise ValueError("PressureLaneV1 requires pressure observability package")
        self.scenario = scenario
        self.recorder = recorder
        self.runtime = PressureObservabilityRuntime(
            scenario.pressure_observability_v1
        )
        self._causal_states = {}
        self._legacy_states = {}
        self._qualification_index = {}

    def causal_update(
        self,
        *,
        year: int,
        previous_pressure,
        observations,
        resulting_pressure,
    ) -> None:
        channel_by_id = {
            x.channel_id: x for x in self.scenario.demand_pressure_v1.channels
        }
        self._causal_states = {}
        for observation in observations:
            key = (observation.location_id, observation.channel_id)
            channel = channel_by_id[observation.channel_id]
            state = self.runtime.causal_state(
                year=year,
                location_id=observation.location_id,
                channel_id=observation.channel_id,
                unit=observation.unit,
                opening_pressure=float(previous_pressure.get(key, 0.0)),
                decay=channel.decay,
                unmet_demand=observation.unmet,
                gain=channel.gain,
                required=observation.required,
                available=observation.available,
            )
            actual = float(resulting_pressure.get(key, 0.0))
            if not math.isclose(
                state.prequalification_pressure,
                actual,
                rel_tol=0,
                abs_tol=1e-12,
            ):
                raise ValueError("pressure ledger diverges from causal engine state")
            self._causal_states[key] = state
            self.recorder.pressure_states.append(state)

            if not self.runtime.package.emit_contributions:
                continue
            for component in observation.quantified_components:
                self.recorder.pressure_contributions.append(
                    self.runtime.contribution(
                        pressure_state_id=state.pressure_state_id,
                        year=year,
                        location_id=observation.location_id,
                        component_type=component.component_type,
                        source_id=component.source_id,
                        quantity=component.quantity,
                        unit=component.unit,
                        sign=1,
                        semantics=CAUSAL_SEMANTICS,
                        channel_id=observation.channel_id,
                    )
                )
            if observation.available:
                self.recorder.pressure_contributions.append(
                    self.runtime.contribution(
                        pressure_state_id=state.pressure_state_id,
                        year=year,
                        location_id=observation.location_id,
                        component_type=observation.available_component_type,
                        source_id=(
                            observation.available_source_id
                            or f"state:{channel.available_field}"
                        ),
                        quantity=observation.available,
                        unit=observation.unit,
                        sign=-1,
                        semantics=CAUSAL_SEMANTICS,
                        channel_id=observation.channel_id,
                    )
                )

    def legacy_update(
        self,
        *,
        year: int,
        opening_pressure,
        structural_signals,
        resulting_pressure,
        decay: float,
        gain: float,
    ) -> None:
        self._legacy_states = {}
        keys = set(opening_pressure) | set(structural_signals) | set(resulting_pressure)
        for location_id, project_id in sorted(keys):
            state = self.runtime.legacy_state(
                year=year,
                location_id=location_id,
                project_archetype_id=project_id,
                opening_pressure=float(opening_pressure.get((location_id, project_id), 0.0)),
                decay=decay,
                structural_signal=float(
                    structural_signals.get((location_id, project_id), 0.0)
                ),
                gain=gain,
                discharge=0.0,
            )
            actual = float(resulting_pressure.get((location_id, project_id), 0.0))
            if not math.isclose(
                state.prequalification_pressure,
                actual,
                rel_tol=0,
                abs_tol=1e-12,
            ):
                raise ValueError("pressure ledger diverges from legacy engine state")
            self._legacy_states[(location_id, project_id)] = state

            if (
                self.runtime.package.emit_contributions
                and state.structural_signal
            ):
                self.recorder.pressure_contributions.append(
                    self.runtime.contribution(
                        pressure_state_id=state.pressure_state_id,
                        year=year,
                        location_id=location_id,
                        component_type="LEGACY_STRUCTURAL_SIGNAL",
                        source_id=f"legacy:{project_id}",
                        quantity=state.structural_signal,
                        unit="legacy_structural_signal_unit",
                        sign=1,
                        semantics=LEGACY_SEMANTICS,
                        project_archetype_id=project_id,
                    )
                )

    def causal_qualification(
        self,
        *,
        year: int,
        actor_id: str,
        opportunity,
        threshold: float,
    ):
        outputs = {}
        units = {}
        for channel in self.scenario.demand_pressure_v1.channels:
            output = float(
                getattr(
                    opportunity.project.output_capacities,
                    channel.available_field,
                )
            )
            if output > 0:
                outputs[channel.channel_id] = output
                units[channel.channel_id] = channel.unit
        record = self.runtime.causal_qualification(
            year=year,
            actor_id=actor_id,
            location_id=opportunity.location_id,
            project_archetype_id=opportunity.project.project_archetype_id,
            threshold=threshold,
            pressure_states=self._causal_states,
            project_outputs=outputs,
            channel_units=units,
        )
        self._store_qualification(record)
        return record

    def legacy_qualification(
        self,
        *,
        year: int,
        actor_id: str,
        opportunity,
        threshold: float,
    ):
        key = (
            opportunity.location_id,
            opportunity.project.project_archetype_id,
        )
        state = self._legacy_states.get(key)
        if state is None:
            state = self.runtime.legacy_state(
                year=year,
                location_id=opportunity.location_id,
                project_archetype_id=opportunity.project.project_archetype_id,
                opening_pressure=0.0,
                decay=0.0,
                structural_signal=0.0,
                gain=1.0,
                discharge=0.0,
            )
            self._legacy_states[key] = state
        record = self.runtime.legacy_qualification(
            year=year,
            actor_id=actor_id,
            location_id=opportunity.location_id,
            project_archetype_id=opportunity.project.project_archetype_id,
            threshold=threshold,
            pressure_state=state,
            project_capital_cost=opportunity.project.capital_cost,
        )
        self._store_qualification(record)
        return record

    def _store_qualification(self, record) -> None:
        key = (
            record.year,
            record.actor_id,
            record.location_id,
            record.project_archetype_id,
        )
        if key in self._qualification_index:
            raise ValueError("duplicate pressure qualification record")
        self._qualification_index[key] = len(
            self.recorder.pressure_qualifications
        )
        self.recorder.pressure_qualifications.append(record)

    def link_selected_decision(
        self,
        *,
        year: int,
        actor_id: str,
        location_id: str,
        project_archetype_id: str,
        decision_id: str,
    ) -> None:
        key = (
            year,
            actor_id,
            location_id,
            project_archetype_id,
        )
        index = self._qualification_index.get(key)
        if index is None:
            raise ValueError("selected decision has no pressure qualification")
        current = self.recorder.pressure_qualifications[index]
        if not current.pressure_qualified:
            raise ValueError("selected decision references unqualified pressure")
        self.recorder.pressure_qualifications[index] = self.runtime.link_decision(
            current,
            decision_id,
            selected=True,
        )

    def close_legacy_year(self, *, resulting_pressure) -> None:
        if not self._legacy_states:
            return
        for key in sorted(self._legacy_states):
            state = self._legacy_states[key]
            closing = float(resulting_pressure.get(key, 0.0))
            discharge = max(
                0.0,
                state.prequalification_pressure - closing,
            )
            if (
                not self.runtime.package.record_legacy_discharge
                and discharge > 1e-12
            ):
                raise ValueError("legacy discharge occurred but recording disabled")
            updated = replace(
                state,
                discharge=discharge,
                closing_pressure=closing,
            )
            self.runtime.validate_state(updated)
            self.recorder.pressure_states.append(updated)


__all__ = ["PressureLaneV1"]
