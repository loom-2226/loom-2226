"""Rover-integration trade for shuttle v1. Structural rules only; every number is in
rover_trade_inputs.json and ../shuttle_inputs.json. Run: python3 rover_trade.py"""
import hashlib, json, pathlib
import numpy as np

HERE = pathlib.Path(__file__).parent
TI = json.loads((HERE / "rover_trade_inputs.json").read_text())
SI = json.loads((HERE / ".." / "shuttle_inputs.json").read_text())
run_id = hashlib.sha1((HERE / "rover_trade_inputs.json").read_bytes() + (HERE / ".." / "shuttle_inputs.json").read_bytes()).hexdigest()

rng = np.random.default_rng(TI["seed"]); N = TI["samples"]
U = {k: rng.uniform(SI["mass"][k]["min"], SI["mass"][k]["max"], N) for k in TI["core_components"]}
base_tps = rng.uniform(TI["base_tps_core_t"]["min"], TI["base_tps_core_t"]["max"], N)
adds = {kind: {k: rng.uniform(a, b, N) for k, (a, b) in spec["adds_t"].items()} for kind, spec in TI["integration"].items()}
S = TI["scaling"]; r = TI["reserve"]
limit = r["start_t"] - r["floor_t"] + r["replaced_shuttle_t"]

def core_mass(o):
    p = o["pod_od_m"] / TI["reference_pod_od_m"]; h = o["hull_d_m"] / TI["reference_hull_d_m"]
    spec = TI["integration"][o["integration"]]
    keep = sum(TI["gear_door_ramp_shares"][s] for s in spec["keep_shares"])
    c = (U["pressure_pod_titanium_shell_t"] * p ** S["pod_shell_exponent"]
         + U["pressure_pod_fittings_seals_t"] * p ** S["pod_fittings_exponent"]
         + U["folding_rover_chassis_t"] * p ** S["chassis_exponent"]
         + U["hull_thermal_structure_t"] * h ** S["hull_structure_exponent_on_diameter"]
         + base_tps * h ** S["base_tps_exponent_on_diameter"]
         + U["crew_habitat_thermal_package_t"] * (S["crew_thermal_fixed_fraction"] + S["crew_thermal_per_crew_fraction_of_4"] * o["crew"] / 4)
         + U["landing_gear_door_ramp_t"] * keep
         + sum(U[k] for k in ["torch_low_high_engine_t", "small_belly_thrusters_t", "reactor_power_distribution_t",
                              "custody_capsule_dry_t", "avionics_controls_yaw_t", "water_tank_insulated_t"]))
    return c + sum(adds[o["integration"]].values()) if adds[o["integration"]] else c

lines = [f"run_id {run_id}", f"core-dry limit for {r['floor_t']} t reserve floor: {limit:.2f} t",
         "| Option | Core dry p5 / mid / p95 (t) | Keeps floor | Reserve at mid (t) | Bay exit | Fits | Note |",
         "|---|---|---|---|---|---|---|"]
for o in TI["options"]:
    c = core_mass(o); lo, mid, hi = np.percentile(c, [5, 50, 95])
    lines.append(f"| {o['name']} | {lo:.2f} / {mid:.2f} / {hi:.2f} | {(c <= limit).mean()*100:.1f}% | "
                 f"{r['start_t'] - (mid - r['replaced_shuttle_t']):.2f} | {o['g8_exit']} | {'yes' if o['fits'] else 'NO'} | {o['note']} |")
print("\n".join(lines))
