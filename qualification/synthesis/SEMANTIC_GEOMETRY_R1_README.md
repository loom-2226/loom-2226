# Semantic Geometry R1

R1 is a deterministic, derived-only semantic sidecar over the existing governed `GeometryPackage`.

It adds identity, provenance, geometry role, visual-mutability constraints and explicit engineering status without changing source mesh vertices/triangles or creating new physical authority.

R1 intentionally leaves subsystem classification OPEN. It does not guess that a cylinder is a propellant tank, a box is a reactor, or any source node owns physical volume. Those classifications require governed upstream evidence.

Primary API:

- `build_semantic_geometry(source_governed_package)`
- `validate_semantic_geometry(semantic_package, source_governed_package)`
- `canonical_json(semantic_package, source_governed_package)`

Authority: `DERIVED_SEMANTIC_GEOMETRY_ONLY`.
