# Wayfarer v0.5.2: torch heat package

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING.** v0.5.1 (sha `88a3112e...`) plus kT's decisions of 2026-10-25 on torch heat. No canon promotion, no runtime integration. v0.5 in PR #430 stays as archived.

## Why

v0.5.1 declared that at most 387 MW (34 ppm of the 11.36 TW jet) of torch heat reaches the ship, with no mechanism. A heat budget (`torch/torch_heat_budget.py`, non-governing) shows an open burn would put about 9,500 GW on the ship. kT asked what could be done without losing performance, and chose a package:

1. **Heat leaves with the exhaust.** Each pellet is wrapped in a shell of remass that soaks up the burn and leaves as exhaust (Fusion Driven Rocket principle). The torch becomes pulsed, about 1-10 pulses a second. Same jet from about 12.6 TW of fusion instead of about 23 TW.
2. **Cleaner fuel.** He3-rich, spin-polarised D-He3: neutrons about 0.76% of fusion energy. This is what keeps the magnet coils' cryo load small.
3. **Thick, closed shell.** Traps 99.98% of the burn's light and 85% of its neutron energy.
4. **Burn 6 m aft of the reactor face** (x 52.3 m), inside the hull envelope. Halves the light on the face.
5. **Hot fins.** Four fins on the strake lines aft of the shield at 1,750 K (kT: "Let's go 1750"). A layout search (`torch/fin_layout.py`) found four on the strake lines best: 5 or 6 fins add mass for almost no span, and crowd the aft RCS clusters.

Result: 1.40 GW reaches hot structure, 0.48 MW the magnet coils, 5.0 MW/m2 the reactor face.

## What changed in the inputs

| Item | v0.5.1 | v0.5.2 |
|---|---|---|
| `torch.thrust_point_x_m` | 46.3 | 52.3 (burn point) |
| `torch.neutron_source` | 1 m column, x 39.3-46.3 | 0.3 m burn, x 52.0-52.6 |
| `hot_fins` | none | 4 at 40/140/220/320 deg, x 34.3-53.3, root r 4.75, 14 x 2 m pleats, 1,750 K, 4 kg/m2 per face + 4 t allowance |
| `ledger.engineering_reserve_t` | 67.5 | 46.476 (21.024 t moved to `torch_hot_fins_t`; dry mass unchanged) |
| `radiators.torch_span_m` | (full 24 m) | 4.0 |
| criteria (new checks for new hardware, existing thresholds unchanged) | | G4 reactor-face light <= 10 MW/m2 (ITER divertor, PUBLISHED); G8 fins >= 1.0 m outside the slot edge lines (A); G9 one fin lost, torch >= 50% (A) |

The reserve is now spread over the other dry parts at 46.5 t instead of 67.5 t; the fins carry no growth margin of their own.

## What changed in the gates

- **G4:** the 387 MW torch-leak check is replaced by three checks: fins carry the hot heat (1.49 GW capacity against 1.40 GW, using certify's own standard-library view factor with the torch chain taken as a 4.75 m cylinder, conservative); strakes at 4 m carry the coils' cryo heat plus habitat; light on the reactor face 5.0 MW/m2. Declared: `torch_heat` (narrowed, **PENDING** kT's acceptance of the wording) and `torch_fin_temperature` (ACCEPTED).
- **G6:** source moved to the burn point. The shadow cone narrows because the source is further aft: docking collar margin 0.79 to 0.53 m (limit 0.5), habitat 1.0 to 0.8 m.
- **G8:** new check, fins clear the shuttle corridor by 1.05 m.
- **G9:** new check, one fin lost: torch at 88%.
- **G10 card:** per-state inertia with fins out; hot-fin block; thrust point; "fold fins before big slews".
- **G11:** two new departures (torch internals, hot fins): 14 in all.
- **Images:** torch-burn view now shows fins out at 1,750 K and strakes at 4 m; new view from aft showing the fins and the shuttle lane; viewer burn mode unfolds the fins.

## For Sol to re-check

1. `torch/` is new and non-governing. `certify.py` imports `torch/torch_heat_budget.py` (standard library). `torch/fin_layout.py` needs numpy and is exploration only.
2. The G4 hot-fin check uses a 2D view factor; a 3D model would credit the fins' ends.
3. The narrowed torch gap's numbers are model assumptions (`torch/torch_heat_inputs.json`), not results; the shell leak is a physics unknown, the 1,750 K life is an engineering one.
4. Trim now pivots on the burn point at x 52.3 m.
