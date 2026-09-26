# SOLAR-BASELINE-01 Coverage

Existing body identities: **110**. Active snapshot rows matched: **110/110**. Deterministic external crosswalk matches: **99/110 (90.0%)**. Identity holds: **4**. New bodies: **0**.

Assertions: **788 generated**; 758 CANDIDATE, 30 HOLD, 0 REJECT. 786 unique source-lineage keys; 2 repeated rows retained and not counted as independent lineage. Preferred facts: 0. There are 36 multi-value body/property groups, preserved in [`source_conflicts.json`](source_conflicts.json).

## Coverage by body class

| Class | Bodies | With candidates | Coverage |
|---|---:|---:|---:|
| ASTEROID | 17 | 17 | 100.0% |
| BARYCENTER | 9 | 9 | 100.0% |
| BINARY_ASTEROID_PRIMARY | 3 | 0 | 0.0% |
| CENTAUR | 1 | 1 | 100.0% |
| COMET | 7 | 7 | 100.0% |
| DWARF_PLANET | 11 | 11 | 100.0% |
| INTERSTELLAR_OBJECT | 3 | 3 | 100.0% |
| NATURAL_SATELLITE | 31 | 29 | 93.55% |
| NEAR_EARTH_ASTEROID | 7 | 7 | 100.0% |
| PLANET | 8 | 8 | 100.0% |
| SPACECRAFT | 5 | 0 | 0.0% |
| STAR | 1 | 1 | 100.0% |
| TRANS_NEPTUNIAN_OBJECT | 3 | 3 | 100.0% |
| TROJAN_ASTEROID | 4 | 3 | 75.0% |

## Property coverage

| Property code | Candidate assertions | Bodies | Coverage of catalog |
|---|---:|---:|---:|
| ABSOLUTE_MAGNITUDE | 42 | 42 | 38.18% |
| ABSOLUTE_VISUAL_MAGNITUDE_V1_0 | 10 | 10 | 9.09% |
| BULK_DENSITY | 49 | 48 | 43.64% |
| COLOR_INDEX_B_V | 17 | 17 | 15.45% |
| COLOR_INDEX_I_R | 1 | 1 | 0.91% |
| COLOR_INDEX_U_B | 17 | 17 | 15.45% |
| COMET_NUCLEAR_MAGNITUDE_PARAMETER | 4 | 4 | 3.64% |
| COMET_NUCLEAR_MAGNITUDE_PHASE_COEFFICIENT | 3 | 3 | 2.73% |
| COMET_NUCLEAR_MAGNITUDE_SLOPE_PARAMETER | 4 | 4 | 3.64% |
| COMET_TOTAL_MAGNITUDE_PARAMETER | 9 | 9 | 8.18% |
| COMET_TOTAL_MAGNITUDE_SLOPE_PARAMETER | 9 | 9 | 8.18% |
| EFFECTIVE_DIAMETER | 36 | 36 | 32.73% |
| EQUATORIAL_RADIUS | 10 | 10 | 9.09% |
| GEOMETRIC_ALBEDO | 40 | 39 | 35.45% |
| GM | 105 | 70 | 63.64% |
| LONG_AXIS | 43 | 43 | 39.09% |
| MAGNITUDE_SLOPE_PARAMETER | 14 | 14 | 12.73% |
| MASS | 10 | 10 | 9.09% |
| MEAN_RADIUS | 39 | 39 | 35.45% |
| POLE_DECLINATION_MODEL | 44 | 44 | 40.0% |
| POLE_ORIENTATION | 9 | 9 | 8.18% |
| POLE_RIGHT_ASCENSION_MODEL | 44 | 44 | 40.0% |
| PRIME_MERIDIAN_MODEL | 44 | 44 | 40.0% |
| ROTATION_PERIOD | 52 | 51 | 46.36% |
| SPECTRAL_CLASS_SMASSII | 21 | 21 | 19.09% |
| SPECTRAL_CLASS_THOLEN | 14 | 14 | 12.73% |
| TRIAXIAL_DIMENSIONS | 15 | 15 | 13.64% |
| TRIAXIAL_RADII | 53 | 51 | 46.36% |

## Missingness

| Disposition | Body/property lanes |
|---|---:|
| AMBIGUOUS_IDENTITY | 108 |
| FIELD_NULL_IN_SOURCE | 0 |
| LEGITIMATE_UNKNOWN | 0 |
| NOT_APPLICABLE | 241 |
| PARTIAL | 0 |
| SCHEMA_LIEN | 0 |
| SEMANTIC_MAPPING_LIEN | 0 |
| SOURCE_DOES_NOT_COVER_BODY_CLASS | 1036 |
| SOURCE_NOT_FOUND | 54 |
| SOURCE_NOT_PRESENT | 870 |
| SUPPORTED | 661 |
| UNKNOWN | 0 |

Missingness states refer only to the selected corpus/property contract. `SOURCE_NOT_PRESENT` means an acquired exact record omitted that exact field; `SOURCE_NOT_FOUND` means no usable record was acquired. Explicit source NULL was not evidenced, so `FIELD_NULL_IN_SOURCE` is zero. Coverage does not claim completeness.
