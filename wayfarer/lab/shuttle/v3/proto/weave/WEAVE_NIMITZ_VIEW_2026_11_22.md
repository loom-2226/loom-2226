# Weave low over calm water: observer view and witness-record comparison (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-22. A theory-to-observation comparison suggested by Sol after 26a3c30. **This does not explain any real event and does not touch AP v0.2.** The Weave mechanism is fictional; the comparison only asks whether its consequences resemble what a witness reported.

Code: `outing_nimitz_view.py`, `nimitz_view_figure.py` → `weave_nimitz_view.png`. Data: `outing_nimitz_view.json`, `outing_nimitz_pass.npz`.

## 1. New regime: hovering low over water on the W2 cushion (DERIVED, static equilibrium)

The cushion is a universal conservative force that cancels gravity inside the field. For two immiscible fluids at rest in such a field, the interface lies on an equipotential of `Φ_tot = g[Z F(r) + z(1 − F(r))]` (field centre at height Z; surface tension neglected).

**The sea is pulled into a bowl beneath the craft.**

| Field-centre height | Bowl depth | Disturbed patch width | Max rim slope | Water displaced | Wave energy if the craft leaves |
|---|---|---|---|---|---|
| 5 m | 9.4 m | 38 m | 45° | 4.0 kt | 122 MJ |
| 10 m | 5.6 m | 35 m | 30° | 1.9 kt | 33 MJ |
| 15 m | 2.0 m | 29 m | 13° | 0.44 kt | 2.5 MJ |
| 19 m | 0.27 m | 18 m | 2° | 43 t | 26 kJ |
| above ~19 m | ~0 | – | – | – | – |

- **Jinking:** the bowl follows the craft. Each abrupt move leaves the old bowl to collapse into ring waves.
- **Steep rims** (≥ 25°, shown white in the figure) are where breaking is likely. That is a proxy only; whitewater, foam and its persistence are **not computed**.
- **Pass** (shift dash, field centre 10 m up, kinematic): water is drawn up as much as 8.7 m behind the field centre, with a trough of about 4.8 m. About 1,000 m² of surface is displaced by more than 0.3 m. Nothing reaches the hull: under it the surface stays at least 3 m below the belly.

## 2. Witness record used

Primary source: David Fravor's written statement to the House Oversight Committee, 26 July 2023.

**Items taken from it:**
- calm seas with no whitecaps;
- a white-water patch that stood out;
- a small white Tic Tac-shaped object "moving very abruptly over the white water";
- "no Rotors, No Rotor wash, or any visible flight control surfaces";
- the white water "was also gone" when they turned back;
- the object "does not emit any IR (infrared) plume from a normal propulsion system".

**Not in the primary statement and therefore not used:** the size or shape of the white water, the object's height above it during the first observation, and anything about objects underwater. Some secondary retellings give these details; they are not used here.

## 3. Comparison

| Reported (primary) | Weave prediction (this lane) | Assessment |
|---|---|---|
| White water on an otherwise calm sea | Hovering with the field centre below ~19 m pulls the sea into an 18–38 m bowl with steep rims; breaking at the rims is likely | **Correspondence in kind.** Foam not computed; the patch's size and shape are not in the primary record |
| Object moving abruptly *over* the white water | The disturbance is centred under the craft and follows its jinks; each jink leaves a collapsing bowl | **Consistent in kind.** It requires the craft within ~19 m (field centre) of the water. A report placing it much higher would need another cause |
| No rotors or rotor wash | Cushion hover: air ≤ 0.16 m/s, ~140 Pa, no downwash | **Consistent** |
| White water gone on return | The bowl collapses into ring waves once the craft leaves (≤ ~0.1 GJ). Breaking subsides; foam lifetime not computed | **Cannot assess** without return time and a foam model |
| No IR plume | No exhaust. Heat depends on the unknown loss fraction | **Not established** |
| Abrupt manoeuvres | 71–110 g jinks with crew under ~1 g (outing 1) | Behavioural resemblance; the real accelerations are not independently established |

## 4. Falsifiers and limits

- **Falsifier:** Weave predicts that the water disturbance exists only when the field dips into the sea (field centre within ~19 m) and is a *depression beneath the craft*. White water verified with the object far above the sea, or a verified quiet water crossing (outing 4), would contradict this configuration.
- The bowl is a static equilibrium. How quickly it forms and collapses, the breaking, the spray and the foam are not modelled.
- One field size (R 15 m) is shown. Other sizes scale the patch.
- **Overall:** this is a resemblance between a fictional mechanism's consequences and one witness's description. It is not evidence about the real event.

**Sources:**
- [David Fravor, Statement for House Oversight Committee (26 July 2023)](https://oversight.house.gov/wp-content/uploads/2023/07/David-Fravor-Statement-for-House-Oversight-Committee.pdf)
- [House hearing record, 26 July 2023 (govinfo)](https://www.govinfo.gov/content/pkg/CHRG-118hhrg53022/html/CHRG-118hhrg53022.htm)

## 5. Does the bowl form fast enough? (Sol, after 1ba4d27)

Code: `outing_bowl_dynamics.py`, `bowl_dynamics_figure.py` → `weave_bowl_dynamics.png`. Data: `outing_bowl_dynamics.json`, `outing_bowl_dynamics_snaps.npz`.

**Model:** a coarse linear free-surface response in deep water. The cushion acts as the equivalent surface pressure that would hold the equilibrium bowl, and each Fourier mode relaxes toward it at its own frequency `ω = √(g|k|)`.
- Domain: periodic, 512 m, 1 m grid.
- Inviscid; no breaking or foam.
- Small-slope theory applied to a bowl with 30° rims: **timing is an estimated timescale, not a validated prediction; amplitudes are coarse** (narrowed after Sol review).

| Case (field centre 10 m up; equilibrium depth 5.6 m) | 0.5 s hover | 5 s hover | 5 s hover, 2 s ramp-on |
|---|---|---|---|
| Bowl depth at departure | 0.6 m (11%) | 3.2 m (57%, mid-slosh) | 4.7 m (84%) |
| Deepest plunge before departure | 0.6 m | 10.3 m (≈1.8× equilibrium at ~2.6 s) | 9.8 m |
| Time to 63% depth | – | 1.15 s | 2.0 s |
| Old spot after the 30 m jink | rises +3.3 m at +3.5 s | rises **+5.6 m** at +2.7 s | +4.4 m at +2.9 s |
| Peak surface slope | 45° | 46° | 49° |
| Surface energy at 25 s (outgoing waves **plus** the bowl still held under the cushion at the new spot) | 83 MJ | 100 MJ | 127 MJ |

**Findings:**
- **Formation lag (ESTIMATE, coarse linear).** The bowl takes ~1–2 s to form and then sloshes. A cushion switched on faster than the bowl's ~5 s natural period plunges to almost twice the equilibrium depth before settling. Avoiding the overshoot needs ramps much longer than ~5 s.
- **A half-second hover barely marks the sea** (0.6 m dimple).
- **Jinks leave the water behind.** The bowl cannot follow a 0.5 s, 30 m move. The old pit is abandoned and rebounds into a central rise of up to ~5.6 m about 2–3 s later. A new pit plunges under the craft's new position, and ring waves from both overlap. Slopes reach 45–49°, so breaking is likely (proxy; foam not modelled). The disturbance lingers, weakening, at the old spot for ~10 s or more.
- **Picture:** a craft hovering for a few seconds dimples the sea. Each abrupt jink leaves behind a collapsing pit that throws up a central hump, while a new pit opens under it. Repeated jinking over one area would churn a patch of ring waves and rebound humps that lags the craft.
- **Signature:** this comes from the **gravity cushion**, not the translational shift. The two prototype technologies now have distinct observable signatures.
- **Limits:** the response is linear on a strongly nonlinear shape. There is no breaking, foam, spray or viscosity; deep water and calm seas are assumed. Real overshoot and rebound would be reduced and turned into breaking and spray. **UNDETERMINED** beyond timing and order of magnitude.

Branch closed here per Sol ("one more short outing, then move on").

**Sol review of 72a9440 (accepted, branch closed):**
- The 1–2 s timing is an estimated gravity-wave timescale. Slopes of 30–49° are outside linear validity, and formation, rebound and breaking can interact.
- The 25 s energy figure includes the bowl still held under the cushion at the new spot, so it is not all outgoing wave energy.
- **AP note.** The lagging disturbance is a new, potentially distinctive prediction. The modelled persistence of 10 s or more is unresolved against the report that the white water was gone on return: reliable timing showing near-immediate disappearance would challenge this model.
- **Disposition:** the shift governs motion, the cushion governs support, and their signatures differ and can lag the craft. No further Tic Tac work. AP evidentiary conclusions are unchanged.
