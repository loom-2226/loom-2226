# Weave manoeuvring: the "tic-tac" mode of the metric drive
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON prototype lane. kT chose option 3 (2026-11-21).
- kT waives the §18A doctrine and near-body certification for this lane.
- kT authorises the lane to challenge CANON II §7.1a and §7.1b.
- Nothing here changes canon, hardware or mass bookings. kT decides.

**Builds on:**
- `engineering/current/LOOM_2226_METRIC_LOOM_WEAVE_FICTIONAL_ENGINEERING_FOUNDATIONS_v0.1.md` (BASELINE), §§7, 8, 17, 19.
- Sol's review `../exp2/SOL_THREE_OPTIONS_REVIEW_2026_11_21.md` (595baf4).
- The options brief `../exp2/THREE_OPTIONS_FOR_SOL_2026_11_21.md`.

**Files:**
- `weave_cycle.py/.json`: the decisive test.
- `weave_ops.py/.json`: the operations model.
- `weave_figures.py` → `weave_card.png`, `weave_sortie.png`.

## Mechanism (canon-anchored)
- **Metric moves the ship without changing its local kinetic state or loading the crew** (CANON I §5.3).
- **Weave §7:** metric is continuous Weave deformation with the relational attachment fixed. **§8:** no remass.
- **The tic-tac is the same physics in a new regime:** sub-second, short, near a body.
  - It hovers, dashes and dead-stops; the stop is free because the ship never gained kinetic speed.
  - No g-load, no exhaust.

## Lane rules
| Rule | Content | Canon status |
|---|---|---|
| **W1** | Inside a body's sphere of influence, the Weave's momentum partner is that body. | Departs §7.1b, which names the Sun. Lane-authorised. |
| **W2** | ENERGY-B is counted in the partner's frame. Height gain is paid from the field bank or the reactor (powered channel). | Departs §7.1a. Lane-authorised. |
| **W3** | Arrival kinetic state equals departure state, carried by local frames. **No free velocity steering.** | Canon §7.1a kept. |
| **W4** | §18A doctrine and §6 near-body certification waived. | kT decision, lane only. |

W3 matters: **the Weave changes position, and the torch owns velocity.** Free velocity turns would be gravity assists anywhere inside a planet's sphere of influence (`weave_cycle.json`), which is setting-scale. W3 is what keeps the torch economy intact.

## Decisive test: closed 1 km up/down cycle, 61 t (Sol's smallest test)
| Rule | Net extractable work per cycle | Verdict |
|---|---|---|
| S, canon as written (Sun partner, Sun-frame ENERGY-B) | **+598 MJ** | **Pump.** The source is the Sun exchange (Δp × 29.8 km/s), a §7.3 hard kill. |
| W1/W2, local partner | **0** (losses only) | **Closed** |

Under W1/W2, any closed loop of dashes, climbs and descents nets only losses, because gravity is conservative in the partner frame. **Near-body Weave is admissible only with W1.**

## What fuels it, what limits it
**Fuel:** reactor electricity into the field bank. No remass.

**Shuttle module** (L² CANDIDATE scaling, not canon):

| Item | Value |
|---|---|
| Mass | 13.2 t (13.8 t with frost charges and heat exchanger) |
| Mc | 1.5 kg |
| Nodes | 31 |
| Field bank | 0.3 GJ |
| Cryo lift at 20 K | 22 kW (3.9 MW electrical; CANON II §5 cryo electrical/cold ratio 175 W/W) |

**Cold budget**
- **Heat per dash (ASSUMPTION):** 0.25–4 MJ at 20 K, central 1 MJ. Anchored to canon ramp cold energies: 0.2 MJ NORMAL to 4.1 MJ HARD for Wayfarer.
- **Buffer before HOLD:** about 1.5 MJ (ASSUMPTION).

| Cold per dash | Dashes from buffer + 12 frost charges | Cooldown per dash, air | Cooldown per dash, vacuum |
|---|---|---|---|
| 0.25 MJ | 70 | 11 s | 82 s |
| **1 MJ (central)** | **18** | **45 s** | **5.5 min** |
| 4 MJ | 4 | 3 min | 22 min |

- **Frost charge:** 3 kg of liquid H2 (+3 kg dry), absorbing 1.34 MJ by boiling at ~20 K. Vented or ejected; optional glowing decoy bricks. Refilled on Wayfarer.
- **Hot side:** in air, an air heat exchanger lets the cryo run at its full rate. In vacuum the radiator limits it (~3 kW lift), so frost charges matter most in vacuum.

**Paid height (W2):**

| Body | Height on the field bank alone | Reactor-sustained climb |
|---|---|---|
| Earth | ~500 m | ~43 m/s |
| Mars | 1.3 km | — |
| Moon | 3.0 km | — |
| Titan | 3.6 km | — |

On the way down, descents return energy into the bank.

**Wear:**
- Mc tile wear per dash is **UNKNOWN**. Track it as campaign wear points.
- **Wayfarer's tiles are shared with its Loom drive** (CANON II §3), so hard Weave use spends the way home.

**Still open:**
- WCS can return "infeasible" near terrain (Weave §17).
- Boundary/air behaviour is **UNKNOWN**: the H1/H2/H3 hypotheses in `../exp2/EXPERIMENT_2_2026_11_21.md`.

## Manoeuvre card (central case)
| Move | Energy | Cost / limit |
|---|---|---|
| Dash (level) | free | ~1 MJ cold; wear |
| Stop (end of dash) | free | — |
| Hover | holding only | hold cold load (open) |
| Climb | pay m·g·h | bank ~500 m (Earth), then reactor |
| Descend | returns m·g·h | bank headroom |
| Change velocity | **not Weave** | torch or fans |
| Dodge | a dash | sheds a frost charge |
| Cooldown | — | air ~45 s; vacuum ~5.5 min per dash |

## Mission closure: the catch
- **Vehicle:** the leading adaptive shuttle (fold 17 m + adaptive camber + Osteon cautious, 37.3 t dry).
- **Hot extraction closes** with a Weave lift to 2 km only if the **module weighs ≤ ~9.5 t**. A lift to 200 m allows ≤ ~5 t. Lifting higher than 2 km does not help.
- **The L² candidate module (13.8 t) fails:** 27.5 t of water needed against 23 t carried.
- **Possible routes:**
  - a module ~30% lighter than L² (canon's small-ship advantage, CANON I §6.6, is not quantified);
  - the Weave as a mission kit;
  - a lower Wayfarer rendezvous.

  Not decided.

## Example sortie (`weave_sortie.png`, central case, sea level)
1. Silent Weave descent from 500 m, recharging the bank.
2. Pickup with no plume while the cryo cools.
3. Threat: 3 dodges. The second one sheds one frost charge.
4. Silent Weave climb on bank, then reactor.
5. Torch lights at 2 km.

## Decisive unknowns (ranked)
1. **The boundary/air law:** silent, a bang, or impossible in air.
2. **Cold heat per dash:** this sets the dodge count and the cooldown.
3. **Module mass:** must reach ≤ 9.5 t for hot extraction.
4. **Mc wear per dash.**
5. **Hold cold load near a body.**
