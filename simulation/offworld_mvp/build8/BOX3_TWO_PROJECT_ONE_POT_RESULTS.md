# Build 8 PR B: Two Projects, One Pot of Money

**RESEARCH / NON-CANON / OPT-IN / IN-MEMORY.** Base:
`6f3e80c05dd3348e324c03716c6cfa10fb3cf0f2`.

No database, container, World Authority, hidden-WORLD generator, frozen file,
baseline, pinned result, or placeholder is involved. One instance of the
existing `MethodologyHardenedBuild4Kernel` holds one `SPN` and two distinct
Offworld projects with distinct nodes, cash accounts, activities, and states.
No new policy or numerical ranking rule was introduced.

## Visible assumptions and actual policy input

- One sponsor on `EARTH:X`: opening money **100 MODEL_CURRENCY**.
- Project `P-A`: `OFF:PROJECT:A`, `cash:A`, `ACT-A`, commitment **60**,
  priority **1**.
- Project `P-B`: `OFF:PROJECT:B`, `cash:B`, `ACT-B`, commitment **60**,
  priority **2**.
- Aggregate commitments **120**, exceeding available capital **100**.
- Both activities are proposed and immediately eligible; no timing filters.
- Existing frozen policy `SPONSOR_PORTFOLIO_V1` reads **priority,
  affordability, eligibility and states**, not beliefs. Its tie-break and
  selection semantics are untouched.
- Only admitted, authored synthetic signal and its existing-rule Bayesian
  belief enter the actor-visible snapshot. Two separate controls:
  `NEGATIVE` derives posterior **0.2**, `POSITIVE` derives **0.8**
  from prior **0.5** with detection **0.8** and false-positive **0.2**.
  No physical/geological hidden truth exists in this in-memory fixture.
  These are **hypothetical visible information states**, not real observations
  of an actual LOOM body. No seed, priority, cost or budget was tuned to force
  a changed policy decision.

The *initial* policy snapshot includes:
`SPN`, `account_balance=100`, `AUTHORIZE_ACTIVITY`, `DEVELOP`, objective
`RETURN`, one admitted observation ID and visible signal, the derived belief
and prior, `portfolio.AVAILABLE_CAPITAL=100`, and for each activity its
project ID, project status `PROPOSED`, activity status `PROPOSED`,
commitment `60`, fixed priority `1`/`2` and window valid `1`.
Nothing else, notably no hidden truth, region material states or WORLD seed,
reaches the policy snapshot.

The unchanged portfolio policy chooses `ACT-A`, reason
`SELECTED_PRIORITY_AFFORDABLE`, reservation **60**. The kernel authorizes,
starts and completes the administrative `CAPITAL_ALLOCATION` activity.
A real `OTHER_INVESTMENT` transfer of **60** crosses from `SPN:POOL`
(Earth) to `cash:A` (Offworld) in year **2**, with decision/activity lineage.
Kernel status transition: `P-A PROPOSED -> DEVELOPMENT`.

The remaining sponsor balance is **40**, less than `P-B`'s **60**
commitment. The *same frozen policy* considers `ACT-B` alone and returns
`DEFER`, `INSUFFICIENT_AVAILABLE_CAPITAL`. The consumer records a causal
event with that decision and keeps `P-B` `PROPOSED`, disposition
`DEFERRED_NOT_ABANDONED`. Deferral is a recorded outcome, **not** a false
claim that the frozen kernel has a separate DEFERRED project lifecycle status.

## Results: both belief states

| Item | Before | After negative-belief case | After positive-belief case |
|---|---:|---:|---:|
| Sponsor shared cash | 100 | 40 | 40 |
| `P-A` cash | 0 | 60 | 60 |
| `P-A` status | PROPOSED | DEVELOPMENT | DEVELOPMENT |
| `ACT-A` status | PROPOSED | COMPLETED | COMPLETED |
| `P-B` cash | 0 | 0 | 0 |
| `P-B` status | PROPOSED | PROPOSED (explicitly deferred) | PROPOSED (explicitly deferred) |
| `ACT-B` status | PROPOSED | PROPOSED | PROPOSED |
| Sponsor belief | 0.5 | 0.2 | 0.8 |
| Funded activity | none | ACT-A | ACT-A |

**Result: funding choice did NOT change when belief changed.** This is the
honest outcome of the existing priority-first portfolio policy.

The initial policy snapshot fingerprints differ:
- Negative: `5545a6cee9a595743d9a85bec80dbd6d8ccbff7a7db5910c3b7429e321ac617e`
- Positive: `bbaf84e2cc1155ba112f2aa55e739a384cbd8f49145e08b91f34386646d09430`

## Capital gauge, each simulated year, both scenarios

Amounts in MODEL_CURRENCY. These are direct breakdowns of the **unchanged**
kernel `earth_impact.capital_diverted_to_offworld` and transactions. The
project allocations are **parts of** the total, never added on top. The
existing Build 8 freight-gauge function supplies the final freight line.

| Year | A received | B received | Unattributed | New draw | Recycled draw | Total Offworld draw | Study spend | Earth-side freight |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 60 | 0 | 0 | 60 | 0 | 60 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

For **every year**: `new draw + source-proven recycled draw = unchanged
kernel Offworld draw`, and `A + B + unattributed = Offworld draw`.
No returned-fund/appropriation transactions exist in this authored case, so
the recycled line is legitimately **zero**. Returns received and other
Offworld purchases from Earth are **zero** in all three years.
No hidden limit, budget filter or governor is applied.

## Determinism and limits

Two independent reconstructions of each belief case match in their **entire
returned report**, including policy decision IDs, admitted snapshot,
transaction, causal record evidence, gauge and kernel decision-state
fingerprint. Negative-case fingerprint:
`b190472905b93d0717759f66af5256bc6285b0b85730eb71f55a168ed360b76c`.
Positive-case fingerprint:
`cee090845f48cac2b6a1cb39f436d7bf076398eeb2435e9e0085d3522bbbe782`.

This is **in-memory deterministic re-execution**, not World Authority
persistence/reopen qualification. Existing main source and pins remain
unchanged. The case proves accounting shadow and a real decision consequence;
it does **not** prove belief-responsive funding, actual geological evidence,
external economic realism, study spending, freight payments, true recycled
return flows, market clearing, price formation, banks, contracts, multi-agent
negotiation, failed production, repeat studies or multiple payer ownership.
Future behavior is not inferred from absent transactions.

Run locally, with no database:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:src:simulation/offworld_mvp/phase3b/kernel python -B -m unittest -v simulation.offworld_mvp.build8.test_box3_two_project_choice`.
