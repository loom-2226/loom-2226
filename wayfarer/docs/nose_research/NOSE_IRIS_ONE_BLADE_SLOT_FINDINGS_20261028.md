# Wayfarer central iris: one leaf into an armoured slot | 28 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT CERTIFIED**

Bootstrap verified live `loom-2226/loom-2226` PR #432 remains open, head `3485830a56dfead79b2ef8bba031a595b536fbb5`. Source Rev 7 pressure hull, sensors, crew and Metric nodes unchanged; isolated research branch only. Source of hypothesis is the user's 16-leaf iris shutter inspiration.

## Narrow experiment

The prior failed mechanism rotated the protective leaf outward, *then* translated it aft. A thick blade could not pass through the original opaque shoulder without cutting it. Rather than inventing a large exterior hatch, test **the reverse sequence** on exactly one physical leaf:

1. From the closed, flush centre face, translate the full-thickness blade **aft while still inside the open r≤1.8 m circular central aperture**. This puts its leading edge behind the adjacent armour lip; no exterior hatch needs to open.
2. Rotate the leaf in 1° increments from 0 to 62°, with a simultaneous axial cam translating the leaf farther aft as its radial footprint grows. Keep it entirely **inside the original shoulder armour**, rather than passing through that armour.
3. At fully open, the single blade is covered by the *existing* opaque outer shoulder, so it does not require a new backing plate in the parked radial region.

**Important modelling assumption:** the experimental 50° angular nose uses **20 cm normal armour thickness** on the faceted shoulder. This is a conservative, newly prescribed local shielding construction corresponding roughly to Rev 7's 20 cm original ellipsoidal shell, not existing manufactured facet CAD or a confirmed material specification. At 50°, that occupies about 31.1 cm in x. The 27 g/cm² armour-equivalent leaf uses the earlier effective accounting density ~1.376 t/m³, giving **19.63 cm actual leaf thickness**. An additional 25 mm nominal axial gap is reserved in the search. That is *not* yet adequate allowance for actual rails or bearings.

The leaf is one truncated 16th-disk sector (nominal aperture R=1.8 m, 22.5° wide plus 1° overlap on either side), rotating about the prior r=1.87 m, 22° off-axis pivot. A grid samples 48 radial × 29 angular points on the leaf, full 0.196 m slab depth, against source pressure-head and analytical fixed faceted armour occupancy. The numerical sweep contains 31 axial withdrawal poses followed by 62 simultaneous axial-cam / angular-rotation poses. The initial 0.12 m central boss remains a separate hypothesis; the shielded slit rim is not manufactured.

## Executed results

| Check | Rotate first, push aft | **Retract before rotating, cam under armour** |
|---|---:|---:|
| Sampled stationary shoulder-armour contacts | **Up to 1,263 point contacts at a pose** | **0** |
| Earliest sampled shoulder contact | Immediately as rotation begins | **None sampled** |
| Least pressure-head clearance through motion | Not a valid clear path | **0.2169 m** |
| Least blade-to-inner-armour axial clearance during rotation | Intersects | **0.0260 m** |
| Minimum allowable axial positioning interval along the cam path | No valid pathway | **0.1929 m** |
| Maximum swept blade radius | ~2.71 m | **2.7099 m** |
| Final blade front axial position | N/A | **x = −0.0168 m** |

The blade's outer radius remains below the original bow-sensor inner radius of 2.90 m and well below forward Metric-node faces near 4.46 m; *mounts, tracks and full field-of-regard clearance remain unchecked*. The 0.026 m separation is an **axial** shell-gap measurement, not a 2.6 cm normal-to-facet clearance.

### The critical limitation: one blade is not sixteen

Repeating exactly the **same cam track** with two adjacent axial leaf levels, whose combined depth is **2 × 0.1963 + 0.020 = 0.4126 m**, has a **negative 0.0234 m necessary positioning interval** at 62°. This is a ~2.3 cm packaging shortfall, before bearings, seals or impact attachments. Therefore **the full two-tier iris does not pass this test**. The single-blade advance is real within this model, but cannot be promoted as physical closure of the full design.

The earlier raised-to-flush lower leaves are even thicker, and their full face still collides during rotation without a second staged separation mechanism. The fixed 12 cm center boss is preferable to a complicated retracting plug but still needs an actual sealed overlap with the leaves.

### Why this differs from the previous rejection

The prior final translation moved a blade *through* the opaque shoulder and correctly produced a collision. The new path moves the blade backward entirely **while it is within the central aperture**, *before* any part of it crosses the aperture's radial rim. At that point the entire thickness is behind the lip of the existing armour. The axial cam tracks the inner boundary as rotation carries the blade outward. Thus the original exterior skin remains intact except for the interface/entry slit at the central-window rim.

This is a **specific mechanism concept**, not a universal geometric proof. The 360° reinforced rim slot and its space for hinges, seals, leaf overlap and substantial actuation loads have not been drawn. Even if one blade works, 16 complete leaves with real bearings may be impossible without further redesign. The large panoramic visibility loss associated with reserving the storage annulus is unchanged by this motion experiment.

## Stop / next physical question

**Keep this one-leaf cam route** as the best experimentally studied non-external iris motion. **Do not adopt the full iris.** The next hard blocker is narrow and measurable: **can both interleaved armoured leaf tiers use a stepped or separate cam path without violating the pressure-head and reinforced slit-rim clearance?**

The present two-tier calculation misses by about 23 mm. Do not expand into a full spacecraft redesign to recover that small theoretical shortfall. If no material/geometry constraint earns the extra space, park the iris.

## Files

- `command/l1_iris_one_blade_slot.py`: executable and deterministic pressure/armour contact test, including failing naive path and 2-tier necessary positioning interval. Output: `command/l1_iris_one_blade_slot_results.json`.
- `render/make_single_blade_slot_viewer.py`: self-contained Android-friendly HTML generator; `render/out/nose_iris_single_blade_slot_viewer.html`. Switch between two kinematic sequences, scrub 0–100% and orbit the 3D nose. It explicitly visualizes **one** rigid 196 mm-thick leaf, not sixteen mechanically installed assemblies.

**One leaf clears the sampled geometry. A complete flush, fully protected iris does not.**
