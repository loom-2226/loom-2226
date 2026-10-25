"""Longeron study: four or five, a sizing pass, and Osteon junctions -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING STUDY on the v0.5.6 baseline (geometry 14bb3c2c...). It changes nothing in the build.
Asked by kT 2026-10-25: (1) decide four or five longerons, (2) size them, with a twist check,
(3) use Osteon (topology-optimised, graded) structure only at the junctions.

Method: closed-form, the same load model as certify.py G5 (everything ahead of the thrust cone is
carried by the longerons at 5 g x 1.5, which is conservative because the tank walls also carry the
water's inertia). Writes structure/longeron_study_results.json.
Usage: python structure/longeron_study.py (standard library only)"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import certify as CT

I, C, G = CT.load()
G0 = CT.G0
M5 = C["G5"]
mat = I["materials"]
E, RHO, S400 = mat["cfrp_e_gpa"] * 1e9, mat["cfrp_density_t_m3"], mat["cfrp_allowable_mpa"] * 1e6
LO = I["longerons"]
X0, X1 = LO["x_m"]
L = X1 - X0
FRAME = I["frames"]["spacing_m"]
T = I["tanks"]

A = {  # assumptions, each stated
    "design_compression_mpa": (250.0, "ENGINEERING_ASSUMPTION: 400 MPa floor x 0.62 knockdown for impact damage, joints and environment (compression after impact)"),
    "splice_allowance": (0.10, "ENGINEERING_ASSUMPTION: +10% on span mass for splices, ply drops and frame clips"),
    "min_wall_mm": (4.0, "ENGINEERING_ASSUMPTION: minimum CFRP tube wall for handling and impact"),
    "ti_ftu_mpa": (900.0, "PUBLISHED_PHYSICS: Ti-6Al-4V ultimate tensile strength ~900-950 MPa"),
    "ti_density": (4.43, "PUBLISHED_PHYSICS: Ti-6Al-4V 4.43 t/m3"),
    "fitting_factor": (2.5, "ENGINEERING_ASSUMPTION: conventional lug/flange fitting, material ~2.5x the ideal (fitting factor 1.15 x load-spreading inefficiency)"),
    "fitting_length_m": (0.8, "ENGINEERING_ASSUMPTION: load is transferred into the frame or cone over ~0.8 m"),
    "fitting_fixed_t": (0.03, "ENGINEERING_ASSUMPTION: bolts, shims and inspection access per fitting"),
    "osteon_saving": ((0.30, 0.40, 0.50), "BUILDER-DERIVED (OST-22), grounded in 2026 topology-optimised metal brackets that save 30-60%: low / central / high"),
    "node_module_t": (0.2, "ENGINEERING_ASSUMPTION: one field-node module; canon gives the plant (88 t) but not a node's mass"),
    "node_mount_t": (0.04, "ENGINEERING_ASSUMPTION: conventional mount on the ring frame nearest the station, in the dry tank-skin gap, tied into the longeron; sized for alignment stiffness, not strength (the 5 g x 1.5 load is only ~15 kN)"),
    "node_hatch_t": (0.015, "ENGINEERING_ASSUMPTION: flush external access hatch per node in the service band (replaces skin, so only the frame and seal count)"),
    "strake_housing_t": (0.05, "ENGINEERING_ASSUMPTION: shallow root fairing per stowed strake, x 14-32.3"),
    "bay_corner_t": (0.12, "ENGINEERING_ASSUMPTION: conventional doubler at each corner of the bay slot"),
    "side_load_g": (0.5, "ENGINEERING_ASSUMPTION: the 0.5 g side load already used for the flight-deck columns"),
    "shear_centre_offset_m": (0.5, "ENGINEERING_ASSUMPTION: offset between the mass line and the shear centre of the slotted section"),
    "cfrp_shear_allow_mpa": (60.0, "ENGINEERING_ASSUMPTION: in-plane shear allowable, quasi-isotropic CFRP"),
}
a = lambda k: A[k][0]

# ------------------------------------------------------------ load (same as G5)
st_name = max(CT.states(I), key=lambda s: G["states"][s]["mass_t"])
st = G["states"][st_name]
parts = {p["id"]: p for p in G["parts"]}
fwd = sum(parts[pid]["mass_t"] for pid in st["parts"] if pid in parts and "torch_chain" not in parts[pid]["tags"]
          and pid != "thrust_cone" and parts[pid]["centroid_m"][0] < X1)
fwd += sum(p["mass_t"] for p in G["fluids_by_state"][st_name])
F_ult = fwd * 1e3 * M5["design_g"] * M5["ultimate_factor"] * G0
F_1g = fwd * 1e3 * C["G9"]["one_longeron_out_g"] * G0
lon_today_t = sum(p["mass_t"] for p in G["parts"] if "longeron" in p["tags"])

# ------------------------------------------------------------ layouts
SILL = (2.75, 2.6)
def layouts():
    five = [("starboard plank", "plank", 4.39, 0.0), ("port plank", "plank", 4.39, 180.0), ("keel plank", "plank", 4.39, 270.0),
            ("slot sill starboard", "tube", SILL[0], SILL[1]), ("slot sill port", "tube", -SILL[0], SILL[1])]
    four = [("upper starboard (slot edge)", "tube", SILL[0], SILL[1]), ("upper port (slot edge)", "tube", -SILL[0], SILL[1]),
            ("lower starboard", "tube", SILL[0], -SILL[1]), ("lower port", "tube", -SILL[0], -SILL[1])]
    def yz(it):
        n, k, u, v = it
        if k == "plank":
            return (u * math.cos(math.radians(v)), u * math.sin(math.radians(v)))
        return (u, v)
    return {"5": [(it[0], it[1], *yz(it)) for it in five], "4": [(it[0], it[1], *yz(it)) for it in four]}

def az(y, z):
    return math.degrees(math.atan2(z, y)) % 360

def node_offset(deg, phase=0.0):
    d = (deg - phase) % 22.5
    return min(d, 22.5 - d)

def tube_for_area(Ar, D):
    t = max(a("min_wall_mm") / 1000, (D - math.sqrt(max(D * D - 4 * Ar / math.pi, 0.0))) / 2)   # exact wall for the area
    Ar = math.pi / 4 * (D ** 2 - (D - 2 * t) ** 2)
    I_ = math.pi / 64 * (D ** 4 - (D - 2 * t) ** 4)
    return t, Ar, I_

def bend_mode(As, pos):
    yb = sum(Ar * y for Ar, (y, z) in zip(As, pos)) / sum(As)
    zb = sum(Ar * z for Ar, (y, z) in zip(As, pos)) / sum(As)
    Iy = sum(Ar * (z - zb) ** 2 for Ar, (y, z) in zip(As, pos))
    Iz = sum(Ar * (y - yb) ** 2 for Ar, (y, z) in zip(As, pos))
    Lh = I["hull"]["length_m"]
    mu = st["mass_t"] * 1e3 / Lh
    return min(4.730 ** 2 / (2 * math.pi * Lh ** 2) * math.sqrt(E * Ix / mu) for Ix in (Iy, Iz)), Iy, Iz

def one_out(As, pos, k_out):
    """lose member k_out; the 1 g limit load stays on the old centroid line, so the survivors also bend."""
    keep = [i for i in range(len(As)) if i != k_out]
    yb0 = sum(As[i] * pos[i][0] for i in range(len(As))) / sum(As)
    zb0 = sum(As[i] * pos[i][1] for i in range(len(As))) / sum(As)
    At = sum(As[i] for i in keep)
    yb = sum(As[i] * pos[i][0] for i in keep) / At
    zb = sum(As[i] * pos[i][1] for i in keep) / At
    Iy = sum(As[i] * (pos[i][1] - zb) ** 2 for i in keep)
    Iz = sum(As[i] * (pos[i][0] - yb) ** 2 for i in keep)
    Iyz = sum(As[i] * (pos[i][0] - yb) * (pos[i][1] - zb) for i in keep)
    My, Mz = F_1g * (zb0 - zb), F_1g * (yb0 - yb)   # moments from the eccentric load
    worst = 0.0
    det = Iy * Iz - Iyz ** 2
    for i in keep:
        y, z = pos[i][0] - yb, pos[i][1] - zb
        # unsymmetric bending (axial load at offset (dy, dz) from the new centroid)
        dy, dz = yb0 - yb, zb0 - zb
        s_b = F_1g * ((dz * Iz - dy * Iyz) * z + (dy * Iy - dz * Iyz) * y) / det if det > 0 else 0.0
        worst = max(worst, (F_1g / At + s_b) / 1e6)
    return worst

def size(layout):
    items = layouts()[layout]
    n = len(items)
    pos = [(y, z) for _, _, y, z in items]
    per = F_ult / n
    sd = a("design_compression_mpa") * 1e6
    Areq = per / sd
    rows, As = [], []
    for name, kind, y, z in items:
        if kind == "tube":
            D = 0.50 if layout == "5" else 0.40   # v0.5.6 sills are 0.5 m; the four-longeron tubes are 0.4 m to clear the strake roots
            t, Ar, Im = tube_for_area(Areq, D)
            pe = math.pi ** 2 * E * Im / FRAME ** 2
            local = 0.3 * E * t / (D / 2) * Ar     # thin-shell local buckling with a 0.5 knockdown (0.605 x 0.5)
            buck = min(pe, local) / per
            rows.append({"name": name, "kind": "CFRP tube", "D_m": D, "wall_mm": round(t * 1e3, 1), "area_m2": round(Ar, 4),
                         "azimuth_deg": round(az(y, z), 1), "stress_mpa": round(per / Ar / 1e6, 1), "buckling_margin": round(buck, 1)})
        else:
            w = 1.2
            h = max(Areq / w, 0.004)
            Ar = w * h
            Im = w * h ** 3 / 12
            buck = (math.pi ** 2 * E * Im / FRAME ** 2) / per
            if buck < M5["buckling_factor"]:      # thicken until the plank no longer buckles between frames
                h = (M5["buckling_factor"] * per * FRAME ** 2 * 12 / (math.pi ** 2 * E * w)) ** (1 / 3)
                Ar, Im = w * h, w * h ** 3 / 12
                buck = (math.pi ** 2 * E * Im / FRAME ** 2) / per
            rows.append({"name": name, "kind": "CFRP plank in the tank-skin gap", "width_m": w, "thick_mm": round(h * 1e3, 1), "area_m2": round(Ar, 4),
                         "azimuth_deg": round(az(y, z), 1), "stress_mpa": round(per / Ar / 1e6, 1), "buckling_margin": round(buck, 1)})
        As.append(Ar)
    f, Iy, Iz = bend_mode(As, pos)
    span_t = sum(As) * L * RHO * (1 + a("splice_allowance"))
    oo = max(one_out(As, pos, k) for k in range(n))
    # tank volume: v0.5.6 net already allows for the two sills inside the tank
    tank_m3 = G["tank_volume_m3"]
    if layout == "4":
        tank_m3 += (2 * math.pi / 4 * 0.50 ** 2 - 4 * math.pi / 4 * 0.40 ** 2) * (T["x_m"][1] - T["x_m"][0])   # two 0.5 m sills out, four 0.4 m tubes in
    # strake root clearance (strake panels r 4.0-4.5, tangential half-width 1.0 m)
    clr = []
    for _, kind, y, z in items:
        if kind != "tube":
            continue
        D = 0.50 if layout == "5" else 0.40
        th = az(y, z)
        sa = min(I["radiators"]["azimuths_deg"], key=lambda s: abs((s - th + 180) % 360 - 180))
        d = math.radians((th - sa + 180) % 360 - 180)
        r = math.hypot(y, z)
        along, across = r * math.cos(d), abs(r * math.sin(d))
        clr.append(round(4.0 - (along + D / 2), 3) if across < 1.0 + D / 2 else None)
    return {"n": n, "members": rows, "span_mass_t": round(span_t, 2), "first_bending_hz": round(f, 2), "Iy_m4": round(Iy, 3), "Iz_m4": round(Iz, 3),
            "one_out_worst_mpa": round(oo, 1), "tank_volume_m3": round(tank_m3, 1), "tank_needed_m3": 315.0,
            "strake_root_clearance_m": clr,
            "node_azimuth_offset_deg": [round(node_offset(r["azimuth_deg"]), 1) for r in rows],
            "node_stations_on_longerons": [round(s, 2) for s in (53.3 * (k + 0.5) / 13 for k in range(13)) if X0 < s < X1]}

def fittings(layout, n, stations):
    per = F_ult / n
    v = a("fitting_factor") * per * a("fitting_length_m") / (a("ti_ftu_mpa") * 1e6)
    end_each = v * a("ti_density") + a("fitting_fixed_t")
    var_part = 2 * n * v * a("ti_density")
    fixed = 2 * n * a("fitting_fixed_t")
    mounts = n * len(stations) * a("node_mount_t")
    corners = 4 * a("bay_corner_t")
    hatches = n * len(stations) * a("node_hatch_t")
    housings = 4 * a("strake_housing_t")
    conv = var_part + fixed + mounts + corners + hatches + housings
    lo, mid, hi = a("osteon_saving")
    ost = {k: round(conv - s * (var_part + mounts + corners), 2) for k, s in (("low_saving", lo), ("central", mid), ("high_saving", hi))}
    return {"end_fittings": 2 * n, "end_fitting_each_t": round(end_each, 3), "node_mounts": n * len(stations), "node_mount_place": "ring frame nearest each station, in the dry 18 cm tank-skin gap; the longerons run inside the remass tank, so nothing mounts on them directly",
            "node_hatches_t": round(hatches, 2), "strake_root_housings_t": round(housings, 2), "bay_corners": 4,
            "conventional_t": round(conv, 2), "osteon_t": ost}

def torsion(sz):
    """slotted section: the tank's closed C-cell carries torque (Bredt); in the 0.8 m between the tank end (31.5) and the slot end (32.3)
    the section is open, so the longerons carry it as a short portal (differential bending, fixed-fixed)."""
    Tq = fwd * 1e3 * a("side_load_g") * G0 * M5["ultimate_factor"] * a("shear_centre_offset_m")
    tL = T["x_m"][1] - T["x_m"][0]
    A_cell = G["tank_volume_m3"] / tL
    q = Tq / (2 * A_cell)
    t_wall = min(p["t_mm"] for p in G["tank_structure"]["panels"] if p["item"] in ("outer wall", "inner wall")) / 1e3
    tau = q / t_wall
    gap = I["hull"].get("slot_x_m", [18.0, 32.3])[1] - T["x_m"][1]
    rows = sz["members"]
    r_m = math.hypot(*SILL) if sz["n"] == 4 else 4.0
    V = Tq / (sz["n"] * r_m)
    M = V * gap / 2
    worst = 0.0
    for r in rows:
        if "D_m" in r:
            D, t = r["D_m"], r["wall_mm"] / 1e3
            Im = math.pi / 64 * (D ** 4 - (D - 2 * t) ** 4)
            worst = max(worst, M * D / 2 / Im / 1e6)
        else:
            w, h = r["width_m"], r["thick_mm"] / 1e3
            worst = max(worst, M * (h / 2) / (w * h ** 3 / 12) / 1e6)   # plank bends about its weak axis (worst case)
    return {"torque_mnm": round(Tq / 1e6, 2), "cell_shear_flow_kn_m": round(q / 1e3, 1), "cell_wall_shear_mpa": round(tau / 1e6, 1),
            "cell_wall_allow_mpa": a("cfrp_shear_allow_mpa"), "open_gap_m": round(gap, 2), "portal_bending_mpa": round(worst, 1)}

if __name__ == "__main__":
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING study on the v0.5.6 baseline; the build is unchanged",
           "load": {"state": st_name, "mass_ahead_of_cone_t": round(fwd, 1), "F_ultimate_mn": round(F_ult / 1e6, 1), "F_1g_mn": round(F_1g / 1e6, 2)},
           "today": {"longeron_mass_t": round(lon_today_t, 2), "stress_mpa": 65.1, "allowable_mpa": 400, "note": "from G5; no end fittings or node mounts are in the 35 t"},
           "assumptions": {k: {"value": v[0], "prov": v[1]} for k, v in A.items()}, "layouts": {}}
    for lay in ("5", "4"):
        sz = size(lay)
        sz["fittings"] = fittings(lay, sz["n"], sz["node_stations_on_longerons"])
        sz["torsion"] = torsion(sz)
        sz["total_conventional_t"] = round(sz["span_mass_t"] + sz["fittings"]["conventional_t"], 2)
        sz["total_osteon_t"] = {k: round(sz["span_mass_t"] + v, 2) for k, v in sz["fittings"]["osteon_t"].items()}
        sz["saving_vs_today_t"] = {k: round(lon_today_t - v, 1) for k, v in sz["total_osteon_t"].items()}
        out["layouts"][lay] = sz
    (ROOT / "structure/longeron_study_results.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["load"]), json.dumps(out["today"]))
    for k, v in out["layouts"].items():
        print("\n== layout", k)
        for m in v["members"]:
            print(" ", m)
        for kk in ("span_mass_t", "first_bending_hz", "one_out_worst_mpa", "tank_volume_m3", "strake_root_clearance_m", "node_azimuth_offset_deg",
                   "node_stations_on_longerons", "fittings", "torsion", "total_conventional_t", "total_osteon_t", "saving_vs_today_t"):
            print(" ", kk, v[kk])
