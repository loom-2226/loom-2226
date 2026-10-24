"""Relational plant placement for concept B/F v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
UNCONSTRAINED EXPLORATION (canon set aside, physics kept). Mass ledger read from the
repo seed; B-layout geometry and the three placements are authored below as inputs."""
import json, math, sqlite3, sys
from pathlib import Path
REPO = Path(sys.argv[1])
db = sqlite3.connect(":memory:")
db.executescript((REPO / "geometry/wayfarer_geometry_seed.sql").read_text())
ledger = {i: (m, x, y, z) for i, m, x, y, z in db.execute("SELECT id,mass_t,x_m,y_m,z_m FROM mass_elements")}
INPUTS = {
    "b_layout": {"tank_r_in": 2.9, "bay_half_w": 2.2, "bay_half_h": 1.75, "bay_x": [19.25, 30.75],
                 "shuttle_x": 25.0, "transfer_tunnel_r": 1.0},
    "plant_density_t_m3": [1.0, 1.5],
    "fore_block_x": [14.0, 19.25], "aft_block_x": [30.75, 36.0],
}
L = INPUTS["b_layout"]

def keel_sides(n=900):
    r, hw, hh = L["tank_r_in"], L["bay_half_w"], L["bay_half_h"]
    h = 2 * r / n; area = mz = keel = sides = 0.0
    for i in range(n):
        for j in range(n):
            y = -r + (i + .5) * h; z = -r + (j + .5) * h
            if y * y + z * z > r * r: continue
            if abs(y) < hw and abs(z) < hh: continue      # bay
            if abs(y) < hw and z >= hh: continue          # exit slot stays clear
            a = h * h; area += a; mz += a * z
            if abs(y) < hw: keel += a
            else: sides += a
    return area, mz / area, keel, sides

area, zc, keel, sides = keel_sides()
bay_len = L["bay_x"][1] - L["bay_x"][0]
r = L["tank_r_in"]; tun = L["transfer_tunnel_r"]
fx0, fx1 = INPUTS["fore_block_x"]; ax0, ax1 = INPUTS["aft_block_x"]
zones = {
    "fore_block_m3": math.pi * (r * r - tun * tun) * (fx1 - fx0),
    "aft_block_m3": math.pi * r * r * (ax1 - ax0),
    "keel_and_sides_m3": area * bay_len,
    "keel_only_m3": keel * bay_len, "sides_only_m3": sides * bay_len,
}
need = [ledger["relational_plant"][0] / d for d in INPUTS["plant_density_t_m3"][::-1]]
options = {
    "R1 split fore + aft": [(44.0, (fx0 + fx1) / 2, 0.0), (44.0, (ax0 + ax1) / 2, 0.0)],
    "R2 keel and sides": [(88.0, sum(L["bay_x"]) / 2, zc)],
    "R3 single aft block": [(88.0, (ax0 + ax1) / 2, 0.0)],
}

def com(plant):
    items = [(m, x, z) for k, (m, x, y, z) in ledger.items() if k not in ("relational_plant", "planetary_launch")]
    items.append((ledger["planetary_launch"][0], L["shuttle_x"], 0.0))
    items += plant
    M = sum(m for m, _, _ in items)
    return sum(m * x for m, x, _ in items) / M, sum(m * z for m, _, z in items) / M, M

today = com([(88.0, ledger["relational_plant"][1], 0.0)])
items = [(m, x, z) for k, (m, x, y, z) in ledger.items()]
M = sum(m for m, _, _ in items)
ref = (sum(m * x for m, x, _ in items) / M, sum(m * z for m, _, z in items) / M)
out = {"zones": zones, "plant_volume_needed_m3": need, "keel_sides_centroid_z_m": zc,
       "today_dry_com": {"x": ref[0], "z": ref[1]},
       "b_with_plant_on_axis_impossible_com": {"x": today[0], "z": today[1]}, "options": {}}
for name, plant in options.items():
    x, z, _ = com(plant)
    out["options"][name] = {"com_x": x, "com_z": z, "shift_x_vs_today": x - ref[0], "offset_z": z}
print(json.dumps(out, indent=1))
