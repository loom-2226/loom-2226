"""L2 viewport band: the full load path -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING STUDY on the v0.5.7 rev 3 candidate (geometry 262b21a3...). It changes nothing in the build.
Answers Sol's qualification on PR #432: the rev 3 check spread the axial load over 23 mullions but did not show
the path through the interrupted pressure shell, the end rings and the window joints.

The band cuts the pressure shell round 330 deg of L2. Load paths, closed-form:
  1. Hoop tension over the band height: carried by two edge rings (sill and head), half each. The glass is NOT
     relied on to pass hoop tension through its edge joints (glass in tension at a clamped joint is the weak point).
  2. Panes: flat-plate bending between mullions, sill, head (and a mid transom in the 1.6 m lounge), two pressure
     panes each carrying full load.
  3. Axial flow: the shell's axial flow (pressure end load, or thrust on the mass ahead) collects into the mullions;
     each ring is a continuous beam between mullions.
  4. Ring-to-shell junction: the stiff ring restrains the shell's pressure growth (discontinuity bending).
  5. Joints: each mullion root carries its share into the ring (bolted, conventional; the Osteon fork can be integral).
Writes habitat/viewport_band_study_results.json. Usage: python habitat/viewport_band_study.py"""
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
CR = json.loads((ROOT / "habitat/crew_systems_results.json").read_text())
VB = I["habitat"]["crew_systems"]["viewport_band"]
R = I["hull"]["pressure_r_m"]
t_sh = 0.03                     # pressure hull wall (build: DomeCyl t 0.03)

A = {   # assumptions, each stated
    "p_pa": (101.325e3, "cabin pressure, 1 atm"),
    "pressure_factor": (2.0, "proof/ultimate factor on pressure loads, as used for the L4 bulkhead (crew_systems)"),
    "ti_allow_mpa": (600.0, "Ti-6Al-4V: 900 MPa UTS, knocked down for joints (same as the rev 3 mullion check)"),
    "ti_shear_mpa": (550.0, "Ti-6Al-4V bolt ultimate shear"),
    "ti_density": (4.43, "t/m3"),
    "shell_e_gpa": (60.0, "quasi-isotropic CFRP laminate (the 150 GPa in materials is the unidirectional longeron value)"),
    "shell_allow_mpa": (250.0, "CFRP design stress after the 0.62 knockdown used for the longerons"),
    "nu": (0.3, ""),
    "pane_allow": ({"ALON 2026": 70e6, "ceramic 2226 (crown milestone)": 200e6}, "design stress for flat panes in bending"),
    "ceramic_density": (3.69, "t/m3"),
}
a = lambda k: A[k][0]
p_u = a("p_pa") * a("pressure_factor")


def plate_beta(ab):
    """simply supported rectangular plate, max stress = beta p b^2 / t^2 (Roark Table 11.4 case 1a)."""
    tab = [(1.0, 0.2874), (1.2, 0.3762), (1.4, 0.4530), (1.6, 0.5172), (1.8, 0.5688), (2.0, 0.6102), (3.0, 0.7134), (4.0, 0.7410), (99, 0.75)]
    for (r0, b0), (r1, b1) in zip(tab, tab[1:]):
        if ab <= r1:
            return b0 + (b1 - b0) * (max(ab, 1.0) - r0) / (r1 - r0)
    return 0.75


def run():
    segs = VB["segments"]
    sp = R * math.radians(VB["mullion_spacing_deg"])          # mullion spacing, m
    n_mull = CR["viewport_band"]["mullions"]
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING study on v0.5.7 rev 3; the build is unchanged",
           "assumptions": {k: {"value": v[0], "note": v[1]} for k, v in A.items()}, "mullion_spacing_m": round(sp, 3)}
    # 1. hoop over the band height, half to each edge ring
    hmax = max(s["x_m"][1] - s["x_m"][0] for s in segs)
    hoop = {}
    for h, nm in ((0.6, "general band 0.6 m"), (hmax, f"lounge {hmax:.1f} m")):
        T = p_u * R * h / 2
        hoop[nm] = {"ring_tension_kn": round(T / 1e3, 1), "ti_area_needed_cm2": round(T / (a("ti_allow_mpa") * 1e6) * 1e4, 1)}
    out["1_hoop_to_edge_rings"] = hoop
    # 2. panes as plates
    panes = {}
    for nm, (b_span, a_span) in {"general band (0.6 x 1.13 m)": (0.6, sp), "lounge, no transom (1.13 x 1.6 m)": (sp, hmax),
                                 "lounge with a mid transom (0.8 x 1.13 m)": (hmax / 2, sp)}.items():
        b, L = min(b_span, a_span), max(b_span, a_span)
        beta = plate_beta(L / b)
        panes[nm] = {m: round(b * math.sqrt(beta * p_u / s) * 1e3, 1) for m, s in a("pane_allow").items()}
    out["2_panes_mm_each"] = panes
    # 3. axial flow into the mullions; ring as a continuous beam between mullions
    q = max(p_u * R / 2, CR["viewport_band"]["axial_load_thrust_mn"] * 1e6 / (2 * math.pi * R))   # N/m of circumference
    M = q * sp ** 2 / 12
    dx, w = 0.14, 0.04                                           # ring: 14 cm along the ship x 4 cm radial (bending about the radial axis)
    Z = w * dx ** 2 / 6
    A_r = dx * w
    sig_b = M / Z / 1e6
    T_lounge = hoop[f"lounge {hmax:.1f} m"]["ring_tension_kn"] * 1e3
    sig_comb = sig_b + T_lounge / A_r / 1e6
    ring_t = 2 * A_r * 2 * math.pi * R * a("ti_density")         # two full rings (they close over the washroom)
    out["3_rings"] = {"axial_flow_kn_m": round(q / 1e3, 1), "mullion_load_kn": round(q * sp / 1e3, 1), "ring_moment_knm": round(M / 1e3, 1),
                      "ring_section_cm": [dx * 100, w * 100], "bending_mpa": round(sig_b, 1), "with_lounge_hoop_mpa": round(sig_comb, 1),
                      "allow_mpa": a("ti_allow_mpa"), "two_rings_t": round(ring_t, 2), "ok": sig_comb <= a("ti_allow_mpa")}
    # 4. discontinuity bending in the shell next to a rigid ring
    E, nu = a("shell_e_gpa") * 1e9, a("nu")
    s_hoop = p_u * R / t_sh
    s_bend = 3 / math.sqrt(3 * (1 - nu ** 2)) * p_u * R / t_sh   # rigid ring: M0 = p/(2 beta^2), sigma = 6 M0 / t^2 = 1.82 pR/t
    s_ax = p_u * R / (2 * t_sh)
    beta_l = (3 * (1 - nu ** 2) / (R ** 2 * t_sh ** 2)) ** 0.25
    out["4_shell_at_ring"] = {"hoop_mpa": round(s_hoop / 1e6, 1), "axial_mpa": round(s_ax / 1e6, 1), "discontinuity_bending_mpa": round(s_bend / 1e6, 1),
                              "axial_plus_bending_mpa": round((s_ax + s_bend) / 1e6, 1), "allow_mpa": a("shell_allow_mpa"),
                              "decay_length_m": round(math.pi / beta_l, 3), "ok": (s_ax + s_bend) / 1e6 <= a("shell_allow_mpa")}
    # 5. joints
    Pm = q * sp
    d_b = 0.016
    cap = 4 * 2 * math.pi / 4 * d_b ** 2 * a("ti_shear_mpa") * 1e6   # 4 bolts, double shear
    out["5_mullion_root_joint"] = {"load_kn": round(Pm / 1e3, 1), "four_M16_double_shear_kn": round(cap / 1e3, 1), "margin": round(cap / Pm, 2), "ok": cap / Pm >= 1.5}
    # mass vs the rev 3 allowance
    area = VB["glazed_area_m2"]
    frame_allow = area * VB["kg_per_m2"]["frame_and_mullions"] / 1e3
    mull_t = n_mull * 0.05 * 0.20 * (sum((s["x_m"][1] - s["x_m"][0]) * (s["theta_deg"][1] - s["theta_deg"][0]) for s in segs) / 330) * a("ti_density")
    transom_t = 0.04 * 0.08 * R * math.radians(60) * a("ti_density")
    lounge_area = sum((s["x_m"][1] - s["x_m"][0]) * R * math.radians(s["theta_deg"][1] - s["theta_deg"][0]) for s in segs if s["x_m"][1] - s["x_m"][0] > 1.0)
    pane_extra = lounge_area * 2 * max(0.0, panes["lounge with a mid transom (0.8 x 1.13 m)"]["ceramic 2226 (crown milestone)"] - 16) / 1e3 * a("ceramic_density")
    need = ring_t + mull_t + transom_t
    out["mass"] = {"rings_t": round(ring_t, 2), "mullions_t": round(mull_t, 2), "lounge_transom_t": round(transom_t, 3), "frame_needed_t": round(need, 2),
                   "frame_allowed_rev3_t": round(frame_allow, 2), "lounge_pane_extra_t": round(pane_extra, 3),
                   "band_increase_t": round(max(0.0, need - frame_allow) + pane_extra, 2)}
    out["verdict"] = all(out[k]["ok"] for k in ("3_rings", "4_shell_at_ring", "5_mullion_root_joint"))
    return out


if __name__ == "__main__":
    r = run()
    (ROOT / "habitat/viewport_band_study_results.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: v for k, v in r.items() if k != "assumptions"}, indent=1))
