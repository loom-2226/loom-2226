# Finite Weave dash: effective M2 field model and conservation closure
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON scientific report answering SOL's handoff (e17fd62). No canon, hardware or mass changes. Returned to kT and SOL for review.

**Verdict labels:** DERIVED / ASSUMED / INCONSISTENT / UNDETERMINED.

**Inputs:**
- `SOL_FINITE_METRIC_DASH_PHYSICS_2026_11_21.md` (e17fd62).
- `engineering/current/LOOM_2226_METRIC_LOOM_WEAVE_FICTIONAL_ENGINEERING_FOUNDATIONS_v0.1.md` (main), §§5, 7, 8, 15–17, 19.

**Files:**
- `dash_charges.py/.json`: conserved-charge ledger.
- `dash_ambient.py/.json`: ambient-matter transport.
- `dash_figure.py` → `dash_physics.png`.

**Earlier lane rules W1–W4 and the ops numbers** (1 MJ per dash, 18 dodges, 13.8 t module) are NOT used here. They remain hypotheses.

**Test dash:**
- 61 t shuttle.
- Domain radius R = 10 m, wall δ = 2 m.
- 100 m/s: 1 s ramp up, 1 s cruise, 1 s ramp down.
- Displacement 200 m.

## 1. Candidate effective M2 model
**Geometry** (foundations §5):
- ds² = −c²dt² + (dx^i − β^i dt)(dx_i − β_i dt).
- Lapse N = 1; flat spatial metric γ_ij = δ_ij.
- Shift β = v(t)·F(x − X(t)), with Ẋ = v.

**Two members of the family:**
- **Alcubierre-type** (SOL): F = f(r)·e_x.
- **Natário-type** (zero expansion): F = ∇×(½ f(r) e_x × r), so ∇·β = 0.
- Both use f = ½[1 − tanh((r − R)/δ)].

**Dynamics:**
- G_μν = 8πG(T^ship + T^W), where T^W is the effective Weave source.
- That source comes from the foundations §16 parent action S[W,Φ] = S_R[W] + S_matter[Φ,W], with δS/δW = J_Φ.

**Premise (ASSUMED, stated as the foundations sketch it):**
- S is local and diffeomorphism-invariant.
- The exterior is asymptotically flat.
- Metric operation keeps the global sector Λ fixed (§15).

**Consequence of the premise (DERIVED):**
- Noether's theorem and the Bianchi identity give ∇_μ T^μν_total = 0.
- The asymptotic Poincaré charges are conserved, changing only by flux at infinity: energy E, momentum P, angular momentum J and the **boost (centre-of-energy) charge K = E·X − c²P·t**.

**Optional exchange channel** (the unknown being tested): either an exterior tail of the Weave field reaching other matter (R2), or a nonlocal exchange (R3).

## 2. Is the moving metric a genuine solution?
| Item | Verdict |
|---|---|
| The target geometry carries an inertial interior through start–dash–stop (SOL) | **DERIVED** |
| Einstein's equations are "solved" by any metric if T is defined as G/8πG; that is not a solution | definitional |
| Hamiltonian constraint with flat slices: ρ_E = (K² − K_ijK^ij)/16πG. Alcubierre: ρ_E < 0 in the wall. Natário (K = 0): ρ_E = −K_ijK^ij/16πG ≤ 0 everywhere. No positive-energy source can produce either. | **DERIVED** |
| Ordinary-GR sourcing (negative energy ~ −1.9×10³² J for the test, SOL) | **INCONSISTENT** with the energy conditions |
| M2 supplies that exotic stress-energy (foundations §16 permission) | **ASSUMED**: no S_R action and no actuator law beyond the reduced calibration β = χ_M·J_M/N_eff |
| Dynamic attainability (does a source with its own equations of motion reach this T?) | **UNDETERMINED** |

## 3. Energy and momentum ledger (including transients)
**Field alone:**
- A compact Weave domain is exactly flat outside, so its asymptotic E, P and K are zero at every instant (**DERIVED**).
- Its local exotic energy (~10³² J) must therefore be balanced inside the domain by the source. That actuator cost is **UNDETERMINED**.

**Ship plus field, isolated:**

| Phase | What conservation requires |
|---|---|
| Start | P = 0 still holds, so during cruise the field must carry momentum −m·v (6.1 MN·s). In an exotic sector this can cost zero energy. (DERIVED requirement; feasibility ASSUMED.) |
| Cruise | K grows by m·c²·v·t. Field energy can absorb it as a tiny asymmetry (~6×10⁻¹⁰ of the wall scale). |
| Stop and relax | The ship ends displaced by ΔX with field relaxed and nothing else changed, so K has changed by m·c²·ΔX = 1.1×10²⁴ J·m. That violates K conservation. **INCONSISTENT.** |

SOL's note is correct that no *net impulse* is required. It is incomplete: the **centre-of-energy charge** is conserved too.

**The only closures:**

| Route | Requirement for the test dash | Verdict |
|---|---|---|
| R1: radiate the impulses away | ≥ 2·m·v·c = **3.7×10¹⁵ J** | DERIVED bound; prohibitive |
| R2: exterior Weave field reaching environment matter (local partner) | partner impulse 6.1 MN·s; ½mv² = **3.0×10⁸ J** supplied at start, returnable at stop; Earth displaced by 2×10⁻¹⁸ m | DERIVED structure; needs S_R with exterior range (UNDETERMINED) |
| R3: nonlocal exchange with a distant partner (canon §7.1b type) | in the Sun frame ±dp·v_rel = **±1.8×10¹¹ J** | needs M1 nonlocality; partner law UNDETERMINED |
| R4: permanent field remnant (energy-dipole "scar") | ±energy separation of order m·c²·ΔX (±5.5×10²¹ J over 200 m) | mathematically allowed in an exotic sector; physically extreme; UNDETERMINED |
| R5: Loom-type sector change Λ_A → Λ_B (M1) | no flux needed | outside Metric by construction: this is option 2 / Weave seams (§19) |

**Environment:**
- Natário domain: ambient air kinetic energy ~23 MJ during cruise, returned at stop.
- Alcubierre domain: ~31 GJ of compression in the dust limit (see §6).
- Outgoing radiation from field ramps: **UNDETERMINED** apart from the R1 bound.

## 4. Position, velocity and crew
- **Crew acceleration:** ~0 inside the plateau, because interior Eulerian observers are geodesic (**DERIVED**, SOL).
- **Position change:** needs one of closures R1–R5 (**DERIVED**).
- **Velocity change:** with an exchange channel (R2/R3), u_f = u_i + ΔP/m. **Velocity can change** (**DERIVED** structure).
  - The energy is the change in kinetic plus potential energy *in the partner frame*.
  - Examples: stop from 300 m/s absorbs 2.7 GJ; start to 1 km/s supplies 31 GJ.
  - The ship can stop relative to an observer without conventional acceleration. The momentum goes to the partner, and the kinetic energy goes to the source, which must absorb it.
- **The earlier "torch owns velocity" rule (W3)** was a lane choice. **It is not derived**, and it is withdrawn as a physical claim.
- **Canon tension:**
  - Canon reaches 0.268c from a ~2 GJ bank.
  - With R2/R3 and immediate discharge, ½mv² for Wayfarer at 0.268c is ~4×10²¹ J.
  - Canon's own Metric is therefore consistent with the charge theorem only through R4 or R5, or through a partner law that has not been written.
  - **The blocker identified here is canon's blocker too.**

## 5. Closed cycles
- **Complete system returned** (ship, field, source, environment and partner all restored): no net work. **DERIVED** from conservation.
- **Partner at rest in the local potential frame** (e.g. Earth near Earth): a metric up-hop with no source input must conserve mechanical energy *in that frame*. From a hover it is forbidden; with input it pays m·g·h. The cycle nets zero. **DERIVED.**
- **Partner moving relative to where energy is harvested** (e.g. the Sun near Earth):
  - A 1 km up/down cycle harvests 0.6 GJ for 61 t. This is not perpetual motion: it is energy-conserving extraction of Earth–Sun relative motion, and unbounded in practice. **DERIVED.**
  - Canon ENERGY-B counted in the Sun frame is equivalent to a Sun partner, so it inherits this harvest.

## 6. Atmospheric boundary (`dash_ambient.py`, `dash_physics.png`)
**Exact kinematics (DERIVED):**
- With N = 1 and flat slices, Eulerian observers are geodesic.
- Matter initially at rest where β = 0 stays Eulerian, so **ambient matter moves with dx/dt = β**, with d ln ρ/dt = −∇·β.
- A uniform-pressure perfect fluid is consistent with this wherever ∇·β = 0.
- **The domain's expansion field decides the disturbance.**

**Results for the 200 m test dash:**

| | Alcubierre-type | Natário-type (∇·β = 0) |
|---|---|---|
| Compression | air in the path piled to ×189 at the stop | none: density ×1.00 everywhere |
| Behind the dash | channel at 0.007 of ambient density | ambient air passes around; on-axis air drifts forward |
| Energy | compression ~31 GJ | ambient kinetic energy ~23 MJ, returned at stop |
| What happens in real air | a blast plus a thunderclap. The dust limit overstates the pile-up because real air sends pressure waves ahead. | silent in the ideal-fluid limit |
| Interior air | — | carried with the domain |

**Verdicts:**
- Silent passage for zero-expansion domains: **DERIVED** for an ideal fluid.
- Blast for Alcubierre-type domains: **DERIVED** (dust bound).

**Still UNDETERMINED:**
- Earth's gravity. N ≠ 1, so ambient matter is held hydrostatically rather than Eulerian; this matters for vertical motion.
- Free surfaces: water displaced by the domain makes waves.
- Solids: a domain overlapping ground drags rock and stresses it.
- **The missing coupling:** whether S_matter couples ordinary matter to the Weave **only through g_eff** (minimal coupling, assumed above) or **directly to W**.

## 7. Does it fit within M1/M2?
| Part | Verdict |
|---|---|
| Geometry and inertial crew | within M1's metric readout (§5, §15) |
| Exotic sourcing | M2 permission (§16). **ASSUMED**; no constitutive law |
| Charge closure | needs either an **exterior range of S_R** (inside M2, no new permission) or **nonlocal exchange** (canon declares it in §7.1b; the foundations do not formalise it in §§15–16) |
| Free displacement with no flux | is R5, an M1 sector change, i.e. Loom-type |

**No third miracle has been shown to be necessary.** The **exchange law is missing**, so overall: **UNDETERMINED**.

## 8. The exact blocker and the smallest next experiment
**Blocker:** the **exterior range λ and matter coupling of the linearised Weave response S_R**. Equivalently: does the Weave field reach anything outside the domain, and through what? This one property decides:
- the partner, and therefore the energy cost;
- whether velocity changes are local and cheap (R2), frame-harvesting (R3), or need Loom events (R5);
- how much the air or ground is pushed, beyond the minimal-coupling transport above.

**Smallest next experiment:**
- Write the linearised S_R as one vector (shift) field sourced by the Mc current: L = −(1/4)F_ij F^ij − ½ m_W² β² + β·J_Mc, with range λ = 1/m_W, coupling to matter minimally through g only.
- Solve the exterior field for the test dash at three ranges: λ → 0 (compact), λ ~ R, and λ → ∞.
- For each, read off the partner distribution, the energy in the partner frame and the ground/air momentum flux.
- No other parameter is needed.

## Consequences if a channel closes (reported, not restricted)
**If R2 or R3 exists**, the Weave is a **propellant-free, inertia-free manoeuvring drive**:
- Velocity can change.
- Energy cost = change in kinetic plus potential energy in the partner frame.
- No physical acceleration cap appears; limits are source power and storage and the actuator, all UNDETERMINED.
- **Zero-expansion designs pass silently through air.**

**What that would transform:**
- The torch's role (velocity is no longer torch-only).
- Remass economics.
- Combat doctrine (inertialess jinks, silent approach).
- Orbit insertion (it becomes an energy question, not a propellant question).

**With a Sun-type partner near planets**, it also becomes an energy harvester of orbital relative motion.

**None of this is promoted.** kT decides.
