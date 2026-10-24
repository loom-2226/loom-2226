"""Shuttle propulsion trade v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Reads every input from shuttle_options.json.
For each propulsion option and job: tonnes left for ship + payload after
burning the round-trip delta-v out of the shuttle's wet mass."""
import json, math, sys
from pathlib import Path
G0 = 9.80665
o = json.loads((Path(__file__).parent / "shuttle_options.json").read_text())
wet = o["shuttle_wet_t"]["value"]
jobs = o["jobs_round_trip_from_low_orbit_km_s"]
rows = {}
for name, p in o["propulsion_options"].items():
    rows[name] = {j: wet * math.exp(-v["dv"] / p["ve_km_s"]) for j, v in jobs.items()}
if "--json" in sys.argv:
    print(json.dumps(rows, indent=2)); sys.exit()
print(f"{'tonnes left of ' + str(wet) + ' t':22s}" + "".join(f"{j:>8s}" for j in jobs))
for name, r in rows.items():
    print(f"{name:22s}" + "".join(f"{r[j]:8.1f}" for j in jobs))
tw = o["earth_takeoff_thrust_to_weight"]["value"]
F = tw * wet * 1000 * G0
for name, p in o["propulsion_options"].items():
    print(f"Earth lift-off at {tw} T/W, {name}: thrust {F/1e3:.0f} kN, jet power {0.5*F*p['ve_km_s']*1e3/1e9:.2f} GW")
