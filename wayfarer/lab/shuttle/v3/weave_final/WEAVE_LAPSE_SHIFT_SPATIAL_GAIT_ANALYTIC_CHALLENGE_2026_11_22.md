ALL bodies. ALL sponsors. 2026-2226.

# One-arm challenge: lapse, shift, spatial metric, and possible temporal gait

**Status:** NON-CANON / NON-RUNTIME / ANALYTIC ONLY. kT hypothesis, Claude reviewer challenge, Sol independent analytic screen. No new Builder permission, constitutive control law, simulator, geometry, CCR, or canon change. For Claude independent review.

**Sources in this branch:** `TEMPORAL_OBSERVATION_ANALYTIC_NOTE_2026_11_22.md` (the adopted N=1 null), `GAIT_TEST_2026_11_22.md` (a chosen two-control connection, not a derived Builder law), `BUILDER_RULEBOOK_2026_11_22.md` (R1 shift carriage, R2 experimental directional W2, R4 external exchange, R5 conditional ledger). Governing physical firewall: `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.5.md` §§2, 7.3, 21. Research context: Gourgoulhon's 3+1 formalism; numerical relativity ADM constraint equations; Wisdom 2003 spacetime swimming.

## 1. What the previous null establishes (and does not)

Metric sign convention, consistent with Tic Tac:
```
ds² = -N² c² dt² + gamma_ij (dx^i - beta^i dt)(dx^j - beta^j dt).
```
For a normal-observer trajectory `dx^i=beta^i dt`, `dτ=N dt`. The prior screen imposed `N=1` and flat spatial `gamma_ij`; therefore `dτ=dt` for an ideally field-comoving clock. The absence of a new field-induced proper-time offset **was built into the selected metric**. It was a correct within-model null, **not** evidence against the possibility of a different lapse profile.

**Critical gauge firewall:** `N, beta, gamma` are 3+1 fields dependent on foliation/coordinates, not three freely adjustable invariant physical knobs. A uniform global `N(t)` with no spatial structure is a time-coordinate reparametrisation; selecting a different time label does not alter physical clock comparison. Physically compare proper times of specified clocks brought to a shared event, measured redshifts, local curvature, asymptotic charges and the motion relative to identified partners. In a static/stationary comparison the lapse ratio can encode an observable redshift when the relevant observers/normalisation are specified; the bare ratio is not universally invariant under arbitrary slicing.

## 2. Original restrictions A1–A5

| Item | Existing shortcut | Honest relaxation |
|---|---|---|
| A1 | N=1 for the Weave | Allow spatially varying **positive** N tied to physical observers; nontrivial spacetime curvature/stress may result |
| A2 | Flat 3-metric; zero expansion in the shift example | Allow curved gamma; note **3-curvature and expansion K are distinct**. Flat slices need not imply zero extrinsic curvature |
| A3 | Static or slowly varying fields | Allow temporal derivatives, but derive extrinsic curvature, energy flux and tidal/causal effects; dynamic control is not free |
| A4 | W2 potential-type lapse treated separately | Integrate W2 into the **same** N sector for accounting, avoiding two separate 'time/gravity fields' charged twice |
| A5 | Coordinate time t treated as a flight parameter | Ask whether Builder control can alter **physical proper-time relations**; changing chart t is not itself time engineering |

## 3. Independent checks of Claude's fast claims

- **Clock rate:** for `dx=beta dt`, `dτ=Ndt`. Lapse `N>0` can alter accumulated rates along designated normal worldlines, without reversing proper-time orientation; no time travel is conferred. `N=0` is a lapse/foliation degeneracy; a specific chart may put a horizon there, but the condition **alone does not prove a physical event horizon**.
- **Acceleration:** Eulerian observers' proper acceleration vector is `a_i=c² D_i ln N` (for the adopted units/sign). A ratio 2:1 across a 1 m wall implies a mean logarithmic-gradient scale `c² ln2/(1 m)≈6.23e16 m/s²≈6.36e15 g`. This is the acceleration needed to hold the normal congruence, **not** a claim that every free-fall passenger instantly feels that acceleration.
- **10% clock ratio:** stationary-lapse effective potential contrast `Delta Phi_eff=c² ln(1.1)≈0.09531 c²≈8.56e15 J/kg`. Neutron-star-scale as a gravitational-potential analogy, not an ordinary weak-field design law. This does not determine local source energy or wall stress.
- **Flat 3-slices do not imply a cheap field.** Analytic GR example with `beta=0`, `gamma_ij=delta_ij`, `ds²=-N(t,x)²c²dt²+dx²+dy²+dz²`:
  `R^(3)=0`, `K_ij=0`. The Hamiltonian constraint gives Eulerian energy density `rho=0` (zero cosmological constant). In geometric units the Einstein tensor is `G_tt=G_xx=0`, `G_yy=G_zz=(∂²_x N)/N`, `R=-2 (∂²_x N)/N`; no `∂t N` term appears in this specialised tensor. More generally, for spatial N(x,y,z), `G_ij=(delta_ij laplacian(N)-∂i∂j N)/N`. Physical transverse stress is `S_yy=S_zz=(c⁴/8πG)(N_xx/N)`. A smooth localised rise/fall of N in a one-dimensional wall needs both signs of `N_xx`, so **negative transverse stress and NEC/WEC problems occur somewhere** for this GR matter source. `rho=0` does NOT mean zero stress, zero curvature, viable stress-energy, or zero physical resource cost. This is a specified GR toy geometry, not the existing fictional Builder constitutive law. A global compact nontrivial lapse bubble on exact flat asymptotic slices has zero ADM mass and cannot evade the standard energy-condition obstruction by relabelling clock time.
- **No chronology shortcut:** a positive, globally well-defined lapse and spacelike slices allow a monotonic global time function in the toy; do not infer CTCs or physically reversed proper time. CTCs remain a hard kill absent explicit kT permission.

## 4. Minimal analytic counterexample: clock offset without gait holonomy

Take `beta=0`, `gamma=delta`, `N(t,x)=1+epsilon*f(x)*u(t)`, with `f=1` in a central interior, `f=0` for an external comparison clock, both stationary, `u(t_0)=u(t_1)=0`, `N>0`. Two clocks synchronised at `t_0`, compared with a suitable common-frame reunion/clock comparison afterwards, have
```
Delta tau_centre - Delta tau_outer = epsilon * integral[t0 to t1] u(t) dt.
```
Therefore **YES:** a lapse pulse that returns all control parameters to baseline can leave a measurable relative proper-time offset; this is plain differential aging. If the signed time integral is zero, this toy produces **zero** net offset. Doubling the pulse duration doubles the offset: it is a *dynamical time integral*, **not automatically a rate-independent geometric holonomy**. No coordinate displacement is implied for stationary interior/exterior clocks, and this toy imports the nontrivial GR wall stresses above.

Even a physically nonzero clock offset does not establish that any local clock runs backward or that a hull can occupy alternative future events simultaneously.

## 5. Three exact answers to the gait questions

**Q1. Does variable/time-dependent N itself supply the connection curvature missing from the gait experiment?** **NO, not automatically.** Curvature of the 4D spacetime metric (Riemann tensor) is different from the control-space connection curvature `F_ab=∂a A_b-∂b A_a+[A_a,A_b]` used in `V=A(q) qdot`. A nontrivial `N(x)` may give 4D curvature but no defined two-control gait at all; the prior `GAIT_TEST` deliberately inserted a curved A(q) and did not derive it from Einstein's equations. Derive the *vehicle/control* response first before testing F.

**Q2. Can a closed shape/control cycle leave a net clock offset, displacement, or both?** **Clock offset YES in the toy, as accumulated elapsed proper time, even with one control; displacement NOT IMPLIED.** A genuine rate-independent shape-cycle holonomy (or persistent change in canonical state at the same control settings) requires an actual control connection and comparison after a closed loop. Two clocks with different histories can age differently without there being a new geometric locomotion law.

**Q3. Can joint N–beta cycles produce effects absent from beta-only cycles?** **POSSIBLE, NOT DERIVED.** A varying lapse can alter the timelike geodesic/clock response, and interactions with a spatially varying shift can lead to ordering-sensitive trajectories. But a mixed-loop result must be invariant under coordinate change, have specified worldlines and partner exchange, and survive comparison to gauge-equivalent and elapsed-time-controlled paths. Merely setting nonzero N and beta, or drawing a rectangle in parameter space, does not establish new Builder translation, permanent velocity or time holonomy.

## 6. Smallest follow-on, only if kT wants it

Keep the existing Tic Tac geometry and gait control concepts. Define only **two** bounded control modes in a compact, positive-lapse, asymptotically anchored 1+1 or 2+1 metric; allow W2 to occupy the lapse sector; compare:
1. N-only pulse versus no field: reunited-clock proper-time difference, curvature/stresses, no invented movement law.
2. Beta-only closed loop versus N–beta reversed-order loop **under identical endpoint conditions and proper-duration controls**: compare proper time, physical displacement relative to external anchored observer and final ordinary velocity. Include a pure-coordinate/gauge null.
3. Stop immediately if there is no specified physical law mapping the hull's controls to N/beta/gamma and its trajectory; **report that missing constitutive relation**, do not insert a convenient curved control connection.

Necessary checks: ADM energy/linear and angular momentum as applicable, energy conditions and wall gradients/stress, physical signal observables, causality/no CTCs, and an external exchange partner wherever momentum changes (Builder rulebook **R4**, not R1).

**STOP:** analytic examination supports reopening the N=1 and spatial-flatness assumptions as RESEARCH QUESTIONS, *not* authorising lapse engineering, time reversal, arbitrary spacetime edits, gait propulsion, or changes to canon. Claude to independently review this note.
