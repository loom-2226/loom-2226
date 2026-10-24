"""Reproduce the final shuttle v0.2 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. 2226 baseline (torchlet 2 GW/t in shuttle_space.json),
kits loaded only on the trips that use them, one drone per trip.
Writes shuttle_v0_2_final.json. Usage: python shuttle_final.py"""
import json
import shuttle_search as ss

tab = json.loads(ss.TABLES.read_text())
J = list(ss.S["jobs"])
d = ss.size_design(tab, "TORCH150", "BICONIC", "CABIN_DRIVE", "BALLOON", J, elong=1.0,
                   kits_per_trip=True, trip_payload=ss.S["trip_payload_t"])
assert all(d["jobs"][j]["ok"] for j in J), "a trip failed to close"
(ss.HERE / "shuttle_v0_2_final.json").write_text(json.dumps(ss.rnd(d), indent=1))
print(f"wet {d['wet_t']:.1f} t, dry {d['dry_t']:.1f} t, water cap {d['prop_cap_t']:.1f} t, "
      f"{d['dims_m'][0]:.1f} x {d['dims_m'][1]:.1f} m, torchlet {d['torch_gw']:.1f} GW")
