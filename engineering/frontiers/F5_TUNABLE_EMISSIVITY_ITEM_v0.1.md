# F5-TE-01: tunable-emissivity hull skin (PROPOSED Frontier item) v0.1

ALL bodies. ALL sponsors. 2026-2226.

**Status:** PROPOSED for the F5 family of `WAYFARER_2226_ENGINEERING_FRONTIER_REGISTER_v0.1.md`. Not entered in the register and not frozen. NON-GOVERNING; `class:engineering`. No canon promotion.

**Origin:** kT decision 2026-10-26 (open an F5 item for tunable emissivity); Sol AGREE with qualification 2 the same day. First consumer: Wayfarer v0.5.7 rev 7 (`design/wayfarer/v0.5.7/inputs/wayfarer_v05_inputs.json`, `skin.flanks`, `cold_running`).

## What it projects

One ordinary-engineering capability: a hull surface whose infrared emissivity can be switched between a high state (shedding heat) and a low state (holding heat in, lower thermal signature).

| Parameter | Scenario value | Basis |
|---|---|---|
| High-state emissivity | 0.85 | the existing Wayfarer habitat skin-radiator value; ordinary white thermal-control coatings reach this today |
| High-state solar absorptivity | 0.15 | same; a light surface |
| Low-state emissivity | 0.10 | low-e metal surfaces reach this today, but not on a switchable surface at hull scale |
| Switching | between the two states in flight, many cycles | small-scale variable-emittance devices exist in 2026; hull-scale, long-life, wide-range switching is the 2226 projection |

These are bounded scenario values, not hindcast forecasts. The emissivity range itself is the projection: 2026 switchable devices cover a narrower range at small scale.

## Rules for every consumer

1. **Stefan-Boltzmann is the accountant.** Radiated power is emissivity x sigma x T^4 x area. Emissivity stays between 0 and 1.
2. **No radiative multiplier and no unexplained heat sink.** Low emissivity reduces radiation at a given temperature. It does not remove heat, store it without consequence, or guarantee a low observable signature.
3. **Cold running is finite.** Retained heat must go into a stated thermal buffer with a stated heat capacity and allowed temperature rise, and the consumer must state when the buffer is full.
4. **Optical appearance is separate.** A metallic or mirror look in the low state is a proposed optical property, not a consequence of low infrared emissivity, and it must be declared as such.

## First consumer result (Wayfarer rev 7, certify.py G4 declared item `cold_running`)

Habitat heat 58.1 kW (46.5 kW x 1.25 margin) less 7.1 kW still leaking through 177 m2 of low-state skin at 290 K warms the 50 t of protected water by 15 K in about 17 h. Relational-plant and cryoplant standby heat in a coast is not modelled (OPEN) and would shorten this.

## Open before entry in the register

- Device class and its 2026 anchor (evidence card).
- Switching time, cycle life and degradation under dust and radiation.
- Mass per m2 over the substrate.
- Whether the low state can coexist with the hull's erosion and node-face requirements.
