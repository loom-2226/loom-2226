# Same physics, different craft: is the shuttle privileged in Weave operation?
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON physics. No canon, hardware or mass changes; kT decides.

**kT revised direction (2026-11-21):**
- The shuttle may be privileged by its smaller size and experimental technology, so Wayfarer does not need the same manoeuvring envelope.
- Both share M1/M2 physics and the same conservation principles.
- Derive what can be derived; do not invent scaling restrictions.

**Files:**
- `dash_scaling.py/.json`.
- `scaling_figure.py` → `scale_privilege.png`.
- Builds on `WEAVE_DASH_FIELD_MODEL_2026_11_21.md`, including its SOL-review corrections.

## 1. Foundations audit: where the exchange law should be
| Source | What it gives |
|---|---|
| Weave §7 | Metric = continuous Weave deformation with relational adjacency L fixed; β_machine = χ_M·J_M/N_eff is a calibration projection, not a field law |
| Weave §8 | ṁ_remass = 0. Hold power = cryo + control + correction + loss. The 2 GJ bank is a "formation/ramp/transient/abort reservoir, not propulsion fuel". "Local and global conservation bookkeeping remains a required fictional engineering closure." |
| Weave §15 | M1: global sector Λ determines effective geometry. Metric = Λ fixed; Loom = Λ_A → Λ_B. |
| Weave §16 | M2: S[W,Φ] = S_R + S_matter, δS/δW = J_Φ; Mc supplies a strong controllable source. No S_R is given. |
| CANON II §7.1a/b | ENERGY-B arrival law; the Sun is declared as nonlocal momentum partner; "a local coupler is not required"; field energy enters by identity. |

**Audit result:**
- **No document specifies where Metric's energy-momentum exchange occurs or why it is conservative.**
- The strongest defensible reading, as SOL proposed: the bank is control energy, and the large exchange runs through the M1 relational sector, nonlocally, as canon §7.1b already declares.
- **The missing permission is an explicit M1 exchange law:** who receives the momentum and centre-of-energy shift, at what rate, and in which frame energy is counted.
- That law is required equally by Wayfarer's existing Metric and by the shuttle's dash. **UNDETERMINED.**

## 2. Correction to SOL's figure
SOL's thin-wall estimate E_− ≈ −c²v²R²/(36Gδ) evaluates to **−1.9×10³¹ J** for R = 10 m, δ = 2 m, v = 100 m/s, **not 10³²**. The numerical integral here gives 1.89×10³¹ J.

Consequence for `WEAVE_DASH_FIELD_MODEL`: the R4 comparison ratio becomes ~6×10⁻⁹, not 6×10⁻¹⁰.

## 3. What can be derived about scale and geometry
**Common geometry:** unit lapse, flat slices, β = v(t)·F(x − X(t)).

**Exact expressions:**
- Eulerian energy density: ρ_E = (c²/16πG)(K² − K_ijK^ij).
- The ramp-rate stress term, linear in a = dv/dt: S^(a) = (c²/8πG)·a·½(∂_iF_j + ∂_jF_i).

**Results:**

| Result | Verdict |
|---|---|
| The geometric field demand does **not depend on payload mass**: the interior is flat, and G·m/(Rc²) ~ 10⁻²² | **DERIVED** |
| Snowplough mode (Alcubierre-type): demand ∝ v²·R^1.94·δ^−0.99, i.e. **∝ v²R²/δ** (area over wall). The ramp term ∝ a·R^1.9 and is independent of the wall. | **DERIVED** (numerical fit, matches the thin-wall formula) |
| Silent mode (zero-expansion, curl construction): demand ∝ v²·R^3.2·δ^−2.8, tending to **v²R⁴/δ³** for thin walls. The ramp term ∝ a·R^2.5·δ^−0.8. | **DERIVED** for this construction |
| **Why silent mode scales worse:** a zero-expansion domain must route the displaced flux (v·πR²) around itself through the wall shell, so the transverse flow ~ v·R/δ and the demand grows faster than area. **Small domains and thick walls are favoured.** | **DERIVED** (physical argument; matches the fit) |
| Causality (light-crossing ~3×10⁻⁸ s) and adiabaticity (τ/(δ/c) ~ 10⁷ at a 0.1 s ramp, against canon's ~5×10⁸ screen) **do not limit** 0.01–0.1 s ramps | **DERIVED** |
| Ramp stress dominates velocity stress when the ramp time is shorter than δ/v (~20 ms here) | **DERIVED** |
| Real control bandwidth (Mc, node and cryo response; WCS §17) | **UNDETERMINED** |
| How actuator energy and hardware map to geometric demand | **UNDETERMINED** (no M2 law) |

## 4. Shuttle versus Wayfarer
Spheres of equal area stand in for real hulls; the shape factor is **UNDETERMINED**.

**Size and demand:**

| Craft | Domain area | R_equiv | Silent-mode demand at 100 m/s | Mass per area |
|---|---|---|---|---|
| Shuttle | 284 m² | 4.75 m | 1.4×10³¹ J | 215 kg/m² |
| Wayfarer | 1,900 m² (CANON II §12) | 12.3 m | 2.7×10³² J | 615 kg/m² |

**Shuttle advantage in v² (or acceleration) per unit field capacity, under three hardware hypotheses:**

| Hardware hypothesis | Snowplough mode | Silent mode |
|---|---|---|
| HW1: capacity ∝ area (L² candidate plant, same node density) | 1.0× | **~3×** |
| HW2: identical hardware on both craft | 6.7× | **~20×** |
| HW3: prototype with k× capacity per area | k × the above | k × the above (k not derived) |

**Exchange demand** (momentum and centre-of-energy shift, ∝ mass): **2.9× lower per unit area** for the shuttle.

## 5. Answer to kT's question
- **Size alone does not privilege the shuttle in snowplough mode** if hardware scales with area (HW1).
- **It does privilege it in silent mode,** by about 3× even under HW1, and by more under any fixed-hardware comparison.
- **The shuttle carries less mass per unit area,** so the exchange it needs is ~3× smaller per unit domain.

These are **derived geometric consequences of the same physics, not invented restrictions.** The shuttle is the natural first platform for an **atmospheric, silent, high-bandwidth Metric mode**, while Wayfarer's large domain suits vacuum snowplough-mode cruise.

**Beyond geometry** (prototype construction: denser Mc, faster control, thermal and life trade-offs):
- These are plausible engineering advantages, k in HW3, and **not derived**.
- The thermal and wear numbers from the earlier ops model remain hypotheses.

**One rule binds both craft:** the M1 exchange law (§1). Until it is written, neither craft's Metric closes, and nothing here says what a dash costs in actuator energy.
