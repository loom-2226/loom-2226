"""Hot-fin layout search -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. For N = 3..8 radial fins (edge-on to the burn), mirror-symmetric about the slot's plane,
keeping the shuttle corridor clear, find the azimuths that need the shortest equal span to reject the torch heat.
View factor to space by 2D ray casting (fins block each other and the torch chain blocks them).
Angles phi are measured from +Z (the slot side). Inputs: fin_layout_inputs.json. Needs numpy."""
import json, math
from pathlib import Path
import numpy as np
HERE = Path(__file__).parent
I = json.loads((HERE / "fin_layout_inputs.json").read_text())
SIG = 5.670374419e-8
RC = I["body_radius_m"]["value"]
W = I["shuttle_corridor"]["slot_half_width_m"] + I["shuttle_corridor"]["clearance_m"]
RMAX = I["max_root_standoff_m"]["value"]
CH = I["chord_m"]["value"]
NP, ND = I["search"]["points_per_face"], I["search"]["directions"]
U = -1 + (2 * np.arange(ND) + 1) / ND          # sin(psi), stratified: equal weight in 2D diffuse emission
PSI = np.arcsin(U)


def root_r(phi):
    a = abs(phi) % 360
    a = min(a, 360 - a)
    if a < 90:
        r = W / math.sin(math.radians(a))
        return max(RC, r) if r <= RMAX else None
    return RC


def escape_integral(phis, span, roots=None):
    """Sum over all fin faces of the integral of the view factor to space along the span (m).
    roots: optional root radius per fin (default: the corridor rule in root_r)."""
    r0 = roots if roots is not None else [root_r(p) for p in phis]
    u = np.array([[math.sin(math.radians(p)), math.cos(math.radians(p))] for p in phis])   # (y, z)
    a = np.array([r * uu for r, uu in zip(r0, u)])
    b = np.array([(r + span) * uu for r, uu in zip(r0, u)])
    t = (np.arange(NP) + 0.5) / NP
    total = 0.0
    for i in range(len(phis)):
        pts = a[i] + np.outer(t, b[i] - a[i])                   # (NP, 2)
        for side in (1, -1):
            n = side * np.array([-u[i][1], u[i][0]])
            d = np.cos(PSI)[:, None] * n + np.sin(PSI)[:, None] * u[i]     # (ND, 2)
            P = pts[:, None, :] + 1e-6 * n                      # (NP, 1, 2)
            hit = np.zeros((NP, ND), bool)
            # torch chain cylinder
            bb = (P * d[None]).sum(-1)
            cc = (P ** 2).sum(-1) - RC ** 2
            disc = bb ** 2 - cc
            tt = -bb - np.sqrt(np.maximum(disc, 0))
            hit |= (disc >= 0) & (tt > 1e-9)
            for j in range(len(phis)):
                if j == i:
                    continue
                e = b[j] - a[j]
                den = d[:, 0] * e[1] - d[:, 1] * e[0]                       # (ND,)
                ok = np.abs(den) > 1e-12
                q = a[j] - P                                                 # (NP,1,2)
                tj = (q[..., 0] * e[1] - q[..., 1] * e[0]) / np.where(ok, den, 1)
                uj = (q[..., 0] * d[:, 1] - q[..., 1] * d[:, 0]) / np.where(ok, den, 1)
                hit |= ok & (tj > 1e-9) & (uj >= 0) & (uj <= 1)
            total += (1 - hit.mean(axis=1)).mean() * span
    return total


def capacity_gw(phis, span, T, roots=None, chord=None):
    return I["emissivity"] * SIG * T ** 4 * (chord or CH) * escape_integral(phis, span, roots) / 1e9


def span_needed(phis, T, q, roots=None, chord=None):
    lo, hi = 0.5, 200.0
    if capacity_gw(phis, hi, T, roots, chord) < q:
        return None
    for _ in range(22):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if capacity_gw(phis, mid, T, roots, chord) < q else (lo, mid)
    return hi


def corridor_margin_m(phis, roots):
    """Smallest sideways distance (m) from any +Z-side fin to the edge of the shuttle corridor (negative = inside)."""
    m = float("inf")
    for p, r in zip(phis, roots):
        a = abs(p) % 360
        a = min(a, 360 - a)
        if a < 90:
            m = min(m, r * math.sin(math.radians(a)) - W)
    return m


def layout(N, free):
    """free: the angles (deg from +Z, 0-180) of the mirror pairs; odd N adds one fin at 180 (-Z)."""
    phis = [p for f in free for p in (f, -f)]
    if N % 2:
        phis.append(180.0)
    return phis


def gaps(phis):
    s = sorted(p % 360 for p in phis)
    return [(s[(k + 1) % len(s)] - s[k]) % 360 for k in range(len(s))]


def feasible(phis):
    if any(root_r(p) is None for p in phis):
        return False
    return min(gaps(phis)) >= I["rcs_gap_deg"]["value"]


def optimise(N, T, q):
    npair = N // 2
    pmin = math.degrees(math.asin(W / RMAX))
    # start: spread evenly over the arc the corridor leaves free
    arc = [pmin + k * (360 - 2 * pmin) / (N - 1) for k in range(N)]
    free = sorted(p for p in arc if p < 180 - 1e-6)[:npair]
    best = span_needed(layout(N, free), T, q) if feasible(layout(N, free)) else 1e9
    step = 8.0
    while step >= I["search"]["angle_step_deg"]:
        improved = True
        while improved:
            improved = False
            for k in range(npair):
                for dlt in (-step, step):
                    trial = list(free)
                    trial[k] = min(179.0, max(pmin, trial[k] + dlt))
                    ph = layout(N, trial)
                    if not feasible(ph):
                        continue
                    s = span_needed(ph, T, q)
                    if s is not None and s < best - 1e-3:
                        best, free, improved = s, trial, True
        step /= 2
    return sorted(free), best


if __name__ == "__main__":
    out = {"corridor_half_width_m": W, "min_pair_angle_deg": math.degrees(math.asin(W / RMAX)), "layouts": {}}
    q = I["heat_gw"]["value"]
    for T in I["temperatures_k"]:
        for N in range(3, 9):
            free, s = optimise(N, T, q)
            ph = layout(N, free)
            face = 2 * N * CH * s
            vf = q * 1e9 / (I["emissivity"] * SIG * T ** 4 * face)
            m = face * I["fin_kg_per_m2_face"] / 1000
            z = sum((root_r(p) + s / 2) * math.cos(math.radians(p)) for p in ph) / N
            out["layouts"][f"{N}@{T}"] = {"N": N, "T": T, "angles_from_plusZ_deg": sorted(round(p % 360, 1) for p in ph),
                "span_m": round(s, 2), "face_m2": round(face), "planform_m2": round(face / 2), "mass_t": round(m, 1),
                "view_factor": round(vf, 3), "fin_centroid_z_m": round(z, 2), "min_gap_deg": round(min(gaps(ph)), 1),
                "roots_m": [round(root_r(p), 2) for p in ph]}
            print(f"T {T} N {N}: angles {out['layouts'][f'{N}@{T}']['angles_from_plusZ_deg']} span {s:5.1f} m, "
                  f"planform {face/2:6.0f} m2, {m:5.1f} t, view {vf:.2f}, min gap {min(gaps(ph)):.0f} deg")
    (HERE / "fin_layout_results.json").write_text(json.dumps(out, indent=1))
