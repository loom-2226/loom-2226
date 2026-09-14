# E1 Neptune Plasma / EM Source Qualification v0.1

Classification: ENGINEERING / SOURCE QUALIFICATION / NON-CANON / NO RUNTIME POLICY

## Result

Voyager 2 Neptune encounter plasma, magnetic-field, plasma-wave, and energetic-particle data exist as machine-readable NASA PDS products.

This is materially stronger source availability than the neutral-atmosphere profile lane. It does **not** establish a local 2226 endpoint environment.

`HISTORICAL_MACHINE_READABLE_DATA != LOCAL_2226_ENDPOINT_STATE`

## Qualified source families

- **PLS** — NASA PDS Voyager 2 PLS Neptune Encounter Data Bundle, `urn:nasa:pds:vg2-pls-nep::1.0`, DOI 10.17189/2qxe-9f25. Derived ion density, temperature and velocity across solar-wind, magnetosheath and magnetosphere intervals, plus electron products. Encounter coverage 1989-08-24 through 1989-08-30.
- **MAG** — NASA PDS Voyager 2 Magnetometer Neptune Encounter Data Bundle, `urn:nasa:pds:vg2-mag-nep::1.0`, DOI 10.17189/cv12-7d61. Magnetic-field data in Heliographic and Neptune Longitude System coordinates at multiple resampled rates. Encounter coverage 1989-08-22 through 1989-08-30.
- **PWS** — NASA PDS Neptune encounter plasma-wave spectrum-analyzer products, including 4-second edited electric-field spectral intensity data over the encounter period.
- **LECP** — NASA PDS Voyager 2 Neptune low-energy charged-particle encounter products with counting-rate / flux measurements.

## Example reproducible PLS product

PDS collection `urn:nasa:pds:vg2-pls-nep:data-pro-magsphere::1.0` contains 48-second derived magnetospheric proton density, temperature and velocity data for 1989-08-25T04:10:00Z through 1989-08-25T05:08:00Z.

This establishes that at least part of the plasma lane is not merely a published qualitative claim: reduced, derived, machine-readable encounter data are archived.

## Boundary

All of these products remain bound to Voyager 2's spacecraft trajectory, instrument response, coordinate frame, processing level, and the 1989 encounter epoch.

This qualification does not authorize:

- temporal propagation to 2226;
- spatial interpolation away from the sampled trajectory;
- transformation into a local endpoint value without a separately qualified geometry/frame adapter;
- treating plasma-wave spectral intensity as a generic electric-field vector;
- converting energetic-particle flux directly to ionizing dose rate without a response/shielding model;
- Geometric Admissibility scoring;
- Loom coherence inference;
- metric-collapse policy;
- Navigator/runtime/campaign mutation.

## Engineering next step

Adapt one PDS family at a time behind the existing `PlanetaryEnvironmentState` interface. Start with a narrowly defined machine-readable source whose semantics already align with an interface field. The best first candidate is either:

1. MAG magnetic-field vector samples with explicit epoch, spacecraft position and source coordinate frame; or
2. PLS plasma number-density/moments with the same explicit trajectory binding.

Do not build a synthetic 2226 magnetosphere first. Earn the historical adapters, coordinate semantics, and uncertainty/provenance chain before any evolution model.
