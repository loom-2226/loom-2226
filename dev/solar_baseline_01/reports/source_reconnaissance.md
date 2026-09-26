# SOLAR-BASELINE-01 Source Reconnaissance

## Sources selected and actual use

- **JPL Solar System Dynamics SBDB API**: exact NAIF/SPK-keyed object responses, 55 acquired JSON artifacts from 56 requests; physical-parameter arrays, alternate designations, object IDs and cited reference strings were used. The exact-object API documents identifier lookup and `phys-par`; this was selected over a changing bulk/query result because the task is bounded to existing LOOM identities. API signature documentation/acquisition discrepancy is preserved: first acquisition expected 1.0 and rejected responses, live payloads declared 1.3. Frozen successful responses were validated as 1.3. Pluto SPK 999 was rejected HTTP 400, and Bennu’s extended NAIF ID was reconciled only using NAIF’s documented legacy/extended numbered-asteroid rule and exact returned ID. Orbit-state payload is retained raw but not transformed into Solar Facts.
- **JPL SSD planetary physical-parameter reference page**: HTML snapshot, canonical name plus body-class crosswalk for planets/dwarf planets only; source sections, reported units, references, and footnotes preserved. The page is mutable, so the acquired file hash is the release identity for this replay.
- **JPL SSD satellite physical-parameter reference page**: HTML snapshot; numeric NAIF code crosswalk; GM, radius, density and source reference columns parsed without unit invention.
- **NAIF generic PCK `pck00011_n0066.tpc` and GM DE440 text kernel**: frozen kernel files; body-coded coefficients parsed with original expressions. PCK orientation and prime-meridian coefficients remain physical models, not observations. GM values are kept as separate reference/dynamical quantities. Kernel text metadata and IDs retained.
- **NAIF ID Required Reading**: frozen documentation used to interpret ID/barycenter semantics and the documented numbered-asteroid extended/legacy alias relationship. Four systems named as barycenters but represented in LOOM as primaries are held, never guessed.
- **Identity authority snapshot**: read-only `loom_solar.body` and active identifier reference from current main-backed `loom_dev`; used solely as a crosswalk target and copied into candidate reference tables with source snapshot hash.
- **SBDB API/query docs and field/count metadata**: retained to bind the adapter to actual endpoint behavior and document why the mutable query API was not used for acquisition. JPL documents warn query pagination can drift as the catalog changes; exact object IDs avoid broad imports and page-boundary drift.

## Not selected

Horizons was examined as time-dependent ephemeris/state authority, not ingested: that domain belongs to Phase-4 and would duplicate state vectors. SBDB query/bulk interfaces were not used to download large body populations. PDS, WGCCRE, USGS Gazetteer and Hubble/mission corpora were not added because they would expand the empirical scope beyond the inexpensive general physical-parameter floor in this mission; they are reasonable targeted-enrichment candidates if future coverage needs them.

## Limits and provenance

The candidate preserves the acquired source artifact SHA-256, byte count, product/authority, URL, capture timestamp, version/signature when exposed, and parser-derived source lineage. SBDB cited reference codes were preserved but not all underlying papers were separately acquired; JPL compiled values are not mislabeled as direct observation. NAIF kernel physical-model status is retained. No explicit product-level redistribution license was found inside selected artifact files; NASA’s general data-use policy has third-party material caveats, so this remains a nonblocking licensing/provenance lien. Acquisition required network access once; replay uses only frozen files.

## Primary documentation

- [JPL SBDB API](https://ssd-api.jpl.nasa.gov/doc/sbdb.html)
- [JPL SBDB Query API](https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html)
- [JPL SBDB filters](https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html)
- [JPL planetary physical parameters](https://ssd.jpl.nasa.gov/planets/phys_par.html)
- [JPL satellite physical parameters](https://ssd.jpl.nasa.gov/sats/phys_par/)
- [NAIF ID Required Reading](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html)
- [NAIF generic kernels](https://naif.jpl.nasa.gov/naif/data_generic.html)
- [NAIF PCK Required Reading](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/pck.html)
- [NASA data-use policy](https://www.earthdata.nasa.gov/engage/open-data-services-software/data-use-policy)
