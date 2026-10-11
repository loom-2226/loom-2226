# Step 3 acceptance stop (2026-10-11)

The isolated yearly path now settles at completion, publishes stage knowledge
at contract/completion, releases deliverables, and applies subcontract failure,
re-sourcing, and payments in their modeled years. Legacy `run_screened` and all
frozen references remain unchanged.

**STOP: strict acceptance is not met.** All three scenarios differ in the
**ordering of `build8_knowledge`**, first at index 25. The records, including
their authored year stamps, are the same multiset, but the user's current rule
allows event order alone to differ. Do not silently relax knowledge ordering.

Other comparisons across all three: work outcomes/dates, screening, occupied
capacity, balances, semantic event multisets, and economic transaction multisets
match. Transaction ID sequences match exactly; no IDs added or removed.

- `screen_default`: knowledge list order differs; fingerprint identical;
  all transaction IDs and parent references identical.
- `screen_sub`: knowledge list order differs; fingerprint identical;
  all transaction IDs and parent references identical.
- `screen_sub_failure`: knowledge list order differs; fingerprint differs:
  frozen `545f07aa01c3cb9143f8457beb6580837f33d05f0534dded2ec4095f8cfb51ac`
  versus yearly `6f939cb778c2fe1779af350dc134bd8dee87a98003067579e8ba2dbe0da92bd1`.
  Transaction IDs exist in both but their assigned economic transfers shift at
  `tx-000055` through `tx-000059` because chronological completion reverses two
  legacy settlements. Changed parent references:
  - `tx-000055`: `[DEC-a8ae4fd125759609427e, COMMISSION:Axiom]` -> `[DEC-ccc23d7df6887ebc91aa, BUILT:Interlune]`
  - `tx-000057`: `[tx-000055]` -> `[DEC-a8ae4fd125759609427e, COMMISSION:Axiom]`
  - `tx-000058`: `[DEC-ccc23d7df6887ebc91aa, BUILT:Interlune]` -> `[tx-000057]`
  - `tx-000059`: `[tx-000058]` -> `[tx-000057]`

Private observation: legacy invokes `explore_paid(2, ...)` yet records the
resulting `OBSERVED` knowledge at authored year **2026**. The yearly path
preserves that year stamp, and compares it literally. It does not infer a
calendar year from kernel epoch 2 or rewrite the historical knowledge record.
This is a pre-calendar policy/evidence setup, not an annual observation step.

Known duplication: `screened_yearly.py` copies the original experiment setup
and `eligible_subcontract_parties` helper. Later removal should extract the
unchanged setup/eligibility into a single shared helper invoked by both entry
points, with exact legacy baseline regression first. Do not do that during this
stopped acceptance run: it would widen the change and risk frozen behavior.

The strict acceptance test is intentionally red on all three knowledge-order
mismatches. No baseline is modified. No merge is authorized.
