# Builder prototype lane: programmable structure, metric cushion, metric impulse
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON research lane authorised by kT (2026-11-21). It may supersede canon *technology* limits, but not deeper physics. No canon change, no Wayfarer change, no winner. Conventional and Osteon results (`../study/`) stand as the verified-by-model baseline. Numbers here are the values each hypothesis would **require**, not results.

**Files:** `w1_programmable.py/.json`, `w1_sweep.py/.json`, `metric_wildcards.py/.json`, `ledger_figure.py` → `prototype_ledger.png`, `concept_render.py` → `hero_concepts.png`. Engine `explorer/engine.py`: wildcard `programmable`; combined wildcards are written `a+b`.

## Deeper physics kept (from canon) vs technology that may be challenged

- **Kept:**
  - local conservation ∇·T = 0 and ledger closure (CANON II §7.3);
  - no free work or free momentum cycles, no commandable reactionless wake (§21);
  - no FTL metric and no chronology exploit (§5, §21);
  - domain/identity continuity: no partial-hull domains (§2);
  - the two-miracle budget (M1/M2, no third miracle, §2).
- **Challengeable technology:**
  - plant scale (~88 t, §3; the L² size law is only a "candidate fit, not canon", §6.2);
  - certified ramp ≥ 10 s and ~0.4 Mkm path (§5, §9);
  - near-body environmental certification (§6);
  - the scoped ENERGY-B arrival rule (§7.1a), under which metric transit is energy-neutral for the ship;
  - torch/metric exclusivity (§14);
  - doctrine that metric is not a close-combat dodge (§18A);
  - the material baseline.

## W1: programmable structure (shape and stiffness switching)
- **New physical effect needed:** none. Builder-derived structure that switches shape and stiffness. Osteon is the only Builder material with repo evidence; this lane extrapolates from it.
- **Modelled:**
  - wing folds flat to the hull for stowage and morphs span (up to 20 m) and camber in flight;
  - wing mass taken as 1.5× a conventional wing (sensitivity);
  - morphing camber credited with a lift-coefficient cap of 5 (sensitivity).
- **Alone (#2643, 17 m span, 23.1 t tank):** passes **evacuation**; hot touchdown 47.5 m/s. Hot extraction still fails because the torch can't give the 2.5 g escape climb at ~64 t (thrust-short). B5 + programmable at 14 m also passes evacuation (49.2 m/s).
- **Its real value:**
  - it makes the unverified wing stowage problem tractable (folds flat);
  - glide L/D 7.0–7.5;
  - water landings 4–6 m/s slower;
  - landing protection (crush and planing stiffness) is plausible but not modelled.
- **Decisive unknowns:** stiffness while morphing, actuation mass, stowed shape, heating of morphing skins during re-entry.

## W2: local metric "cushion" (lift-off and landing to ~2 km)
- **New physical effect needed: a *powered* metric channel.** Onboard energy goes into the ship's ordinary state, with the Sun as the declared momentum partner (§7.1b). Under canon's ENERGY-B rule, a metric hop conserves the ship's mechanical energy, so **it cannot lift you for free: height must be paid**. Whether a powered channel is part of M2 or a third miracle is the deepest open question in this lane.
- **Energy:** lift ~55–65 t to 2 km at ~240 m/s takes ~3 GJ at 60% efficiency, ~150 MW for ~20 s. That is ~1 t of flywheel (1 kWh/kg, 150 kW/kg, kT ship-power record). Landing gives back ~1.2 GJ, about a 12 K rise if dumped into the water tank.
- **The first 10 km does not pay.** It needs ~16–37 GJ and ~4–10 t of storage; module mass then costs more ascent water than the 0.98 km/s it saves. The cushion to 2 km is the useful version.
- **Module mass by scaling law:**

  | Scaling of Wayfarer's plant (~284 m² envelope) | Module | Mc | Nodes | Cryo, NORMAL | Radiator at 900 K |
  |---|---:|---:|---:|---:|---:|
  | L² | ~13 t (+1 t mounts) | ~1.5 kg | ~31 | ~0.5 MW | ~16 m² |
  | L¹ | ~34 t | | | | |
  | Unscaled | 88 t | | | | |

- **Decisive number:** the hot-extraction water budget closes only if the module is **≤ ~12 t** (6 couches, Osteon cautious) or **≤ ~8 t** (#2643 without Osteon; or 8 couches on 14.3 m). The L² candidate estimate (~14 t) is just over.
- **What it buys:**
  - no torch exhaust over people;
  - near-zero touchdown speed, so the landing-speed limit disappears;
  - the 2.5 g torch escape climb is no longer needed: the torch lights at 2 km at T/W 1.4.
- **Matter interaction:** the wall must stay clear of the hull, the water and people (domain continuity). That means hovering ≥ ~6–8 m up and keeping the envelope clear. Correction power near the ground (§6.3) is unknown and could dominate.
- **Occupants:** a metric interior rides inertially. Canon's 10 s ramps to 0.27c imply that, or crew would see enormous loads. So the cabin is weightless while the ship rises, and the hand-over to the torch is the load event.
- **Failure:** losing the field at a few hundred metres means falling. Recovery is fans plus wing, or an emergency torch start. Asymmetric collapse that cuts the hull is catastrophic and must be designed out.

## W3: metric impulse ("tic-tac" lateral and vertical moves)
- **New effect needed:** km-scale hops with ~0.1 s ramps near a body. The adiabatic margin stays huge: ramp ÷ wall light-crossing ≈ 10⁷, against canon's own screen of ~5×10⁸. So the semiclassical stress-energy (RSET) adiabatic screen is not the blocker.
- **Energy under ENERGY-B:**
  - **Level hops cost ~0 J** in ordinary energy, plus formation and correction losses, which are unknown.
  - Down-hops arrive faster by √(2gΔh) and must be braked.
  - **Up-hops are forbidden** unless the ship already has the speed (1 km needs 140 m/s). With W2's powered channel, a 1 km up-hop costs 0.44 GJ.
  - A level hop has **zero net ordinary momentum change**, so the occupant load is ~0. That matches reported "no g, no exhaust" behaviour.
- **What deep physics refuses: silence.** A 45 t shuttle hopping 1 km in 0.5–1 s at sea level drives ~0.2–0.9 GJ into the air (Mach 3–6 shock, or a thunderclap as the vacated volume collapses). A silent hypersonic dash at low altitude would break ∇·T = 0 with the air. At 10 km altitude the figure drops by about a third.
- **Superseded technology:** the ramp and path card, near-body certification, plant scale, doctrine §18A.
- **Hardware:** shares W2's module but needs much faster node control.
- **Failure:** a collapse mid-hop leaves you at the departure velocity (benign). Asymmetric collapse, or matter entering the wall (aircraft, missiles, birds, terrain), is the hazard.

## Combinations (after the separate runs)
Rough model, #2643, 6 couches unless noted:

| Configuration | Result |
|---|---|
| Osteon cautious alone | all five ✓ (hot touchdown headroom 0.5 m/s) |
| W1 + Osteon cautious (17 m) | all five ✓, hot touchdown **44.3 m/s** (5.7 m/s headroom), dry 38.4 t |
| W1 + Osteon + 14.3 m, 8 couches | hot ✗: torch thrust-short at ~64 t |
| W2 (8 t module) alone | all five ✓ (hypothesis), dry 47.9 t |
| W2 (8 t) + W1 + Osteon | all five ✓ (hypothesis), dry 48.0 t; with 8 couches on 14.3 m, the water budget fails by 1.5 t |

## Strongest prototype hypotheses (kT decides)
1. **"Osteon + programmable flying boat":** W1 + Osteon at 12.8 m. The only hero configuration that needs no new physics. All five missions with real landing margin, and the stowage problem becomes a material property rather than a mechanism.
2. **"Field-cushioned extraction shuttle":** W2 on top of hypothesis 1. Vertical, exhaust-free extraction from water or a crowd, weightless cabin on lift-off. It stands or falls on two unknowns: a **powered metric channel within M2** and a **shuttle relational module of ≤ ~8–12 t**.
3. **"Metric skip" (W3) as an evasive escape, not a dogfight move:** energetically almost free when level, but **loud**. A low-altitude hop is a thunderclap. The visible, audible signature is the price; the tic-tac "silence" is the one part physics refuses.

## Decisive unknowns
- Plant scaling law (L² candidate vs worse).
- Whether a powered metric channel is inside M2.
- Near-matter correction power (§6.3).
- Wall–air and wall–water interaction.
- Morphing-structure mass and stiffness.
- Stowage of any wing in the bay.

## Correction (2026-11-21, during the Weave review)
**What changed:** the W3 statement "up-hops are forbidden unless the ship already has the speed (1 km needs 140 m/s)" used the *local* frame. That is wrong.

**Why:** CANON II §7.1a ENERGY-B counts kinetic energy in the **Sun-barycentric** frame, where a shuttle sitting on Earth already moves at about 29.8 km/s.

**What an up-hop costs instead:** v_a = √(v_s² − 2gΔh) ≈ v_s − gΔh/v_s.
- That is about **0.33 m/s of heliocentric speed per km of height**, so up-hops are not forbidden.
- The energy (about 0.6 GJ per km for 61 t) is drawn from heliocentric kinetic energy.

**Consequence (unresolved):**
- Hop up by metric, fall back conventionally while harvesting the fall energy, then trim the small relative velocity: in the Earth frame that cycle nets about 0.6 GJ per km.
- The Earth-frame source is the Sun-partner exchange, Δp·v_rel ≈ 61 t × 0.33 m/s × 29.8 km/s.
- Near-body metric with the canon Sun partner is therefore an energy pump against the §7.3 no-free-work firewall.
- This is related to canon's own MONITOR cycle residual (§7.1b). Flagged; not resolved here.

## Status (2026-11-22): Weave prototype in use

Option 3 (Weave manoeuvring) is the working prototype. The research arc runs from d056040 to cab469f in `weave/`:

- coupled conservative toy;
- finite domain;
- lapse vs zero-expansion shift;
- exact ideal-fluid transport;
- gust check (atmospheric branch closed at 4b62812);
- GR source ledger (closed at cab469f).

The zero-expansion shift is the leading geometry. Its underlying exchange physics is UNKNOWN and recorded as a research mystery, not a blocker (see `weave/WEAVE_SOURCE_CLOSURE_2026_11_22.md` §6). Still non-canon.
