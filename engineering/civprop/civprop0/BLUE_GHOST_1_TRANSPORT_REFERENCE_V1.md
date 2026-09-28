# Blue Ghost 1: completed lunar transport reference

**Class:** engineering. **Reference:** Firefly Blue Ghost Mission 1, NASA CLPS
TO19D, completed in March 2025. It uses the same customer–commercial-provider
service structure as Roo-ver, with a different provider, lander, payload and
site. This reference does **not** transfer vehicle performance to Roo-ver.

The [pinned calculation](runs/blue_ghost_1_transport_reference_v1.json) keeps
four **observed outcomes** separate from prospective feasibility:

| Segment | Observed evidence |
|---|---|
| Launch | SpaceX Falcon 9 launched on 15 January 2025; Blue Ghost separated into Earth orbit 66 minutes later. |
| Transfer | Firefly reported trans-lunar injection on 8 February and a successful lunar orbit insertion burn beginning 13 February CST (14 February UTC). |
| Lunar delivery | NASA confirmed upright landing near Mons Latreille in Mare Crisium at 03:34 EST on 2 March. |
| Site operations | NASA reported all ten delivered instruments operated; Firefly received final data around 18:15 CDT on 16 March. |

Every segment is `OBSERVED_COMPLETE`; `prospective_feasibility` is
`NOT_ASSESSED`. This is a demonstrated outcome for **this mission**, not a
generic provider capacity or a prior for another CLPS flight.

Minimum defensible calculations from reported clock times:

| Interval | Derived value | Precision |
|---|---:|---|
| Launch → Earth-orbit separation | 1.100 h | Reported minutes |
| Launch → lunar-orbit-insertion burn start | 715.667 h (29.819 d) | Reported minutes; burn start is not an exact orbit-arrival event |
| Burn start → landing | 390.717 h (16.280 d) | Reported minutes |
| Launch → landing | 1,106.383 h (46.099 d) | Reported minutes |
| Landing → last data | about 350.683 h (14.612 d) | Last-data time is approximate |

Firefly separately describes approximately **25 days in Earth orbit, 4 days
in lunar transit and 16 days in lunar orbit**. These are rounded operational
phase descriptions, not equations that must reproduce the timestamp intervals.
Its trans-lunar injection update supplies only a calendar date and no time
zone, so the reference does not invent a TLI clock time or exact TLI→LOI
duration.

A read-only `loom_solar` registry query and the promoted DE440 adapter resolved
Earth and Moon states at the launch, burn-start and landing epochs. The
simultaneous Earth–Moon separations were respectively **386,885 km**,
**397,576 km** and **362,130 km**. They are body geometry context. They are
neither spacecraft positions nor path length, delta-v, transit speed or a
route solution.

**Semantics qualified for CIVPROP:** identify the mission/customer/provider;
keep launch, transfer, delivery and operations as separate evidence claims;
record event epochs with precision and source; calculate elapsed time only
between clock-qualified events; retain explicit observed-versus-prospective
status; and pin the Solar state provenance used for geometry. The public data
used here do not establish spare payload capacity, trajectory state history,
vehicle mass history, propulsion margin or transferable performance for
Roo-ver. No Lambert solver is required to establish these semantics.

Primary evidence: [Firefly mission record](https://fireflyspace.com/missions/blue-ghost-mission-1/),
[Firefly event updates](https://fireflyspace.com/news/blue-ghost-mission-1-live-updates/),
[NASA landing confirmation](https://www.nasa.gov/news-release/touchdown-carrying-nasa-science-fireflys-blue-ghost-lands-on-moon/),
and [NASA mission conclusion](https://www.nasa.gov/news-release/nasa-science-continues-after-fireflys-first-moon-mission-concludes/).
The source assertions and event precision are pinned in
[the one-mission fixture](blue_ghost_1_reference.json).

**Revalidation:** changes to source-reported event times, event interpretation,
live Solar registry or pinned DE440 assets invalidate the corresponding
calculation. Existing Roo-ver and CIVPROP-0 behavior is unchanged.
