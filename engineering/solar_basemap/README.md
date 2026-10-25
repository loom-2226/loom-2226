# Progressive Solar basemap — architecture spike

Status: **architecture/specification complete; prototype NOT implemented or qualified**.
Primary class: `class:engineering`. Work item: Kevin's Progressive Solar Basemap
architecture / evidence / implementation-spec spike, 28 September 2026 (Melbourne).
This is bounded runtime architecture and delivery engineering under the existing
upstream Navigator lane, not successor scientific research or a new physical model.

Read [ADR](ADR-001.md), then [product contract](PRODUCT_CONTRACT.md),
[authority contract](AUTHORITY_PROVENANCE.md), [refinement](LOD_REFINEMENT.md),
and [Luna handoff](LUNA_IMPLEMENTATION_HANDOFF.md).
Evidence: [repository/external research](RESEARCH_EVIDENCE.md),
[legacy forensics](LEGACY_FORENSICS.md), [measurements](evidence/measurements.json),
[existing-client browser measurements](evidence/browser_measurements.json).
Delivery: [prototype plan](PROTOTYPE_PLAN.md), [acceptance](ACCEPTANCE_BENCHMARKS.md),
[production follow-on](PRODUCTION_FOLLOW_ON.md).

## Verified starting authority

- Main at bootstrap: `b22703ab7ce5586fecfeda0998d19b7d1fbbfe30`.
- Dependency PR #299: OPEN, not draft; head
  `f0c373a4deb5589584619b64a91ac2ac1d2ed936`; loom-gate SUCCESS.
- Specification branch: `engineering/progressive-solar-basemap-spec`, based on
  main in `/home/ubuntu/LOOM_SOLAR_BASEMAP`. Inspector worktree unchanged.
- Live read-only authority: `loom_dev/loom_solar` via Inspector port 8765;
  ledger SHA `fd0784e9fdcaea22d9e8e8b8c93b6ca5db8e6cd84ce293be1bdf4310c8db23a7`.
- 2226 publication epoch: `2226-01-01T00:00:00 TDB`, ET `7131844800.0`.
  110 identities; 103 resolved (90 direct, 13 governed propagated); seven
  unresolved. This is a new epoch measurement, not a reclassification of Q8.

## Governing scope and impact

Read authoritative main's START HERE, current workstate/status overlay, governance
baseline, authority model, change control, research boundary, dependency policy,
root and engineering AGENTS, and WALTER activation. The Integrated Runtime /
Navigator architecture owns campaign mutation and numerical authority; this ADR
specifies a separate derived publication consumer. Current Metric/Loom/Weave
work plan remains a separate downstream overlay concern. Canon Solar Atlas and
registered canon baseline remain governing for world context; this spike proposes
no new world facts, celestial identities, infrastructure inventory or physics.
No CCR is needed for the declared representational/software contract.

| Dependency | Disposition in this spike |
|---|---|
| Solar PostgreSQL, kernels, resolver, ET overlay, Inspector qualification | UNCHANGED_COMPATIBLE; read-only consumers only |
| Existing Navigator, GIS, campaign authority | UNCHANGED_COMPATIBLE; inspected as donors, not modified |
| Future QA basemap client and Navigator basemap adapter | REVIEW_REQUIRED at implementation; new contract below |
| Release, Android/Windows launchers, deployment, design tokens | UNCHANGED_COMPATIBLE; no release or service changes |
| Future static facilities/routes | UNKNOWN_UNREGISTERED until their own authority/knowledge contracts exist |

Mutations are restricted to this engineering directory: documents, a proposed
schema, and disposable decision experiments. No production compiler, API,
renderer or schema migration is added. Qualification evidence under Inspector's
`docs/qualification` remains untouched. No PR is merged; no Phase 5 begins.
Rollback: revert the specification commit; running services/data are unaffected.

## Artifact index

`generation-spec.json` pins the chosen prototype policies and twelve reference-curve requests.
`product.schema.json` is a prototype serialization specification, not a registered
Solar authority schema. `bench/measure.py` reads the existing API and generates
legacy **test-only** fixtures in memory. `bench/browser.cjs` measures existing
clients. `bench/validate.py` checks this packet and reproduces its format/error
calculations offline. `evidence/sample_corpus.json` is a derived, nonauthoritative
capture of five exact governed path responses at the specified epoch, solely to
repeat the decision experiment. It must never be imported as physical authority.
