# Generic dated transport to money: Build 8 opt-in trial

**TEST_ONLY · NON-CANON · NON-RUNTIME · NOT merged on authoring.**

This is a small **generic** Build 8 consumer of merged `OnDemandTravel`,
not a Ceres-only travel subsystem. The authoring table in
`transport_money_rows.py` lists Ceres first and an illustrative Mars
project second. All project, sponsor, origin, destination, review trigger,
vehicle, source, wait, flight-range and funding choices live **only in
the rows**. The logic in `transport_to_money.py` contains no sponsor/body
special cases. The legacy Ceres money chain and all Build 7/frozen paths
are untouched.

## Source and assumptions

Both requirements use:
- A real observed Route 1 campaign review from the unchanged 90-body
  Ceres downstream run. The annually dated review's **year-end UTC**
  is a visible *settlement convention*, not a historical observation
  that the review occurred at 23:59:59 that day.
- Every calendar departure for **730 days**, with no weekly sampling.
- The same merged zero-rev prograde Lambert/direct SPICE path, default
  0.25-day flight durations, and a row-authorised **45–3000 day**
  flight bracket. Changing that bracket changes the geometry key.
- An explicitly TEST_ONLY 20-tonne-spacecraft `CARGO_DELIVERY`
  service with **10/10 km/s** endpoint caps. This is NOT qualified
  vehicle physics and 20 tonnes is not certified cargo capacity.
- A real Build 7 `CARGO_DELIVERY` 2026 median proportional-burden
  price anchor, held flat by provisional assumption. It is applied
  AFTER geometric lookup and vehicle filtering, not inside the cache.
  One-way quote in model currency:
  `Decimal(2026 service rate) * (departure_vinf + arrival_vinf) / 1000`,
  rounded once to six decimal places; selection uses minimum quoted
  price with deterministic tie breaks (departure/time/speeds).
- Commitment at the accepted order, **pay at departure**, and
  **TEST_ONLY scripted delivery at the modelled orbital arrival**.
  Orbital arrival is not qualified surface unloading.

The daily search scans the entire wait limit. An empty admissible set
reports `NO_FEASIBLE_DEPARTURE`, followed by
`WAIT_LIMIT_EXHAUSTED` at its deadline. A nonempty but unaffordable
quote reports `BLOCKED_UNAFFORDABLE` and has no order, payment,
departure, delivery, or productive capacity.

## Financial mechanics

Each new standalone seed-factory project uses actual **frozen Kernel**
account transfers. Original project capital is an authored, explicitly
labelled project input. The opt-in FUNDED row receives **one additional
TEST_ONLY opening source** equal to its selected transport quote:

    original_project_funds = 0.080 MODEL_CURRENCY
    seed_shipment_test_funding = selected_cargo_quote
    total_opt_in_source_funds = 0.080 + selected_cargo_quote

This is a transparent **scenario endowment**, not an internal minting
transaction. After setup, the sum across accounts is conserved exactly.
Capital is disbursed Earth→Offworld for the seed factory, and the
shipment's separate Earth→Earth transport payment is recorded with
`TRANSPORT_PAYMENT` only on actual departure. The equipment creates
productive capital only after scripted delivery through the kernel's
existing `spend_capex` and `capitalize` calls. The other row
retains only its authored base funds and demonstrates blocking.

The existing Earth-impact capital equation is preserved, not redefined:

    offworld_draw == new_capital_draw + recycled_returned_cash_spent

The dated gauge ALSO exposes **committed_unpaid**, **in_transit** and
**delivered_cumulative**. These are separate exposure/physical measures,
not additional capital draw. Dates belong to the Build 8 event manifest;
the kernel's year-only financial entries settle in the corresponding
calendar year. No income, capacity, or capitalisation precedes arrival.

## Determinism and scope

The scenario result includes a SHA-256 over complete stable-ordered
JSON state, including actual yearly ledger fingerprint and exact date
events. Wall-clock timing is excluded. The geometry key excludes
vehicle and price and includes source hashes, solver version, transfer
family and the *new* flight-duration grid identity. No geometry cache
file is saved into Git; opt-in caches belong outside the repository.
No fabricated freight physics, outer routes, sponsor agents, production
model, kernel modification, or historical Ceres retrospective mutation.

The first review builds the seed factory as a **separate opt-in financial
project** using the same frozen accounting engine; it does **not**
retcon the 2039–2045 original Ceres storyline. That original storyline's
8,798 transactions, 249 receipts and pinned returns/gauge stay intact.

The tests cover both rows using identical generic logic, 31 December
carryover, block/no feasible/exhaustion statuses, zero early capacity,
exact funding and cash conservation, byte-identical replay, and the
3,000-day cache signature. Real 730-day scans and the generated results
are inspected separately on quantifactus.
