# Metric Arrival Law v1 proposal

STATUS: DRAFT, NOT CANON. Pending kT approval.

**ALL bodies. ALL sponsors. 2026–2226.**

**Authority:** This is an intake draft for a *scoped* amendment to Canon II Engineering, Ships and Operations v2.4, sections 7.1–7.3. Baseline main: b4330385fd5de47af4199a22a37cc1bacf8c660f, after merged lab PRs #442–#444. No governing canon, registered CCR, default, Navigator or lab card is changed by this document.

## Proposed rule: ENERGY + orbit-relative heading B

Propose a declared calibrated natural arrival-velocity closure for ordinary Solar System Metric transit. The already-governing empirical, path-dependent U^M_gamma remains the **general** Metric ordinary-state propagator. This scoped rule fixes arrival velocity in the proposed operating regime, not path, position, phase, collapse certification or capture.

Use an approximately **Sun-barycentric kinetic counting frame**, and departure/arrival local orthonormal matrices F_s, F_a with columns Sun-radial, orbital prograde/tangential and orbit normal. After any PAID departure vector burn:

```text
v_a²      = |v_s|² + 2(Phi_s - Phi_a)
v_a_vec   = sqrt(v_a²) * F_a * F_s^T * (v_s / |v_s|)
v_a² < 0  : forbidden until PAID preburn makes arrival energetically possible
v_a = 0 or |v_s| = 0 : heading undefined, boundary not qualified
```

The lab evaluates Phi_i = -GM_sun/|r_i| - GM_i/(0.5 Hill_i); **0.5 Hill is diagnostic**, not a proposed universal canon acquisition/collapse radius. Potentials are frozen endpoint samples, even with moving planetary positions.

**Circular, tangential, aligned prograde endpoints only:**

```text
dv_pre = sqrt(v_target² + 2(Phi_a - Phi_s)) - v_source
```

This is the scalar speed increment when positive, **not** a general eccentric/inclined solution. Full vector optimisations charge heading changes and their ordinary torch impulse. Arrivals are not automatically matched: ordinary torch/RCS/tugs or other accounted exchange must pay remaining planet-relative velocity.

## Ledger and limitations

The Sun is the proposed nonlocal exchange partner, part of the Metric miracle rather than a demonstrated local coupler. For ship mass m fixed during the transit:

```
ship_dp = m * (v_arr - v_dep); sun_dp = -ship_dp
ship_dL = r_arr x (m*v_arr) - r_dep x (m*v_dep)
sun_dL = -ship_dL
       = -r_dep x ship_dp - (r_arr-r_dep) x (m*v_arr)
sun_recoil_K = |sun_dp|^2 / (2*M_sun)
field_work = -(ship_dK + m*(Phi_arr-Phi_dep) + sun_recoil_K)
```

The orbital/position-transport term is mandatory: an impulse term alone does not close angular momentum between distant endpoints. These Sun/field balancing entries are **identities by construction**, not independently tested physics. Solar recoil energy is negligible but cannot establish a physical coupling.

## Limits that remain open

**FROZEN-POTENTIAL WARNING:** moving Sun and planets lack one exact global Killing energy. The approximate barycentric velocity frame and Sun-centered endpoint potentials are a surrogate, not a validated time-dependent N-body work ledger. Local planetary gravity in burns, solar torque mechanism and orbital capture are unqualified. Existing Canon II environment/RSET hard gates and thermal/fin closure remain open. No path or collapse geometry is solved by this velocity law.

Step 4's phase-dependent kinetic cycle residual remains **MONITOR**: no free-work loop is authorized. A phase sweep for the sign and bound is a later diagnostic, not a condition manufactured for this proposal.

**Separate kT decisions:** adopt the scoped in-universe velocity closure; then decide whether any default-on behavior is justified. The laboratory Metric card stays in place. Navigator remains parked.

## Evidence supporting a *declared operational closure*, not fundamental proof

| Source | Narrow result |
| --- | --- |
| Step 1 | IDENTITY gives unpaid frozen-potential kinetic energy, approximately 1.958 GJ/kg for Jupiter surface to Pluto and 190.732 GJ/kg for Sun photosphere to Pluto; ENERGY closes that accounting exploit. |
| Step 2 | Outbound ENERGY can require a paid pre-jump torch burn to make arrival speed real. |
| Step 3 | Optimised orbit-relative B: Earth to Mars 4.828 km/s versus the circular scalar 4.794; Earth to Jupiter 10.392 versus circular 10.227. Orbit angle matters. |
| Step 4 | E-J-E requires a ~7.908 km/s initial seed (~264 MJ/kg), then leaves +44.86 kJ/kg kinetic phase residual, approximately 1.5 m/s at 30 km/s. Cycle residual is MONITOR; zero frozen mechanical ledger is by construction. |
| FQ11, merged #443 | Real finite Earth to Mars: raw 19.431/77.740 m/s mismatch nominal/1% underburn; 5 Hz RCS and finite trim give 0.121/0.481 m/s, consuming 2.983/3.172 tonnes. |
| FQ12, merged #444 | Jupiter to Earth: no preburn, 10,116.7 s Metric transit, 10.392 km/s inbound velocity mismatch. Finite brake ~1,069.744 s; 1% underbrake misses by 104.202 m/s, then 10.699 s finite torch trim recovers. Both finish ~0.821 m/s, ~6.175 t remass, 5 Hz RCS turn ~98.374 kg. |

FQ11/FQ12 show the *ship's ordinary propulsion and remass* can handle these assumed natural arrival states. They do **not** independently validate ENERGY-B or the Sun E/p/L mechanism. No canon, Navigator or default was modified to obtain those results.

## FQ12 known bias and optional RCS clean-up

Final moving-Earth target minus ship in J2000-oriented components is (−0.0600, +0.0277, −0.8187) m/s nominal and (−0.0507, +0.0398, −0.8187) m/s under-brake. The **−0.819 m/s z bias** remains after axial torch trimming. Both cases PASS within 1 m/s; this is non-blocking and also recorded in merged PR #444's conversation.

Optional later flight procedure only: a **finite 5 Hz RCS translation** to remove ~0.82 m/s. Ideal source-card water m*dv/ve ~0.49 t at ~1,166.5 t wet mass and RCS ve=1,960 m/s. Actual nozzle allocation, control and water consumption are **not yet simulated**. This clean-up is not a new canon or FQ12 pass criterion.

## Authority and stop condition

This is **CCR intake material, not an allocated or approved CCR**. The current registry records CCR-2026-0001 and -0002, without an approved Metric-arrival implementation request. Under canon/AGENTS.md, a controlled change to canon/current requires a specifically registered CCR in APPROVED_FOR_IMPLEMENTATION state. A later authorised implementation PR must update only the required governing text, authority/baseline manifests, hashes, validation and supersession records.

**Requested kT ruling:** approve or decline the scoped ENERGY-B arrival-velocity canon claim with its declared scientific limits. Decide any **default-on** operational adoption separately. The lab card stays. Navigator remains parked. This draft must not be merged as if it were the canonical law.
