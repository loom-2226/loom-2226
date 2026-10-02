# Actor Baseline 2026 V0.3 — Functional Initialization Qualification

**NON_CANON / DERIVED+ESTIMATED INITIALIZATION / PRE-ACTOR-BEHAVIOR**

Purpose: make the 233 candidate institutions sufficiently heterogeneous and economically functional to enter Step 8 without requiring a perfect historical reconstruction.

## Inputs

- candidate roster: LOOM_GROUP_AGENT_SEED_2026_v0.3.json;
- validated Earth authority: earth-v0-1-9934d0ac-20260925;
- specifically global 2026 rows derived from earth_sector_year.

No new external capital/economic dataset was introduced.

## Method

Each actor receives lifecycle status, functional/inactive flag, scale class and score derived from its 2026 seed evidence, mapped Earth economic sector, role-specific financial-capacity semantics, central/low/high initialization estimate, operating-capacity index, confidence, method and source references.

The estimate is explicitly a **model initialization parameter**, not a claimed historical balance-sheet fact. It is anchored to a fraction of validated 2026 investment in the mapped Earth sector and modified by an actor scale class inferred from the seed's 2026 evidence.

Ranges are deliberately wide: 0.25x–4x the central estimate.

## Lifecycle result

- total candidates: 233;
- active/operating functional initialization: 228;
- historical/inactive: 2 (PRO_PLANETARY_RESOURCES, PRO_DEEP_SPACE_INDUSTRIES);
- proposal/pending/inactive: 3 (CERT_LORS101, REG_EU_SPACE_ACT, SUP_ROCKETDYNE).

Historical/proposal actors remain useful as analog/evidence nodes but cannot transact at the 2026 boundary.

## Financial semantics

A single numeric field does **not** mean the same thing for every category. CAPITAL means deployable financing capacity; OFFTAKER procurement capacity; INSURER underwriting capacity; CARRIER fleet/service investment capacity; PROSPECTOR venture/project-development capacity; SUPPLIER_PRIME company capital/independent-R&D capacity; STATE policy/program capacity; certification/registry/soft-power values are institutional operating capacity.

These capacities are ceilings/context for later role logic, not automatic spendable cash.

## Population-envelope check

Central estimates for every category remain below the 2026 investment aggregate of the mapped validated Earth sector. Current category shares include approximately CAPITAL 6.4% of mapped SERVICES investment, CARRIER 10.4% of SHIPS_AEROSPACE investment, PROSPECTOR 0.35% of SHIPS_AEROSPACE investment, SUPPLIER_PRIME 4.0% of SHIPS_AEROSPACE investment, INCUMBENT_INDUSTRY 6.1% of BULK_MATERIALS investment, OFFTAKER 1.3% of BULK_MATERIALS investment, and INFRASTRUCTURE 1.3% of TRANSPORT_LOGISTICS investment.

This is an anti-explosion sanity constraint, not proof that the individual allocations are historically exact.

## Authority rule after initialization

2026 estimates may seed actor state. They do not recur as annual grants. Once actor behavior is enabled, commitments, transactions, revenue/cost, asset changes, failures and institutional events must update actor state endogenously.

Future Postgres macro/sector state may continue to define environmental constraints where already governed, but it may not overwrite named-actor histories.

## Qualification target

The baseline is suitable for **functional actor testing**, not historical financial research. Before promotion beyond research status, sensitivity should vary the central estimates within their recorded ranges and verify that major civilization outcomes are not artifacts of a single arbitrary initialization.
