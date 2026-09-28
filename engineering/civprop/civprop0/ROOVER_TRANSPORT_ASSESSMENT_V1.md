# Roo-ver transport assessment v1

**Class:** engineering. **As of:** 29 September 2026. **Overall:** `UNKNOWN` for
the named Roo-ver / NASA CLPS CT-4 / Intuitive Machines IM-5 mission. This is a
bounded service and state screen, not a trajectory or flight-success claim.
No canon closure, transport physics, Earth/Solar authority, or CIVPROP-0 behavior
changes. The disposable [run artifact](runs/roover_transport_mid2030_v1.json)
records the exact request, four segment results, live Solar state provenance,
registry hash and manifest hash.

| Segment | Result | Evidence and remaining limit |
|---|---|---|
| Launch | `UNKNOWN` | An initial **mid-2030** IM-5 launch target is reported, but no booked day/window, launch vehicle or accepted mass allocation is in the admitted envelope. |
| Earth–Moon transfer | `UNKNOWN` | Qualified Earth/Moon states exist for the sample epoch. No departure/arrival pair, transfer design, duration, delta-v or propulsion margin is established. |
| Lunar delivery | `FEASIBLE` **for the named planned service scope only** | NASA awarded Intuitive Machines end-to-end delivery of the manifested Roo-ver/MNP to the lunar South Pole region. This establishes a service path; it does not certify a final flight mass, exact site or landing outcome. |
| Site and operations | `UNKNOWN` | The provider targets Mons Malapert, and ELO2 is to operate Roo-ver. Final coordinates, terrain, deployment, power/data terms and a 14-day performance guarantee are unqualified. |

The [Australian Space Agency](https://www.space.gov.au/meet-roo-ver) describes
Roo-ver as around **20 kg** and expected to operate for **up to 14 Earth days**.
[NASA's award](https://www.nasa.gov/missions/artemis/clps/nasa-selects-intuitive-machines-to-deliver-artemis-science-tech-to-moon/)
lists the full rover/instrument suite at about **75 kg**. Neither figure is a
provider capacity or spare-mass limit. A requirement beyond the Agency's
14-day plan is `INFEASIBLE` **within that documented plan**, not physically
impossible. A destination outside the contracted South Pole region is likewise
`INFEASIBLE` for this named service path. Different mass or exact-site requests
remain `UNKNOWN` until separately qualified.

The initial mid-2030 target comes from [Intuitive Machines' filing](https://www.sec.gov/Archives/edgar/data/1844452/000162828026035236/lunr-20260331.htm).
**1 July 2030 00:00 UTC is only a reproducible reference sample inside that
reported target period.** It is not a scheduled departure or arrival. A
read-only `loom_solar` registry query and its qualified DE440 adapter resolved
fresh Earth and Moon states at that epoch in `J2000/ECLIPTIC`, `km,km/s`.
Their separation is **401,540.021 km** and relative speed **0.983673 km/s**.
Those quantities describe contemporaneous geometry, not route distance,
transfer delta-v or flight time.

`python -m engineering.civprop.civprop0.roover_transport` regenerates the
assessment from live read-only Solar authority. Tests exercise the four segment
statuses, scope failure, 14-day plan limit, unknown mass/site requirements,
state-provenance rejection and deterministic assessment. The existing actor
access and CIVPROP-0 regression tests also pass.

**Revalidation:** change to the CLPS manifest, target period/site, Roo-ver
mass or operations plan, live Solar registry, or pinned DE440 asset invalidates
the corresponding service or geometry result. No route planner or Lambert
solver is justified yet: the immediate gaps are a booked mission window,
accepted payload/lander envelope, final site and provider trajectory or
performance data.
