# Shuttle explorer: corrected baseline, Osteon basis, bay options and families
ALL bodies. ALL sponsors. 2026-2226.

**Status:** research/design exploration in answer to Sol's brief (kT, 2026-11-21). Non-canon. No Wayfarer geometry, mass or canon change. Nothing selected; kT decides.
**Model:** explorer engine `616beacfeb63` (`explorer/engine.py`, `missions.py`). Numbers: `study/study_numbers.json`, `explorer/wildcard_screen.json`, `explorer/bay_screen.json`, `bay/bay_trade.json`, `bay/occupancy.json`, `families/families.json`. Picture: `study/study_comparison.png`.

## 1. Corrections, then a rerun of the whole population (3,200 designs)

- **Touchdown mass is computed per mission:** dry + mission payload + the water still needed after landing, or a 1 t reserve when the mission may refill at sea.
- **Thrust check:** a leg fails when the 7.7 GW torch would need exhaust below its 10 km/s floor to give the demanded acceleration. Hot extraction's 2.5 g climb fails this above ~63 t at the start of the climb.
- **Refill time** is conditional: the fan reactor's full power goes to distillation (2.26 MJ/kg), and the unit is capped at 40 t/h (assumption).
- **Kits are labelled** as carried or not demonstrated: sprint water not demonstrated; Venus kit and rover kit demonstrated for B4-S only.
- **Caveats are carried on every design:** stowed wings, fans and floats; bay opening and G8 exit for B4-S only; float stability; interior as a volume sum; blown-flap lift as an assumed line.

**Effect.** Among 6+ couch designs passing every gate (735), without a wildcard: Earth 466, evacuation **2** (was 5), hot extraction **0** (was 1). The water touchdown with the climb water aboard is the universal blocker for hot extraction (735 of 735). The 8 g turn is next (523), then thrust (197).

**Leading designs, corrected:**

| Design | Before | After |
|---|---|---|
| B5 | Earth ✓, evac ✗, hot ✗ | the same; hot now also fails thrust and water |
| #2643 (6 couches, 13.7 m telescoping wing, 8 m² fans, 30 m³ floats, rover kit) | all five ✓ | evac ✗ by 0.1 m/s, hot ✗ by 2.6 m/s |
| #2845 (former lightest Osteon all-five) | — | conventional: Earth ✗ |

## 2. Osteon component basis

- **Established (Wayfarer mass_basis):** 13 longeron, end-fitting and bay-corner-doubler items, 3.7 t conventional. Osteon (Builder OST-22) versions would save 0.8–1.4 t, i.e. **22–38%**. This is **not assumed** in Wayfarer's own mass.
- **Proposed shuttle application (assumption):** only primary load-bearing structure of that kind is eligible. Shares: hull structure 0.6, wings 0.6, gear/door/ramp 0.5, crash mounts 1.0, plus the cabin pressure wall in the optimistic case only.
- **Not eligible:** entry TPS, floats (fabric), water tank, torch, fans and reactor, avionics, cabin outfit, rover.
- **B5:** **11.55 t eligible** (12.6 t optimistic), not ~21 t. It saves **2.5 / 3.5 / 4.8 t** (cautious 22% / central 30% / optimistic 38%), not 6.4 t. Yesterday's uniform 30% on all airframe items, floats included, was wrong.

| 6+ couch designs passing (of 735) | none | cautious | central | optimistic |
|---|---:|---:|---:|---:|
| Evacuation | 2 | 66 | 100 | 144 |
| Hot extraction | 0 | 6 | 17 | 69 |
| All five | 0 | 6 | 17 | 69 |
| All five, 8 couches | 0 | 0 | 0 | 3 |

Yesterday's figures (170 all-five, 37 with 8 couches) do not survive the corrections.

## 3. Bay options (Wayfarer side)

Wayfarer's geometry record (read-only):
- **Bay bore:** x 18.25–32.05, r 2.4.
- **Remass tank:** a C-slot annulus wrapped round the bay (x 18–31.5, r 2.45–4.28).
- **Ends of the bay:** the relational plant's fore block (r < 2, x 14–17) and aft block (x 32.3–34.3, beside the 55 t torch manifold).
- **Lengthening is limited by the plant and equipment at the ends, not by remass.** Widening is limited by remass and the canonical fuel lobes.

| Option | Physical change | Remass removed | Wayfarer ECON Δv | Structure | Conflicts |
|---|---|---:|---:|---:|---|
| A 12.8 m (today) | — | 0 | 707.8 km/s | — | — |
| **B 14.3 m** | bore x 17.0–32.3; move the x 17–18 band (electrical 23.3 t, house battery, house reactor B, C-lite, ~59 m³) into the fore annulus x 14–17, which the record shows **87 m³ free**; reroute crew tunnel 1 | **0** | unchanged | +0.9 t | G3 trim: ~26 t moved ~1.5 m forward (~3 cm CG); today's worst trim is 0.356° of 0.5° |
| C 16.8 m | bore x 14.5–32.3; relational plant fore block off the axis; ~36 m³ into the remass annulus | ~36 t | −95 km/s (−13.4%) | +3.1 t | plant layout and node topology change → Loom recertification (CANON II §12.1); remass 245.39 t is CANON (CCR-2026-0004); asymmetric plant in a C-annulus |
| D 18 m | bore would cut into the habitat (aft bulkhead, L5) or the torch manifold and plant aft block | — | — | — | **conflicts with Wayfarer invariants: stop** |
| Wider bore r 2.7 m | tank inner wall out 0.3 m over 13.5 m | ~42 t | −110 km/s (−15.5%) | — | canonical D–He3 CSlot fuel lobes share the annulus (CANON II §13.3) |

**What the shuttle gains** (300 lightest 6+ couch designs stretched in the parallel body):
- **Median interior headroom:** 11 → 24 m³ (14.3 m) → 45 m³ (16.8 m).
- **Landing and hot extraction barely improve,** because longer is heavier.
- **Without Osteon,** 16.8 m drops to 103 of 300 feasible. **With Osteon central,** all-five passes go 2 → 7 → 1.
- **So length buys cabin and cargo volume:** 8 couches, a long-haul cabin and cargo racks. It does not buy agility.

## 4. Families

| Family | Verdict |
|---|---|
| Osteon lifting body | **The strongest line:** #2643 + Osteon (below) |
| Larger conventional (longer bay) | 14.3 m (option B) is cheap and gives 8 couches **only with Osteon**; conventional 14.3 m/8 couches fails the Earth water budget |
| Modular expedition (kits) | Built into the leaders already: rover as a kit, sprint water, Venus kit, desalination. Kit masses stay on Wayfarer's payload line; fit and deploy are demonstrated only for B4-S's rover and Venus kit |
| Dedicated atmospheric lander | #2430 compact sea courier: no wings, fans + sea refill, 52.8 t on Wayfarer, Earth ✓, but evac and hot ✗ (60.7 m/s touchdown, 7.8 °/s) |
| Vacuum-only utility | B5 core without wings, fans, floats or entry TPS: **32.7 t dry**, Δv **25 km/s** on 23 t; Moon round trip 4.2 t water, Europa-class 3.6 t. A mission swap for airless campaigns, not a second vehicle (one bay) |
| Builder-enabled adaptive structure | Only as a **sensitivity**: the high-lift / morphing case (CL cap 6) is human 2226 tech in the model, not a Builder effect. No canon basis for a Builder morphing structure. Osteon is the only Builder item with repo evidence |
| Metric-assisted landing / manoeuvring ("tic-tac") | **Blocked by canon.** One NORMAL ramp is ~0.40 million km of metric path (§9.1); "metric is not a close-combat dodge" (§18A); wake used as commandable reactionless thrust and FTL metric are hard kills (§21, §5); the plant is ~88 t (§3). Closest legal: Osteon-light airframe, full-power torch with a steerable magnetic nozzle (up to ~2.5 g), quiet electric fans. Agile, never invisible (sensor primacy, §18A) |
| Independent interplanetary courier | B5 with the 23.1 t tank: Δv **10 / 20 / 41 km/s** at 25 / 50 / 100 km/s top exhaust. Months-long transfers fit; Wayfarer-class transits (hundreds of km/s) do not. The 3-day hop cabin, consumables and radiation limit it, not propulsion |
| **Independent FTL courier / daughtercraft** | see §5 |

## 5. FTL courier: plausible?

**Not as a shuttle. Decisive blocker:** the only relational plant in canon is the unified metric/Loom plant: **~88 t, 10 kg Mc-299m, 208 nodes, 2 GJ bank, 150 kW-class 20 K cryoplant** (CANON II §3). Canon gives no smaller design and calls the legacy smaller sizings non-governing (§1). A shuttle-size Loom drive would be invented physics/engineering.

**As a daughtercraft:** it would be a second Loom-capable ship. Loom-capable ships number a few dozen worldwide (CANON I §2.2, §5.4), and Wayfarer is already "unusually small" for one.
- **Mass (estimate):** plant 88 t + torch 7 t + 60–110 t structure, habitat and thermal ≈ **155–205 t dry**. With ~20 km/s of momentum-matching water at 50 km/s (Loom momentum matching is "ordinary torch / external exchange", §12): **~230–310 t wet**.
- **Mc:** 10 kg, ~0.8% of a year's world serviceable flow in a supply-short market (§3.1).
- **Carried by Wayfarer:** it cannot fit any bay option. Carried externally, Wayfarer's ECON Δv falls **708 → 546–579 km/s (−18 to −23%)**. It joins Wayfarer's Loom domain (configuration lock, §12.1), and metric/Loom thermal and boundary solutions change.
- **Verdict:** plausible as a **separate second ship acquired in play** (strategic: packet carriage, independent extraction, reconnaissance, diplomacy), not as Wayfarer equipment.

## 6. Answers

1. **Strongest corrected conventional shuttle:** **#2643**. 6 couches, 38.3 t dry, **56.3 t on Wayfarer (−10.2 t vs B5)**. Earth, orbital and surface ✓; evacuation misses by 0.1 m/s; hot extraction ✗ (touchdown +2.6 m/s). B5 itself: Earth, orbital, surface only.
2. **Strongest Osteon candidate:** **#2643 + Osteon**. Passes **all five in the cautious, central and optimistic cases**: 53.9 / 53.1 / 51.8 t on Wayfarer, hot-extraction touchdown headroom 0.5 / 1.4 / 2.6 m/s, evacuation 2.6 / 3.5 / 4.6 m/s. Thin but holds across the whole Osteon range.
3. **Most valuable larger-bay option:** **B, 14.3 m**. No remass lost; move the x 17–18 equipment band into free fore-annulus space, +0.9 t structure, re-check trim. With Osteon central, **#2643 at 14.3 m carries 8 couches and passes all five** (56.1 t on Wayfarer; hot passes by only 0.2 m/s at central and fails by 1.0 m/s at cautious). 16.8 m costs ~36 t of canon remass and a relational-plant move; 18 m conflicts.
4. **Most interesting modular / specialist:** the **vacuum utility configuration** (32.7 t, 25 km/s), a kit swap for airless campaigns, not a second vehicle. Runner-up: the **compact sea courier** for routine Earth runs.
5. **FTL courier:** not plausible as a shuttle (no relational plant below ~88 t / 10 kg Mc in canon). Plausible only as a separate ~0.2–0.3 kt Loom ship.

**Next physical design experiment (for kT to choose):** stowage and exit check of **#2643 (13.7 m telescoping wing, 8 m² fans, 30 m³ floats) at 12.8 m and at 14.3 m**. It hinges on margins under 3 m/s and on parts never placed in the bay. Run Osteon at the cautious case.

**Not checked anywhere yet:** stowed wings/fans/floats, bay opening and exit clearance except B4-S, float stability, a real interior layout, the blown-flap lift line, Wayfarer trim for option B.
