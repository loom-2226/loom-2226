# Wayfarer v0.5.7 rev 4: decisions and structure review (addendum for PR #432)

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING.** No canon promotion, no runtime integration. Do not put the amendment in `canon/current/`. Leave PR #430 as is. Let loom-gate run; no bypass. **The build is unchanged:** geometry sha256 `646ac1bad6852d1c7b25e92e3dd79e46e2d6b719d2edd20270af86203d6ab359`.

This one file replaces the addendum zip. It contains:

1. kT's decisions of 2026-10-26, to merge into `inputs/kt_decisions.json`.
2. The certification status after those decisions.
3. The structure review: findings and a proposed rev 5.
4. The review's results (`structure/structure_review_v057_results.json`).
5. The review script (`structure/structure_review_v057.py`), so the results can be reproduced.

Re-running `python3 certify.py` with the decisions in section 1 regenerates `out/certification_report.json` and `out/CERTIFICATION_REPORT_v0.5.md`.

---

## 1. kT's decisions, 2026-10-26

Add these three entries under `"decisions"` in `inputs/kt_decisions.json`, and set `"date": "2026-10-26"`:

```json
{
 "crown_dome": {
  "decision": "ACCEPTED",
  "date": "2026-10-26",
  "kT": "Agree to 1-3 (1: the crown dome assumption).",
  "as": "Crown dome over L1 and the L2 viewport band: proof-tested transparent ceramic panes up to 2.3 m (band panes 16-18 mm plates) as a 2226 materials milestone; tambour gores and shutters of armour-equivalent Strata laminate (Builder-derived, MHL-22); the dome and shutters open only at low speed or with the bow out of the dust flow, closed for solar particle events, radiation belts and torch burns."
 },
 "berth_viewports": {
  "decision": "ACCEPTED",
  "date": "2026-10-26",
  "kT": "Agree to 1-3 (2: the shielded viewport assumption).",
  "as": "Every opening below the crown carries an acrylic shield plug and insert with at least the g/cm2 they replace (armour 27, berth ring 8, shelter jacket 20), so berths and shelter keep their screens with the shutters open; the dose is accepted as a provision until a transport check (OLTARIS) is run; plugs are encapsulated and counted as fire load."
 },
 "habitat_changes_v057": {
  "decision": "APPROVED",
  "date": "2026-10-26",
  "kT": "Agree to 1-3 (3: the habitat changes).",
  "as": "kT approves, as design owner: berths 2.10 x 0.70 m with a 4 cm partition; medical opening at 202 deg; the L3 floor-edge water collar; one berth per person (G7); viewports in the berth ring; the service-section shield band. Sol remains second reviewer."
 }
}
```

## 2. Certification status after the decisions

`certified` = **false**. Rule: every gate PASS or PASS-DECLARED and every declared assumption ACCEPTED by kT; then both reviewers sign and loom-gate passes.

| Gate | Title | Verdict |
|---|---|---|
| G1 | Mass and fluids ledger | PASS |
| G2 | Torch and reach | PASS |
| G3 | Balance and attitude | PASS |
| G4 | Power and heat | PASS-DECLARED |
| G5 | Structure and loads | PASS |
| G6 | Radiation | PASS-DECLARED |
| G7 | Compartments and crew space | PASS |
| G8 | Shuttle, drones and bay exit | PASS |
| G9 | Failures and reserves | PASS |
| G10 | Mission suite (Navigator, run by Sol) | OPEN |
| G11 | Canon fit | PASS |
| G12 | Images | PASS |

| Gate | Declared item | kT |
|---|---|---|
| G4 | `torch_heat` | ACCEPTED |
| G4 | `torch_fin_temperature` | ACCEPTED |
| G4 | `plant_power` | ACCEPTED |
| G6 | `berth_viewports` | ACCEPTED |
| G6 | `crown_dome` | ACCEPTED |
| G6 | `shelter_life_support` | ACCEPTED |
| G6 | `gcr` | ACCEPTED |
| G6 | `torch_neutrons` | ACCEPTED |

Every declared item is ACCEPTED. What remains: Sol flies G10 in Navigator, both reviewers sign, and loom-gate passes.

---

## 3. Structure review

**NON-GOVERNING REVIEW, 2026-10-26** (kT: "let's evaluate 4"). Baseline: rev 4, geometry `646ac1ba...`. **The build is unchanged.** Source: `structure/structure_review_v057.py` (results in `structure_review_v057_results.json`). The review deliberately looks for load cases and methods the design checks did not cover.

**Same day:** kT accepted `crown_dome` and `berth_viewports`, and approved the v0.5.7 habitat changes as design owner (`inputs/kt_decisions.json`). Every declared item is now ACCEPTED. `certified` stays false until G10 is flown and both reviewers sign.

## Verdict

The structure is sound in concept. Every member closes a load path, and nothing fails against the 400 MPa material floor that G5 uses. The review found **one sizing shortfall, one gap in the G5 method, and one unchecked joint problem**. All three are fixable in a rev 5, at about 1.5 t from the 53 t reserve.

## A. Longerons: bending was not checked, and G5 overstates their area

- **Bending.** G5 checks axial load only. The thrust line sits 0.40 m from the centre of the mass ahead, which gives 13.5 MN·m. A 0.5° thrust error adds 9.1 MN·m.
- **Method.** G5 takes the member area from part mass, and part mass includes the spread engineering reserve. That reserve is a mass margin, not material. In v0.5.6 this didn't matter, because the members were six times oversized; with members sized tight, it does.

| | Axial | Axial + bending | Design (sized to) | Floor (G5) |
|---|---|---|---|---|
| G5 method (area 0.0868 m²) | 212 MPa | 237 MPa | 250 | 400 |
| Real material (area 0.0739 m²) | 249 MPa | **279 MPa** | 250 | 400 |

**Fix:**
- **Tubes:** wall from 72 mm to about 83 mm at the same 0.40 m diameter (+11.5% area, +1.2 t of tube; end fittings +12%, about +0.2 t).
- **G5:** compute longeron area from the structure-line share, and add the combined axial + bending check.

## B. Viewport band: two connections the study did not show (both pass)

- **Ring to shell.** 436 kN/m of shear flow on 2 rows of M10 titanium bolts at 50 mm pitch: 10.9 kN per bolt against 43 kN capacity (margin 4.0). Bearing on the CFRP is 36 MPa against 400.
- **Shear across the band.** There are no diagonals across the band, so sideways load is carried by the mullions bending (a Vierendeel frame). 89 kN of lateral load gives 74 MPa in the mullions against 600.

## C. Thermal mismatch between the titanium rings and the CFRP shell (not covered)

- **The problem.** Titanium expands about 17 times more than the CFRP laminate. Over a 50 K swing (shutters opening to deep space and closing), a 27 m ring differs from the shell by **about 11 mm**. Bolted rigidly, the ring would carry about 46 MPa and the joint would work back and forth every cycle, so fatigue matters.
- **Fix:** compliant attachments (slotted holes or titanium flexure fingers, an Osteon-friendly detail). Or make the rings CFRP and keep titanium only at the mullion roots.

## Recommended rev 5 (small)

1. Longeron walls to 83 mm, and end fittings +12% (about 1.4 t in all).
2. G5: area from the structure line, plus a combined axial + bending check.
3. Band rings: compliant attachments, or CFRP rings; add a thermal check.
4. Re-run all gates.

---

## 4. Review results

`structure/structure_review_v057_results.json`:

```json
{
 "header": "ALL bodies. ALL sponsors. 2026-2226.",
 "status": "NON-GOVERNING review of v0.5.7 rev 4",
 "assumptions": {
  "thrust_misalignment_deg": {
   "value": 0.5,
   "note": "ENGINEERING_ASSUMPTION: torch thrust vector error / gimbal authority used by the trim budget"
  },
  "design_mpa": {
   "value": 250.0,
   "note": "the design stress the longerons were sized to (400 MPa floor x 0.62)"
  },
  "floor_mpa": {
   "value": 400.0,
   "note": "materials.cfrp_allowable_mpa (what G5 checks against)"
  },
  "dT_K": {
   "value": 50.0,
   "note": "ENGINEERING_ASSUMPTION: ring-to-shell temperature swing as shutters open to deep space and close"
  },
  "alpha_ti": {
   "value": 8.6e-06,
   "note": "Ti-6Al-4V"
  },
  "alpha_cfrp": {
   "value": 5e-07,
   "note": "quasi-isotropic CFRP, in-plane"
  }
 },
 "A_longerons": {
  "state": "S2",
  "mass_ahead_t": 1001.9,
  "cg_ahead_m": [
   20.109,
   0.019,
   -0.383
  ],
  "F_ult_mn": 73.7,
  "moment_offset_mnm": 13.5,
  "moment_misalignment_mnm": 9.1,
  "area_G5_m2": 0.0868,
  "area_structure_line_m2": 0.0739,
  "G5_method": {
   "axial_mpa": 212.2,
   "plus_bending_mpa": 237.3
  },
  "structure_line": {
   "axial_mpa": 249.3,
   "plus_bending_mpa": 278.8
  },
  "design_mpa": 250.0,
  "floor_mpa": 400.0,
  "area_needed_for_design_m2": 0.0824,
  "area_increase_pct": 11.5,
  "extra_span_mass_t": 1.22,
  "findings": [
   "G5 computes longeron area from part mass, which includes the spread engineering reserve (a mass margin, not material): unconservative once members are sized tight",
   "G5 checks axial load only; the thrust line's offset from the mass ahead and a 0.5 deg thrust error add bending"
  ]
 },
 "B_band": {
  "ring_to_shell": {
   "shear_flow_kn_m": 435.7,
   "bolts": "2 rows of M10 Ti at 50 mm",
   "per_bolt_kn": 10.9,
   "bolt_shear_capacity_kn": 43.2,
   "margin": 3.97,
   "cfrp_bearing_mpa": 36.3,
   "bearing_allow_mpa": 400,
   "ok": true
  },
  "vierendeel_shear": {
   "lateral_kn": 89.1,
   "mullion_moment_knm": 6.2,
   "mullion_weak_axis_mpa": 74.4,
   "allow_mpa": 600,
   "ok": true,
   "note": "no diagonals across the band, so lateral shear is carried by mullion bending (a Vierendeel frame)"
  }
 },
 "C_thermal": {
  "ring_circumference_m": 27.02,
  "free_mismatch_mm": 10.9,
  "ring_stress_if_locked_mpa": 46.2,
  "verdict": "not covered by any check: a bolted Ti ring on a CFRP shell fights a ~10 mm circumferential mismatch every shutter cycle; needs compliant (slotted or flexure) attachments, or a CFRP ring with titanium only at the mullion roots"
 }
}
```

## 5. Review script

`structure/structure_review_v057.py` (Python 3, standard library; run from the package root):

```python
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
```
