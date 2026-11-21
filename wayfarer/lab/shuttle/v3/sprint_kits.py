"""Shuttle v3: get-in/get-out kits (not a dogfighter). ALL bodies. ALL sponsors. 2026-2226.
NON-CANON ROM screen. Reuses step2_propulsion and agility models."""
import json, math, numpy as np
import step2_propulsion as S2, agility as AG
out = {"header": "ALL bodies. ALL sponsors. 2026-2226."}
# 1) hard egress all the way to orbit: liftoff T/W 1.4 (normal) vs 2.0/2.5 for the first 3 km/s
legs = lambda tw: [(200, .1, 1), (300, 1.3, 9.81), (3000, tw, 9.81), (6400, .8, 9.81), (400, .1, 1)]
out["egress_to_orbit_water_t"] = {tw: S2.water(40, 2.6, legs(tw))[0] for tw in (1.4, 2.0, 2.5)}
# 2) level dash on fans: power needed vs speed (wings in and out), sea level, 59 t
vw, vc = AG.vehicle(True), AG.vehicle(False)
def power_MW(veh, V, m=59.0, h=0.0):
    al, CL, CD, S = AG.polar(veh); q = .5 * AG.rho(h) * V * V; cl = m * 1e3 * 9.81 / (q * S)
    if cl > CL.max(): return None
    cd = float(np.interp(cl, CL, CD)); return round(q * S * cd * V / 0.75 / 0.93 / 1e6, 1)
out["dash_MWe_sea_level_59t"] = {V: {"wings_out": power_MW(vw, V), "wings_in": power_MW(vc, V)} for V in (150, 200, 250, 270)}
json.dump(out, open("sprint_kits.json", "w"), indent=1); print(json.dumps(out, indent=1))
