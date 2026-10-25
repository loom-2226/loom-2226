from __future__ import annotations

"""Bridge qualified Q4 finite-attitude timing into bounded Q5 RCS energy screens.

This module deliberately stays inside authority already earned elsewhere:

* Q4 v0.4 supplies reference-wet-docked 90/180 degree finite transition times
  with a documented 20 percent settle margin;
* the Q4 allocation screen supplies physical resultant thrust demand per mount
  for the corresponding pure torque axes;
* Q5 v0.2 supplies candidate exhaust velocities, conversion efficiencies and
  thermal-buffer screening capacities.

The powered duration used here is the ideal symmetric bang-bang portion of the
existing Q4 timing model: qualified transition time / 1.20.  The additional
20 percent is retained as settle margin and is NOT silently assumed to be
full-thrust RCS firing.

This earns energy and equivalent-expellant screening for the existing pure
attitude qualification cases only.  It does not invent duration for the
combined maneuver suite or qualify a closed-loop control law.
"""

import json
from pathlib import Path
from typing import Any

from wayfarer_power_thermal import conversion_waste_heat_W, kinetic_jet_power_W
from wayfarer_rcs_allocation import build_rcs_allocation_screen

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
_SETTLE_FACTOR = 1.20
_ROOT = Path(__file__).resolve().parents[1]
_Q4_PATH = _ROOT / "engineering" / "current" / "wayfarer_q4_hud_attitude_envelope_v0.4.json"
_Q5_PATH = _ROOT / "engineering" / "current" / "wayfarer_q5_power_thermal_envelope_v0.2.json"

_AXIS_TO_WRENCH = {"ROLL": "TX", "PITCH": "TY", "YAW": "TZ"}
_ANGLES = (90, 180)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _worst_physical_thrust_for_axis(
    allocation: dict[str, Any], *, control_case: str, wrench_axis: str
) -> dict[str, Any]:
    if control_case == "NOMINAL":
        screens = [(None, allocation["screens"]["NOMINAL"])]
    else:
        screens = list(allocation["screens"]["ONE_CLUSTER_OUT"].items())

    candidates: list[dict[str, Any]] = []
    for failed_cluster, screen in screens:
        for sign in ("PLUS", "MINUS"):
            case = screen["cases"][f"{wrench_axis}_{sign}"]
            candidates.append(
                {
                    "failed_cluster": failed_cluster,
                    "sign": sign,
                    "total_resultant_mount_thrust_N": float(case["total_resultant_mount_thrust_N"]),
                    "max_physical_mount_utilization_fraction": float(case["max_physical_mount_utilization_fraction"]),
                    "physical_mount_commands": case["physical_mount_commands"],
                }
            )
    return max(candidates, key=lambda item: item["total_resultant_mount_thrust_N"])


def _candidate_energy_screen(
    *, total_thrust_N: float, powered_duration_s: float, exhaust_velocity_m_s: float,
    efficiencies: list[float], thermal_buffers_GJ: list[float]
) -> dict[str, Any]:
    jet_power_W = kinetic_jet_power_W(total_thrust_N, exhaust_velocity_m_s)
    jet_energy_J = jet_power_W * powered_duration_s
    waste_power = [conversion_waste_heat_W(jet_power_W, eta) for eta in efficiencies]
    waste_energy_J = [value * powered_duration_s for value in waste_power]
    expelled_mass_kg = total_thrust_N * powered_duration_s / exhaust_velocity_m_s
    worst_waste_GJ = max(waste_energy_J, default=0.0) / 1.0e9

    return {
        "exhaust_velocity_km_s": exhaust_velocity_m_s / 1000.0,
        "jet_power_GW": jet_power_W / 1.0e9,
        "jet_energy_GJ": jet_energy_J / 1.0e9,
        "equivalent_expelled_mass_kg": expelled_mass_kg,
        "conversion_waste_heat_MW_by_efficiency": {
            f"eta_{eta:.2f}": value / 1.0e6 for eta, value in zip(efficiencies, waste_power)
        },
        "conversion_waste_heat_energy_GJ_by_efficiency": {
            f"eta_{eta:.2f}": value / 1.0e9 for eta, value in zip(efficiencies, waste_energy_J)
        },
        "gross_worst_conversion_heat_fraction_of_buffer": {
            f"buffer_{buffer_GJ:.0f}GJ": worst_waste_GJ / buffer_GJ
            for buffer_GJ in thermal_buffers_GJ
        },
        "radiator_transient_credit_applied": False,
    }


def build_q5_attitude_energy_bridge() -> dict[str, Any]:
    q4 = _load(_Q4_PATH)
    q5 = _load(_Q5_PATH)
    allocation = build_rcs_allocation_screen()

    efficiencies = [float(value) for value in q5["rcs"]["conversion_efficiency_screening"]]
    buffers_GJ = [float(value) for value in q5["thermal_buffer"]["usable_energy_GJ_screening"]]
    ve_candidates = {
        "lead_20kms": float(q5["rcs"]["lead_exhaust_velocity_km_s"]) * 1000.0,
        "alternate_50kms": float(q5["rcs"]["alternate_exhaust_velocity_km_s"]) * 1000.0,
    }

    state_name = "REFERENCE_WET_DOCKED"
    state = q4["mass_states"][state_name]
    control_cases: dict[str, Any] = {}
    all_slews: list[dict[str, Any]] = []

    for control_case in ("NOMINAL", "ONE_CLUSTER_OUT"):
        q4_case = q4["control_cases"][control_case]
        slews: dict[str, Any] = {}
        for axis, wrench_axis in _AXIS_TO_WRENCH.items():
            physical = _worst_physical_thrust_for_axis(
                allocation, control_case=control_case, wrench_axis=wrench_axis
            )
            for angle in _ANGLES:
                timing_key = f"{axis.lower()}_{angle}"
                qualified_time_s = float(q4_case["reference_wet_docked_slew_s"][timing_key])
                powered_time_s = qualified_time_s / _SETTLE_FACTOR
                settle_margin_s = qualified_time_s - powered_time_s
                total_thrust_N = physical["total_resultant_mount_thrust_N"]
                propulsion = {
                    label: _candidate_energy_screen(
                        total_thrust_N=total_thrust_N,
                        powered_duration_s=powered_time_s,
                        exhaust_velocity_m_s=ve_m_s,
                        efficiencies=efficiencies,
                        thermal_buffers_GJ=buffers_GJ,
                    )
                    for label, ve_m_s in ve_candidates.items()
                }
                payload = {
                    "axis": axis,
                    "angle_deg": angle,
                    "wrench_axis": wrench_axis,
                    "qualified_transition_time_s": qualified_time_s,
                    "powered_bang_bang_time_s": powered_time_s,
                    "settle_margin_time_s": settle_margin_s,
                    "settle_factor_source": _SETTLE_FACTOR,
                    "worst_screen_sign": physical["sign"],
                    "worst_screen_failed_cluster": physical["failed_cluster"],
                    "total_resultant_mount_thrust_kN": total_thrust_N / 1000.0,
                    "max_physical_mount_utilization_fraction": physical["max_physical_mount_utilization_fraction"],
                    "candidate_propulsion_screens": propulsion,
                }
                slews[f"{axis}_{angle}"] = payload
                all_slews.append(payload)
        control_cases[control_case] = {
            "qualification_source": q4["standard_id"],
            "slews": slews,
        }

    max_heat_GJ = max(
        max(
            screen["conversion_waste_heat_energy_GJ_by_efficiency"].values(),
            default=0.0,
        )
        for slew in all_slews
        for screen in slew["candidate_propulsion_screens"].values()
    )
    max_jet_energy_GJ = max(
        screen["jet_energy_GJ"]
        for slew in all_slews
        for screen in slew["candidate_propulsion_screens"].values()
    )
    max_expellant_kg = max(
        screen["equivalent_expelled_mass_kg"]
        for slew in all_slews
        for screen in slew["candidate_propulsion_screens"].values()
    )

    return {
        "standard_id": "WAYFARER_Q5_RCS_ATTITUDE_ENERGY_BRIDGE_V0.1",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "scope": "QUALIFIED_Q4_PURE_ATTITUDE_TIMING_TO_Q5_ENERGY_SCREEN",
        "source_q4_timing": q4["standard_id"],
        "source_q4_allocation": allocation["standard_id"],
        "source_q5_envelope": "wayfarer_q5_power_thermal_envelope_v0.2.json",
        "mass_states": {
            state_name: {
                "mass_t": state["mass_t"],
                "center_of_mass_m": state["center_of_mass_m"],
                "inertia_diag_kg_m2": state["inertia_diag_kg_m2"],
                "control_cases": control_cases,
            }
        },
        "summary": {
            "max_checked_jet_energy_GJ": max_jet_energy_GJ,
            "max_gross_conversion_waste_heat_energy_GJ": max_heat_GJ,
            "max_equivalent_expelled_mass_kg": max_expellant_kg,
            "all_checked_gross_conversion_heat_within_50GJ_buffer_screen": max_heat_GJ <= min(buffers_GJ),
            "thermal_buffer_screening_GJ": buffers_GJ,
        },
        "authority_limits": {
            "combined_maneuver_duration": "OPEN_Q4_Q5",
            "translation_maneuver_duration": "OPEN_Q4_Q5",
            "closed_loop_control_law": "OPEN_Q4",
            "gimbal_slew_dynamics": "OPEN_Q4",
            "minimum_impulse_bit": "OPEN_Q4",
            "working_fluid": "OPEN_Q2_Q4",
            "exhaust_velocity_selection": "CANDIDATE_SCREEN_ONLY",
            "conversion_efficiency": "CANDIDATE_SCREEN_ONLY",
            "radiator_transient_response": "OPEN_Q5",
            "physical_radiator_geometry": q5["radiator"]["physical_geometry_status"],
            "thermal_buffer_medium": q5["thermal_buffer"]["medium_status"],
        },
        "notes": [
            "Powered time is derived from the existing Q4 symmetric bang-bang timing model by removing its explicit 20 percent settle margin; no new maneuver timing is invented.",
            "The worst physical resultant thrust across torque sign, and across A/B/C/D failures for degraded control, is used for conservative instantaneous power and energy screening.",
            "No radiator rejection credit is applied to the transient heat-energy comparison because radiator transient response and final geometry remain open.",
            "Equivalent expelled mass follows impulse / candidate exhaust velocity and does not select a working fluid or authorize use of protected water.",
            "Combined and translational maneuver energy remain unavailable until their displacement/attitude histories and control timing are separately earned.",
        ],
    }
