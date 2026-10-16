# SOLAR REACH Step 1: G1 → Route 1 seam, proposal only

BASE: `19377b854c529e74afc61202d9eb2e780c5b4884`
CLASS: RESEARCH / NONCANON / PROPOSAL / NO NEW RUNTIME
STATUS: HARD STOP BEFORE SIMULATION: `G1_ONE_ACTOR_OPENING_NOT_ROUTE1_MULTI_ACTOR_OPENING`.

## Requested result
Inventory the 201-year Route 1 run, propose one authored scenario and two contrasting settings, and test whether merged G1 can supply the opening to the existing 20-sponsor conductor without creating a new campaign framework.

## Source findings
The complete file/line/value inventory is in `SOLAR_REACH_STEP1_VALUE_INVENTORY.md`. The authored draft is `solar_reach_scenario.json` with SHA-256 `2551c693b73156f4d81ba3b3d0cbc566be9ec411728cf8e434502c1f95534f81`.
The existing G1 requires exactly one actor and one node and cannot host the country-funded 20-sponsor Route 1 opening. Route 1 instantiates its own historical Build 7 opening, adds 80-country investment assertions and sponsor Agents later, and accepts no externally constructed G1 kernel. This is a real integration seam, not a missing setting.

## What was deliberately not executed
The two authored settings were **not** run because execution would silently revert to Route 1's separate opening and fail the user's explicit seam stopping rule. Therefore funded bodies, ledger totals, conservation and setting deltas are `NOT_MEASURED`. Previously recorded 90-body results are historical comparison only, not A/B results.

## Single decision before continuation
kT must choose whether a narrowly authored multi-sponsor G1 extension and a small Route 1 kernel-injection seam are acceptable. Do not authorize new campaign orchestration or a frozen edit. If this cannot remain narrow, retain Route 1 as a self-contained in-memory test and drop the artificial G1 integration requirement for the first visible slice.

## Boundaries
No code, test, runtime, frozen path, old PR, database, WORLD, WALTER or phone screen touched. No PR amendment, ready-for-review or merge without asking kT first.
