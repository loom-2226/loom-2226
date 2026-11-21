# Weave coupled dash: one effective action (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-21. Responds to Sol's review of 27d8fb4: couple one dynamic wall coordinate to one relational mode from a common effective action, and attempt the 200 m dash with no externally imposed reaction. No canon, hardware or mass changes.

Code: `weave_coupled.py` (run), `coupled_figure.py` → `weave_coupled.png`. Data: `weave_coupled.json`, `weave_coupled_series.json`.

## 1. Why the shift-only action was not usable (DERIVED)

With `L_i = ½ m_i (ẋ_i − β)²` and `β = Ẋ_d f(x − X_d)`, the Noether charge for a common translation is

`P = Σ m_i w_i (1 − f_i) + ∂L_wall/∂Ẋ_d + μ ξ̇`, with `w = ẋ − β`.

A payload carried at `w = 0` inside `f = 1` contributes nothing. That action treats carriage as a change of frame, so it cannot test conservation: the payload's physical momentum (which in GR sits in its far field) is absent from the books.

## 2. Effective action used (1D, v ≪ c)

```
L = Σ ½ m_i ẋ_i² − U_springs                ship matter (hull 59 t, crew 1 t, cargo 1 t)
    − Σ m_i G(t) (x_i − X_d)                 universal carriage field in the domain
    + ½ M_w Ẋ_d²                             wall collective coordinate
    + ½ μ ξ̇² − ½ k_c (X_d − ξ − s(t))²       relational mode + wall–mode coupling
```

Controls `G(t)` and `s(t)` are the M2 actuation. Every term depends on differences of coordinates only, so `P = Σ m ẋ + M_w Ẋ_d + μ ξ̇` is exactly conserved (Noether). Energy changes only through the explicit time dependence: `dW = Σ m (x − X_d) dG + F_c ds`.

Parameters: `M_w = 1 t`, `μ = 5.97e24 kg` (Earth as the relational mode), `k_c = 1e9 N/m`, crew/cargo springs `2e6 N/m`, quintic 200 m / 3 s profile, `dt = 1e-5 s`.

## 3. Assumptions stated openly

| Id | Assumption | Status |
|---|---|---|
| A1 | A controllable, universal (mass-proportional) carriage field inside the domain: a lapse gradient, admitted by the §5 ADM form (N). | ASSUMED (M2 actuation) |
| A2 | The domain wall is a collective coordinate with an effective inertia. | ASSUMED |
| A3 | The wall couples to a relational environmental mode through a translation-invariant interaction. This is the M1 exchange law. | ASSUMED, new M1 constitutive assumption |

## 4. Results

| Check | Result | Verdict |
|---|---|---|
| Hull displacement | 200.000 m, final speed 8e-14 m/s | DERIVED within the action |
| Crew felt load | peak 7e-11 g (numerical residue); a conventional push would peak ≈ 13 g | DERIVED: universal field ⇒ no tidal load |
| Wall tracks hull | error 3e-14 m | control result |
| Total momentum | drift 1e-7 N·s against a 7.8e6 N·s peak ship+wall momentum | DERIVED (Noether), checked |
| Centre of mass (all sectors) | 3e-7 kg·m; ship+wall move 1.24e7 kg·m, relational mode moves −1.24e7 kg·m (ξ = −2.1e-18 m) | consistent |
| Energy | ΔE − W ≤ 11 kJ (integration error) against a 484 MJ peak transient | DERIVED, checked |
| Net actuator work | −7.9 kJ (≈ 0); the 484 MJ peak is ½(m_ship + M_w)v² lent and recovered | holds only if recovery is lossless (UNDETERMINED) |

The field moves the shuttle, the crew stay inertial, and momentum and energy close with nothing imposed from outside the action.

## 5. What this does and does not show

- It is **not** reactionless. The reaction is real and goes into the relational mode, exactly as a car's goes into the road. With Earth as the mode, the recoil is unobservable (2e-18 m).
- The extraordinary content has been moved, not removed. It now sits entirely in A3: that a metric domain wall can exchange momentum with distant mass through a translation-invariant coupling. That is a sharper form of §7.1b's "local coupler not required", and it is the single claim that M1 must now supply or refuse.
- A1 is the M2 claim that the shuttle can generate a uniform lapse gradient over its own volume. This is where the size privilege from `WEAVE_SCALE_PRIVILEGE_2026_11_21.md` enters. The model here does not price A1's geometric demand.
- Peak power: the actuator must lend about 0.48 GJ within about 1.5 s (≈ 0.6 GW peak) and take it back. Loss in that round trip is the real running cost and is UNDETERMINED.
- The same structure applies unchanged to Wayfarer's Metric: same action, same conservation; only the mode partner and scale differ. No scaling restriction was added.

## 6. Open items

1. Derive A3 from the M1 sector (or show M1 forbids it). This is the decisive item.
2. Price A1: geometric demand of a uniform lapse gradient over a shuttle-sized domain.
3. Round-trip loss model for the lent kinetic energy.
4. Separate the v² and acceleration comparisons in `scale_privilege.png` (earlier Sol qualification).
