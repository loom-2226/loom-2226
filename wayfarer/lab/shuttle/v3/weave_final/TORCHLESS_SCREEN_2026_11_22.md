ALL bodies. ALL sponsors. 2026-2226.

# Torchless Tic Tac: one narrow screen (Sol brief)

**Question:** can the existing W2 cushion and Weave shift take her from the surface to a velocity-matched rendezvous with Wayfarer in low orbit with no conventional thrust? The screen uses only established behaviour and invents no exchange mechanism.

**Code:** `torchless_screen.py` → `torchless_screen.json`. NON-CANON.

## Verdict

**It does not close with established behaviour.** It stops at one precise missing capability.

| Element | Result |
|---|---|
| **Weave shift** | **Cannot change her velocity: DERIVED.** The lane's slow-geodesic law, dw/dt = −w·∇b, is homogeneous in w. A hull that starts at rest relative to the exterior is carried along, then left at rest when the field ends, for **any** shift profile and in any frame. This is a property of the established law, not of the dashes we happened to choose. |
| **W2 cushion** | **Can in principle.** It is a potential-type field that already changes velocity: the climb at (1.4 − 1) g to 2 km, paid from the flywheel, with the partner unknown. The same field type and the same bookkeeping, pointed horizontally, would give orbital speed. **Only vertical is established.** |
| **Wayfarer supplies the velocity** | Not credible. Wayfarer cannot match a vehicle at zero orbital speed. |

## What orbit needs

Figures for 46.5 t, a due-east launch from the equator, to 200 km:

| Quantity | Value |
|---|---|
| Δv | 7.32 km/s (orbit 7.79 km/s, less Earth's rotation of 0.47 km/s) |
| Energy delivered | **1.5 TJ**; 2.5 TJ from the source at the lane's 60% efficiency |
| Momentum to the partner | 3.4e8 N·s |
| Angular momentum to the partner | 2.2e15 kg·m²/s; Earth's spin changes by a fraction of 4e-19 |
| At the cushion's 0.4 g | 31 min of acceleration over ~6,800 km of ground track; peak source power 2.4 GW |
| Flywheel | 3 GJ, about 0.1% of what is needed |

## Precise missing capability

1. **A directional cushion mode.** The cushion's acceleration would have to be commandable horizontally, not tied to local gravity, for about 31 min. It is established only vertically, to 2 km.
2. **A TJ-class energy source.** Only the torch's 7.7 GW reactor qualifies, so a torchless Tic Tac keeps the reactor. It drops the nozzle and most of the 23 t of water.
3. **The same exchange-law gap as now** (the R1 law and its partner). Using the cushion as **main propulsion** with an unknown partner is a new capability claim beside §7.3 and §21: it is an independently commanded momentum source. It needs explicit CCR text, and it is exactly the kind of capability Sol warned against granting just because we want it.

## Consequence to weigh

Without a torch, a field failure over an airless body such as the Moon or Europa leaves **no fallback**: there is nothing for parachutes to work in, and there is no torch.

## Decision for kT

- **Keep the torch.** Status quo, nothing lost.
- **Grant the directional cushion** as a declared prototype behaviour, by CCR revision. She would keep the reactor, drop the water and nozzle, and accept no fallback on airless bodies.
