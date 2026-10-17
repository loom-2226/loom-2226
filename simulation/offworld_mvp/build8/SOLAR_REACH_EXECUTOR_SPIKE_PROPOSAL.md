# Executor-first Solar Reach spike: proposal first

BASE: 19377b854c529e74afc61202d9eb2e780c5b4884
CLASS: Build 8 noncanon TEST_ONLY in-memory kernel experiment
AUTHORIZED: One new DRAFT PR, no edits to pre-existing PR #423 or #424.

## Single experiment and scope
- One canonical solar_reach_cast.json owns ALL experimental parameters
  including scenarios, clock, source references, opening money, sponsor wants,
  executor opening beliefs, real/estimate cost, cash, capacity, bid/refusal
  policy, award policy, outcome schedule, and comparison mutations.
- Full public Solar catalog, full 2026–2226 clock, both short and long casts.
  No actor/body/year count constants in new code.
- Use unchanged kernel accounts, agents (Sponsor only), transfers and
  invariants. Executor is a Build8-local autonomous decision object because
  frozen AgentKind has no EXECUTOR; never falsely type it as Sponsor.
- One contested initial contract, with one later authored qualifying
  request so a delivery/failure outcome can affect a subsequent real bid.
- Each Executor sees only its own cash/capacity/market and reliability
  beliefs and contract. TEST_ONLY outcome is host-only until delivered, never
  in the decision input. Market-price and risk beliefs update from observed
  public outcomes/award prices according to authored learning rules.
- Source pins and complete canonical authored cast file are printed.
  Run identity includes scenario digest, selected cast, pinned source files,
  resolved initial beliefs and all experiment parameters. Replay digest
  includes all per-year body states, kernel ledger and evolving beliefs.
- Two complete reruns for each cast: compare both to first fingerprint.
  For every year assert conserved money and no overlapping capacity.
- Knob tests: capacity, margin, price belief, reliability prior, funding
  must each cause a named award, bid, cost or decision change.
- Outcome labels explicitly TEST_ONLY, not WORLD truth/physical arrival.
  All bodies remain represented, but ineligible identities remain idle.

## STOP
Any frozen edit, duplicated account/transfer ledger, hidden WORLD value,
invented physical mission/population, fixed cast/body/year count, or
non-reproducible or source-unpinned outcome. No DB, WORLD or WALTER.

## PR preparation rule
Commit proposal BEFORE implementation, tests and report on same
private branch. Open draft PR once only when finished. Do not edit the
opened PR further without asking kT first.
