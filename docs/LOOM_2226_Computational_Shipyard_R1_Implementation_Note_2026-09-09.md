# LOOM 2226 — R1 Implementation Note

R1 uses an additive semantic sidecar rather than modifying `MeshPrimitive` or `GeometryPackage` in place.

Reason: the existing governed synthesis geometry is already regression-tested and content-hashed. Replacing its dataclasses merely to carry visualization metadata would cause a wide hash/schema disturbance without adding engineering value. The sidecar preserves source geometry byte-for-byte while binding semantic records to source primitive IDs and source hashes.

A later governed migration may embed semantic metadata directly in GLB node extras or a dedicated semantic asset manifest. That downstream serialization choice must not change the authority boundary established here.
