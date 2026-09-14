# E1 Neptune J2-Corrected Local Tidal Reference v0.1

## Purpose

Carry forward the material Neptune `J2` correction established by the preceding rotation/multipole materiality qualification, while preserving the already-earned E1 collapse endpoint and all remaining epistemic limits.

This is a bounded local-geometry reference qualification. It does not define Geometric Admissibility, an exclusion radius, a physical collapse boundary, a drive-coupling rule, runtime policy, or campaign-state mutation.

## Preserved endpoint

- body: `NEPTUNE`
- collapse radius: **26,085.768742 km**
- collapse epoch: `2226-08-22T09:07:59.475571Z`
- arrival epoch: `2226-08-22T09:45:17.864616Z`
- endpoint status: `EARNED_OPERATIONAL_HANDOFF_NOT_FUNDAMENTAL_BOUNDARY`

The endpoint is not moved or re-solved.

## Why the result is an envelope

The preceding qualification established that measured Neptune `J2` is material at the declared 1% local-geometry model resolution, while `J4` and the conservative frame-dragging screen are not material at this stage.

However, endpoint planetographic latitude/orientation remains unresolved. Therefore a single J2-corrected tidal tensor would invent information we have not earned.

The qualified object is instead a full-colatitude orientation envelope at the fixed endpoint radius. The sweep uses 721 samples from 0 to 180 degrees and preserves the axisymmetric weak-field monopole-plus-J2 model.

## Inputs

- Neptune GM: **6,836,529.0 km^3/s^2** from the already-qualified LOOM celestial-data lineage;
- LOOM mean radius for altitude reporting: **24,622.0 km**;
- gravity-field reference radius: **25,225.0 km**;
- `J2 = 0.00340913806941493`;
- `sigma(J2) = 2.9e-6`.

The 25,225 km gravity-field reference radius is not substituted for the LOOM mean radius.

## Nominal J2-corrected tidal envelope

The spherical-monopole tidal Frobenius norm at the earned endpoint is:

- **9.434097626759738e-07 s^-2**.

Across unresolved colatitude, the monopole-plus-J2 total tidal norm spans:

- minimum: **9.253649957398604e-07 s^-2**;
- maximum: **9.524357073448463e-07 s^-2**.

Relative to the monopole norm, the total norm therefore changes by approximately:

- minimum: **-1.9127178507%**;
- maximum: **+0.9567364072%**.

This asymmetry is expected: the already-qualified J2 correction norm itself is always positive, but the correction tensor can partially oppose or reinforce monopole components depending on orientation.

The principal tidal-eigenvalue envelope is:

- most negative: **[-3.906704817595004e-07, -3.7777867756589795e-07] s^-2**;
- middle: **[-3.8698710913275684e-07, -3.7777867756589795e-07] s^-2**;
- most positive: **[7.555573551317959e-07, 7.776575908922572e-07] s^-2**.

The reconstructed monopole-plus-J2 tidal tensor remains trace-free to numerical precision, providing an internal convention/sign check for the vacuum weak-field reference.

## Published source uncertainty

The published `J2` ±1 sigma interval is propagated through a full orientation sweep for each bound. This uncertainty does not collapse the unresolved orientation into a single endpoint value.

The scope is explicitly:

`PUBLISHED_J2_1SIGMA_ONLY_NOT_2226_MODEL_EVOLUTION`

Evolution of Neptune's gravity field between the source epoch and 2226 remains unresolved and is not silently treated as zero.

## Qualified claim

`J2_CORRECTED_LOCAL_TIDAL_REFERENCE_QUALIFIED_ORIENTATION_REMAINS_UNRESOLVED`

This supersedes the spherical-monopole-only tidal reference for the next local-geometry reasoning step, but only as a bounded orientation envelope.

## Preserved unresolved quantities

- unmeasured `J6` and higher zonal harmonics;
- endpoint planetographic latitude and orientation;
- Neptune gravity-field evolution to 2226;
- full rotating-Neptune spacetime;
- local stress-energy / matter density;
- EM-to-metric coupling;
- causal structure from an eventual qualified spacetime model;
- domain-size binding to admissibility;
- Loom coherence;
- lattice coherence.

No unresolved quantity is silently set to zero.

## Authority boundary

This step creates:

- no admissibility score;
- no admissibility threshold;
- no exclusion radius;
- no Hill/SOI policy;
- no metric-drive coupling rule;
- no runtime-policy mutation;
- no campaign-state mutation;
- no LLM calculation/state/execution authority.

## Next bounded step

`ASSESS_LOCAL_STRESS_ENERGY_MATTER_DENSITY_RELEVANCE_BEFORE_COMPOUND_GEOMETRIC_ADMISSIBILITY`

The next question is whether local matter/stress-energy at the earned Neptune endpoint is material to the local spacetime description before any compound Geometric Admissibility decision is attempted.
