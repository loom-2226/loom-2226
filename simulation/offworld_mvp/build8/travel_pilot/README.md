# Travel pilot: 2026 authored 2-tonne vehicle envelope

**TEST_ONLY · ENGINEERING_PROVISIONAL · NON-CANON · NOT CONNECTED TO A SIMULATION RUN**

This offline pilot uses existing qualified SPICE body states and Lambert transfers
for Earth–Mercury, Earth–Mars and Mars–Ceres, 2026–2031. The Moon–Mars
example retains the provisional Build 7 3/5-day Moon–Earth local-leg proxy.

## Vehicle assumption, not price calibration

kT selected **candidate B**, a hypothetical **2-tonne orbital reconnaissance
reference ship at the 2026 baseline**. Each *individual trajectory* must
satisfy **departure hyperbolic excess speed ≤10.0 km/s AND arrival hyperbolic
excess speed ≤10.0 km/s**. Those are **authored assumptions**, neither
physically qualified performance nor canon. **Heavier ships, different
payloads and other service types require their own vehicle rows.**

The previous **73.430819 km/s departure** and **56.091356 km/s arrival**
maxima came from the *separate* maxima in 522 priced 2026 Build 7 anchor
rows. They are historical evidence for the abandoned **price-anchor
envelope**, **not current vehicle limits**. The Build 7 reference inputs
and their price rate are unchanged.

The price still uses the authored **2026 median Build 7 price per unit of
transfer burden**, held flat through 2226 by assumption. This proxy
is not an empirical vehicle fare.

## Search and interpretation

For each candidate departure date, the pilot scans all three flight-time
brackets (45–180, 180–520, 520–1400 days) at **2-day flight-duration
spacing**. It first admits trajectories meeting **both** limits, then
minimizes cost *within discovered feasible intervals* and keeps a small
cost/time Pareto set. No infeasibility penalty is mixed into cost.
Departures remain weekly, with the original ±14 **calendar-day**
one-day refinement around feasible local cost minima.

The known **eight Mercury weekly witnesses** from the preceding 10/10
read-only review are explicitly required to survive. The pilot separately
rechecks **three sampled otherwise-closed weeks per route**, across the
full flight-time range, at **0.25-day** spacing, eight times denser than
the regular screen. These are **closures at tested resolution**, not
mathematical proofs that there is no sub-resolution transfer. A failed
audit blocks result generation; it must not be labeled as a closed window.

The arrival leg's orbital capture is still represented only by an
arrival-v-infinity **bound**, not computed propellant. Aerobraking is
not automatically permitted. All previous epistemic fail-closed rules
for Bennu and missing coverage remain unchanged.

The small deterministic `pilot_result.json` contains a derived table
of **feasible and closed weekly departures**, cheapest/costliest
opportunities, eight Mercury witnesses, per-date dense closure audit
records, and the recorded technology/cost provenance. Runtime timing
is reported externally because elapsed CPU time is nondeterministic.

**Neither an admitted Lambert trajectory nor a date with no sampled
trajectory is a qualified mission design or certified flight capability.**
