"""Hostile tests for CIVPROP Pressure Observability V1."""
from __future__ import annotations

import unittest

from .pressure_observability_v1 import (
    PressureObservabilityRuntime,
    PressureStateV1,
    load_pressure_observability_package,
)


PACKAGE = {
    "format": "CIVPROP_PRESSURE_OBSERVABILITY_V1",
    "contract_version": "1.0.0",
    "emit_contributions": True,
    "emit_all_qualifications": True,
    "record_legacy_discharge": True,
}


class PressureObservabilityV1Tests(unittest.TestCase):
    def setUp(self):
        self.package = load_pressure_observability_package(PACKAGE)
        self.runtime = PressureObservabilityRuntime(self.package)

    def test_causal_state_arithmetic_closes_exactly(self):
        state = self.runtime.causal_state(
            year=2030,
            location_id="LUNA_SURFACE",
            channel_id="HABITAT",
            unit="person",
            opening_pressure=10.0,
            decay=0.60,
            unmet_demand=20.0,
            gain=0.24,
            required=25.0,
            available=5.0,
        )
        self.assertEqual(state.decayed_pressure, 6.0)
        self.assertEqual(state.added_pressure, 4.8)
        self.assertEqual(state.prequalification_pressure, 10.8)
        self.assertEqual(state.discharge, 0.0)
        self.assertEqual(state.closing_pressure, 10.8)
        self.runtime.validate_state(state)

    def test_causal_path_rejects_synthetic_discharge(self):
        state = self.runtime.causal_state(
            year=2030,
            location_id="LUNA_SURFACE",
            channel_id="HABITAT",
            unit="person",
            opening_pressure=10.0,
            decay=0.60,
            unmet_demand=20.0,
            gain=0.24,
            required=25.0,
            available=5.0,
        )
        bad = PressureStateV1(
            **{
                **state.__dict__,
                "discharge": 1.0,
                "closing_pressure": 9.8,
            }
        )
        with self.assertRaises(ValueError):
            self.runtime.validate_state(bad)

    def test_legacy_state_exposes_explicit_discharge(self):
        state = self.runtime.legacy_state(
            year=2029,
            location_id="LUNA_SURFACE",
            project_archetype_id="HABITAT",
            opening_pressure=10.0,
            decay=0.60,
            structural_signal=8.0,
            gain=0.24,
            discharge=3.0,
        )
        self.assertEqual(state.semantics, "LEGACY_PROJECT_PRESSURE")
        self.assertAlmostEqual(state.prequalification_pressure, 7.92)
        self.assertEqual(state.discharge, 3.0)
        self.assertAlmostEqual(state.closing_pressure, 4.92)
        self.runtime.validate_state(state)

    def test_qualification_records_all_channel_ratios_and_controlling_channel(self):
        states = {
            ("LUNA_SURFACE", "HABITAT"): self.runtime.causal_state(
                year=2030,
                location_id="LUNA_SURFACE",
                channel_id="HABITAT",
                unit="person",
                opening_pressure=0.0,
                decay=0.60,
                unmet_demand=30.0,
                gain=0.24,
                required=40.0,
                available=10.0,
            ),
            ("LUNA_SURFACE", "POWER"): self.runtime.causal_state(
                year=2030,
                location_id="LUNA_SURFACE",
                channel_id="POWER",
                unit="MW",
                opening_pressure=0.0,
                decay=0.60,
                unmet_demand=1.0,
                gain=0.24,
                required=1.0,
                available=0.0,
            ),
        }
        q = self.runtime.causal_qualification(
            year=2030,
            actor_id="AUS",
            location_id="LUNA_SURFACE",
            project_archetype_id="HABITAT",
            threshold=0.55,
            pressure_states=states,
            project_outputs={"HABITAT": 4.0, "POWER": 0.1},
            channel_units={"HABITAT": "person", "POWER": "MW"},
        )
        self.assertEqual(len(q.channel_ratios), 2)
        self.assertEqual(q.controlling_channel_id, "POWER")
        self.assertAlmostEqual(q.controlling_ratio, 2.4)
        self.assertTrue(q.pressure_qualified)

    def test_below_threshold_is_recorded_not_discarded(self):
        state = self.runtime.causal_state(
            year=2030,
            location_id="LUNA_SURFACE",
            channel_id="HABITAT",
            unit="person",
            opening_pressure=0.0,
            decay=0.60,
            unmet_demand=1.0,
            gain=0.24,
            required=1.0,
            available=0.0,
        )
        q = self.runtime.causal_qualification(
            year=2030,
            actor_id="AUS",
            location_id="LUNA_SURFACE",
            project_archetype_id="HABITAT",
            threshold=0.55,
            pressure_states={("LUNA_SURFACE", "HABITAT"): state},
            project_outputs={"HABITAT": 4.0},
            channel_units={"HABITAT": "person"},
        )
        self.assertFalse(q.pressure_qualified)
        self.assertAlmostEqual(q.controlling_ratio, 0.06)


if __name__ == "__main__":
    unittest.main()
