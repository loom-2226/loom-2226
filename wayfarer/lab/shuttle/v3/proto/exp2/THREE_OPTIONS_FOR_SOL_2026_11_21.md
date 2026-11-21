# Three extraordinary-capability options, for Sol's review
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON options held by kT (2026-11-21). No winner, no canon change, no hardware.

**Sol's question:** which option sits cleanest against LOOM's existing miracles (M1 relational geometry; M2 matter/Mc coupling, metric), and which gives the best gameplay mechanics and story hooks?

## Option 1: Gravity steering (powered local-partner metric)
**Law:**
- The field can give its free-falling interior an acceleration up to 1.5 × g_P.
- g_P is the pull of the dominant local body.
- The reaction goes to that body.
- The onboard device pays F·v_rel.

**Status:** a postulate, not a derivation. In general relativity the numbers do not close: ~1e13–1e14 kg of exotic mass, and a momentum partner is still needed. It relies on M2's existing stress-energy waiver.

**Canon departures:**
- §7.1a ENERGY-B (powered).
- §7.1b Sun partner (local partner instead).
- §18A.
- Near-body certification.

**Trajectory test:** 61 t shuttle to LEO with zero propellant in 19.4 h on 29 MWe; 768 m/s per day at 1 AU for any ship; near-free plane changes. That makes it a setting-scale technology.

**Sources:** `EXPERIMENT_2_2026_11_21.md` (BMD-1 sections); `bmd1_*.py/.json`; `gs_trajectory.*` (78890fd); economics in `GRAVITY_STEERING_SCARCITY_ECONOMY_2026_11_21.md` (86fa8ec).

## Option 2: Short Loom jumps (Loom resolution / fine structure)
**Idea:** the Loom has a relational resolution limit.
- A place is defined by its relationships. Points that are close together have nearly identical relational signatures, so today's lattices cannot distinguish "here" from "there".
  - Selectivity separation is 40 on the CANON II §12 card.
  - A short jump would therefore revert to its origin (CANON I §6.12).
- This is consistent with canon: there is no Loom use inside Sol, and the hidden graph's nodes are star systems.
- The ladder of difficulty: interstellar (canon) → body-to-body → kilometre hops near a surface. Long jumps are easy, short jumps hard: the Loom is "far-sighted".
- The breakthrough would be finer lattice selectivity, possibly through Builder insight.

**Existing canon rules that apply:**
- No net energy from any jump sequence (§6.8), so climbing a gravity well must be paid for. Jumps between points of equal potential are cheap.
- Formation takes minutes or more and is visible; commit 0.25 s; transition sub-second (§6.7).
- Reversion and displacement risks (§6.12).
- Configuration lock (CANON II §12.1).
- Emergence into "macroscopically occupied" volumes is forbidden (§6.11). Whether sea-level air counts is open.
- Scarcity is built in: only dozens of Loom-capable ships exist (§5.4), and Mc is limited (CANON II §3.1).

**Most grounded use:** Wayfarer jumps between bodies in vacuum with its existing lattice; the shuttle does the conventional descent and climb. Shuttle-sized lattices (~13 t at the L² candidate scaling) are the least plausible version.

**Decisive unknown:** does the relational substrate distinguish places inside a star system at all, and at what scale? This connects to the Relational Topography (RT) research.

## Option 3: Weave manoeuvring (agile metric, the "tic-tac")
**Source:** `engineering/current/LOOM_2226_METRIC_LOOM_WEAVE_FICTIONAL_ENGINEERING_FOUNDATIONS_v0.1.md` on main (non-canon engineering baseline).
- §7: metric is continuous Weave deformation with the relational attachment fixed.
- §8: no remass.
- §17: Weave Control Synthesis (WCS) inverse control.
- §19: seams, where attachments are near-degenerate.

**Mechanism:**
- Canon metric already moves the ship without changing its local kinetic state or loading the crew (CANON I §5.3).
- That gives hover, zip and dead stop: no g, no exhaust.
- Tic-tac is the same physics with sub-second ramps, small amplitude and near-body operation.
- The barriers are certification and doctrine, not physics: CANON II §6 near-body certification, §9 ramps (10 s), §18A, §14 torch/metric exclusivity.

**Energy:** ENERGY-B counts kinetic energy in the Sun-barycentric frame, so a 1 km metric climb near Earth costs only about 0.33 m/s of heliocentric speed (correction recorded at b44a114).

**Catch:**
- Hopping up by metric and falling back while harvesting nets about 0.6 GJ per km cycle (61 t). The energy comes from the Sun-partner exchange.
- That is an energy pump against the §7.3 firewall, related to canon's MONITOR cycle residual (§7.1b).
- Air interaction at the bubble boundary is open: see the W3 boundary hypotheses in `EXPERIMENT_2_2026_11_21.md`.

**Decisive unknowns:**
- What closes the near-body energy loop.
- The ramp-time floor.
- Boundary versus air.

## Option 3 addendum (kT, 2026-11-21): Weave fuel/limits and expendable heat sinks
**What powers it and what limits it:**
- **Fuel:** reactor electricity into a field bank. No remass.
- **Limits:**
  - Cold-side heat (the 20 K node cryo load) — the hardest limit.
  - Mc-299m tile wear.
  - The **shared Metric/Loom plant**: aggressive Weave use spends the Loom lattice.
  - Bank cadence.
  - Weave Control Synthesis (WCS) feasibility near matter.
  - Air at the boundary.
- **kT:** the §18A doctrine is waived for this lane.

**kT proposal: a limited number of sheddable heat sinks give a "dodge" ability; otherwise recovery needs time.**

**Canon anchor:** the CANON II §18A thermal combat clock ("throttles, cools, dumps heat or disengages") already allows dumping heat.

**Two ways to build the sinks:**
- **Cold-side "frost charges" (primary).**
  - Liquid H2 boils at 20 K, the node temperature, absorbing 446 kJ/kg of latent heat with no cryocooler. The boil-off is vented.
  - Dodges per kg = 0.446 / Q_dash (Q_dash = cold-side heat per dash in MJ, UNKNOWN). For example, at Q_dash = 1 MJ, a 100 kg charge (1.4 m³) gives ~45 dodges; at 10 MJ, ~4.
  - Refill comes from Wayfarer's water by electrolysis and liquefaction (~tens of MJ/kg; Wayfarer-side work, not shuttle).
- **Hot-side bricks (optional decoys).**
  - Phase-change bricks (e.g. LiH, ~2.6 MJ/kg fusion near 960 K) take the cryocooler's reject heat and are then ejected glowing, doubling as IR decoys.
  - They do not relieve the 20 K bottleneck.

**Without sinks:** recovery time is set by the cryocooler's lift rate at 20 K and the radiator area. That is the "needs time" clock (not modelled).

**What sinks do not fix:** Mc tile wear and the shared Loom lattice. Dodging still spends the way home.
