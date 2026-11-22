ALL bodies. ALL sponsors. 2026-2226.

# Tic Tac mission role: local-only vs Wayfarer-matched pickup

**Status:** RESEARCH / NON-CANON / ANALYTIC ONLY. No flight simulation, design change, canon/CCR amendment or deployment decision.
**Prompt:** Claude reviewer, 2026-11-22: assess (1) local-only Tic Tac and (2) Wayfarer matching the surface pickup against *existing* Wayfarer canon. Orbit is not necessary for a powered shuttle to stay aloft, but relative velocity still must be matched for docking.

## Authoritative sources and applicability

- Governing: `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.5.md` §§2, 6–7.3, 13–14, 15–16, 21.
- Governing packaging: `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.5a.md` §1: a **carried orbit-to-atmosphere-to-surface launch**, semi-recessed vacuum bay, lateral departure, explicit DOCKED / ABSENT state. No canon requirement that Wayfarer itself hover over a planet.
- Current Wayfarer design inputs: `wayfarer/config/wayfarer_v05_inputs.json`, torch power ceiling **11.361 TW jet**, CRUISE thrust **11.361 MN**, discrete ECON / CRUISE / EXPEDITE modes. These are engineering inputs, not proof of atmospheric or stationary operation.
- Canon detailed S1 mass **1,167.532687 t**, normal remass **245.390432 t**, protected water **50 t**, with live-mass accounting required.
- `wayfarer/config/kt_decisions.json`: accepted G10 segmented burn doctrine **<=165 min torch segments; >=15 min coasts**, and adopted torch-heat design assumptions.
- Shuttle experimental operating card and `DIRECTIONAL_W2_ASCENT_2026_11_22.md`: W2 cushion/Weave tested near the surface, profile cushion ceiling ~2 km; a 200 km Wayfarer rendezvous requires ordinary velocity matching. Shuttle status NON-CANON, CCR-2026-0005 remains PROPOSED.

## Option 1: Tic Tac limited to near-body operations; Wayfarer stays in orbit

**Role: attractive. Closed round-trip: NO.**

The Tic Tac may hover, dart, translate locally, descend and conduct surface/ocean missions without needing a sustained orbit *for its local role*. But normal orbital Wayfarer is still moving at roughly orbital velocity; the experimental Weave shift changes coordinate position without providing the matching ordinary velocity. Its current W2 cushion profile does not establish orbital-altitude reach. A descent from a carried orbital launch may be studied with the existing blunt-body entry/fallback screen, but getting back to the parent ship is **not closed**.

Thus saying 'Wayfarer comes to her' silently imports option 2. Alternatively, one must explicitly pay for a shuttle ascent, use separately qualified local pickup infrastructure, or keep the craft deployed locally without routine mothership recovery. None is automatically granted.

There is no change to existing docking geometry: the 12.8 × 3.8 m Tic Tac fits the pre-existing bay; a final docked state still requires position, velocity, attitude, field interference and latching compatibility. The 15 m-radius shuttle field cannot be assumed safe when it overlaps Wayfarer at the terminal docking interface.

## Option 2: Wayfarer brakes to a low-altitude co-rotating pickup, holds, then reboosts

**Conventional dynamical principle: possible in vacuum. Actual near-surface Wayfarer operation: NOT QUALIFIED.**

For an *illustrative* equatorial Earth 200 km circular starting orbit, the circular speed is ~7.79 km/s and co-rotating speed ~0.48 km/s; cancelling the tangential mismatch calls for ~7.31 km/s of ordinary delta-v. At full S1 mass and ECON `v_e = 3,000 km/s`, an isolated impulse would spend **~2.84 t remass one way**, ~5.7 t for a two-way pair (before trajectory, climb/descent and hover). These are *rocket-equation sensitivities*, not a feasible interception trajectory or approved pickup plan. Orbital braking and reboost cannot be treated as instantaneous at fixed altitude; actual burn timing and finite thrust matter.

Station keeping requires approximately `F = m g(r)` upward, plus small corrections for rotating coordinates; this is a continual high-thrust burn, not an RCS hold or a free Metric capability. Analytic bounds at initial S1 mass:

| Illustrative support point | Gravity | Required thrust | Existing-mode ideal remass rate |
|---|---:|---:|---:|
| Earth surface / ~2 km | ~9.81 m/s² | **11.45 MN** | CRUISE full thrust **11.361 MN is slightly insufficient at S1**; EXPEDITE (1,000 km/s) needs **~41.2 t/h**, assuming available throttling. An *unqualified continuously variable* ~1,984 km/s mode could reduce this to ~20.8 t/h. Do not book that interpolated mode as canon. |
| Earth 200 km | ~9.23 m/s² | **10.78 MN** | CRUISE 2,000 km/s, throttled, **~19.4 t/h** (optimistic model). |
| Mars surface (sensitivity only) | ~3.71 m/s² | **4.33 MN** | ECON 3,000 km/s **~5.2 t/h** if deep throttling is possible (unqualified). |
| Moon surface (sensitivity only) | ~1.62 m/s² | **1.89 MN** | ECON 3,000 km/s **~2.3 t/h** if deep throttling is possible (unqualified). |

Power: at full torch operation the engineering heat screen assumes ~11.361 TW directed jet power and predicts ~**1.40 GW reaches hot ship structure** at step S4; accepted high-temperature fins mitigate this in the *engineering assumptions*, but near-planet atmosphere/plume recontact, radiator view factors, field/dock proximity, shield and engine duty are not qualified. This is NOT a basis to declare a near-surface ship safe, especially above water, a settlement or an occupied landing site. Even a short wait spends remass, produces heat and exposes the environment to the exhaust.

The accepted **165 min burn / >=15 min coast** doctrine also precludes *indefinite uninterrupted* stationary hover without a separate solution. A 15 min ballistic coast is not station keeping.

**Decisive geometry conflict for Earth:** placing Wayfarer ~200 km high avoids atmosphere but does **not** put it within the Tic Tac's current ~2 km cushion operating profile. Bringing Wayfarer down to the shuttle's presently demonstrated reach puts the ~57 m torch ship deep inside atmosphere, with unqualified drag/thermal loads, major exhaust hazard, docking while thrusting, and field-overlap issues. No accepted Wayfarer near-surface pickup card or certified low-altitude Metric support was found in the cited canon.

## Disposition

1. **Recommend option 1 as the Tic Tac's mission identity**: a locally operating, non-orbital Builder craft. This is a role choice, not proof of end-to-end surface-to-Wayfarer return.
2. **Do not adopt option 2 as the default retrieval solution.** It is an expensive and unqualified mothership operation; the energy mismatch has moved, not vanished. Its remass may be tolerable for *brief* encounters because Wayfarer has immense `v_e`, but atmospheric and terminal docking closure is absent.
3. **Retain ordinary orbital Wayfarer operations** as the only currently grounded default. Whether the shuttle itself must match orbital velocity, a separate asset performs transfer, or the Tic Tac remains locally deployed is open. Do not grant near-surface Wayfarer station keeping by implication.
4. No decision required on reactorless Builder operation or connection curvature. No canon change.

**STOP:** analytic comparison complete. Actual pickup profile, finite burn trajectory, atmospheric heat, plume, and docking dynamics are not solved by this screen.
