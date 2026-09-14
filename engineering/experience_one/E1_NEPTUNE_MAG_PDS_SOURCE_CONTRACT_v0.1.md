# E1 Neptune MAG PDS Source Contract v0.1

## Purpose
Freeze the first real-data source pairing before parser implementation.

Selected MAG collection: `urn:nasa:pds:vg2-mag-nep:data-nls-12s-asc::1.0`, DOI `10.17189/e467-dz93`, ASCII, Neptune Longitude System, 12-second cadence, coverage `1989-08-24T18:00:00.557Z` through `1989-08-26T08:19:48.379Z`.

Required trajectory companion: Voyager 2 Neptune West Longitude System Coordinates 12s Trajectory Data Collection, providing spacecraft position relative to Neptune.

## Pairing rule
`MAG_SAMPLE + EXACT_SAME_EPOCH_SOURCE_TRAJECTORY_POSITION`

No interpolation. No implicit frame transform. A missing exact trajectory epoch fails closed and the MAG row is not exposed through the historical exact-sample adapter.

## Current authority
Parser implemented: NO. Real record ingested: NO. Frame-transform, interpolation, 2226 endpoint, Geometric Admissibility, and Loom-coherence authority: ZERO.

## Next step
Acquire the PDS4 collection/product labels and ASCII data members, validate record layout and source metadata, then implement a parser from the labels rather than guessed column positions.
