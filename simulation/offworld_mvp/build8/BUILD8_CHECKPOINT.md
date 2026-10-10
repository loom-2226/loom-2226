# Build 8 multi-organization / 80-economy checkpoint

Status: active Build 8 development baseline, **not canon or qualification**. Do not regress to Build 7's three representative Agents (`PUB`, `FIN`, `SPN`) as the Build 8 population.

## Retained implementation

- `opening.py` admits 80 national 2026-2035 investment-capacity envelopes into a disposable Build 8 opening. Country investment is a bounded financing input, not an actor budget or free cash.
- `sponsor_executor_network_trial.py` represents 20 named public/private Sponsors and 16 executor roles, with overlapping organizations counted once. Awards remain pending physical plans; awards are not deliveries or earned executor revenue.
- `country_sponsor_allocation_trial.py` exercises bounded national-to-Sponsor allocation and conservation.
- `all_agents_country_trial.py` exercises all 80 economy envelopes and the existing 20-Sponsor/16-executor authored network. It is a trial of organization participation and account allocations, **not** evidence that 32 independent kernel Agents made decisions. Do not silently promote its roster, country preferences, or appetite to canonical world identity or policy.
- `all_agents_controls_trial.py` checks appetite extremes, equal allocation weights, competing commitments, and non-interference when a Sponsor is removed.

## Reproduced observations (2026-10-11, quantifactus)

With `PYTHONPATH=src:simulation/offworld_mvp/phase3b/kernel:.`:

- `python3 -m simulation.offworld_mvp.build8.all_agents_country_trial`: PASS and deterministic replay; 80 economies, 20 Sponsors, 16 executor roles, 32 unique organizations, 41 allocations, 57 economies without eligible Sponsors. Mobilized 25.10396510558080532339 and allocated 10.55502917702657340999999999 fictional capital units.
- `python3 -m simulation.offworld_mvp.build8.all_agents_controls_trial`: PASS; 0%/100% appetite, equal weights, competing commitment rejection without mutation, and unchanged allocations in 79 economies when Interlune is excluded.

These results validate the narrow experimental behavior only, not autonomous decision-making or a full-world epoch.

## Known gaps and next executable objective

The Build 8 opening currently inherits the three generic Build 7 Agents from `_build_kernel`; the network trial registers organization accounts and allocates money but does not make each named organization an independent Agent with information-bounded policy decisions. World Authority records actor references, snapshots, beliefs and decisions, but an exhaustive world-to-Offworld Agent population path has not been demonstrated. Preserve the 80-economy and multi-organization baseline while connecting actual existing Offworld Agent decisions to capital and project consequences. Do not introduce a CIVPROP dependency or another actor registry to achieve this.

Next: exercise one Build 8 epoch with the existing multi-organization economy and capability-limited Agent decisions, preserving identity, observation access, financial conservation, and replay. Stop and report any actual missing world/Agent authority rather than inventing actors, revenues, capabilities or physical deliveries.

This checkpoint does not authorize promotion to canon, qualification, or merging to main.

## Reproduction boundary and preservation (2026-10-11)

All 16 formerly untracked Build 8 scripts are preserved as **disposable, noncanon experiments** on this work branch, not promoted into runtime authority. The 80-economy experiment imports `ROOT` from `two_economy_source_finance_trial.py`; that file must accompany it.

**A fresh clone alone is not enough to execute these experiments.** Several scripts assume an external Earth v4 baseline at `/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24`, which is not stored in this repository. Fresh-clone import verification and execution with separately supplied baseline inputs are distinct checks. Do not describe the branch as fully self-contained or portable until that input is supplied.

The country trial currently uses an authored opportunity gate of 1 and authored capital appetite/preferences. Its allocations carry the mobilization transaction as lineage, not an admitted Sponsor decision authority. The control now gives both competitors positive, unequal allocations from the same finite pool, with project cost strictly between their allocations; it tests share-level scarcity, not a full endogenous market.

Reporting rule: preserve and commit scripts before reporting them as retained; verify import from a clean clone; separately state which external inputs are needed to run them. Never equate a successful import with reproducible execution.

## Safeguards

Earth v4 root is configured once in `opening.py`: `LOOM_EARTH_V4_ROOT`, falling back to the existing quantifactus location. Supply an accessible Earth v4 baseline separately. This removes embedded paths from 13 Build 8 modules but does **not** bundle the data.

`test_source_closure.py` imports tracked Build 8 modules from a fresh `git archive HEAD` checkout; untracked local files cannot satisfy imports. The test intentionally runs against committed HEAD, so newly staged work must be committed before checking its closure. The lunar continuation module additionally requires the optional `psycopg` Python package and a configured PostgreSQL `runtime` service for execution. If `psycopg` is absent, the test reports that optional dependency rather than treating it as a missing repository file.

## October 11 guard follow-up

The source closure test reports the number and identity of optional module skips, allowing only the `lunar_2027_continuation_trial` module when `psycopg` is absent. It verifies committed `HEAD`, **not** uncommitted working-tree edits. Missing Earth v4 directory raises an actionable error pointing to `LOOM_EARTH_V4_ROOT`. `test_sponsor_evidence_gate.py` exercises existing scripted policy outcomes (positive, economic decline, low-belief decline, funding wait) with synthetic observations; it is **not** observation-driven world evidence or autonomous multi-Agent behavior.

## Synthetic lunar observation access control

`test_three_sponsor_observation.py` tests whether three private-kind RETURN Sponsors diverge from observation access alone. Existing Build 7 `explore_paid` generates deterministic noisy signals from **authored synthetic** lunar truth; `publish_observation` applies recipient likelihoods and information access; existing Sponsor prospecting policy decides. A/C receive identical public observations, B also receives a private observation. Negative private evidence yields A/C INITIATE_PROJECT and B DECLINE; positive private evidence changes B to INITIATE_PROJECT without changing A/C. Sharing the negative private evidence makes all three DECLINE. Deterministic replay is asserted. The private-signal flip is implemented by changing authored hidden truth between synthetic scenarios, **not** by altering a recorded signal in the same world. The private water-bearing observation's relevance to volatile prospecting is a trial-only authored assumption. This is not live World Authority admission, a recorded lunar run, an autonomous Agent policy, or canonical physics. No banking machinery.

### Deferred database fixture (parked)

Later, when explicitly reactivated, use the approved read-only World Authority connection to export **only admitted lunar observation records and their receipts** for run `SOLAR_MATERIAL_1cd519072074d72fe42bb2f9:44f9a944ba26d099`. Exclude sealed truth and hidden state. Record run ID, source commit, export date, exact query and per-record SHA-256; label the frozen copy **snapshot, not live admission**. Re-read live records and verify hashes and fixture-versus-live Sponsor decisions. This is a later task, not a prerequisite for the in-memory three-Sponsor test. No database connection is attempted by that test.

### Bounded Sponsor consequences (noncanon synthetic campaign)

`test_three_sponsor_consequences.py` advances the same fixed-seed in-memory lunar information-access trial to existing kernel transfers and Sponsor project status transitions. Each Sponsor begins with 1.00 synthetic capital units and an independent PROPOSED project. An `INITIATE_PROJECT` policy result causes a 0.25 transfer from the Sponsor to its project cash and a PROPOSED→DEVELOPMENT transition; `DECLINE` causes PROPOSED→ABANDONED without investment. Negative B-private evidence: A/C invest (0.50 total), B declines; positive B-private evidence: all three invest (0.75 total). A/C are invariant across the private-evidence change; deterministic replay and kernel invariants are asserted. This is a scripted decision-to-consequence adapter in a test, not an autonomous campaign, construction spending, real-world lunar admission, or canonical economics. The World Authority fixture remains parked.
