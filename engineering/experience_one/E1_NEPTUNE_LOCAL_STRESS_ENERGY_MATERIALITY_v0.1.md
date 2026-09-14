# E1 Neptune Local Stress-Energy Materiality v0.1

Status: ENGINEERING QUALIFICATION CANDIDATE  
Class: ENGINEERING  
Authority: NO RUNTIME / CAMPAIGN / ADMISSIBILITY POLICY AUTHORITY

## Purpose

Assess whether local ordinary-matter, plasma, and electromagnetic stress-energy near the already-earned Neptune collapse endpoint is large enough, under standard general relativity, to materially change the local spacetime description before Compound Geometric Admissibility is formulated.

This work does **not** move the endpoint, resolve endpoint latitude/orientation, define a GA threshold, create an exclusion radius, or assume any LOOM-specific electromagnetic-to-metric coupling.

## Fixed earned inputs

- Body: Neptune
- Earned collapse radius: `26085.768742 km`
- Qualified J2-corrected tidal Frobenius envelope lower edge: `9.253496458704657e-07 s^-2`
- Engineering materiality resolution: `1%`

The lower edge of the already-qualified J2 envelope is used as the conservative comparison scale.

## Standard-GR comparison

For an equivalent local mass density `rho`, the Einstein-equation source-curvature scale is screened as:

`8*pi*G*rho/c^2`

The qualified tidal geometric scale is screened as:

`lambda/c^2`

so the dimensionless comparison ratio is:

`8*pi*G*rho/lambda`.

This is an engineering order-of-magnitude materiality screen, not a full Einstein-Maxwell solution and not a detailed atmospheric or magnetospheric model.

## Present-day observational scale proxies

### Upper atmosphere

Melin et al. (2018), summarizing Voyager-era Neptune ionosphere/thermosphere results including Lyons (1995) and Broadfoot et al. (1989), reports a modeled H3+ peak around `1400 km` above the 1-bar level at about `1.1 nbar`, with upper-atmospheric temperature around `550 K`; an exospheric temperature around `750 K` is also discussed.

Reference: https://academic.oup.com/mnras/article/474/3/3714/4655202

For a simple H2 scale proxy at `1.1 nbar` and `550 K`:

- number density: about `1.4486e16 m^-3`
- mass density: about `4.8486e-11 kg/m^3`
- standard-GR Ricci-to-qualified-tidal materiality ratio: `< 1e-12`

This is a present-day scale proxy, **not** a claim that the 2226 atmosphere is known.

### Magnetic field

Voyager 2 magnetic-field modeling by Connerney, Acuña, and Ness (1991) gives a Neptune dipole magnitude of about `0.14 G R_N^3`, with a strongly tilted, multipolar field; quadrupole terms are comparable to or larger than the surface dipole field and higher-order structure is important close to the planet.

References:
- https://ntrs.nasa.gov/citations/19920029286
- https://agupubs.onlinelibrary.wiley.com/doi/10.1029/91JA01165

`0.14 G` is therefore used here only as a planetary magnetic-field **scale proxy**, not as a resolved field magnitude at the E1 endpoint.

Its magnetic energy density is far below the 1% materiality requirement under ordinary GR.

### Plasma

Voyager 2 particles-and-fields summaries report generally low plasma densities near Neptune, around `5e-3 cm^-3`, rising to about `1 cm^-3` at magnetic-equatorial crossings.

Reference: https://ntrs.nasa.gov/citations/19920062659

The qualification uses the larger `1 cm^-3` density and an intentionally conservative `100 keV` per-particle energy as an engineering stress-test scale. The `100 keV` value is **not** asserted to be the characteristic local plasma temperature.

The resulting standard-GR source-curvature scale remains far below 1% of the qualified Neptune tidal scale.

## What would 1% materiality require?

At the conservative low end of the qualified J2-corrected tidal envelope, standard-GR local source curvature would need approximately:

- equivalent mass density: `5.516457539690285 kg/m^3`
- equivalent energy density: `4.957944782078408e17 J/m^3`
- H2 pressure at `550 K`: `1.2515137281341452e7 Pa` ≈ `125.15 bar`
- magnetic field: `1.116273905608525e6 T`

These are source-strength equivalences for the 1% engineering screen, not predicted physical conditions.

## Decision

`LOCAL_STRESS_ENERGY_NOT_MATERIAL_AT_ONE_PERCENT_STANDARD_GR_SCREEN_PRESERVE_2226_ENVIRONMENT_UNCERTAINTY`

Present-day Neptune atmosphere, magnetic-field, and plasma scales are many orders of magnitude below what would be required for ordinary local stress-energy to perturb the qualified tidal geometry at the 1% engineering resolution.

This does **not** erase uncertainty about Neptune in 2226. The 2226 atmosphere and magnetosphere remain unresolved. It means only that ordinary-GR local stress-energy would have to change by enormous factors before it became material at the current engineering resolution.

## Preserved unresolved

- 2226 local atmospheric state
- 2226 local magnetospheric state
- endpoint planetographic latitude and orientation
- endpoint magnetic-field vector
- unmeasured J6 and higher zonal harmonics
- full rotating Neptune spacetime
- EM-to-metric coupling beyond standard GR
- causal structure from an eventual qualified spacetime
- domain-size binding to admissibility
- LOOM coherence
- lattice coherence

## Authority boundary

- admissibility threshold: NOT DEFINED
- runtime policy mutation: ZERO
- campaign state mutation: ZERO
- LLM calculation authority: ZERO
- endpoint movement: ZERO
- LOOM-specific EM coupling assumption: ZERO

## Qualified next step if Pixel qualification passes

`ASSESS_COMPOUND_GEOMETRIC_ADMISSIBILITY_MODEL_FORM_WITHOUT_BINDING_RUNTIME_POLICY`
