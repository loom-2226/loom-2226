ALL bodies. ALL sponsors. 2026-2226.

# Tic Tac / Wayfarer planet-frame relational lock: analytic screen

**Status:** NON-CANON RESEARCH / NON-RUNTIME / PROPOSAL. kT concept; Claude independent review (numbers PASS, findings), Sol analytical reconciliation. **No new physical permission granted.** No simulations, geometry, cradle, canon, CCR or design mass change.

**Question:** Can Wayfarer occupy a natural stationary orbit in a rotating planet-centred frame while a Tic Tac follows a planet-locked relational path between surface and ship, arriving with compatible ordinary position and velocity rather than buying a separate orbital rendezvous?

**Relevant authority:** `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.5.md` §§2, 7.1a–7.3, 13, 21; the live `kt_decisions.json` and the NON-CANON `BUILDER_RULEBOOK_2026_11_22.md` (R1 no lasting velocity from Weave shift, R2 directional W2, R4 external exchange partner unknown, R5 conditional ledger, R7 chosen natural-arrival rule, R8 conditional accessibility). Continuation of `TICTAC_DOCKING_RECOVERY_CANDIDATES_2026_11_22.md`. Canon §7.1b's Sun partner is scoped to ordinary Solar System Metric transit; **do not transfer it to the prototype**.

## 1. Exact idealised Earth calculation (constant mass, spherical Earth, equatorial surface/GEO, fixed angular rate)

Use `m=48,500 kg`, `mu_E=3.986004418e14 m³/s²`, `Omega_E=7.2921159e-5 rad/s`, `R_E=6,378,137 m`, `r_GEO=(mu/Omega²)^(1/3)=42,164,169 m`; GEO altitude = **35,786.0 km**. This is an analytical fixture, not a solved mission trajectory.

- Inertial tangential speeds: `Omega*R_E=465.1 m/s`; `Omega*r_GEO=3,074.7 m/s`. Thus a **2,609.6 m/s** inertial tangential velocity change occurs even though the endpoints are fixed in Earth-rotating coordinates.
- `Delta L=m Omega(r_GEO²-R_E²)=6.14369e15 kg·m²/s`.
- Gravitational potential-energy gain: `Delta U=m mu(1/R_E-1/r_GEO)=2.572502 TJ`.
- Kinetic-energy gain from increasing co-rotating tangential speed: `Delta K=0.5 m Omega²(r_GEO²-R_E²)=0.224002 TJ`.
- **Total inertial mechanical-energy gain `Delta E=Delta U+Delta K=2.796504 TJ`.**
- A simple torque lock to Earth's spin could transfer `Omega Delta L=0.448005 TJ` of rotational energy **if and only if such a physical coupling exists**. Earth loses corresponding spin angular momentum; a coordinate label is not a source.
- **Remaining work in the rotating frame `Delta E'=Delta E-Omega Delta L=2.348499 TJ`**, equivalently the change in `m Phi_eff` with `Phi_eff=-mu/r-0.5 Omega² r²`. It needs an accounted onboard, external, or other explicitly granted source. It does not arise for free merely by naming Earth as a partner. Under a pure Earth-torque coupling with the stated `Delta L`, the 0.448 TJ contribution is the appropriate spin-energy transfer; using Earth's spin for the *full* 2.80 TJ would require an additional exchange mechanism/ledger.

**Reviewer reconciliation:** Claude's values 2.35 + 0.45 = 2.80 TJ PASS to rounding. In the current rulebook the *external exchange partner* concept is R4 (R1 labels ideal shift carriage), so call the proposed Earth connection a candidate R4 closure, **not** an already chosen R1 partner.

## 2. Three models, and the missing permission

| Model | Status | What physically happens | Payment and failure |
|---|---|---|---|
| Ordinary unit-lapse Weave shift follows prescribed positional displacement | **DERIVED WITHIN ADOPTED WEAVE FIELD MODEL** | Moves position but does **not** impart the required inertial tangential velocity. In a rotating-frame plot the position may be aligned but physical velocity is not; docking is unsafe | Separate velocity-matching propulsion/exchange needed; otherwise high-relative-speed encounter/abort |
| Weave translation + directional W2 changes ordinary velocity to `Omega r` as radius increases | **CONDITIONAL**, directional W2 already an experimental grant; long-range work/heat and control not closed | Could in principle attain both matching position and velocity if adequate paid work and angular momentum exchange exist | Field source/energy and unknown partner account for the full actual trajectory; failure leaves a suborbital/unmatched vehicle |
| **Planet-frame relational lock** continuously preserves fixed longitude/latitude coupling and supplies `dL=2m Omega r dr` during ascent | **NEEDS EXPLICIT kT PERMISSION** for the proposed constitutive law, partner and reach (unless independently derived later) | Arrives at GEO with tangential speed matched by construction, but must still stop radial motion and dock mechanically | Provisional Earth coupling can account for `Omega Delta L≈0.448 TJ`; remaining **2.348 TJ** must have a specified paid source, possibly existing W2 if hardware/thermal closure eventually allows it. No free-work loop |

Important: a rotating coordinate system is a coordinate choice, not a physical coupling. Existing R1 geodesic carriage alone does not implement a rotating-frame velocity lock. A near-field W2 is not a previously demonstrated 35,786 km acceleration/energy system. Do not silently extend human long-baseline certified Metric to the Builder.

## 3. Reach versus local field size

The Tic Tac's **15 m sphere is its local field radius, not a demonstrated upper bound on cumulative travel**. However, its current tested Weave manoeuvres are tens to hundreds of metres and the `GAIT_TEST_2026_11_22.md` exhibits unbounded cumulative displacement only with a **chosen nonzero configuration-space curvature**, not a derived Builder property. Continuous surface-to-GEO travel (~35,786 km altitude) therefore lacks an established accessible route, operational speed, thermal closure and partner exchange. R3 local Loom hops are a separate **ungranted** permission.

At GEO Wayfarer can maintain near-fixed Earth-relative longitude *in an equatorial, circular geostationary orbit*, subject to perturbation corrections. Generic geosynchronous, inclined or elliptical orbits are not ground-stationary. Non-equatorial surface launch points can remain fixed relative to a geostationary ship in the same Earth-rotating frame; their path is not simply equatorial radial ascent and requires separate geometry/accounting.

## 4. Other bodies: idealised stationary orbit screen

One-body `r_stat=(mu/Omega²)^(1/3)` must lie beyond the surface and inside a useful long-term dynamical stability region, not merely be mathematically real.

| Body | Candidate stationary orbital radius | Approximate verdict |
|---|---:|---|
| Earth | 42,164 km from centre; 35,786 km altitude | **YES**, geostationary equatorial orbit |
| Mars | ~20,428 km from centre; ~17,038 km altitude | **YES**, areostationary equatorial orbit; perturbations/Phobos operations not assessed |
| Moon | ~88,465 km from centre, above lunar Hill ~61,500 km | **NO** stable lunar-synchronous stationary orbit |
| Venus | ~1,537,000 km from centre, outside Venus Hill ~1,010,000 km | **NO** useful stationary satellite orbit |
| Mercury | ~242,900 km from centre, outside Mercury Hill ~220,000 km | **NO** useful stationary satellite orbit |
| Titan | ~75,600 km from centre, outside Titan Hill ~52,000 km | **NO** useful Titan-stationary orbit |
| Small fast rotators | variable | **CONDITIONAL** if `r_stat` lies above terrain and inside a stable orbit region; no blanket generalisation |

These Hill radii and stationary distances are approximate analytical screens, not calibrated ephemeris or trajectory qualification. They do not prohibit ordinary orbit, local spacecraft operation, or the separately accepted small-airless-body Wayfarer near-surface exception. This is an option specific to rotating-body *stationary orbit*, not a universal docking doctrine.

## 5. Recovery, descent and abort

- Under the lock assumption, stop **radial** motion at the rendezvous and verify the **full relative six-degree-of-freedom state** before approaching the Wayfarer bay; a nose hatch and geometric fit do not establish a safe grapple/latch. Field-envelope interference near the 57 m ship is not screened. No cradle is assumed.
- If the lock fails **below GEO**, the craft's instantaneous co-rotating tangential speed `Omega r` is generally *below* local circular-orbit speed; it cannot safely coast in that orbit. Abort/return requires independent propulsion or an actually demonstrated rescue mode. The operation is not fail-safe merely because it stays vertically aligned on a map.
- Descending from GEO reverses the effective potential difference. Depending on the physical exchange, as much as **2.35 TJ of rotating-frame mechanical work** may have to be recovered, returned to a source, or dissipated. The reverse angular momentum exchange also changes Earth's spin-energy ledger. Returning energy is not guaranteed by a reversible trajectory drawing; no free-work cycle.
- **Failure mode** if velocity not matched: cannot dock; remain distant and retry only with a physically capable fallback. No instantaneous mass-domain splice, hull overlap or unexplained motion reset.

## Disposition

**Worth a narrow future screen, not adopted.** This is a more specific candidate than arbitrary Builder velocity matching: it would constrain permissible arrival states to an actual rotating planetary frame and naturally yield a matching Wayfarer at GEO. It is NOT yet cheaper, feasible or demonstrated. The remaining climb work, angular momentum coupling, long-reach access and thermal duty cannot be erased by choosing coordinates.

**No canon change or selected physics permission. STOP after analytic screen.** Claude reviewer can pass/fail the accounting and the separation between coordinate description and physical coupling.
