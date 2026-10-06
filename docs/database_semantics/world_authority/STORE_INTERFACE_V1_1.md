# World Authority V1.1 — bounded fixture metadata onboarding

Primary class: `class:data`. This is an additive successor to the frozen
`world-authority-v1-2026-10-06` store contract. V1 DDL, ETL, source snapshot,
candidate science, identities, role grants and Agent views are unchanged.
Build 6E is a consumer and never owns a World Authority credential or SQL path.

## Architectural finding

The accepted Build 6E fixture needs two independently authored `wa_geo.location`
rows (site and local feature), two `wa_geo.location_relation` rows, one structural
`wa_meta.unit` row and one lexical `wa_geo.time_support` row before its separately
authorized science admission. V1 already has these tables, immutable/serializable
guards and science-writer INSERT privileges, but no public store operation to
write them. `install_exact_world` accepts only `wa_world` rows, while
`record_fixture_admission` correctly requires a pre-existing time row. Direct
6E SQL would violate the one-way ownership boundary. Therefore only store
surface and focused qualification change; no DDL, migration or grant change.

The accepted source catalogs Cabeus as `location_kind=SITE`,
`original_region_type=LOCAL_SITE`, `origin_kind=EMPIRICALLY_IDENTIFIED`.
Build 6E's prose calling it a `REGION` must be corrected. The new operation
accepts an empirical parent of type `REGION` or `SITE`; `CONTAINS` is an
owner-authored siting warrant, never scientific extrapolation or inherited
source scope.

## Public operations

`install_authored_site_metadata(connection, manifest)` accepts exactly:

```
profile = WA_AUTHORED_SITE_METADATA_V1
authorization_ref : nonempty owner authorization reference
identity_authority = LOOM_BUILD6E_NAMED_WORLD_V1
body_key, parent_location_key : accepted catalog semantic keys
site_key, site_name, feature_key, feature_name : explicit authored identities
unit_key = MODEL_RESOURCE_UNIT_BY_FAMILY
```

Only a separately authenticated `wa_science_writer` principal may call it.
The store resolves the accepted body and empirical parent; it creates an
authored `SITE` and `LOCAL_FEATURE`, both with unknown geometry, and explicit
parent→site and site→feature `CONTAINS` records. It cannot write a body,
empirical location, scientific support/assertion/admission, `wa_world` physics,
runtime event or Agent information. The structural unit remains
`UNCHARACTERIZED`, with no conversion to kg, tonnes or a scientific quantity.

IDs use `stable_uuid('AUTHORED_LOCATION', identity_authority,
length_prefixed(body_key, authored_key).decode(), 'IDENTITY_V1')`; they are
independent of WORLD seed, scenario and run. The canonical manifest SHA-256 and
authorization reference are embedded in `source_ref` and the relation
`warrant_ref`; they bind the exact authored meaning for audit. The owner-held
manifest is a governance input, not an Agent-visible scientific fact.

`install_fixture_time_support(connection, admission_manifest)` uses the exact
existing `WA_FIXTURE_ADMISSION_MANIFEST_V1` validator and V1 time identity
recipe. It inserts or compares only the `LEXICAL`/`SIM_TIME` helper row. It
neither creates nor authorizes a scientific admission. The governor still calls
`record_fixture_admission` with its own login in a later transaction. If that
step fails, the time row is inert and exact retry is safe. Scientific source
epochs remain their original NULL/UNKNOWN values.

Both operations require an idle connection, set a SERIALIZABLE transaction,
verify the authenticated session principal belongs only to the designated
route, then use `SET LOCAL ROLE wa_science_writer`. Advisory locks serialize
competing attempts. Existing full-column insert-or-exact-match checks apply;
unequal rows, incomplete replay and extra manifest fields fail. The metadata
transaction is atomic. The store returns `INSERTED` or `ALREADY_MATCHED`,
plus the two authored location UUIDs for the site operation.

Authorization is the separately controlled science-writer credential plus
the explicit owner reference in the manifest. These operations do not turn
arbitrary supplied text into an owner decision; the caller must present the
governed manifest under that credential. The frozen V1 science-writer DB role
already has broader ETL privileges, so no new database capability is granted.
Runtime, world-writer, governor, admission-writer, reference and Agent logins
cannot call these operations; Agent login cannot read the private `wa_geo`
catalog. The trusted 6E runtime gets no science-writer credential.

The old V1 import, admission, WORLD and epoch operations retain their exact
contracts. A successor implementation may not change the frozen V1 tag, source
snapshot, SQL migration or historical qualification evidence.
