[Reading 32 lines from start (total: 32 lines, 0 remaining)]

# Semantics
## Scientific side
body/body_identifier: stable LOOM identity and external authority crosswalk.
source/source_artifact: bibliographic authority separated from acquired bytes. REMOTE_REFERENCE_ONLY deliberately has no fake hash.
ephemeris_source/coverage: metadata only; no duplicated state-vector time series.
region: named spatial support hierarchy.
spatial_product: map/model/raster/product metadata with resolution/depth support.
observation: measurement event/support.
sample: physical returned or collected material with collection relationship.
scientific_assertion: typed empirical/model/derived claim. admission_status is independent of ontology.
material_evidence: composition/resource-relevant evidence. Detection and abundance are separate.
coverage: explicit supported/unknown/source-gap states.
reconciliation/supersession/knowledge_event: disagreement and history.

## Scope law
BODY does not imply local uniformity. REGION, FOOTPRINT and LOCAL_SITE do not extrapolate upward. SAMPLE is always SAMPLE_ONLY unless an explicit later relationship supports extrapolation. MODEL_DOMAIN is not observation.

## Epistemic law
REAL_EVIDENCE = observation/measurement/detection as supported by source.
MODEL_INFERENCE = interpretation constrained by observations.
DERIVED = computed from explicit inputs.
REALIZED_OBSERVATION = future slot for observations generated/realized from an empirical context; not hidden truth.
SCENARIO and HIDDEN_WORLD are structurally excluded from scientific_assertion.

## Hidden WORLD
generation_model and generation_policy define how uncertainty may later be resolved. world_realization binds a model/seed to a body. hidden_world_state stores fictional realization values. project_site and deposit exist only beneath a world realization. They currently contain zero rows.

## Non-implication rules
Detection != abundance. Abundance != accessible stock. Accessible stock != recoverable resource. Recoverable resource != reserve. Unknown != zero. Nondetection at finite sensitivity != absence.

## Admission
All newly researched ChatGPT rows are CANDIDATE. Existing LOOM candidate rows remain candidate. No preferred scientific fact is manufactured by this lab.

[executed on device: quantifactus (0a7cbeb3-2e9a-42f9-9eb3-6b06217d0074)]

## Atmospheric vertical-coordinate extension (Mercury/Venus expansion)
Scientific vertical support is now explicit and typed: ALTITUDE, DEPTH_BELOW_SURFACE, PRESSURE_LEVEL or NONE, with min/max, unit and datum. This prevents Venus atmospheric altitude from being mislabeled as subsurface depth. The fields are nullable, so original six-body semantics are unchanged. A future profile may be represented as multiple bounded assertions/observations or an external spatial/model product; this lab deliberately does not become a climate time-series database.

## Temporal support (Vesta / outer planets / Pluto expansion)
observation_time_start / observation_time_end and assertion valid_time_start / valid_time_end provide general interval support. They bound when evidence was acquired or empirically applicable; they do not assert that the underlying physical state began or ended at those timestamps. Single-epoch evidence may use equal start/end. Vertical and temporal support are orthogonal.

ATMOSPHERIC_DOMAIN, INTERIOR_DOMAIN, and ASSOCIATED_STRUCTURE are region types, not new ontologies. Atmospheres may use ALTITUDE or PRESSURE_LEVEL vertical coordinates. Interior-domain observations and assertions remain MODEL_INFERENCE where structure is inferred from gravity/seismology/equations of state. Ring regions belong to the parent body relational context but are not atmosphere, interior, or body material inventory.

## Returned-sample collection time
sample.collection_time_start and sample.collection_time_end preserve the collection epoch independently of return-to-Earth or laboratory-analysis dates. Sample linkage establishes provenance, not body representativeness. SAMPLE assertions require sample_id and normally SAMPLE_ONLY representativeness.

## Galilean ocean/interior epistemics
A magnetic, gravity, geologic, tidal or thermal observation is not an observed interior layer. Conductive-layer, ocean, ice-shell, magma-layer, differentiation and high-pressure-ice structures are MODEL_INFERENCE unless a specific source supports a stronger epistemic class. Intrinsic magnetic field and induced magnetic response are separate properties. Transient activity requires observation linkage and temporal support.

## Saturnian icy moons and Titan
Plume composition is evidence about sampled plume/ice-grain material, not direct bulk-ocean abundance. Ocean, ice-shell, hydrothermal, differentiation and tidal-heating structures remain MODEL_INFERENCE unless separately justified. Dense-atmosphere evidence uses the same generic vertical coordinates (ALTITUDE or PRESSURE_LEVEL), spatial scopes and valid-time support used elsewhere; Titan does not introduce a separate atmospheric ontology. Surface liquids are spatial features/evidence, never resource or reserve records.

## Sparse outer-system coverage and circumbinary dynamics
An imaged encounter footprint is not whole-body geology. Sparse targets may terminate at BODY or FOOTPRINT constraints with explicit UNKNOWN at deeper semantic levels. Circumbinary orbit assertions identify the dynamical architecture; numerical propagation remains governed by JPL/NAIF rather than hand-built two-body database ephemerides. Ancient-ocean, capture and cryovolcanic histories remain MODEL_INFERENCE unless independently observed.
