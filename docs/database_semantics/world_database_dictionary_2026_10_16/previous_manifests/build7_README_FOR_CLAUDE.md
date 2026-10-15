# LOOM Priority 1 Build7 + World Authority metadata

Build7: live PostgreSQL 16 schema and catalog from previous verified ZIP,
including authored migration 002.

World Authority: two independently qualified PostgreSQL 18.6 clusters as
observed October 6, 2026. Tables/grants/extensions/settings agree;
cluster A has one extra role, wa_q_reference. Qualification ports
are historical and currently not listening; this DOES NOT prove a
currently running World Authority instance.

Qualified inventory contains 77 tables, their owners and RLS flags, 12
roles in cluster A (name/SUPERUSER/LOGIN/BYPASSRLS), 1007 table grants, extension
versions, and migration 001 SHA-256 pinned to the source DDL.

The qualified deterministic source-export manifest gives row counts only
for tables present in that export. Other table counts are NOT RECORDED,
not inferred to be zero. No live October 16 PG18 row counts are claimed.
RLS policies are transcribed from pinned SQL, not a fresh live pg_policies
query. Qualifier did not preserve all server-level role attributes,
memberships, grantable flags, sequence/function privileges, or pg_policies
catalog. The live PostgreSQL 18 inspection remains outstanding.

No fictional hidden values, source row content, science observations,
database connection strings, passwords or secrets are included.
Never execute the included reference DDL to interpret this package.
