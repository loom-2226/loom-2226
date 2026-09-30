"""CIVPROP Pressure Observability V1.

Pure audit contracts for pressure transitions and qualification. This module does
not choose projects or mutate simulation state. It mirrors pressure arithmetic,
assigns stable IDs, and fails closed if emitted state does not reconstruct.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional


FORMAT = "CIVPROP_PRESSURE_OBSERVABILITY_V1"
CONTRACT_VERSION = "1.0.0"
CAUSAL_SEMANTICS = "CAUSAL_DEMAND_CHANNEL_PRESSURE"
LEGACY_SEMANTICS = "LEGACY_PROJECT_PRESSURE"


def _finite(value: Any, name: str, *, nonnegative: bool = True) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    if nonnegative and out < 0:
        raise ValueError(f"{name} must be nonnegative")
    return out


def _stable_id(prefix: str, *parts: object) -> str:
    payload = json.dumps(parts, separators=(",", ":"), allow_nan=False).encode()
    return f"{prefix}-" + hashlib.sha256(payload).hexdigest()[:20]


@dataclass(frozen=True)
class PressureObservabilityPackage:
    format: str
    contract_version: str
    emit_contributions: bool
    emit_all_qualifications: bool
    record_legacy_discharge: bool


@dataclass(frozen=True)
class PressureContributionV1:
    contribution_id: str
    pressure_state_id: str
    year: int
    location_id: str
    component_type: str
    source_id: str
    quantity: float
    unit: str
    sign: int
    semantics: str
    channel_id: Optional[str] = None
    project_archetype_id: Optional[str] = None


@dataclass(frozen=True)
class PressureStateV1:
    pressure_state_id: str
    year: int
    location_id: str
    semantics: str
    unit: str
    opening_pressure: float
    decay: float
    decayed_pressure: float
    required: Optional[float]
    available: Optional[float]
    unmet_demand: Optional[float]
    structural_signal: Optional[float]
    gain: float
    added_pressure: float
    prequalification_pressure: float
    discharge: float
    closing_pressure: float
    channel_id: Optional[str] = None
    project_archetype_id: Optional[str] = None


@dataclass(frozen=True)
class PressureChannelRatioV1:
    channel_id: str
    pressure_state_id: Optional[str]
    unit: str
    pressure: float
    project_output: float
    ratio: float


@dataclass(frozen=True)
class PressureQualificationV1:
    qualification_id: str
    year: int
    actor_id: str
    location_id: str
    project_archetype_id: str
    semantics: str
    threshold: float
    pressure_qualified: bool
    controlling_ratio: float
    controlling_channel_id: Optional[str]
    channel_ratios: tuple[PressureChannelRatioV1, ...]
    decision_id: Optional[str] = None
    selected: bool = False


def load_pressure_observability_package(
    data: Mapping[str, Any],
) -> PressureObservabilityPackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected pressure-observability contract")
    values = {}
    for key in (
        "emit_contributions",
        "emit_all_qualifications",
        "record_legacy_discharge",
    ):
        value = data.get(key)
        if type(value) is not bool:
            raise ValueError(f"{key} must be boolean")
        values[key] = value
    return PressureObservabilityPackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        **values,
    )


def load_pressure_observability_path(
    path: Path,
) -> PressureObservabilityPackage:
    return load_pressure_observability_package(json.loads(Path(path).read_text()))


class PressureObservabilityRuntime:
    def __init__(self, package: PressureObservabilityPackage):
        self.package = package

    @staticmethod
    def causal_state_id(year: int, location_id: str, channel_id: str) -> str:
        return _stable_id(
            "ps",
            CAUSAL_SEMANTICS,
            int(year),
            location_id,
            channel_id,
        )

    @staticmethod
    def legacy_state_id(
        year: int,
        location_id: str,
        project_archetype_id: str,
    ) -> str:
        return _stable_id(
            "ps",
            LEGACY_SEMANTICS,
            int(year),
            location_id,
            project_archetype_id,
        )

    def causal_state(
        self,
        *,
        year: int,
        location_id: str,
        channel_id: str,
        unit: str,
        opening_pressure: float,
        decay: float,
        unmet_demand: float,
        gain: float,
        required: float,
        available: float,
    ) -> PressureStateV1:
        opening = _finite(opening_pressure, "opening pressure")
        decay_value = _finite(decay, "decay")
        if not 0 <= decay_value < 1:
            raise ValueError("causal decay must be in [0,1)")
        gain_value = _finite(gain, "gain")
        required_value = _finite(required, "required")
        available_value = _finite(available, "available")
        unmet_value = _finite(unmet_demand, "unmet demand")
        expected_unmet = max(0.0, required_value - available_value)
        if not math.isclose(unmet_value, expected_unmet, rel_tol=0, abs_tol=1e-12):
            raise ValueError("unmet demand does not reconstruct from requirement/capacity")
        decayed = opening * decay_value
        added = unmet_value * gain_value
        prequalification = decayed + added
        state = PressureStateV1(
            pressure_state_id=self.causal_state_id(
                year,
                location_id,
                channel_id,
            ),
            year=int(year),
            location_id=location_id,
            semantics=CAUSAL_SEMANTICS,
            unit=unit,
            opening_pressure=opening,
            decay=decay_value,
            decayed_pressure=decayed,
            required=required_value,
            available=available_value,
            unmet_demand=unmet_value,
            structural_signal=None,
            gain=gain_value,
            added_pressure=added,
            prequalification_pressure=prequalification,
            discharge=0.0,
            closing_pressure=prequalification,
            channel_id=channel_id,
            project_archetype_id=None,
        )
        self.validate_state(state)
        return state

    def legacy_state(
        self,
        *,
        year: int,
        location_id: str,
        project_archetype_id: str,
        opening_pressure: float,
        decay: float,
        structural_signal: float,
        gain: float,
        discharge: float,
    ) -> PressureStateV1:
        opening = _finite(opening_pressure, "opening pressure")
        decay_value = _finite(decay, "decay")
        signal = _finite(structural_signal, "structural signal")
        gain_value = _finite(gain, "gain")
        discharge_value = _finite(discharge, "discharge")
        decayed = opening * decay_value
        added = signal * gain_value
        prequalification = decayed + added
        closing = max(0.0, prequalification - discharge_value)
        state = PressureStateV1(
            pressure_state_id=self.legacy_state_id(
                year,
                location_id,
                project_archetype_id,
            ),
            year=int(year),
            location_id=location_id,
            semantics=LEGACY_SEMANTICS,
            unit="legacy_pressure_unit",
            opening_pressure=opening,
            decay=decay_value,
            decayed_pressure=decayed,
            required=None,
            available=None,
            unmet_demand=None,
            structural_signal=signal,
            gain=gain_value,
            added_pressure=added,
            prequalification_pressure=prequalification,
            discharge=discharge_value,
            closing_pressure=closing,
            channel_id=None,
            project_archetype_id=project_archetype_id,
        )
        self.validate_state(state)
        return state

    def validate_state(self, state: PressureStateV1) -> None:
        for field in (
            "opening_pressure",
            "decay",
            "decayed_pressure",
            "gain",
            "added_pressure",
            "prequalification_pressure",
            "discharge",
            "closing_pressure",
        ):
            _finite(getattr(state, field), field)
        if state.semantics == CAUSAL_SEMANTICS:
            if state.channel_id is None or state.project_archetype_id is not None:
                raise ValueError("causal pressure identity mismatch")
            if any(
                value is None
                for value in (state.required, state.available, state.unmet_demand)
            ):
                raise ValueError("causal pressure requires demand fields")
            if state.structural_signal is not None:
                raise ValueError("causal pressure cannot carry legacy structural signal")
            if not math.isclose(state.discharge, 0.0, rel_tol=0, abs_tol=1e-12):
                raise ValueError("causal pressure cannot use synthetic discharge")
            expected_added = float(state.unmet_demand) * state.gain
        elif state.semantics == LEGACY_SEMANTICS:
            if state.project_archetype_id is None or state.channel_id is not None:
                raise ValueError("legacy pressure identity mismatch")
            if state.structural_signal is None:
                raise ValueError("legacy pressure requires structural signal")
            if any(
                value is not None
                for value in (state.required, state.available, state.unmet_demand)
            ):
                raise ValueError("legacy pressure cannot claim causal demand fields")
            expected_added = float(state.structural_signal) * state.gain
        else:
            raise ValueError("unknown pressure semantics")

        expected_decayed = state.opening_pressure * state.decay
        expected_pre = expected_decayed + expected_added
        expected_close = max(0.0, expected_pre - state.discharge)
        if not math.isclose(
            state.decayed_pressure,
            expected_decayed,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError("decayed pressure does not reconstruct")
        if not math.isclose(
            state.added_pressure,
            expected_added,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError("added pressure does not reconstruct")
        if not math.isclose(
            state.prequalification_pressure,
            expected_pre,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError("prequalification pressure does not reconstruct")
        if not math.isclose(
            state.closing_pressure,
            expected_close,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError("closing pressure does not reconstruct")

    def contribution(
        self,
        *,
        pressure_state_id: str,
        year: int,
        location_id: str,
        component_type: str,
        source_id: str,
        quantity: float,
        unit: str,
        sign: int,
        semantics: str,
        channel_id: Optional[str] = None,
        project_archetype_id: Optional[str] = None,
    ) -> PressureContributionV1:
        if sign not in {-1, 1}:
            raise ValueError("pressure contribution sign must be -1 or +1")
        amount = _finite(quantity, "pressure contribution quantity")
        return PressureContributionV1(
            contribution_id=_stable_id(
                "pc",
                pressure_state_id,
                component_type,
                source_id,
                amount,
                unit,
                sign,
            ),
            pressure_state_id=pressure_state_id,
            year=int(year),
            location_id=location_id,
            component_type=component_type,
            source_id=source_id,
            quantity=amount,
            unit=unit,
            sign=sign,
            semantics=semantics,
            channel_id=channel_id,
            project_archetype_id=project_archetype_id,
        )

    def causal_qualification(
        self,
        *,
        year: int,
        actor_id: str,
        location_id: str,
        project_archetype_id: str,
        threshold: float,
        pressure_states: Mapping[tuple[str, str], PressureStateV1],
        project_outputs: Mapping[str, float],
        channel_units: Mapping[str, str],
    ) -> PressureQualificationV1:
        threshold_value = _finite(threshold, "qualification threshold")
        rows = []
        for channel_id in sorted(project_outputs):
            output = _finite(project_outputs[channel_id], "project output")
            if output <= 0:
                continue
            key = (location_id, channel_id)
            state = pressure_states.get(key)
            pressure = 0.0 if state is None else state.prequalification_pressure
            state_id = None if state is None else state.pressure_state_id
            unit = channel_units[channel_id]
            rows.append(
                PressureChannelRatioV1(
                    channel_id=channel_id,
                    pressure_state_id=state_id,
                    unit=unit,
                    pressure=pressure,
                    project_output=output,
                    ratio=pressure / output,
                )
            )
        if rows:
            controlling = max(rows, key=lambda x: (x.ratio, x.channel_id))
            controlling_ratio = controlling.ratio
            controlling_channel = controlling.channel_id
        else:
            controlling_ratio = 0.0
            controlling_channel = None
        qualified = controlling_ratio >= threshold_value
        return PressureQualificationV1(
            qualification_id=_stable_id(
                "pq",
                CAUSAL_SEMANTICS,
                int(year),
                actor_id,
                location_id,
                project_archetype_id,
            ),
            year=int(year),
            actor_id=actor_id,
            location_id=location_id,
            project_archetype_id=project_archetype_id,
            semantics=CAUSAL_SEMANTICS,
            threshold=threshold_value,
            pressure_qualified=qualified,
            controlling_ratio=controlling_ratio,
            controlling_channel_id=controlling_channel,
            channel_ratios=tuple(rows),
        )

    def legacy_qualification(
        self,
        *,
        year: int,
        actor_id: str,
        location_id: str,
        project_archetype_id: str,
        threshold: float,
        pressure_state: PressureStateV1,
        project_capital_cost: float,
    ) -> PressureQualificationV1:
        if pressure_state.semantics != LEGACY_SEMANTICS:
            raise ValueError("legacy qualification requires legacy pressure state")
        cost = _finite(project_capital_cost, "legacy project capital cost")
        if cost <= 0:
            raise ValueError("legacy project capital cost must be positive")
        ratio = pressure_state.prequalification_pressure / cost
        return PressureQualificationV1(
            qualification_id=_stable_id(
                "pq",
                LEGACY_SEMANTICS,
                int(year),
                actor_id,
                location_id,
                project_archetype_id,
            ),
            year=int(year),
            actor_id=actor_id,
            location_id=location_id,
            project_archetype_id=project_archetype_id,
            semantics=LEGACY_SEMANTICS,
            threshold=_finite(threshold, "qualification threshold"),
            pressure_qualified=ratio >= threshold,
            controlling_ratio=ratio,
            controlling_channel_id=None,
            channel_ratios=(),
        )

    @staticmethod
    def link_decision(
        qualification: PressureQualificationV1,
        decision_id: str,
        *,
        selected: bool,
    ) -> PressureQualificationV1:
        if not decision_id:
            raise ValueError("decision_id required")
        return replace(
            qualification,
            decision_id=decision_id,
            selected=bool(selected),
        )


__all__ = [
    "CAUSAL_SEMANTICS",
    "CONTRACT_VERSION",
    "FORMAT",
    "LEGACY_SEMANTICS",
    "PressureChannelRatioV1",
    "PressureContributionV1",
    "PressureObservabilityPackage",
    "PressureObservabilityRuntime",
    "PressureQualificationV1",
    "PressureStateV1",
    "load_pressure_observability_package",
    "load_pressure_observability_path",
]
