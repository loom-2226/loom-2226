"""Shuttle v3 step 3: shape families inside the Wayfarer bay.
ALL bodies. ALL sponsors. 2026-2226. NON-CANON engineering screen.
Aero uses the v2 ROM tools unchanged (../v2_lifting_body/aero_test.py:
modified Newtonian hypersonic, low-aspect subsonic + vortex lift, 3-D entry)."""
import sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'v2_lifting_body'))
import aero_test as AT

L = 12.8; R_ENV = 2.15; SLOT_W = 3.8          # derived envelope (SHUTTLE_V3_CONSTRAINTS.md section 2)
M_ENTRY_T = 58.0                               # 40 t dry + 2.6 t payload + ~16 t water kept for the climb
M_FLOAT_T = 75.6; RHO_SW = 1.025               # W2 heaviest water-landing case
V_NEED = 1.5 * M_FLOAT_T / RHO_SW              # 50% reserve buoyancy -> 110.6 m3

def mirror(half):
    """half: list of (y>=0, z) from keel (y=0, bottom) round to crown (y=0, top)."""
    h = np.array(half, float)
    return np.vstack([h, (h[-2:0:-1] * [-1, 1])])

FAM = {
 "F1 flying-boat lifting body": dict(
    sec=mirror([(0, -1.15), (1.0, -0.86), (2.0, -0.55), (2.05, -0.30), (1.80, 0.55), (1.25, 1.12), (0.6, 1.28), (0, 1.30)]),
    nose=0.30, nose_pow=0.55, anchor=0.75, plan="body", sharp=True, rn=0.30,
    wings={"fold (B4 type)": (13.0, 8.3), "inflatable/telescoping": (18.0, 14.0)},
    note="V planing belly = heat shield; sharp chines; fat topsides for volume"),
 "F2 lens": dict(
    sec=np.array([(2.12 * math.cos(a), 0.85 * math.sin(a) * (1 - 0.15 * math.cos(a) ** 2)) for a in np.linspace(-math.pi / 2, 3 * math.pi / 2, 40, endpoint=False)]),
    nose=0.45, nose_pow=0.5, anchor=0.5, plan="ellipse", sharp=False, rn=0.60,
    wings={"none": (0.0, 4.24)}, note="gentle entry, compact; thin section loses volume; poor glider"),
 "F3 blended wing": dict(
    sec=mirror([(0, -0.70), (0.9, -0.55), (1.8, -0.22), (2.12, 0.0), (1.8, 0.20), (0.9, 0.62), (0, 0.85)]),
    nose=0.55, nose_pow=0.8, anchor=0.5, plan="arrow", sharp=True, rn=0.25,
    wings={"fold outer panels": (10.0, 8.3)}, note="good glider for its span; thin centre body"),
 "F4 waverider": dict(
    sec=mirror([(0, -0.95), (1.05, -0.45), (2.12, 0.05), (1.4, 0.30), (0, 0.30)]),
    nose=1.0, nose_pow=1.0, anchor=1.0, plan="delta", sharp=True, rn=0.05,
    wings={"none": (0.0, 4.24)}, note="high hypersonic L/D, little volume, poor low-speed"),
}


def d_section(belly=-1.0, r=2.12, top_flat=None, n=14, chine_v=0.0):
    """Flat (or shallow-V) belly, round top following the bay circle: the fullest lifting section."""
    yb = math.sqrt(r * r - belly * belly)
    half = [(0, belly - chine_v), (yb * 0.5, belly - chine_v * 0.5), (yb, belly)]
    a0 = math.atan2(belly, yb)
    for a in np.linspace(a0, math.pi / 2, n)[1:]:
        half.append((r * math.cos(a), r * math.sin(a)))
    half[-1] = (0, r)
    return mirror(half)
FAM["F5 D-section, flat belly"] = dict(sec=d_section(-1.0), nose=0.30, nose_pow=0.55, anchor=0.85, plan="body", sharp=True, rn=0.35,
    wings={"fold (B4 type)": (13.0, 8.3), "inflatable/telescoping": (18.0, 14.0)},
    note="fullest section the bay allows with a flat lifting belly")
FAM["F6 D-section, shallow-V belly"] = dict(sec=d_section(-0.95, chine_v=0.30), nose=0.30, nose_pow=0.55, anchor=0.85, plan="body", sharp=True, rn=0.35,
    wings={"fold (B4 type)": (13.0, 8.3), "inflatable/telescoping": (18.0, 14.0)},
    note="F5 with a ~9 deg planing V: boat belly that still lifts")

def scale(fam, t):
    s = min(1.0, (max(t, 1e-3) / fam["nose"]) ** fam["nose_pow"]) if fam["nose"] > 0 else 1.0
    if fam["plan"] == "ellipse":
        s = max(0.03, math.sqrt(max(0.0, 1 - ((t - 0.62) / 0.62) ** 2))) if t < 0.62 else max(0.55, math.sqrt(max(0.0, 1 - ((t - 0.62) / 0.75) ** 2)))
    return s

def mesh(fam, n=48):
    sec = fam["sec"]; zmin, zmax = sec[:, 1].min(), sec[:, 1].max()
    za = zmin + fam["anchor"] * (zmax - zmin)
    ts = np.linspace(0, 1, n); rings = []
    for t in ts:
        s = scale(fam, t)
        rings.append(np.c_[np.full(len(sec), t * L), sec[:, 0] * s, za + (sec[:, 1] - za) * s])
    tris = []
    m = len(sec)
    for i in range(n - 1):
        for j in range(m):
            a, b, c, d = rings[i][j], rings[i][(j + 1) % m], rings[i + 1][j], rings[i + 1][(j + 1) % m]
            tris += [(a, c, b), (b, c, d)]
    ctr0 = rings[0].mean(0); ctr1 = rings[-1].mean(0)
    for j in range(m):
        tris.append((ctr0, rings[0][j], rings[0][(j + 1) % m]))
        tris.append((ctr1, rings[-1][(j + 1) % m], rings[-1][j]))
    T = np.array(tris)
    return T, rings

def volume(T): return abs(np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6)

def fit(rings):
    P = np.vstack(rings)[:, 1:]; yc = 0.0
    zs = np.linspace(P[:, 1].min(), P[:, 1].max(), 401)
    rr = [np.hypot(P[:, 0] - yc, P[:, 1] - z).max() for z in zs]
    zc = float(zs[int(np.argmin(rr))]); r = min(rr)
    w, h = np.ptp(P[:, 0]), np.ptp(P[:, 1])
    return dict(center_z_m=round(zc, 3), max_radius_m=round(float(r), 3), width_m=round(float(w), 2), height_m=round(float(h), 2),
                fits=bool(r <= R_ENV + 1e-6 and min(w, h) <= SLOT_W))

def evaluate(name, fam):
    T, rings = mesh(fam)
    n, A = AT.geom(T); Swet = float(A.sum()); Sb = float(AT.planform(T))
    Abase = float(np.abs(np.array([0.5 * np.linalg.norm(np.cross(t[1] - t[0], t[2] - t[0])) for t in T[-len(fam["sec"]):]])).sum())
    V = volume(T)
    pol = [(a, float(np.divide(*AT.newtonian(T, Sb, Swet, a, 1.2)))) for a in range(10, 56, 5)]
    a_fly = 40 if fam["sharp"] else max([p for p in pol if 15 <= p[0] <= 45], key=lambda p: p[1])[0]
    res = dict(note=fam["note"], fit=fit(rings), volume_m3=round(V, 1), S_body_m2=round(Sb, 1), Swet_m2=round(Swet, 1),
               base_m2=round(Abase, 2), reserve_buoyancy_pct=round((V - M_FLOAT_T / RHO_SW) / (M_FLOAT_T / RHO_SW) * 100),
               meets_W2=bool(V >= V_NEED), hyper_LD_max=round(max(p[1] for p in pol), 2), wings={})
    v = dict(T=T, S_body=Sb, S_wing=0.0, span=float(np.ptp(T[..., 1])), Swet=Swet, Abase=Abase, sharp=fam["sharp"], rn=fam["rn"])
    e = AT.entry(v, "Earth", M_ENTRY_T * 1e3, a_fly)
    res["earth_entry"] = {k: round(float(e[k]), 2) for k in ("alpha", "LD", "beta", "peak_g", "peak_q_Wcm2", "heat_load_MJm2", "crossrange_km")}
    for wn, (Sw, span) in fam["wings"].items():
        vw = dict(v, S_wing=Sw, span=max(span, v["span"]))
        l = AT.landing(vw, 1.225, 9.81, M_ENTRY_T * 1e3 * 0.75)   # lands with most climb water still aboard? use 75% of entry mass (~43.5 t)
        res["wings"][wn] = dict(S_wing_m2=Sw, span_m=span, subsonic_LD_max=round(l["LDmax"], 2),
                                touchdown_ms=round(l["v_td"], 1), sink_ms=round(l["sink"], 1))
    return res, T

if __name__ == "__main__":
    AT.build()
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.",
           "basis": dict(length_m=L, envelope_radius_m=R_ENV, slot_width_m=SLOT_W, entry_mass_t=M_ENTRY_T,
                         float_mass_t=M_FLOAT_T, volume_needed_W2_m3=round(V_NEED, 1),
                         landing_mass_note="subsonic numbers at 43.5 t (75% of entry mass) at sea level"),
           "families": {}, "reference": {}}
    meshes = {}
    for name, fam in FAM.items():
        out["families"][name], meshes[name] = evaluate(name, fam)
        print(name, json.dumps(out["families"][name]))
    B4 = AT.VEH["B4 double fold"]
    e = AT.entry(B4, "Earth", M_ENTRY_T * 1e3, 40)
    l = AT.landing(B4, 1.225, 9.81, M_ENTRY_T * 1e3 * 0.75)
    out["reference"]["B4-S (today)"] = dict(volume_m3=82.45, reserve_buoyancy_pct=round((82.45 - 73.76) / 73.76 * 100), meets_W2=False,
        S_body_m2=round(B4["S_body"], 1), hyper_LD_max=round(max(float(np.divide(*AT.newtonian(B4["T"], B4["S_body"], B4["Swet"], a, 1.2))) for a in range(10, 56, 5)), 2),
        earth_entry={k: round(float(e[k]), 2) for k in ("alpha", "LD", "beta", "peak_g", "peak_q_Wcm2", "heat_load_MJm2", "crossrange_km")},
        wings={"fold (B4)": dict(span_m=8.3, subsonic_LD_max=round(l["LDmax"], 2), touchdown_ms=round(l["v_td"], 1))})
    print("B4", json.dumps(out["reference"]))
    json.dump(out, open(os.path.join(HERE, "shape_families.json"), "w"), indent=1)
    np.savez_compressed(os.path.join(HERE, "shape_families_meshes.npz"), **{k.split()[0]: v for k, v in meshes.items()})
