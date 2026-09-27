# Progressive scene product contract v0.1

This, `product.schema.json`, and `generation-spec.json` define the prototype interface. All `must` rules
below require semantic validation in addition to JSON Schema structural checks.
No consumer needs the QA viewer's DOM, state variables, or scene reconstruction.

## Publication layout

```text
current.json                         optional small mutable build pointer
builds/<build_id>/manifest.json       entrypoint; no absolute host paths
objects/<sha256>.json                 root + each node/LOD package
objects/<sha256>.json.gz              deterministic gzip transport variant
provenance/<sha256>.json[.gz]          source dictionary + retained-sample audit
```

All resource URIs are relative to the publication root (not the manifest directory); no credentials, data URLs or
external resolver endpoints. Server may serve `.json` with Content-Encoding gzip;
hashes are of **uncompressed** canonical JSON. Transport hashes/lengths can also
be recorded. MIME `application/json`; ETag quoted uncompressed hash, correct Vary:
Accept-Encoding, immutable hashed object URLs; mutable pointer revalidated with
ETag. No CDN, service worker or commercial scene service is required. Loopback
static server supports Pixel tunnel using existing access arrangements.

Two data requests provide useful context: manifest then root. Shell, vendored
Three.js and design/font assets are measured separately. Root embeds all identity,
status and node descriptors, available epoch marker positions, and coarse
heliocentric curves for the eight planets. It includes the unresolved catalog.
Higher curve levels and local-system reference curves load independently as one
package per node/level; details/provenance load only on inspection. There is no
request per body/frame and no request to Solar authority during camera movement.

## Records

Schema document `$defs` are referenced by the future compiler and client validator.
Unknown major schema fails; optional `extensions` are namespaced and ignorable.
Prototype v0.1 rejects undeclared fields outside extensions so misspellings fail.

- **Manifest**: schema, `build_id`, `build_spec_id`, fixed `epoch_et`/`epoch_tdb`,
  frame/units/center, authority record, inputs, root resource descriptor,
  provenance descriptor, `generation` with policies, counts.
- **Resource**: relative `uri`, SHA256 of canonical uncompressed bytes,
  uncompressed byte count, gzip byte count; content encoding is transport only.
- **Root**: schema, build_spec_id, epoch_et, all `features`, flat `nodes`, coarse
  `curves`. Stable feature IDs are governed body IDs; node IDs use `system:MARS`,
  `system:EARTH`, `system:PLUTO`, `solar` etc. Node IDs are presentation identity.
- **Feature**: body ID/name/class, unchanged catalog parent, resolution, reason,
  epoch position or null, source reference or null, geometry status and node ID.
  `geometry_status` = AVAILABLE / NOT_REQUESTED / UNRESOLVED / PARTIAL /
  SAMPLING_LIMIT. This is separate from physical resolution and renderer status.
- **Node**: node ID, presentation parent node or null, anchor ID, authoritative
  anchor position at T, bound center/radius km in anchor-local coordinates,
  members, children, available level descriptors. Semantic parent does not imply
  the bound contains every descendant: explicit `subtree_bound` is unioned by
  the compiler; child traversal uses subtree bound; content culling uses content
  bound. No invisible parent may suppress a visible child incorrectly.
- **Level**: integer level (0 coarse), resource descriptor, maximum measured
  representation error km, vertex/segment counts. Sorted coarse→fine, errors
  nonincreasing. Per-curve errors are also retained inside the chunk.
- **Chunk**: schema, build_spec_id, node_id, level, curves. A replacement package
  contains the same requested feature set as its coarser level; empty/unavailable
  curves are explicit records, not silent disappearance.
- **Curve**: feature_id, semantic enum, anchor ID, horizon reference, frame,
  start/end ET, horizon status, closed=false, resolution/status, segment array,
  gaps, source refs and audit resource. Each segment includes source pair,
  authority class, retained sample indices, and points `[[ET,x_km,y_km,z_km],…]`.
  Coordinates remain Float64 JSON numbers. Every ET maps to the archived original
  sample. Error separates sampling probe residual, simplification deviation and
  GPU conversion budget. Source audit preserves velocities although render chunks
  omit them. Two or more points make a line; one-point segments are kept in audit
  and not drawn. Gap rows record ET bounds and actual reason.

`PHYSICAL_EPOCH_POSITION` is the feature's position semantic; it cannot be reused
for a reference-curve record. For this SUN-centered v0.1 product, optional `PHYSICAL_TRAJECTORY` requires
`anchor_id=SUN` and stores `X_body(t)`; no frozen non-Sun translation is allowed.
Physical trajectories in other selected scene centers require a separately declared
scene-center contract, not reuse of the local-reference renderer. Local reference geometry uses anchor-relative
samples displayed at the frozen anchor at T. See AUTHORITY_PROVENANCE for equations.

## Canonicalization and build identities

Prototype canonical bytes: Python JSON UTF-8, sort_keys=True, separators=(',',':'),
ensure_ascii=False, allow_nan=False, negative zero normalized to zero recursively,
no BOM/newline, finite binary64 numbers serialized with Python's shortest-roundtrip
formatter. Pin Python version in build inputs. IDs/source dictionaries sorted
lexically; ET samples increasing; segment and point ordering chronological;
no set iteration or acquisition wall clock in semantic content.

`build_spec_id = SHA256(canonical(inputs + generation specification))`.
Chunks/audit/root include build_spec_id, not build_id, avoiding circular hashes.
After hashing all resources, `build_id = SHA256(canonical(manifest without
build_id))`. Manifest includes all referenced resource identities transitively
through root; validation traverses and verifies them. Optional wall-clock run
report is outside manifest identity. `current.json` contains build_id and manifest
URI/hash; swapping it never changes existing build content.

Cache keys are `{build_id, uri, sha256}`; geometry buffers also include node/level.
A source/window/spec/policy/toolchain change necessarily changes build identity.
Never key only by body name, UTC date or node ID. HTTP cache is the default; an
in-memory LRU stores decoded chunks. Prototype decoded+GPU geometry budget is
accounted explicitly (see refinement); drop unused finest levels first, keep
root and active/coarse dependencies pinned. Offline distribution copies the same
manifest/object tree, without altering data formats.

## Navigator consumer interface

Future shared JS module exports:

```text
loadBasemap(manifestURL) -> validated handle
handle.catalog() -> complete identity/status list
handle.updateView({eyeKm64, orientation, verticalFov, widthCss, heightCss, dpr})
  -> desired nodes/levels and load requests (no physics)
handle.drawList() -> typed point/line records, local origin, semantics, provenance ID
handle.inspect(featureId) -> authority + generation + visibility reasons
handle.dispose() -> release owned buffers and pending fetches
```

QA and Navigator adapters consume this interface; neither owns the product.
Camera inputs are presentation only. Stable IDs let Navigator overlay its own
validated live states/routes. It must compare overlay epoch/frame/authority
identity; mismatched epoch content is visibly historical context, not current
operational state. No contract says a reference orbit is a navigable route or
collision surface. Player knowledge filtering and private infrastructure cannot
be bypassed by public basemap publication; additional overlays need their own
visibility/access contract before packaging.

## Extension boundary

Static facilities can reuse anchor-local frames, immutable resources and semantic
IDs once their upstream authority is registered. Body meshes can be optional GLB
resources with an explicit transform/units/authority adapter. No guessed shapes,
locations, routes or civilization data are required for v0.1. New binary chunk
media types require a schema version and decoder conformance; current clients
must fail explicitly on unsupported types. Do not build those extensions now.
