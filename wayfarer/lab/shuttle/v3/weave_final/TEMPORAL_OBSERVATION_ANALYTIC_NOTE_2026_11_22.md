ALL bodies. ALL sponsors. 2026-2226.

# Tic Tac: temporal observation, analytic screen

**Status:** NON-CANON, research note only. No model, code, physics permission, CCR or canon change.
**Basis:** `FIRST_FLIGHT_2026_11_22.md`, `WEAVE_SHUTTLE_OPERATING_CARD_2026_11_22.md`, `GAIT_TEST_2026_11_22.md`, and the existing lane's unit-lapse shift and W2 potential-type descriptions.
**Scope:** Crew clock, outside clock, and signal arrival during the existing 75-second calm-ocean sortie. No numerical simulation or new field model.

## 1. Weave: the comoving clock

For the adopted unit-lapse shift metric, write schematically

```
ds² = -c² dt² + gamma_ij (dx^i - beta^i dt)(dx^j - beta^j dt).
```

Along an ideal field-comoving clock trajectory `dx^i = beta^i dt`, proper time satisfies `dτ = dt`. An outside clock in the shift-free region, at the same gravitational reference potential, also has `dτ = dt`. **No shift-induced differential aging** follows from this idealisation. A coordinate speed is not automatically a local speed relative to an inertial observer. Therefore adding ordinary flat-spacetime `v²/(2c²)` time dilation to this comoving trajectory would mix metrics and double count.

For a *separate counterfactual* in Minkowski spacetime, the 30 m / 0.5 s quintic profile of the first-flight sidestep gives `v_peak = 112.5 m/s` and

```
Δτ_flat ≈ ∫v² dt / (2c²)
        = [(10/7) (30 m)² / (0.5 s)] / (2c²)
        ≈ 1.43e-14 s.
```

This is **not** an extra correction to the unit-lapse Weave clock result. It only shows how small conventional kinematic dilation would be for an ordinary trajectory.

## 2. W2 cushion: clock rate relative to sea level

The adopted W2 static-support picture cancels the *interior potential gradient*, with interior potential matched to the field centre. It does not prescribe an extra centre-to-outside clock offset. Hence a clock aboard while hovering at height `h` ticks, to first weak-field order, like an ordinary static clock at that height.

Compared with a sea-level reference clock, the idealised fractional rate difference is `g h / c²`: at 24 m, `2.62e-15` (**dimensionless**, not seconds); at 10 m, `1.09e-15`. For the given 75 s height profile (24 m for 0–9 and 58–75 s, linear 24→10 m over 9–29 s, 10 m over 29–44 s, and linear 10→24 m over 44–58 s):

```
∫h dt = 24*(9+17) + 17*(20+14) + 10*15 = 1,352 m·s
Δτ_crew−sea_level ≈ (g/c²)*∫h dt ≈ +1.48e-13 s.
```

This conditional approximation uses uniform `g`, nonrotating local coordinates and the reported W2 matching rule; it is not an observed clock effect. There is no modelled gradient *across the cabin* in the ideal cushion interior.

## 3. Signals: distinguish travel time, field timing, and Doppler

Ordinary light travel over a 30 m path takes about `1e-7 s`. A first-order *field-related* one-way shift-time perturbation scales as `L β / c²`, which for `L = 30 m` and `β = 112.5 m/s` is about `3.75e-14 s` in a favourable collinear, constant-field estimate. This is a scale, **not** a computed ray trace of the moving 15 m-radius field; sign, path, emission timing and viewing angle matter.

The existing operating card's radar and optical statements refer only to its tested geometries. In the tested head-on radar geometry it reports a track consistent with the hull's motion and negligible direct field signature. Do not infer that all sensor geometries have zero effect. Nor confuse small extra path delay with the potentially obvious apparent translation, regular light-travel delay, or ordinary Doppler from a moving target.

## 4. Conclusion and boundary

**Expected result: null for exotic time behaviour.** The adopted classical shift, W2 potential, geodesic-carriage and signal models contain no temporal-superposition state or joint amplitude over alternative arrival events. They therefore cannot predict that a pilot literally perceives multiple arrival times at once. That proposal is a **separate fictional sensing / relational-accessibility permission**, not an implication of the current field equations.

The event-navigation / mail-deadline idea belongs conceptually in the Research Lab's Loom Drive mechanism lane if kT elects to investigate it. This note does not open that work, authorise RF follow-on tests, select a connection curvature, select a partner, or change the shuttle design.

**STOP:** analytic null check complete; no additional run or rule is needed.
