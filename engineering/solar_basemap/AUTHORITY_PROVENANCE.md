# Authority and provenance contract

Normative for the proposed prototype. Does not amend Solar authority.

## Physical inputs and exclusions

Use PR299's `loom_solar_postgres.load_authority` (repeatable-read, read-only
snapshot), `SolarEphemerisRegistry.source_for`,
`SpiceEphemerisAdapter.service().resolve_et`, and `loom_solar_time` codec.
The adapter checks selected source identity, kernel hashes, native target coverage,
qualified numeric ET windows, and evaluates geometric ECLIPJ2000 states relative
to Sun with `spkgeo`. Governed propagated SPKs retain their existing capability,
qualification, uncertainty and source lineage. The compiler must never choose a
more convenient source or reconstruct orbital elements.

Reuse `Inspector.automatic_plan`, `trajectory`, `relative_state` as a pinned
**offline helper dependency** for the prototype, without modifying them or using
its HTTP server as a production authority API. They use the same service and
preserve seam/gap handling. Native ET migration 020/overlay is a prerequisite,
not an operation this spike or compiler is authorized to apply. If authority
bootstrap mismatches, compilation fails before publication.

The baseline catalog comes from PostgreSQL, including unresolved identities.
No old SQLite seed, Navigator ID list or approximate dynamics can add a body.
Catalog membership and eligible physical geometry are distinct counts.

## Geometry meanings

Let `X_b(t)` be the governed Sun-relative position of body b in ECLIPJ2000 km.
Let `T` be the publication epoch and `t_i` the resolver sample epochs.

| Semantic | Coordinates and permitted use |
|---|---|
| `PHYSICAL_EPOCH_POSITION` | `X_b(T)`, exact sourced epoch marker. Valid only at T. |
| `PHYSICAL_TRAJECTORY` | `X_b(t_i)-X_c(t_i)` with explicit center c; timed physical worldline samples. Optional diagnostic geometry, excluded from default prototype root. Never used as a propagation table. |
| `HELIOCENTRIC_REFERENCE_ORBIT` | A sampled Sun-relative arc anchored at Sun(T), shown as cartographic context at T. Even when numerically identical to a Sun worldline, semantic purpose and finite horizon are explicit. |
| `PARENT_RELATIVE_REFERENCE_ORBIT` | Store `q_i=X_b(t_i)-X_p(t_i)`; draw at `X_p(T)+q_i`. Axes stay inertial ECLIPJ2000; no parent spin/plane alignment is implied. The curve's sample time differs from its display anchor time. |
| `DERIVED_CARTOGRAPHIC_CONTEXT` | Nonphysical annotations/bounds only, with documented derivation and source links. It cannot masquerade as a physical epoch position. No invented belt particles or facilities in the prototype. |

For the SUN-centered v0.1 serialization, optional physical worldlines must use
center SUN. Other selected-center physical trajectories are described above for
semantic contrast, not silently translated with a frozen non-Sun anchor.

“Orbit” does not mean closed, repeating or complete. `REVOLUTION_COMPLETE`,
`MAX_HORIZON_TRUNCATED`, `OPEN_YEAR`, `UNRESOLVED_AT_T0`, phase/coverage limitations
are copied from the governed horizon result. Endpoints remain endpoints; no line
loop, no first-to-last edge, no completion of missing arcs.

At T, Phobos's reference curve passes its epoch marker because
`X_Mars(T)+(X_Phobos(T)-X_Mars(T))=X_Phobos(T)`.
At another sample time the displayed curve deliberately freezes Mars at T;
it is not `X_Phobos(t_i)`. The difference is `X_Mars(T)-X_Mars(t_i)`.
Keep this algebra in the roundtrip test and UI legend. All lengths remain physical
km; only marker/label glyphs have screen size. No orbit enlargement.

## Parent identity versus cartographic anchor

Retain `catalog_parent_id` unmodified, `horizon_reference_id` from the planner,
and `anchor_id` independently. The compiler may select a known physical primary
as a **cartographic reference**, never rewrite catalog parentage.

Prototype anchor policy v1, explicit generation-spec entries:

| Bodies | Anchor | Basis |
|---|---|---|
| MOON | EARTH | Inspector's explicit association; catalog parent remains NULL |
| PHOBOS, DEIMOS | MARS | Same physical primary selected in Q8; catalog/horizon reference may be MARS_SYSTEM_BARYCENTER |
| IO, EUROPA, GANYMEDE, CALLISTO | JUPITER | Governed system plus explicitly declared primary |
| CHARON | PLUTO | Preserve PLUTO_SYSTEM_BARYCENTER catalog relationship separately |
| DIMORPHOS | DIDYMOS | Use only if both IDs and governed relationship resolve at T and over path span |
| Other satellites | Catalog parent if it is a physical body, else explicit system-primary mapping in spec; otherwise no local reference geometry |

The all-catalog prototype publishes positions/status for everyone, with reference
curves required for Sun's eight planets, Moon, Phobos, Deimos and Charon. Other
local families are a production coverage extension after this contract passes;
mark their geometry `NOT_REQUESTED`, never failed or unresolved. The compiler
must not infer parents from strings or fallback silently to Sun. No local arc
when either body or anchor fails resolution. Giant moons/Triton/Titan and asteroid
satellites use the same policy/mechanism when requested; Dactyl/Selam remain
unresolved in the measured ledger. Pluto/Charon is an additional prototype case
precisely because barycenter, physical primary and display origin differ.

## Provenance and reproducibility

Build input identity includes: raw authority ledger digest, canonicalized ledger
snapshot digest, manifest hashes including native ET overlay, complete kernel
asset digests/byte counts, source and coverage rows actually consumed; resolver
Git SHA plus relevant module file hashes, Python/SpiceyPy/CSPICE versions and
platform; compiler SHA/module hashes; schema version; generation specification
hash; ET binary64 bits + TDB label; ECLIPJ2000/SUN/km/aberration NONE; parent-anchor,
horizon, sampling, simplification, serialization and client-policy versions.
Local paths and wall-clock timestamps are audit envelope fields, not semantic
identity. Hash authoritative source bytes, not filenames alone.

Archive exact sample rows before simplification: ET, body/anchor vectors or their
lossless relative subtraction, both source IDs/hashes/capability/coverage and
resolution reasons. Each output segment references that immutable sample artifact
and retained sample indices; store source dictionary once. Seams/gaps are
explicit boundaries even where coordinates happen to meet. A simplifier cannot
cross them. Add known source/coverage boundaries for both body and anchor before
sampling; use the existing boundary-adjacent probe policy. No segment crosses an
unresolved ET window just because its endpoints happen to resolve.

Each sample-audit resource carries its schema identifier, requested body and
cartographic anchor, epoch ET, ECLIPJ2000 frame, km units, aberration `NONE`,
physical-state center `SUN`, and cartographic semantic. This keeps archived
SPICE states distinct from the anchor-relative reference geometry derived from
their subtraction. Its sample count equals the retained exact-state rows.

Deterministic build identity is defined in PRODUCT_CONTRACT. Two builds from the
same pinned environment and input snapshot must be byte-identical (gzip mtime 0).
Cross-platform SPICE arithmetic is not presumed byte-identical: pin toolchain for
prototype PASS. A different toolchain is an explicit new input/build identity;
compare semantic results and provenance before adoption. Preserve signed/native
ET identity; no UTC roundtrip. Sampling error is a numerical representation
metric, separate from physical source uncertainty and qualification.

## Failure and recovery

- Authority/hash/frame/units mismatch: abort whole build; do not update current.
- Unresolved body/anchor: publish catalog/reason with no invented position/curve.
- Partial coverage: publish separately delimited valid arcs and explicit gaps.
- Sampling depth/budget exhaustion: `SAMPLING_LIMIT`; retain valid coarser geometry
  with declared measured error, disqualify it from meeting tighter accuracy gates.
- Truncation: valid finite arc with horizon status, not a failure.
- Client integrity/version failure: reject that artifact, retain last verified
  coarse content of the **same build**, expose diagnostic status; never mix builds.
- Network failure: retry boundedly; report missing detail, keep verified parent.
- Missing shape/radius: display an explicitly symbolic marker. Do not invent a
  physical sphere radius. Shape/surface detail is outside the initial prototype.

Publish to a new build directory, validate it completely, then atomically update
an optional current pointer. Preserve the prior manifest/objects for rollback.
Compiler and client have no database write interface. Frozen research, canon,
Solar authority, Inspector and launchers remain unchanged.
