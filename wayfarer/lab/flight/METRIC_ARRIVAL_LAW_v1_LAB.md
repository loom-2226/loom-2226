# LOOM Metric Arrival Law v1 | kT-approved for LAB only

**ALL bodies. ALL sponsors. 2026–2226.** 2026-11-01. **LAB EXPERIMENT — NOT CANON, NOT NAVIGATOR, NOT A DEFAULT.** Authority at lab adoption: `main` `32a4a45a4f55007bbc5162d19438cd2ffd8300fe`, ship geometry `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`. The existing canonical Metric envelope/HOLD and FQ1–FQ10 remain unchanged unless the new lab flag is explicitly enabled.

## Rule: ENERGY with local Sun-orbit heading B

Use a **declared approximate Sun-barycentric counting frame**. Convert pre-hop ship velocity into its departure Sun-radial/prograde/orbit-normal components. Keep those *components* through Metric; express them in the destination's corresponding solar frame, with speed given by frozen endpoint ENERGY:

```
v_arr² = |v_depart|² + 2 (Φ_depart − Φ_arrive)
v_arr  = sqrt(v_arr²) F_arr F_depart^T (v_depart / |v_depart|)
Φ_i    = −GM_sun / |r_i| − GM_body / (0.5 Hill_body)
```

If `v_arr² < 0`, the state is forbidden until a **paid** pre-jump torch burn makes it nonnegative with a strictly positive speed for a defined heading. Pre-jump burns may steer; full vector Δv is charged. For circular, tangential, aligned endpoints only, the departure increment to match the destination reduces to `sqrt(v_target² + 2(Φ_arr−Φ_depart)) − v_source` when positive. **This scalar rule is not generally exact for eccentric/inclined orbits.**

## Mechanism: Metric miracle with closed books, not a local coupler

The Sun is the **declared E/p/L exchange partner**. The Metric miracle is permitted to couple nonlocally. It must close *energy, linear momentum and angular momentum*; no local nozzle, field actuator or other coupler is asserted or required by this lab rule.

For fixed ship mass `m` during the hop, `p_s=m v_depart`, `p_a=m v_arr`, and reference positions `r_s,r_a` about the Sun:

```
Δp_ship = p_a − p_s            Δp_sun = −Δp_ship
ΔL_ship = r_a × p_a − r_s × p_s
ΔL_sun  = −ΔL_ship
         = −r_s × Δp_ship − (r_a − r_s) × p_a
              [solar spin/impulse]   [solar orbital/transport]
ΔK_sun  = |Δp_sun|² / (2 M_sun)
ΔE_field = −(ΔK_ship + m ΔΦ + ΔK_sun)
```

**Important:** `r × Δp` **alone** omits the transport term when the endpoints differ. Both terms are booked to the Sun's *spin/orbit accounting ledger*, not a simulated change to physical solar rotation. The Sun's recoil energy is negligible; the field-work line is an explicit residual accounting entry, **not independent physical proof**. Torch exhaust receives the opposite preburn impulse; the idealized fusion energy debit is separately booked. The physical fusion/tap/plume closure remains OPEN.

## Declared assumptions and known limits

- **FROZEN-POTENTIAL CAVEAT FOR EVERY OUTPUT:** moving planets create no exact global Killing energy. Sun-only time-propagated JPL endpoint states and frozen Sun + endpoint-body half-Hill potentials are an exploratory surrogate, not a consistent multi-body Hamiltonian.
- Sun-centered JPL state is shifted by an **approximate barycentric solar reflex**. The Sun is the declared momentum partner; the real nonlocal E/p/L interaction and the allocation to solar spin vs orbit are not derived.
- **0.5 Hill** is a diagnostic radius, not a Metric admissibility policy. Metric NORMAL `0.268c` and 10 s ramp supply elapsed time, not ordinary XYZ transit.
- FQ11's preburn is an **ideal impulsive vector burn**; the report gives its nominal CRUISE duration and uses the current source-hash Wayfarer mass/torch card. No actual finite-burn trajectory, propulsion/thermal closure, moving planetary encounter, orbital capture, or Navigator handoff is qualified.
- Conservation pass is an *algebraic lab-ledger closure under assumptions*. No E/p/L empirical validation or physically independent check has been claimed.
- **Step 4 cycle MONITOR, not blocker:** Earth→Jupiter→Earth kinetic residual `+44.86 kJ/kg` corresponds to **~1.5 m/s** at 30 km/s after an **~264 MJ/kg paid energy seed**; end phase and speed need not match. Later diagnostic: sweep departure orbital phase and report **sign and bound** of the resulting cycle residual, with realistic planetary work and full return-state closure. Do not mistake frozen ENERGY zero-residual (by construction) for independent validation.

## Evidence and current decision

**Step 1:** IDENTITY energy creation, Jupiter surface→Pluto ~1.958 GJ/kg and Sun photosphere→Pluto ~190.732 GJ/kg, motivates ENERGY. **Step 2:** outward forbidden states require paid speed. **Step 3:** optimised orbit-relative B: Earth→Mars ~4.828 and Earth→Jupiter ~10.392 km/s; circular comparators ~4.794 and ~10.227. **Step 4:** E→J→E and E→M→J→E need paid seed, N→E→N initially traversable; frozen cycle work residual is phase-dependent; Sun recoil ~10⁻²⁰ m/s per hop, E/p/L mechanism still a declared miracle.

**kT decision:** approve this version for **Wayfarer LAB use only**. The current module is a **standalone, explicitly opt-in FQ11-CALC inverse-map tool** and does NOT hook `flightlab.run`. The actual finite-burn FQ11 is separate future work. All ordinary lab experiments and canonical Metric HOLD default off. The FQ11 report includes source epoch, ship mass, CRUISE Δv/remass, matched Mars velocity, Sun recoil, **absolute Sun angular-momentum transfer magnitude**, spin/orbit split and numerical E/p/L closure. FQ11-CALC is **not a qualification**: inverse arrival matching and the E/p/L balancing ledger are IDENTITIES by construction; only the conditional remass budget is calculated. **No canon or Navigator adoption.**
