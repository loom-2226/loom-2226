# E1 Neptune MAG PDS Source Contract v0.1

## Purpose

Freeze the first real-data source pairing before parser implementation.

Selected magnetic-field collection:
- `urn:nasa:pds:vg2-mag-nep:data-nls-12s-asc::1.0`
- DOI `10.17189/e467-dz93`
- Voyager 2 MAG Neptune NLS coordinates
- ASCII
- 12-second cadence
- coverage `1989-08-24T18:00:00.557Z` through `1989-08-26T08:19:48.379Z`

Required trajectory companion:
- Voyager 2 Neptune West Longitude System Coordinates 12s Trajectory Data Collection
- 12-second spacecraft position vectors relative to Neptune
- source position must be joined by exact epoch only

## Pairing rule

`MAG_SAMPLE + EXACT_SAME_EPOCH_SOURCE_TRAJECTORY_POSITION`

No interpolation is permitted. No implicit coordinate-frame transform is permitted. A missing exact trajectory epoch fails closed and the magnetic-field row is not exposed through the historical exact-sample adapter.

## Current state

This contract does not claim that any PDS data product has yet been downloaded or parsed.

- parser implemented: NO
- real record ingested: NO
- frame-transform authority: ZERO
- interpolation authority: ZERO
- 2226 endpoint authority: ZERO
- Geometric Admissibility authority: ZERO
- Loom-coherence authority: ZERO

## Next step

Acquire the PDS4 collection/product labels and their ASCII data members, validate their hashes/record layout where supplied, then implement a parser from the labels rather than from guessed column positions.
