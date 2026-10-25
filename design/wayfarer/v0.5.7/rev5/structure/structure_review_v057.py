"""Structure review of v0.5.7 rev 4: four longerons and the L2 viewport band -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING REVIEW (kT 2026-10-26: "let's evaluate 4"). Looks for load cases and methods the design checks did not cover.
Writes structure/structure_review_v057_results.json. Usage: python structure/structure_review_v057.py"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import certify as CT

I, C, G = CT.load()
G0 = CT.G0
LO = I["longerons"]
X0, X1 = LO["x_m"]
L = X1 - X0
SS = I["ledger"]["structure_split"]
rho = I["materials"]["cfrp_density_t_m3"]
A_ASSUME = {
    "thrust_misalignment_deg": (0.5, "ENGINEERING_ASSUMPTION: torch thrust vector error / gimbal authority used by the trim budget"),
    "design_mpa": (250.0, "the design stress the longerons were sized to (400 MPa floor x 0.62)"),
    "floor_mpa": (400.0, "materials.cfrp_allowable_mpa (what G5 checks against)"),
    "dT_K": (50.0, "ENGINEERING_ASSUMPTION: ring-to-shell temperature swing as shutters open to deep space and close"),
    "alpha_ti": (8.6e-6, "Ti-6Al-4V"), "alpha_cfrp": (0.5e-6, "quasi-isotropic CFRP, in-plane"),
}
a = lambda k: A_ASSUME[k][0]
out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING review of v0.5.7 rev 4", "assumptions": {k: {"value": v[0], "note": v[1]} for k, v in A_ASSUME.items()}}

# ---------------- A. longerons: the method and combined axial + bending
st_name = max(CT.states(I), key=lambda s: G["states"][s]["mass_t"])
st = G["states"][st_name]
parts = {p["id"]: p for p in G["parts"]}
items = [parts[pid] for pid in st["parts"] if pid in parts and "torch_chain" not in parts[pid]["tags"] and pid != "thrust_cone" and parts[pid]["centroid_m"][0] < X1]
items += G["fluids_by_state"][st_name]
m = sum(p["mass_t"] for p in items)
cg = [sum(p["mass_t"] * p["centroid_m"][k] for p in items) / m for k in range(3)]
a_ult = C["G5"]["design_g"] * C["G5"]["ultimate_factor"] * G0
F = m * 1e3 * a_ult
n = len(LO["items"])
A_part = sum(p["mass_t"] for p in G["parts"] if "longeron" in p["tags"]) / (rho * L) / n        # what G5 uses: part mass includes the spread reserve
A_struct = SS["longerons"] / (1 + 0.10) / (rho * L) / n                                       # the structure line's actual material (10% splices removed)
off = G["thrust_line_offset_m"]
e_z, e_y = cg[2] - off["z"], cg[1] - off["y"]
M_off = F * math.hypot(e_y, e_z)                                                             # thrust line offset from the mass ahead
lever = X1 - cg[0]
M_mis = m * 1e3 * a_ult * math.sin(math.radians(a("thrust_misalignment_deg"))) * lever         # thrust vector error at full ultimate thrust
pos = [(it["y_m"], it["z_m"]) for it in LO["items"]]
def stresses(A):
    Iy = sum(A * z * z for _, z in pos)
    ax = F / (n * A)
    bend = (M_off + M_mis) * max(abs(z) for _, z in pos) / Iy    # bending about the horizontal axis (worst plane, conservative: both moments added)
    return ax / 1e6, bend / 1e6
axp, bp = stresses(A_part)
axs, bs = stresses(A_struct)
need = (F / n + (M_off + M_mis) * 2.6 / sum(z * z for _, z in pos)) / (a("design_mpa") * 1e6)
out["A_longerons"] = {"state": st_name, "mass_ahead_t": round(m, 1), "cg_ahead_m": [round(v, 3) for v in cg], "F_ult_mn": round(F / 1e6, 1),
                      "moment_offset_mnm": round(M_off / 1e6, 1), "moment_misalignment_mnm": round(M_mis / 1e6, 1),
                      "area_G5_m2": round(A_part, 4), "area_structure_line_m2": round(A_struct, 4),
                      "G5_method": {"axial_mpa": round(axp, 1), "plus_bending_mpa": round(axp + bp, 1)},
                      "structure_line": {"axial_mpa": round(axs, 1), "plus_bending_mpa": round(axs + bs, 1)},
                      "design_mpa": a("design_mpa"), "floor_mpa": a("floor_mpa"),
                      "area_needed_for_design_m2": round(need, 4), "area_increase_pct": round(100 * (need / A_struct - 1), 1),
                      "extra_span_mass_t": round((need - A_struct) * n * L * rho * 1.10, 2),
                      "findings": ["G5 computes longeron area from part mass, which includes the spread engineering reserve (a mass margin, not material): unconservative once members are sized tight",
                                   "G5 checks axial load only; the thrust line's offset from the mass ahead and a 0.5 deg thrust error add bending"]}

# ---------------- B. viewport band: connections and shear not in the study
VBR = json.loads((ROOT / "habitat/crew_systems_results.json").read_text())["viewport_band"]
q = VBR["load_path"]["3_rings"]["axial_flow_kn_m"] * 1e3
bolt_d, pitch, rows = 0.010, 0.05, 2
per_bolt = q * pitch / rows
cap_shear = math.pi / 4 * bolt_d ** 2 * 550e6
bearing = per_bolt / (0.03 * bolt_d) / 1e6
m_ahead = VBR["mass_ahead_t"]
V = m_ahead * 1e3 * G0 * (C["G5"]["design_g"] * math.sin(math.radians(a("thrust_misalignment_deg"))) + 0.05) * 1.5   # lateral: thrust error + 0.05 g attitude, x 1.5
nm = VBR["mullions"]
h = VBR["tallest_mullion_m"]
Mm = V / (nm / 2) * h / 2
Zm = 0.20 * 0.05 ** 2 / 6
out["B_band"] = {"ring_to_shell": {"shear_flow_kn_m": round(q / 1e3, 1), "bolts": f"2 rows of M10 Ti at 50 mm", "per_bolt_kn": round(per_bolt / 1e3, 1),
                                   "bolt_shear_capacity_kn": round(cap_shear / 1e3, 1), "margin": round(cap_shear / per_bolt, 2), "cfrp_bearing_mpa": round(bearing, 1), "bearing_allow_mpa": 400,
                                   "ok": cap_shear / per_bolt >= 1.5 and bearing <= 400},
                 "vierendeel_shear": {"lateral_kn": round(V / 1e3, 1), "mullion_moment_knm": round(Mm / 1e3, 2), "mullion_weak_axis_mpa": round(Mm / Zm / 1e6, 1), "allow_mpa": 600,
                                      "ok": Mm / Zm <= 600e6, "note": "no diagonals across the band, so lateral shear is carried by mullion bending (a Vierendeel frame)"}}

# ---------------- C. thermal mismatch between titanium rings and the CFRP shell
circ = 2 * math.pi * I["hull"]["pressure_r_m"]
dl = (a("alpha_ti") - a("alpha_cfrp")) * a("dT_K") * circ
sig_lock = (a("alpha_ti") - a("alpha_cfrp")) * a("dT_K") * 114e9
out["C_thermal"] = {"ring_circumference_m": round(circ, 2), "free_mismatch_mm": round(dl * 1e3, 1), "ring_stress_if_locked_mpa": round(sig_lock / 1e6, 1),
                    "verdict": "not covered by any check: a bolted Ti ring on a CFRP shell fights a ~10 mm circumferential mismatch every shutter cycle; needs compliant (slotted or flexure) attachments, or a CFRP ring with titanium only at the mullion roots"}
json.dump(out, open(ROOT / "structure/structure_review_v057_results.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "assumptions"}, indent=1))
