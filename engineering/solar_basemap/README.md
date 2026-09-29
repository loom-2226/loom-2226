# Progressive Solar basemap

The original architecture spike below is followed by the qualified Mars pilot
(PR #320) and its generic local-system successor. The successor is a
`class:runtime` derived publication/client change under the existing upstream
Navigator lane, not successor scientific research or a new physical model.

Read [ADR](ADR-001.md), then [product contract](PRODUCT_CONTRACT.md),
[authority contract](AUTHORITY_PROVENANCE.md), [refinement](LOD_REFINEMENT.md),
and [Luna handoff](LUNA_IMPLEMENTATION_HANDOFF.md).
Evidence: [repository/external research](RESEARCH_EVIDENCE.md),
[legacy forensics](LEGACY_FORENSICS.md), [measurements](evidence/measurements.json),
[existing-client browser measurements](evidence/browser_measurements.json).
Delivery: [prototype plan](PROTOTYPE_PLAN.md), [acceptance](ACCEPTANCE_BENCHMARKS.md),
[production follow-on](PRODUCTION_FOLLOW_ON.md).

## Original spike authority record

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

The original spike's scope and disposition above describe that work only. The
Mars pilot and generic successor are separately governed runtime worktrees and
do not change Solar authority, resolver, kernel, database, or campaign records.
Their generated products are derived, immutable-addressed publications. The
successor's pre-mutation inventory, build evidence, and qualification packet are
recorded in `prototype/generic-local-systems-v1/`.

## Artifact index

`generation-spec.json` pins the governed generic relationship-driven local-system
curve selection and explicit omission policy.
`product.schema.json` is a prototype serialization specification, not a registered
Solar authority schema. `bench/measure.py` reads the existing API and generates
legacy **test-only** fixtures in memory. `bench/browser.cjs` measures existing
clients. `bench/validate.py` checks this packet and reproduces its format/error
calculations offline. `evidence/sample_corpus.json` is a derived, nonauthoritative
capture of five exact governed path responses at the specified epoch, solely to
repeat the decision experiment. It must never be imported as physical authority.
