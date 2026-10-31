# Propulsion cards for the flight lab

ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-GOVERNING lab data. Built by Claude, 31 October 2026, at kT's request. Not canon, not certified.

## What a card is

One small JSON file per propulsion component type, under `cards/<kind>/`. A ship config names a card with `"card": "<id>"` on an RCS thruster, torch or Metric entry. `lab.py` expands the card before the run and records each card's id and hash in the result (`cards`).

- `fields` are merged into the ship entry. These are **only** values `flightlab.py` already reads.
- `declared` is documentation (working fluid, power source, open questions). It never reaches the simulator.
- A field may live on the card **or** the ship entry, never both. A clash is an error, so a card cannot be silently overridden.
- Ship-side limits stay on the ship: tank, position, direction, heat-rejection ceiling (fins are installed hardware), crew g cap, trim. Engine capability goes on the card.
- Add a card type only when a test needs it. No class tree.

## Cards so far

| Card | What | Lab reads |
|---|---|---|
| `rcs-25kN-rev7` | Rev 7 thruster, fuel unknown | thrust, lag, slew, ve = null |
| `rcs-25kN-water-1000` | Water, warm gas, low power | ve 1.0 km/s |
| `rcs-25kN-water-1960` | Water, heated (~200 s) | ve 1.96 km/s; power source OPEN |
| `torch-e1-working-card` | Six torch mode cards + 1 deg TVC | modes, gimbal limit |
| `metric-rev7-envelope` | Metric operating envelope | modes (beta, ramp, cold load); arrival rule HOLD |

## Proof

`configs/wayfarer_cards.json` expands to exactly `configs/wayfarer.json` (same hash, name aside). Runs of reversal40, translate20, burn120 and metric_canonical are bit-identical in result and telemetry (`card_results/`).

## First thing cards showed

| RCS card | 180 deg flip, 40 s | 180 deg flip, 120 s | 0.5 m/s nudge |
|---|---|---|---|
| water 1.0 km/s | 2.76 t | — | 0.60 t |
| water 1.96 km/s | 1.41 t | 0.47 t | 0.31 t |

A slow flip costs about a third of a fast one. Flip time is a real trade against water.

## Run

```bash
python3 lab.py run configs/wayfarer_rcs_water1960.json experiments/reversal40.json --out lab_results
python3 -m unittest test_cards
```
