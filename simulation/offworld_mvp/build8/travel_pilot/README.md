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

For each of **313 weekly sample dates** per route (2026–2031), one
departure date every 7 calendar days, scan all three flight-time brackets
(45–180, 180–520, 520–1400 days) at **2-day** spacing.
**Every coarse-closed weekly sample date** must be checked again
at **0.25-day flight-time** spacing before calling that sampled date closed.
If the fine scan finds a feasible trajectory, retain its actual
cost/time-Pareto candidates and mark that sampled date open. Both authored
10.0 km/s excess-speed limits must hold on the **same** trajectory.
No infeasibility cost penalties.

This replaces the previous **nine-date sample audit**, which missed
two valid Mercury weekly sample dates. Prior **coarse-only** counts
**8 / 212 / 192 open** (Earth→Mercury / Earth→Mars / Mars→Ceres)
are **superseded**. The corrected counts are **10 / 212 / 192 open** and
**303 / 101 / 121 closed** weekly sample dates, respectively, out of 313
weekly sample dates per route. Across all three routes, **527 coarse-closed
weekly sample dates** receive a 0.25-day flight-time scan and **525 sampled
dates remain closed**. The date-specific evidence and weekly-sample
cheapest/costliest prices appear in the result JSON.

| Route | Cheapest feasible weekly sample date (USD millions) | Costliest feasible weekly sample date (USD millions) |
|---|---|---|
| Earth→Mercury | 2026-05-07: 1294.231012 | 2027-04-15: 1399.340140 |
| Earth→Mars | 2026-10-29: 406.425505 | 2027-11-18: 1222.971297 |
| Mars→Ceres | 2029-06-28: 519.578851 | 2027-09-23: 1334.848459 |

The fixed Mercury witness dates newly recovered are **2026-05-14** and
**2031-05-08**; the eight previously known Mercury weekly sample dates
also remain required. Store the complete fine-checked and confirmed-closed
weekly sample date lists for independent re-verification. The test suite
reruns **every closed weekly sample date** at 0.25-day flight-time resolution.

The 2-day screen, 0.25-day closure check and cost refinement retain
the existing ±14 **calendar-day** daily departure refinement around
feasible local weekly cost minima. A small batched version of the
existing `lamberthub.izzo2015` and direct qualified SPICE span reader
is used for speed; it was validated against scalar Izzo and the
authoritative per-epoch SPICE adapter, including both rescued dates.
It does **not** introduce a new physical model or new source authority.

**A closed weekly sample date means no admissible transfer was found
at that departure date with 0.25-day flight-time sampling. It does not
establish closure of the intervening calendar days or prove continuous
infeasibility or exclusion of alternate transfer families.**

A departure window narrower than the **7-day departure sampling step**
may be missed, especially for Mercury. An **on-demand lookup should scan
daily departure dates inside the requested wait limit**; this pilot's
current scripted lookup only selects from stored sampled options.

## Phone-readable replay summary

From the repository root, in the configured LOOM Python environment:

```bash
python -m simulation.offworld_mvp.build8.travel_pilot.pilot --print-summary
```

Expected concise output:

~~~text
EARTH->MERCURY: 10 open / 303 closed (313 weekly sample dates)
EARTH->MARS: 212 open / 101 closed (313 weekly sample dates)
MARS->CERES: 192 open / 121 closed (313 weekly sample dates)
sha256: 68cebe037945c081843b497b4b085ae38de37af31c09bf6f9fc1f0c57facd574
~~~

This command prints only each route's open/closed weekly sample date counts and
SHA-256 of the committed result JSON. It **reads** that artifact;
it does **not** spend time recomputing 201 years of trajectories.
To regenerate the artifact, use the separate `--output` generation mode.

The arrival leg's orbital capture is still represented only by an
arrival-v-infinity **bound**, not computed propellant. Aerobraking is
not automatically permitted. All previous epistemic fail-closed rules
for Bennu and missing coverage remain unchanged.

The small deterministic `pilot_result.json` contains a derived table
of **feasible and closed weekly sample dates**, cheapest/costliest
opportunities, ten Mercury witnesses, every fine-checked coarse-closed
weekly sample date, rescued dates, the prior nine historical audit samples,
and an explicit weekly-sampling interpretation note,
and the recorded technology/cost provenance. Runtime timing
is reported externally because elapsed CPU time is nondeterministic.

**Neither an admitted Lambert trajectory nor a date with no sampled
trajectory is a qualified mission design or certified flight capability.**
