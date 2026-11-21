# Prototype lane, experiment 2: smallest extraordinary capability
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON research only, per kT's brief of 2026-11-21. No canon change, no Wayfarer change, no new design population, no winner. Numbers are screening results from the explorer ROM plus simple bounds.

**Reference vehicles:**
- Conventional reference: #2643 + Osteon cautious.
- Adaptive reference: W1 + Osteon cautious (17 m span, 18 t tank, 38.38 t dry).
- Bay: 12.8 m baseline, with 14.3 m kept as a contingency.

**Files:** `exp2_w1.py/.json`, `exp2_w2.py/.json`, `exp2_w3.py/.json`, `exp2_figures.py` → `exp2_departure.png`, `exp2_w1_w3.png`.

## Corrections to the first lane note
- **2 km lift energy:** mgh for 60 t raised 2 km is **1.18 GJ**. The earlier "~3 GJ" was (mgh + ½mv²)/η, with v = 125 m/s and η = 0.6; it is now itemised.
- **"20 s" climb:** this contradicted its own 0.4 g profile, which reaches 2 km in 32 s at 125 m/s. Climbing 2 km in 20 s needs about 1 g net.
- **"1 t flywheel":** this uses kT's **declared 2226** storage (1 kWh/kg, 150 kW/kg; ship_power record of 2026-11-01). That is about 10× an ordinary 2026 flywheel. With ordinary storage, no field scenario closes.
- **W3 air energy:** the 0.2–0.9 GJ figure assumed one boundary model (hypothesis 1 or 2 below). It is not a universal requirement.

## W1: programmable structure vs conventional mechanisms
**Osteon vs W1:**
- *Osteon (established):* a static, stronger titanium (22–38% lighter on primary members).
- *Programmable structure (proposed):* geometry or stiffness switching, with no evidence anywhere in the repo.

**Bay fit (geometry):**
- A *conventional* 17 m fold-over-top wing fits: there is a 0.74 m clear band above the spine inside the 2.15 m envelope, and two stacked folded panels need 0.53 m.
- Fans, floats, the cradle and the hinge fittings sharing that band have **not** been checked.
- A single-stage telescoping wing cannot reach 17 m, because 6.4 m panels are longer than the hull is wide.

**Decomposition (model):** all seven variants pass all five missions; they differ in margin.

| Variant | Dry (t) | Hot touchdown (m/s) |
|---|---:|---:|
| A telescoping 13.7 m | 35.95 | 49.5 |
| B conventional fold 17 m | 37.28 | 48.0 |
| D programmable stow only | 38.38 | 49.3 |
| **E conventional fold + adaptive camber** | **37.28** | **43.3** |
| F full W1 (lane reference) | 38.38 | 44.3 |

- The margin comes from adaptive camber (CL cap 5, a sensitivity), **not** from shape-changing stowage.
- Programmable stowage is heavier than a fold in this model (1.5× against 1.2× wing mass).

**Stiffness and control (required values):**
- A flat-stowed wing that locks into a box needs **35–170 MPa** of shear at the locks (8 g × 1.5).
- Friction or vacuum jamming gives about 0.05 MPa, so the locks have to be mechanical (teeth, zippers, bistable shells) or a reversible structural bond.
- An unlocked web turns the box into an open section with about 1% of the torsional stiffness. Lock integrity is therefore flight-critical.

**Actuation:** energy is trivial (0.1–1 MJ). Mass is the open question.

**Adaptive stiffness (credible value):**
- Re-armable slam and crash absorbers.
- At 5 m/s sink, a 0.15–0.30 m adaptive stroke cuts slam load from about 25 g (rigid) to 4–9 g.
- A 16 g crash at 15 m/s needs 0.7 m of stroke, absorbing about 7 MJ, and the absorber can be reset afterwards rather than replaced.

## W2: four departures (M1 field, central assumptions)
**The three mechanisms, kept apart:**
- **M1, reduced effective gravitational loading:** the reaction goes to the planet. It needs a new constitutive relation. It is in tension with the equivalence principle only if it is framed as changing matter rather than as an applied coupling.
- **M2, modified inertia:** in tension with a governing invariant (the equivalence principle, plus momentum or energy on switch-off). It gives no lift, so it is dropped.
- **M3, engineered geometry:** canon-family physics but beyond canon technology. The wall may not cut water or people.

| | to 200 m | to 2 km | exhaust at surface | source energy | peak power | device ceiling (central / pessimistic) | new choice |
|---|---|---|---|---|---|---|---|
| S0 conventional | 5.2 s | 16.5 s | yes | – | – | – | – |
| S1 15 s partial pulse | 5.2 s | 16.5 s | yes | 0.9 GJ | 112 MW | 0.5 t / none | none |
| **S2 field to 200 m** | 9.0 s | 24.2 s | **no** | 0.35 GJ | 67 MW | **3.5 / 3.0 t** | exhaust-free pickup; vertical landing on land (field 0.65 W + fans) |
| S3 field to 2 km | 9.0 s | 28.6 s | no | 3.2 GJ | 218 MW | 7.5 / 5.5 t | exhaust-free to 2 km; 7 t of water spare |

**Findings:**
- **A field climb at 1.5 W is slower off the ground than the torch.** It has to exceed 2.5 W to match the torch's exposure time.
- **Its value is the missing plume, not speed.** The torch at the surface puts MW/m² near its axis.
- **Hover is ideally almost free under M1,** because a static force does no work. Real hover cost is losses plus upkeep (unknown). The torch hovers at 1.4 t of water per minute; the fans carry 35% of weight.
- **The 14.3 m 8-couch variant closes hot extraction only under S3**, with a device of ≤ 4.5 t.
- **Environment:**
  - If the reaction is local rather than planet-wide, the footprint sees about 14 kPa. That is a 1.4 m dimple in water and a crush hazard to people underneath.
  - The torch at 200 m radiates 0.15–4.6 kW/m² to the ground, so it must be pitched away from people.
- The device ceilings above are **integration limits**, not predictions of what such a device would weigh.

## W3: a 50–100 m step
**The three boundary hypotheses:**
- **H1, the region sweeps through the air:** ordinary aerodynamics applies. 100 m in 1 s costs 3–44 MJ and is subsonic; in 0.1 s it costs 0.3–4.4 GJ and is Mach 3.
- **H2, interaction only at the departure and arrival boundaries:** ≤ 56–213 MJ per step (13–51 kg TNT equivalent), a sharp bang that scales with region volume. If the transition swaps the contents of the two volumes, the cost falls toward zero.
- **H3, needs a cleared operating volume:** in practice, vacuum only.

**Survival value:**
- A 50–100 m step completed inside the last 0.5 s defeats a 30 g interceptor's endgame. That interceptor can null only 37 m of offset in that time; an 8 g jink makes 10 m.

**Vacuum:**
- The environment term is zero.
- It supersedes canon technology limits (§18A, the ramp and path card), not invariants: a level step changes neither momentum nor energy.

**Energy ledger:**
- Field creation and recovery are unknown.
- Transition costs m·g·dz for vertical steps.
- The environment term depends on which hypothesis holds.

## Answers
1. **Smallest credible programmable-material capability:** adaptive camber/trailing structure that holds shape at 8 g, plus re-armable slam and crash absorbers, on a conventionally folded 17 m wing. Hot touchdown 43.3 m/s at 37.3 t dry. No new physics; flown morphing trailing edges are its precedent.
2. **Smallest metric effect that materially changes hot extraction:** about 1.5 × weight for about 9 s to 200 m (about 0.35 GJ source, about 70 MW peak), plus about 0.65 × weight to hover alongside the fans. This gives exhaust-free pickup and vertical landing on land, with a device budget of about 3.5 t. A brief partial pulse alongside the torch changes nothing.
3. **What must be resolved before a controlled metric displacement is plausible:** what the field boundary does to matter during a transition — carries or swaps it, pushes it aside, or fails. The same property decides whether a W2 field can start from a floating shuttle.

## Review response (2026-11-21, kT's assessment)
All four challenges are accepted.

1. **Reaction partner.** `w2_coupling.py/.json` bounds every known coupling for 0.9 MN at up to 200 m. None of them works:
   - Gravity would need about 2×10¹³ kg overhead.
   - A Lorentz force across Earth's field would need about 2×10⁹ A.
   - Electrostatic lift is capped by air breakdown at 40 Pa, against 13.4 kPa needed.
   - Inductive repulsion over seawater reaches only metres.

   So W2 is not an ordinary force. It is coherent only as an extension of the canon metric miracle (M2), which already licenses a declared nonlocal momentum partner (§7.1b). Outside M2 it would be a third miracle. Inside M2 it still needs:
   - a powered channel;
   - a generator about 4× lighter than the canon-scaled ~13 t (L²);
   - a boundary that tolerates water, air and people.

   The 0.35 GJ source figure is an *assumed* 60% efficiency, not evidence. Only the 0.18 GJ delivered to the shuttle is kinematics.
2. **Exhaust-free is not disturbance-free.** The claim is now limited to *no torch plume at the pickup*. Fan downwash, a local footprint (~14 kPa if the reaction lands locally), water displacement and boundary effects all remain. The "2 km" line is relabelled a screening assumption.
3. **Slam/crash credit withdrawn.** The reviewer is right that 25 g → 5 g needs 5× the stroke (0.05 → 0.25 m at 5 m/s). That stroke is not designed. The "rigid 25 g" baseline was also a strawman: a deadrise hull gets stroke from water penetration, and seaplane landing loads are a few g. What remains:
   - The bay envelope has 0.64 m clear below the belly, shared with the floats, where a deployable keel/step absorber could stow.
   - A 16 g crash at 15 m/s needs about 0.7 m of stroke.

   Both go to a small mechanical check before any credit is given.
4. **W3 is an advantage, not immunity.** The interceptor result assumes a head-on geometry and no reacquisition model. A level step keeps velocity and attitude, so the trajectory that follows is *offset*, not changed.

## BMD-1: Builder Metric Domain hypothesis (external review, 2026-11-21)
**Status:** label for an experiment, NOT a technology, NOT canon.

**Hypothesis:** a bounded region containing the whole shuttle, with three properties:
1. **Internal continuity:** distances, clocks and local physics stay ordinary inside the region.
2. **External coupling:** changes in the domain's motion exchange energy and momentum with an *identified* partner, so there is no reactionless propulsion.
3. **Boundary matching:** surrounding matter either crosses the boundary continuously or goes through an accounted transition.

The missing invention is a field law that makes all three compatible. Conservation bookkeeping constrains any such mechanism; it is not one.

**Ledger for the W2 200 m lift (checked):**
- **Kinematics:** 61 t at 0.5 g net for 9 s reaches 199 m at 44.1 m/s.
- **Force and energy:** the field force is 898 kN. Field work is 178 MJ, which is 119 MJ of potential energy plus 59 MJ of kinetic energy.
- **Momentum:** the field supplies an impulse of 8.1 MN·s and gravity takes 5.4 MN·s, leaving the shuttle a net 2.7 MN·s.
- **Correction:** the review's "0.40 MN·s to the partner" is wrong. The partner absorbs the full −8.1 MN·s.
  - If the partner is Earth, gravity adds +5.4 MN·s to Earth, so Earth's net is −2.7 MN·s and balances the shuttle.
  - If the partner is the Sun (CANON II §7.1b), the Sun takes −8.1 MN·s and Earth takes +5.4 MN·s.

**Canon flag:**
- External energy coupling is a powered metric channel.
- CANON II §7.1a ENERGY-B currently says metric motion conserves mechanical energy, so it pays no height.
- BMD-1 therefore supersedes a written canon *rule*, not only a technology limit. That is allowed in this non-canon lane **only with kT's explicit acknowledgment**. It is not implied.

**Boundary cases:**

| Boundary | W2 continuous lift | W3 step |
|---|---|---|
| A, impermeable, pushes matter aside | possible with a partner; at 44 m/s it is just a subsonic body in air, but cutting water at the start is the hazard | severe air disturbance likely |
| B, permeable | lifts whatever is inside: air (~1.2 t per 1,000 m³, ~2%) is acceptable and raises an updraft column; water inside lifts a slug of sea | needs an account of matter at the destination |
| C, relocates an enclosed region | gives no lift without extra dynamics | strongest W3 route; may need topology change and raises causality questions |

**Discipline:**
- **Separate boundary laws:** W2 (continuous motion) and W3 (discontinuous relocation) may share generator technology but are tested with *separate* boundary laws. One miracle must not silently solve both.
- **When a single law is allowed:** a single law covering both would be cheaper against the two-miracle budget, but it has to be found, not assumed.

**Test order:**
1. Vacuum.
2. Thin atmosphere (Mars, or high altitude).
3. Sea-level air.
4. Water contact, last.

Force generation and boundary behaviour are tested separately. If the field fails in vacuum or thin air, W2 and W3 stay parked and the conventional fold plus adaptive camber shuttle stands alone.

### kT authorization (2026-11-21)
**kT authorizes this non-canon prototype research to challenge CANON II §7.1a ENERGY-B, including powered metric motion that changes gravitational potential energy.**
- This does **not** change canon.
- It does **not** establish that M2 permits the effect.
- There is no new architecture and no hardware design.

### Three separate properties (not to be conflated)

| Property | Question | Not implied by the others |
|---|---|---|
| **Boundary permeability** | Can ambient matter cross the boundary? | A permeable boundary need not carry what it starts with. |
| **Matter entrainment** | Does matter inside move with the domain? | A comoving domain may still carry air or water even if some exchange is allowed. |
| **Momentum coupling** | Where does the change in the domain's momentum and energy go (the partner)? | Says nothing about which matter is carried. |

**Entrainment options:**
- **Whole-region entrainment:** everything inside comoves, including air (~1.2 t per 1,000 m³, ~2% extra load). It needs **no extra miracle**. The domain must form clear of water, or it lifts a slug of sea.
- **Selective entrainment:** hull and crew carried, air not. This needs the field to tell matter apart.
  - Canon §12.1 has *certified domain membership* (attachment state, lattice, configuration), but only as a certification rule, not a physical sorting law.
  - Coupling that depends on matter type breaks universality.
  - **FLAG:** unless membership is a geometric property of the field (attachment to the node lattice), selective entrainment is an **independent additional miracle**. It is not assumed.

### Vacuum-first experiment (`bmd1_vacuum_ledger.py/.json`)
**Q1. Can the enclosed region stay stable?**
- Yes, if the coupling acts *uniformly* on the domain: the interior is then in free fall, with no tidal stress across a ~15 m region.
- A non-uniform coupling loads the interior, and the crew-continuity property fails.

**Q2. Can the domain change its motion relative to an external reference?**
- Only with a partner. The partner's identity changes everything, because the coupling must deliver the work done *in the partner's rest frame*, P = F·v_rel.
- Lift case: 0.9 MN for 9 s, delivering 178 MJ in Earth's frame.

| Partner | v_rel | Energy the device handles |
|---|---|---|
| Earth, vertical lift | 0 (rotation is perpendicular) | **0.18 GJ**, 40 MW peak |
| Earth, sideways push at the equator | 465 m/s | −3.6 to +3.9 GJ |
| Moon (wrong partner, near Earth) | 1.0 km/s | ±8 GJ |
| **Sun (canon §7.1b)**, lift at dawn or dusk | 29.8 km/s | **±240 GJ, ~27 GW peak**, sign set by local time |

**Q3. Does the ledger close?**
- It closes for every partner.
- With the canon Sun partner, a shuttle-scale lift is about 1,000× more energetic than the lift itself, and its sign changes with time of day.
- A lift-at-dusk / lower-at-dawn cycle would extract Earth's orbital energy. It conserves energy, but in practice it collides with the §7.3 no-free-work firewall.

**Discriminating observable:** the device's energy draw against its velocity relative to candidate partners.

### Minimum new constitutive property
A **powered, uniform coupling between the domain and the local dominant mass**: the body whose gravity dominates locally takes the reaction, and the energy is accounted in that body's frame.

**Where it departs from canon:**
- §7.1a: powered height, now authorized for the lane.
- §7.1b: the partner is local, not the Sun. This is a *second* departure from the canon metric rule. It is **not** yet authorized; it is flagged here for kT.

### Strongest three hypotheses (W2 continuous motion only)

**1. Gravitational-coupling domain**
- *Idea:* the domain's coupling to the *local gravitational field* is controllable (F = −k·m·∇Φ, with k < 0 giving lift). The partner is automatically whatever sources the local field, so no selection rule is needed and the energy stays local (0.18 GJ). It gives no thrust in deep space, which is acceptable for a landing device.
- *Decisive unknown:* can the coefficient k belong to the field-dressed domain without breaking the equivalence principle for ordinary matter? Two further unknowns: the boundary stress at k ≈ −0.5, and whether the domain can form next to water.

**2. Local-partner nonlocal coupling**
- *Idea:* the §7.1b mechanism, but with the partner being the dominant local body instead of the Sun. It allows sideways as well as vertical motion relative to the planet.
- *Decisive unknown:* the **partner-selection law** — what picks Earth over the Sun or Moon, and what happens at a hand-over (the wrong partner costs ±GJ). It also needs a second canon departure from §7.1b.

**3. Canon Sun-partner coupling, powered**
- *Idea:* the most canon-conservative route, with no new partner rule.
- *Outcome:* the ledger closes, but the device must handle ±240 GJ and ~27 GW per lift. The cycle mines planetary orbital energy.
- *Decisive unknown:* none that rescues it at shuttle scale. **Parked.** It is recorded because it shows why the partner rule is the real discovery.

**Entrainment, for hypotheses 1 and 2:**
- Whole-region entrainment is the default; it needs no extra miracle.
- Selective entrainment is **flagged as a possible additional miracle**.

### W3 stays separate
W3 (discontinuous relocation) is not evaluated here. Hypothesis 1 or 2 only bears on W3 if one coherent field law is later shown to support both continuous motion and relocation. That is not assumed.

### kT authorization extended (2026-11-21)
**The BMD-1 lane may challenge both CANON II §7.1a (ENERGY-B) and the §7.1b Sun-partner restriction.**
- This is permission to investigate alternative constitutive laws.
- It is not a canon amendment, and not a finding that M2 supports them.

**kT's ranking:**
1. Local-partner coupling: the general hypothesis.
2. Gravitational-coupling domain: the landing-specific hypothesis.
3. Powered Sun-partner coupling: a **control**, not a development candidate.

### H1 vs H2 at Earth, Titan and deep space (`bmd1_compare.py/.json`)
- **Bound used:** Newtonian only.
- **Lift case:** 1.5 × local weight for 9 s (898 kN at Earth, 124 kN at Titan). Deep space uses a 0.15 g manoeuvre (90 kN).
- **Two ledgers, kept separate:** energy exchanged with the partner, which closes by construction, and energy the onboard device must supply, store or absorb.

**H1, local-partner coupling, with partner weights varying continuously with the gravitational environment:**

| | Weighted by raw g | Weighted by tidal field |
|---|---|---|
| Earth: partner velocity offset | 18 m/s (Sun 6e-4) | 0.8 mm/s |
| Earth: device energy, 9 s lift | +0.03 to +0.32 GJ | **+0.18 GJ** (lift work only) |
| Titan: partner velocity offset | 103 m/s (Saturn 2e-2) | 0.22 m/s |
| Titan: device energy | −0.11 to +0.12 GJ | **+0.004 GJ** |
| Deep space (Sun only) | F × 29.8 km/s: up to 2.7 GW at 90 kN | same |

- **Tidal weighting respects the equivalence principle.** A uniform external field (the Sun at Earth, Saturn at Titan) is invisible to a freely falling domain, so the partner varies continuously and **no named-planet rule is needed**.
- **Raw-g weighting is arbitrary and detectable.**

**H2, gravitational-coupling domain** (passive and active coupling k changed together, keeping Newton's third law):
- **Weight reduction (k from 1 to 0):** the shuttle can at best float. It produces **no upward force**; fans or the torch must still lift it.
- **Actual upward force:** needs k < 0, i.e. repulsion. Net 0.5 g up needs k = −0.5.
- **Switching energy:** changing k changes the interaction energy with *every* source mass, m·Δk·|Φ|:

  | Sources counted | Energy |
  |---|---|
  | Earth alone | ~4 TJ |
  | With the Sun | 58–87 TJ |
  | Including the Galaxy | 9–14 PJ |

  A Machian estimate would approach mc². The 200 m lift itself needs 0.18 GJ.
- **Equivalence-principle drift:** the domain stops sharing its host's free fall. At Δk 1.5 that is 8.9 mm/s² sunward at Earth (58 km per hour of hover) and 38 mm/s² Saturnward at Titan (17 m in 30 s).

### Minimum new constitutive property
A powered momentum-exchange law between a uniformly coupled domain and the surrounding mass distribution. Partner weights come from each body's contribution to the **local tidal field**, and force capacity scales with that field, vanishing in deep space.

**Conservation consequences:**
- **Stress-energy and momentum close with the weighted partners;** recoil is negligible.
- **The device supplies F·v_rel** when pushing along the relative velocity.
- **It must ABSORB F·v_rel** when pushing against it (descents, braking). That means storage or heat rejection, not free energy.
- **No orbital-energy mining,** because the Sun and Saturn weights are only 1e-8 to 1e-5.

### Decisive contradiction
- **H2:** yes. The switching energy m·Δk·|Φ| (TJ to PJ) must either sit on board, which is impossible, or be held outside the device. In the second case H2 has become a partner-coupling theory, i.e. H1 with extra assumptions. H2 also violates the equivalence principle observably, and its weight-reduction form gives no upward force.
- **H1:** none found at this bound. The likeliest hidden contradiction is how a **tidal-weighted** coupling, whose gradient is 3e-6 s⁻² at Earth, can deliver a **uniform**, non-tidal push on a 15 m domain.

### Verdict
**H1 is the better physical hypothesis**: local-partner coupling with tidal-field weighting and force capacity bounded by the environment.
- It needs no named-partner rule.
- It respects the equivalence principle.
- Its onboard energy is the local work (F·v_rel): tens of MW at Earth, sub-MW at Titan.

**Decisive unknowns:**
- **How force capacity scales with the tidal field.** If capacity is not bounded by the environment, H1 becomes deep-space propellantless propulsion at about 30 GW per MN of push. That is comparable to the torch, and a setting-wide change far beyond a shuttle aid.
- **The tidal-to-uniform force question** above.
- **Generator power and mass,** which no closed ledger establishes.

W3 remains separate.

### Review 2026-11-21: corrections accepted
1. **0.18 GJ at Earth.** This is the mechanical work of the idealized lift. It is **not** the generator's energy, which depends on field creation, maintenance and recovery and remains unknown.
2. **H2 is unsupported, not proven impossible.** m·Δk·|Φ| assumed a zero of potential at infinity. The revised framing:
   - A coupling change that does not conserve total gravitational charge has a reference-*dependent* energy ledger, and that dependence is itself the defect.
   - A charge-conserving H2 has to move the compensating charge somewhere. Its minimal-energy form puts it close by, which makes a **mass dipole**: case (2) below.
3. **Tidal fields are tensors.** The partner weights used scalar magnitudes. The full tensor is treated below.

### Single question: can a tidal-field-dependent coupling give a centre-of-mass force? (`bmd1_tidal_force.py/.json`)
Newtonian weak-field limit, full tidal tensor T_ij = ∂_i g_j, with y the position measured from the domain's centre of mass.

**(1) Coupling to ordinary (positive) density through position: NO.**
- Any force density linear in T acting on ρ gives T_ij·∫ρ y_j dV = 0 **exactly, for any shape**, because the first moment about the centre of mass vanishes.
- The residual is the quadrupole term, M·g·(L/R)², which comes to **3 µN** at Earth.

**(2) With a new law: YES, but only via an engineered gravitational DIPOLE moment p.**
- p is an internal vector, not position, coupled to the tidal field: F = T·p, so F/W = 2qL/(mR).
- **Scaling with environment:** at a body's surface T = (8π/3)Gρ_body, set by density and not size. Deep space has essentially zero capacity.
- **Scaling with domain size:** the pole charge needed is about 0.75·m·R/L.

| Where | Dipole needed | Pole mass equivalent at 15 m | Holding energy U = p·g = F·R/2 |
|---|---|---|---|
| Earth (0.9 MN) | 2.9e11 kg·m | 1.9e7 t (3e5 × the shuttle) | **2.9 TJ** (16,000 × the lift work) |
| Titan (124 kN) | 1.2e11 kg·m | 7.9e6 t | 0.16 TJ |
| Moon | 8e10 kg·m | 5.3e6 t | 0.13 TJ |
| 1 km asteroid | 2.3e7 kg·m | 1,500 t (25 × the shuttle) | ~6 kJ |
| Deep space, 1 AU | 1.1e18 kg·m | ~1e14 t | n/a |

- **U is reference-independent,** because the dipole's net charge is zero.
- **It is stored and recoverable, but it has to be held somewhere.**

**(3) Conservation.**
- Local stress-energy and Newton's third law close only if the dipole is also an **active** source, so that its field pulls on the planet.
- That requires negative active mass at one pole: **exotic stress-energy of about 1e7 t per pole at Earth.** This is the class of thing M2 declares, but now at a stated amount.

### Result
- **The tidal field can act as a partner SELECTOR,** setting the weights. It **cannot be the force SOURCE** at planetary scale.
- If BMD-1 keeps tidal weighting, the 0.9 MN must come from a **separately postulated** nonlocal exchange. That is a chosen fictional law, not a derivation from established physics, and the lane must say so.
- **Minimum additional Builder property, if the tidal route is wanted as the source:** an engineered gravitational dipole of about 0.75·m·R per unit length. It is cheap only near small bodies.
- **The shuttle-scale answer** is therefore an explicit postulate: a powered nonlocal momentum exchange, with partner weights from the tidal tensor and capacity bounded by the environment.
- **No further shuttle geometry or hardware** is built around BMD-1 until that postulate is accepted or refined. W3 remains separate.

## kT decision: BMD-1 PARKED (2026-11-21)
BMD-1 is parked as a **successful negative research result**. It is kept as a documented Builder hypothesis.

**What was learned:**
- Ordinary tidal coupling cannot give the 0.9 MN lift.
- The tested gravitational-dipole mechanism is impractical at planetary scale.
- A useful powered local-partner field would need an additional, explicitly fictional constitutive law, and conservation bookkeeping alone cannot justify one.

**Status of that law:** **not authorized** as LOOM physics now, and **not discarded** permanently.

**Qualifications kT recorded:**
- The zero-force result is exact for couplings linear in the tidal tensor acting on positive density about the centre of mass, within the weak-field approximation. It is not a theorem for every possible tidal-dependent interaction.
- U = F·R/2 is an interaction-energy scale, recoverable rather than automatically an operating cost. The dipole is only the one new interaction tested here.
- Nothing here shows that a negative-mass pair could be built or stabilized.

**Next:**
- Return to the conventional shuttle. Conventional fold + adaptive camber is the leading architecture.
- W3 stays an independent speculative question.

## Hypothesis A: metric-gradient assistance (kT, 2026-11-21) (`bmd1_metric_gradient.py/.json`)
**Idea:** engineer the shuttle's geodesic rather than push on it. The interior stays in free fall.

**kT's test:** derive the metric, derive the stress-energy it requires, and see whether the numbers close.

**Static route (comoving potential bump):**
- The minimal source for a uniform 1.5 g interior field over R = 10 m is a cos θ shell, a gravitational "polarised sphere".
- That needs **1.7e13 kg per pole** (3e8 × the shuttle), and one pole must be **negative** mass.
- A ± mass pair self-accelerates (Bondi). It looks reactionless and works anywhere, so there is **no planetary limit**.

**Dynamic route (warp-type shift bubble):**
- Alcubierre-class energy at 44 m/s, R 10 m, wall 1 m is about **−2e31 J (~2e14 kg)** of exotic energy, and that only *moves* the bubble.
- Positive-energy subluminal shells (Fuchs et al. 2024) need very large ADM mass.
- Bobrick & Martire (2021): an accelerating warp metric must obey 4-momentum conservation, and "any warp drive requires propulsion". **A partner is still required.**

**GR verdict: the numbers do not close.** Steering the path instead of the force changes the description, not the bookkeeping.

**Canon:**
- M2 already waives GR stress-energy pricing for Wayfarer (0.268c from a ~2 GJ bank).
- A closes **only if that waiver is extended** to small, near-body, powered domains. That is a canon-policy choice, not physics.

**The form A takes if the waiver is extended: "gravity steering"** (postulate, not derivation)
- **Law:** the domain imposes on its free-falling interior a uniform acceleration of up to k·g_P (k ≈ 1.5).
  - g_P is the Newtonian field of the partner P, the body whose Hill sphere contains the domain.
  - The reaction momentum goes to P.
  - The onboard energy is F·v_rel(P).
- **Natural planetary limit:**

  | Location | Capacity |
  |---|---|
  | Earth | 1.5 × weight (898 kN) |
  | Mars | 0.57 g |
  | Moon | 0.25 g |
  | Titan | 0.21 g |
  | Deep space, 1 AU | 0.0009 g (0.5 kN) |

  This means no revolution in remass.
- **Hovering and slow lifts near a body are nearly free** (v_rel ≈ 0). Fast velocity changes are expensive: about 6 GW at full force in LEO. This is the inverse of a rocket.
- **Caveats:**
  - g_P is not a local observable (equivalence principle), so the law is **nonlocal by construction**, like canon §7.1b.
  - Stress-energy is **not derived**; it relies on the M2 waiver.
  - Boundary versus water and air is still open.

**Other branches:**
- **B (path shortening)** belongs with W3.
- **C (isolation + fans)** is dropped: isolation removes drag, not weight.
