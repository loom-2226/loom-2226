ALL bodies. ALL sponsors. 2026-2226.

# Continuous active hull: narrow screen

**Brief:** kT and Sol, "Continuous Active Hull Hypothesis". NON-CANON research. No vehicle, CCR or booking change.
**Code:** `continuous_hull_screen.py` → `continuous_hull_screen.json`.

## Stopping-condition answer

**In the existing model, the continuous active hull is a different means of generating the same fields. It does not change their controllable behaviour.** Three reasons:
1. The model prescribes the field geometry directly and contains no law linking a generator to the field it makes; the relational sector S_R is unspecified.
2. The stress-energy the field requires sits in the **wall shell**, not on the hull, whoever generates it: 99.8% lies between 11 and 19 m from the field centre, and 1.6e-8 lies inside the hull's 6.4 m radius. A skin source is no closer to the walls than the 8 t module was. Both need the relational sector to act at a distance.
3. Pulling the wall onto the skin would make a different field, not a better generator: the lane's 158 g case shows a shift wall that cuts the hull strains it exponentially.

## The three checks

| Check | Result |
|---|---|
| **A. Symmetric W2/Weave fields from the skin** | Same fields, same source location (wall shell). Nothing measurable changes. |
| **B. Asymmetric, surface-steered shift** | **No lasting velocity.** Six random asymmetric, time-varying, spatially skewed shift fields all displace the hull (0.5–42 m) and leave it at its original velocity, to rounding. The law dw/dt = −(∇b)w is homogeneous in w, so no shift geometry, however finely controlled, gives velocity. |
| **C. Directional potential (cushion/lapse type) pointed sideways** | **Lasting velocity: yes.** 0.4 g ramped over 20 s gives exactly 39.2 m/s that persists after shutdown, **provided the field travels with the vehicle**. A field fixed in space returns almost all of it (1.5 m/s): the hull exits through the reverse walls. |

## What C means

- **The lane already had this physics.** The horizontal "lapse dash" in `WEAVE_GEOMETRY_COMPARE_2026_11_21.md` is exactly this push, and the W2 cushion is its vertical case. **The model places no constraint on direction.** "Vertical only" was an operating and energy booking, not physics.
- **This corrects my torchless screen (80ade29).** The verdict stands: orbit still needs a TJ-class source and an explicit capability grant. But the grant is **"book the existing potential field sideways"**, not a new field type.
- **Conservation:** the field's own (ADM) momentum is identically zero for a compact field on flat slices. So the hull's gain must go to an external partner (R1), exactly as for the cushion's climb. The exchange law and the partner remain unknown, and §7.3 still binds.
- **In air:** a potential push moves the hull **through** the air, with drag, wake and boom; it does not carry the air with her the way the shift does. Horizontal acceleration to orbital speed belongs above the atmosphere: climb on the cushion first.

## Precise missing pieces (unchanged by the hull hypothesis)

1. **The relational sector's constitutive law:** which potential fields are attainable, and at what energy cost, power and duration.
2. **The R1 exchange law and its partner.**

## Value of the hypothesis

It is strong as LOOM narrative: humans look for emitters and find none, because the material is doing the work. It is also a candidate **form** for the missing constitutive law, a surface-sourced relational sector. It is **not testable** in this model, and it neither grants nor forbids directional acceleration.

## Decision this leaves for kT (unchanged)

Keep the torch, or grant a sideways-booked cushion. A grant needs a TJ-class source (keep the reactor), a CCR revision, and acceptance of no fallback on airless bodies.
