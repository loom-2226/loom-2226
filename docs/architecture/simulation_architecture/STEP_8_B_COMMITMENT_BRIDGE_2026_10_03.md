# Step B - Proposition feasibility and commitment bridge

**NON_CANON / UNPROMOTED**

## Purpose

Step B separates exploratory counterparty interest from consequential commitment. It introduces a feasibility firewall in front of the existing qualified Gate-G atomic transaction primitive. It does not create a parallel actor project engine.

An assembled proposition must independently resolve these authorities:

- SPENDABLE_BUDGET
- PROVIDER_CAPABILITY
- ACCESS
- TRANSPORT_FEASIBILITY
- INSURANCE
- CERTIFICATION
- REGULATORY

Each authority is KNOWN satisfied, KNOWN unsatisfied, or UNKNOWN. UNKNOWN blocks. NOT_REQUIRED is supported by the authority type but the initial mandatory set requires all seven; later concrete proposition classes may govern which are required.

Accepted Step-A exploratory responses prove only that a relevant counterparty is willing to investigate. They do not prove any substantive authority.

## Commit path

If and only if the feasibility firewall passes, the bridge constructs the existing Gate-G TransactionRequestV03. Gate G independently rechecks its own budget and provider-capacity authorities and atomically mutates budget, provider capacity, reservation, project, future event, provenance and committed-transaction ledgers.

A Gate-G COMMITTED project then uses existing Gate-H closed-loop machinery. No actor-specific project runtime has been added.

## Qualification controls

Positive control uses explicitly authored qualification authorities for all seven gates, a known budget and known provider capacity. It commits through Gate G and Gate H advances the project from COMMITTED through PROJECT_REVIEW to ACTIVE.

Negative/UNKNOWN controls:
- UNKNOWN transport feasibility blocks before Gate G with TRANSPORT_FEASIBILITY_UNKNOWN and no state mutation.
- KNOWN-unsatisfied certification blocks before Gate G with CERTIFICATION_UNSATISFIED.
- If bridge feasibility is positive but Gate-G budget is absent, Gate G independently rolls back with BUDGET_UNKNOWN.

## Real Step-A proposition control

The Honeybee Robotics (Blue Origin) Australian bulk-materials proposition cannot commit at this checkpoint.

The actor baseline's financial capacity is DERIVED_ESTIMATED initialization capacity. It is not a governed spendable allocation. Therefore SPENDABLE_BUDGET remains UNKNOWN. Exploratory counterparties likewise do not prove provider capability, access, transport feasibility, insurance, certification or regulatory satisfaction.

The real proposition is therefore BLOCKED rather than promoted using qualification-control facts.

## Firewalls

ACCEPT_EXPLORATION != AGREEMENT.
ESTIMATED_INITIAL_CAPACITY != SPENDABLE_BUDGET.
COUNTERPARTY PRESENT != COUNTERPARTY CAPABLE.
TRANSPORT INTEREST != TRANSPORT FEASIBILITY.
CERTIFIER INTEREST != CERTIFICATION.
REGISTRY INTEREST != REGULATORY APPROVAL.
FEASIBLE PROPOSITION != COMMITTED PROJECT.
COMMITMENT OCCURS ONLY THROUGH EXISTING GATE G.
