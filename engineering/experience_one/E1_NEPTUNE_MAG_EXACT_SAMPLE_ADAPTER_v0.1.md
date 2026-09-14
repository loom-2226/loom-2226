# E1 Neptune MAG Exact-Sample Adapter v0.1

## Purpose

Adapt one source-qualified historical Voyager 2 Neptune MAG sample into the existing ordinary planetary-environment interface without creating a magnetic-field model or 2226 endpoint state.

## Source basis

NASA PDS identifies the Voyager 2 Magnetometer Neptune Encounter Data Bundle as `urn:nasa:pds:vg2-mag-nep::1.0`, DOI `10.17189/cv12-7d61`. The bundle contains Neptune-encounter MAG data in Heliographic and Neptune Longitude System coordinates at multiple resampled rates and covers the 1989 encounter.

The Neptune Longitude System source convention defines magnetic-field components as radial R along the Neptune-spacecraft line (positive away from Neptune), east-longitudinal Phi, and colatitudinal Theta. Source position is trajectory-bound.

## Adapter semantics

`HistoricalMagneticFieldSample` carries:
- body;
- exact epoch;
- explicit source frame;
- exact source position;
- magnetic-field vector in nT;
- source identifier;
- source cadence;
- coordinate semantics.

`NeptuneMagExactSampleProvider` emits a `PlanetaryEnvironmentState` only if query body, epoch, frame, and position exactly match the source sample. Magnetic-field components are converted from nT to T.

Any mismatch fails closed.

## Qualification fixture

The qualification/test fixture is explicitly synthetic and identified as `QUALIFICATION_FIXTURE_NOT_PDS_OBSERVATION`. Its numeric values exist only to verify vector conversion and fail-closed behavior. They are not Voyager measurements and may not be treated as historical Neptune observations.

## Epistemic boundary

`PDS_SOURCE_FAMILY_QUALIFIED != PDS_RECORD_INGESTED`

`EXACT_HISTORICAL_SAMPLE != SPATIAL_FIELD_MODEL != TEMPORAL_EVOLUTION_MODEL != LOCAL_2226_ENDPOINT_STATE`

This PR does not ingest a real PDS MAG row. It earns only the adapter contract required to expose a future ingested row without interpolation or hidden frame conversion.

## Authority boundary

- historical exact-sample adapter only;
- no implicit frame transform;
- no spatial interpolation;
- no temporal extrapolation;
- no source numeric uncertainty until separately ingested;
- no 2226 propagation or endpoint authority;
- no Geometric Admissibility authority;
- no Loom-coherence authority;
- no runtime, campaign, or metric-policy mutation;
- no canon promotion;
- no LLM numerical/state authority.

## Next admissible work

Ingest one real machine-readable PDS MAG ASCII collection with an explicit parser, source position/trajectory data, source frame, cadence, provenance, and uncertainty/quality semantics. Only then expose a real historical magnetic-field sample through this adapter.
