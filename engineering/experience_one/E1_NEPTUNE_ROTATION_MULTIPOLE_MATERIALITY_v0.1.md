# E1 Neptune Rotation + Multipole Materiality v0.1

## Purpose

Answer the next bounded Geometric Admissibility precursor question at the already-earned Neptune collapse endpoint:

**Are Neptune rotation or measured nonspherical gravity corrections large enough to change the local-geometry description we need before compound Geometric Admissibility work proceeds?**

This is a materiality screen only. It does not define a Geometric Admissibility threshold, exclusion radius, score, drive-coupling law, runtime policy, or campaign-state mutation.

## Preserved endpoint

- body: `NEPTUNE`
- earned collapse radius: **26,085.768742 km**
- endpoint status: `EARNED_OPERATIONAL_HANDOFF_NOT_FUNDAMENTAL_BOUNDARY`

The endpoint is not moved or re-solved.

## Tests-first decision rule

Before implementation, the branch preregistered a **1% fractional tidal-tensor Frobenius change** as the engineering resolution for deciding whether an additional local-geometry term is worth carrying at this stage.

This 1% value is only a model-resolution rule for this bounded engineering experiment. It is explicitly **not** an admissibility threshold or physical boundary.

Because no Neptune endpoint latitude/orientation has been qualified, the experiment sweeps the full colatitude range from 0 to 180 degrees rather than inventing a location.

## External physical inputs

Measured gravity-field inputs use the Brozovic et al. (2020) / Jacobson lineage as tabulated by Yuan et al. (2021, A&A 654, A66):

- gravity-field reference radius: **25,225 km**;
- `J2 = 3409.138069414930 × 10^-6`;
- `sigma(J2) = 2.9 × 10^-6`;
- `J4 = -33.39891759006578 × 10^-6`;
- `sigma(J4) = 2.9 × 10^-6`;
- Neptune specific angular momentum estimate: **15,903.13513325206 km^2/s**;
- quoted specific-angular-momentum uncertainty used here: **637 km^2/s**.

The 25,225 km gravity-field reference radius is deliberately not confused with LOOM's versioned 24,622 km mean radius used for altitude reporting.

The broader literature also preserves an important epistemic limit: Neptune's measured zonal harmonics are well constrained only through `J4` at this level. Unmeasured `J6+` terms are therefore preserved as unresolved rather than silently set to zero.

## Measured zonal-harmonic result

At the earned radius, full-colatitude sweep gives:

### J2 only

- minimum fractional tidal-tensor correction: **0.009739084350642547** (~0.974%);
- maximum fractional tidal-tensor correction: **0.019127178507173274** (~1.913%);
- maximum occurs at the pole in the axisymmetric reference;
- classification: **MATERIAL at the declared 1% local-geometry resolution**.

The published `J2` 1-sigma range leaves the maximum correction between approximately **0.0191109 and 0.0191434**, so the materiality classification is stable.

### J4 only

- minimum fractional tidal-tensor correction: **0.0001743775605610168** (~0.017%);
- maximum fractional tidal-tensor correction: **0.00043806019448307205** (~0.044%);
- classification: **NOT MATERIAL at the declared 1% local-geometry resolution**.

The published `J4` 1-sigma range does not approach the 1% engineering-resolution line, so this classification is also stable.

## Rotation / frame-dragging screen

The specific-angular-momentum estimate gives a dimensionless spin-length ratio

`a/r = (J/Mc)/r = 2.0335666293768016e-06`.

To avoid false precision, the experiment does not claim a Kerr fit or full rotating-Neptune spacetime. Instead it multiplies `a/r` by a deliberately conservative factor of 10 to screen order-unity angular factors.

Result:

- conservative frame-dragging curvature-scale fraction: **2.0335666293768017e-05** (~0.0020%);
- 1-sigma screened range: approximately **1.95e-05 to 2.12e-05**;
- classification: **NOT MATERIAL at the declared 1% local-geometry resolution**.

This establishes only materiality at the current engineering resolution. It does not qualify a complete rotating spacetime model.

## Decision

`J2_MATERIAL_INCLUDE_BOUNDED_CORRECTION_FRAME_DRAGGING_AND_J4_NOT_MATERIAL_AT_THIS_STAGE`

The spherical-monopole reference is therefore not sufficient by itself for the next local-geometry handoff at the chosen engineering resolution.

The next bounded step is:

`QUALIFY_J2_CORRECTED_LOCAL_TIDAL_REFERENCE_WITHOUT_MOVING_EARNED_ENDPOINT`

Only the material `J2` correction should be carried forward now. `J4` and frame dragging remain documented source terms but do not need to be promoted into the active local-geometry description at this stage.

## Preserved unresolved quantities

- unmeasured `J6` and higher zonal harmonics;
- endpoint planetographic latitude/orientation;
- evolution of Neptune's gravity field to 2226;
- full rotating-Neptune spacetime;
- local stress-energy / matter density;
- EM-to-metric coupling;
- causal structure from an eventual qualified spacetime model;
- domain-size binding to admissibility;
- Loom coherence;
- lattice coherence.

None is silently treated as zero.

## Authority boundary

This step defines:

- no admissibility score;
- no admissibility threshold;
- no exclusion radius;
- no Hill/SOI policy;
- no metric-drive coupling rule;
- no runtime-policy mutation;
- no campaign-state mutation;
- no LLM calculation/state/execution authority.
