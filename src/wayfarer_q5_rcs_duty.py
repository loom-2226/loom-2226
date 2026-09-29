from __future__ import annotations

"""Q5 RCS duty/load bridge derived from the qualified Q4 engineering screens.

This module does not invent a new RCS power architecture.  It consumes the
actual physical resultant thrust demand reported by the Q4 allocator and the
existing Q5 candidate exhaust-velocity/efficiency envelope, then derives jet
power and conversion-waste-heat screening quantities.

Durations, propellant choice, bus topology, plume thermochemistry, radiator
geometry and hardware efficiencies remain open unless separately qualified.
"""

import json
from pathlib import Path
from typing import Any

from wayfarer_power_thermal import conversion_waste_heat_W, kinetic_jet_power_W
from wayfarer_rcs_combined_maneuvers import build_rcs_combined_maneuver_screen

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
_Q5_PATH = Path(__file__).resolve().parents[1] / "engineering" / "current" / "wayfarer_q5_power_thermal_envelope_v0.2.json"


def _load_q5() -> dict[str, Any]:
    return json.loads(_Q5_PATH.read_text(encoding="utf-8"))


def _case_duty(case: dict[str, Any], q5: dict[str, Any]) -> dict[str, Any]:
    total_thrust_N = float(case["total_resultant_mount_thrust_N"])
    lead_ve_m_s = float(q5["rcs"]["lead_exhaust_velocity_km_s"]) * 1000.0
    alt_ve_m_s = float(q5["rcs"]["alternate_exhaust_velocity_km_s"]) * 1000.0
    efficiencies = [float(x) for x in q5["rcs"]["conversion_efficiency_screening"]]

    lead_jet_W = kinetic_jet_power_W(total_thrust_N, lead_ve_m_s)
    alt_jet_W = kinetic_jet_power_W(total_thrust_N, alt_ve_m_s)
    lead_waste = [conversion_waste_heat_W(lead_jet_W, eta) for eta in efficiencies]
    alt_waste = [conversion_waste_heat_W(alt_jet_W, eta) for eta in efficiencies]

    physical = case["physical_mount_commands"]
    nonzero = [cmd for cmd in physical.values() if float(cmd["commanded_thrust_N"]) > 1.0]
    return {
        "failed_cluster": case["failed_cluster"],
        "active_mount_count": case["active_mount_count"],
        "firing_mount_count_gt_1N": len(nonzero),
        "total_resultant_mount_thrust_kN": total_thrust_N / 1000.0,
        "max_physical_mount_utilization_fraction": case["max_physical_mount_utilization_fraction"],
        "lead_20kms_jet_power_GW": lead_jet_W / 1.0e9,
        "alternate_50kms_jet_power_GW": alt_jet_W / 1.0e9,
        "lead_conversion_waste_heat_MW_by_efficiency": {
            f"eta_{eta:.2f}": heat / 1.0e6 for eta, heat in zip(efficiencies, lead_waste)
        },
        "alternate_conversion_waste_heat_MW_by_efficiency": {
            f"eta_{eta:.2f}": heat / 1.0e6 for eta, heat in zip(efficiencies, alt_waste)
        },
        "duration_s": None,
        "energy_draw_GJ": None,
        "thermal_buffer_draw_GJ": None,
    }


def build_q5_rcs_duty_envelope() -> dict[str, Any]:
    q5 = _load_q5()
    combined = build_rcs_combined_maneuver_screen()

    nominal = {name: _case_duty(case, q5) for name, case in combined["nominal_cases"].items()}
    degraded = {
        cluster: {name: _case_duty(case, q5) for name, case in cases.items()}
        for cluster, cases in combined["one_cluster_out_cases"].items()
    }
    all_cases = list(nominal.values()) + [case for cases in degraded.values() for case in cases.values()]

    return {
        "standard_id": "WAYFARER_Q5_RCS_DUTY_ENVELOPE_V0.1",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "source_q4_screen": combined["standard_id"],
        "source_q5_envelope": "wayfarer_q5_power_thermal_envelope_v0.2.json",
        "q5_qualification_status": q5["qualification_status"],
        "duty_class": q5["rcs"]["duty_class"],
        "candidate_exhaust_velocity_km_s": {
            "lead": q5["rcs"]["lead_exhaust_velocity_km_s"],
            "alternate": q5["rcs"]["alternate_exhaust_velocity_km_s"],
        },
        "conversion_efficiency_screening": q5["rcs"]["conversion_efficiency_screening"],
        "nominal_cases": nominal,
        "one_cluster_out_cases": degraded,
        "summary": {
            "max_total_resultant_mount_thrust_kN": max(case["total_resultant_mount_thrust_kN"] for case in all_cases),
            "max_physical_mount_utilization_fraction": max(case["max_physical_mount_utilization_fraction"] for case in all_cases),
            "max_lead_20kms_jet_power_GW": max(case["lead_20kms_jet_power_GW"] for case in all_cases),
            "max_alternate_50kms_jet_power_GW": max(case["alternate_50kms_jet_power_GW"] for case in all_cases),
        },
        "authority_limits": {
            "maneuver_duration": "OPEN_Q4_Q5",
            "working_fluid": "OPEN_Q2_Q4",
            "exhaust_velocity_selection": "CANDIDATE_SCREEN_ONLY",
            "conversion_efficiency": "CANDIDATE_SCREEN_ONLY",
            "electrical_bus_source": "NOT_ASSUMED",
            "physical_radiator_geometry": q5["radiator"]["physical_geometry_status"],
            "thermal_buffer_medium": q5["thermal_buffer"]["medium_status"],
            "plume_thermochemistry": "OPEN_Q4_Q5",
        },
        "notes": [
            "Jet power is derived from total physical resultant mount thrust, not net translational force, so torque-producing counter-thrust is counted.",
            "The calculation uses P_jet = 0.5 F v_e and the existing Q5 candidate exhaust velocities only.",
            "Conversion waste heat is a screening consequence of the existing Q5 efficiency band; it is not a claim that the main electrical bus directly powers the RCS.",
            "Without maneuver duration, no energy draw, buffer depletion, propellant use or radiator transient can be qualified.",
        ],
    }
