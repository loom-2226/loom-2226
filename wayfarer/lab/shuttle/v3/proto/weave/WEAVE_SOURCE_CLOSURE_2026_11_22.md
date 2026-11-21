# Weave source closure: GR ledger and M1/M2 exchange (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-22. Responds to Sol's brief "Weave source closure" after 4b62812. Baseline: R 15 m / wall 2 m zero-expansion shift, 200 m / 3 s quintic dash, 61 t payload. No canon, hardware or mass change.

Code: `weave_source_ledger.py`, `source_figure.py` → `weave_source_ledger.png`. Data: `weave_source_ledger.json`.

## 1. What GR mathematically requires

The prescribed metric is `ds² = −c²dt² + Σ(dxⁱ − bⁱdt)²` (N = 1, flat slices). Its effective stress-energy, `T = G[g]c⁴/8πG` measured by Eulerian observers, follows from the 3+1 equations (Gourgoulhon convention, β = −b):

```
K_ij = −½(∂_i b_j + ∂_j b_i),  K = 0
E    = −K_ij K_ij /16π                    (Hamiltonian constraint)
p_i  = ∂_j K_ij /8π                       (momentum constraint)
4π[(S−E)δ_ij − 2S_ij] = (∂t − L_β)K_ij + 2K_ik K_kj   (evolution)
```

**Validation (DERIVED).** Against the 4D Einstein tensor computed from nested finite-difference Christoffels at V = 0.1c, at 12 random points in the wall, the maximum relative error is 5e-7 for E, 1e-4 for p and 1e-5 for S. The formulas are polynomial in b, so this fixes every sign and factor at all speeds.

**Ledger over the dash (DERIVED):**

| Quantity | Value |
|---|---|
| Local source energy ∫E dV | negative throughout; peak −8.7e32 J at t = 1.5 s (∝ V²); returns to 0 |
| Net source momentum ∫p dV | 0 (numerical residue ≤ 5e-7 of the gross internal flow) |
| Gross internal momentum flow ∫\|p\| dV | up to 1.9e31 N·s (internal, cancelling) |
| Stress trace ∫S dV | up to −2.6e33 J |
| Local energy balance | dE/dt = ∫K_ij S^ij dV, matching within 0.5%: the 3+1 energy equation closes; the source exchanges energy with the gravitational field, not with anything outside |
| Boundary fluxes | fields at the integration boundary ≤ 2e-11 of peak; no flux |
| Energy conditions | E < 0: weak and dominant energy conditions violated (exotic) |

**Sourceability.**
- **DERIVED (mathematical):** the geometry is dynamically sourceable in ordinary GR. Any metric defines `T = G/8π`, the Bianchi identity makes it covariantly conserved, and the local energy balance is verified above.
- **Not established (physical):** sourceable by physically available matter. It needs negative energy density with internal momentum flows of order 10³¹ N·s.

## 2. Which global conserved quantities can actually be calculated

**Field alone (DERIVED).** On flat slices with a compact shift, the ADM energy (from the γ falloff), the ADM momentum (from the K falloff) and the ADM centre-of-mass / boost charge are all **identically zero at every instant**.

The local integral ∫E dV = −8.7e32 J is slice-dependent. Integrating the Hamiltonian constraint gives `∫E dV + ∫K_ijK^ij/16π dV = 0` exactly, so the source's local energy is cancelled by the gravitational (extrinsic-curvature) term. The local energy centroid moves 200 m with the domain, yet no global charge moves. **The field cannot serve as reaction mass.**

**With the payload (linear order).** Validity: Gm/c²R ≈ 3e-24 and b/c ≤ 4e-7, so linear order holds.
- The payload adds E_ADM = mc² = 5.5e21 J.
- Comoving with Eulerian observers (w = 0), it has zero Eulerian momentum density, so P_ADM = 0. This is the GR form of the earlier Noether "lost momentum": the carried payload's momentum is not hidden in the wall. It is absent in the Eulerian frame.
- The ADM boost charge `C = E_ADM X_CM − P_ADM c²t` is conserved, so **an isolated dash cannot end with the payload displaced and everything else restored** (DERIVED; confirms the earlier conditional result with explicit GR charges).

No −mV was assumed. The closure routes follow from the boost charge:

| Route | What carries the centre-of-energy change | Shuttle dash | Wayfarer Metric (1,153.9 t, 0.268c) | Status |
|---|---|---|---|---|
| **R1 External exchange** | A distant body recoils (non-isolated) | Earth recoil 2e-18 m (as in 586f1a4); a Sun partner instead gives a ±2.3e11 J transient in the Sun frame, net ≈ 0 | Exactly canon §7.1b (Sun partner) | CONDITIONAL on an exchange law |
| **R2 Radiation to null infinity** | Radiation carries momentum (E ≥ \|p\|c) | ≥ 2 m V_peak c = **4.6e15 J** radiated per dash, irreversible | ≈ 2.2e22 J (21% of Mc²) per acceleration; rest mass falls 24%; inconsistent with canon ṁ = 0 | DERIVED bound under its premises |
| **R3 Screened zero-energy package** | Source carries ADM energy −mc² co-moving with the payload; +mc² left behind | Leaves a permanent +5.5e21 J mass "ghost" at the start, or keeps a permanently screened shuttle of zero net inertial mass | Same with 1.04e23 J | CONDITIONAL; pathological (zero-inertia package or irremovable ghost) |

R3 is GR-consistent with exotic matter, but its endpoint is unphysical for a working vehicle. R2 is excluded for the Metric by canon numbers and is prohibitive for the shuttle. **R1 is the only route consistent with both vehicles under common conservation principles.**

## 3. What M1/M2 already permits (foundations §§5, 8, 15, 16)

- **§5:** the Weave reads out g_eff and Navigator derives physics with standard GR diagnostics. The Phase 1 ledger therefore applies to g_eff. (DERIVED within the foundations' own readout)
- **§15 M1:** relational configurations determine g_eff. **Metric = deformation with Λ fixed**, so the global sector Λ cannot be the exchange channel in Metric/Weave operation. Any exchange must be a local, long-range relational interaction (or canon's declared nonlocal coupling), not a Λ transition. (DERIVED from §15 definitions)
- **§16 M2:** one parent action `S = S_R[W] + S_matter[Φ, W]` with `δS/δW = J`. If S is translation and diffeomorphism invariant, Noether makes any coupling conservative automatically. But S_R is **unspecified**: neither the sign and falloff of the relational sector's effective ADM energy (R3) nor its range and partner selection (R1) is determined.
- **§8:** "Local and global conservation bookkeeping remains a required fictional engineering closure": explicitly open.
- **Canon II §7.1b:** declares, as canon, a nonlocal Sun exchange of energy, momentum and angular momentum for the Metric. That is an R1 law, declared rather than derived from M1/M2.

## 4. Additional assumption required

Phase 1 identifies one specific unresolved requirement: **an exchange law (R1)**. It must specify how the relational sector's stress couples momentum and energy to distant matter while Λ is fixed, including which body is the partner (nearest mass, Sun, or field-weighted).

The foundations leave this undetermined, so per the brief: **missing constitutive relation reported; stop.** No coupling was invented.

The only existing candidate is canon §7.1b's Sun partner. Applying it to the Weave would not add a new law, but it would remain ASSUMED. It would fix the shuttle's partner as the Sun rather than Earth (as in the 586f1a4 toy). kT and Sol have authorized challenging "Sun-only", so partner selection is the open constitutive choice.

## 5. Has a dynamically conservative shuttle dash been demonstrated?

| Claim | Verdict |
|---|---|
| Shift geometry sourceable in GR (mathematically) | **DERIVED** |
| Source is physically available matter | **UNDETERMINED** (exotic: E < 0, WEC/DEC violated) |
| Field carries no global charge; cannot be reaction mass | **DERIVED** |
| Isolated dash with full restoration is impossible | **DERIVED** (ADM boost charge) |
| Radiation closure costs ≥ 4.6 PJ per dash | **CONDITIONAL** (isolated, no partner); this replaces the withdrawn 3.7 PJ "floor" with a premise-explicit bound |
| Screened zero-energy package | **CONDITIONAL**, pathological endpoint |
| Conservative dash via external exchange | **CONDITIONAL** on an R1 exchange law; shown in the 586f1a4 toy with an Earth partner (A3) |
| R1 law supplied by M1/M2 | **UNDETERMINED**: missing constitutive relation |
| R1 law supplied by canon | **ASSUMED** (§7.1b Sun partner, declared) |

**Answer:** a dynamically conservative dash is demonstrated *conditionally*. It works if the relational sector exchanges momentum and energy with a distant body (R1). It is not derived from M1/M2. One constitutive relation is missing: the exchange law and its partner selection.

The same requirement applies unchanged to Wayfarer's Metric, where canon already assumes it (Sun). No canon change is proposed. The findings return to kT and Sol first.
