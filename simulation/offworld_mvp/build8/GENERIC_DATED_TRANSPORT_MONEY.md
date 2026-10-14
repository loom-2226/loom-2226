# Build 8 generic dated transport-to-money consumer

**TEST_ONLY · NON-CANON · NON-RUNTIME · PR #410 (review only, do not merge)**

The existing legacy Ceres money chain, Build 7 inputs, frozen kernel and
original travel pilot remain unchanged. The generic code handles requirements
authored in `transport_money_rows.py` without sponsor/body special cases.
The first row is Ceres seed equipment (Earth→Ceres, funded). The second is an
illustrative Mars project (Earth→Mars, treasury-unfunded). Both rows use an
observed Route 1 review as their readiness trigger, dated at the **end of its
review year** by an explicit TEST_ONLY annual-settlement convention.

## Authored transport assumptions

- `CARGO_DELIVERY` at the Build 7 2026-held *provisional* rate, not a certified
  freight market price or service.
- TEST_ONLY 10/10 km/s departure/arrival v-infinity caps, **not** qualified
  vehicle physics. The Build 7 20-tonne spacecraft assumption is NOT proof
  of 20 tonnes of usable cargo capacity.
- An authored 730-day departure wait limit, daily sampled departures and
  45–3000-day transfer-duration grid at 0.25-day flight-time spacing.
  The duration bracket is in the geometry cache key; vehicle limits and
  prices are not.
- `CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED`: select cheapest eligible trajectory,
  deterministic tie-breaking, commit on readiness, pay on actual departure.
- TEST_ONLY delivery on the modeled orbital arrival date; **not** a qualified
  descent, cargo unloading, or real-world surface delivery capability.

## Treasury correction: no prefilled seed-funding account

There is NO `TEST_ONLY_EARTH_FUNDING` opening account and no corresponding
prepaid seed balance. Both treasuries begin with **zero**. Each requirement
names the actual payer treasury account, its owner and its country:
`treasury:IND` (Ceres row) or `treasury:TEST` (illustrative Mars row).
The generic consumer checks the existing `return_routing.DESTINATIONS`
public-agency → `country_treasury` rule and the treasury account's country,
owner and account kind, analogous to `resolve_destination`.

The original downstream returned-proceeds appropriation policy has a
**three-year delay** for Ceres owner-return receipts from export sales. The
2039 seed shipment **cannot** be financed from those returns, which do not
exist yet. This experiment uses an explicitly authorised and labelled
**TEST_ONLY national fiscal allocation**, *not* fabricated Ceres returns.
It is bounded by India's modeled national mobilisation that is NOT already
used by Route 1's existing 25% allocation. These source budget caps are
visible in the Ceres data row, derived from the unchanged Earth country
capital inputs and existing `derive_mobilization` law:

| Fiscal year | National mobilisation | Already allocated Route 1 (25%) | Remaining 75% test-only ceiling |
|---|---:|---:|---:|
| 2038 | 2.3877642952672773 | 0.596941073816819325 | 1.790823221450457975 |
| 2039 | 2.5160735260347217 | 0.629018381508680425 | 1.887055144526041275 |

All amounts are MODEL_CURRENCY. These remaining-capacity ceilings are
**not themselves a fiscal commitment**, and no general budget or government
behavior is being added. In this single opt-in demo, the authored fiscal
source releases only the quote amount through year-specific
`EARTH_BOUNDARY` country-origin accounts and *actual frozen-kernel
`transfer` transactions* crediting `treasury:IND`. Each country origin
ends at zero. Thus the treasury's money is received through dated
ledger transactions; **its opening balance is zero**. The external fiscal
envelopes and credited inflows are disclosed, not hidden "free money".
This is the same annual-source accounting idiom used by Route 1, not a
claim that a new source is already canonically appropriated.

The next transfer follows the existing Ceres appropriation pattern:
`treasury:IND → sponsor_budget` with `TxPurpose.PUBLIC_SUBSIDY`, linked
to the treasury's fiscal-credit transaction IDs. Then
`sponsor_budget → Earth-side shipper` with `TRANSPORT_PAYMENT`, linked
to the appropriation transaction. **Both are Earth-to-Earth transfers**;
neither adds to `offworld_draw`. The only Earth-to-Offworld capital draw
is the original `0.080` project disbursement. The separate gauges for
committed, in transit and delivered do not double-count that draw.

### Completed real-trajectory quote and treasury arithmetic

The previously completed full 730-daily-departure, 45–3000-day Lambert
search (11,821 flight-duration samples per day, 8,629,330 solves per
route) selected the following Ceres option:

- Ready: **2038-12-31 23:59:59 UTC** (observed positive 2038 A2 review,
  explicit synthetic annual-close dating).
- Cheapest admissible trajectory in the searched window: departs
  **2039-07-01 23:59:59 UTC**, waits **182 days**, flies **380 days**,
  arrives **2040-07-15 23:59:59 UTC**.
- Endpoint speeds: **6.5147334** and **7.244754** km/s.
- Held-2026 cargo rate: **193.368615750 USD million/(km/s)**.
- Quote (rounded to 6 decimals): **2.660653 MODEL_CURRENCY**.

The treasury's actual TEST_ONLY ledger trace is:

| Event | Treasury before | Change | Treasury after | Transaction |
|---|---:|---:|---:|---|
| Opening | 0 | 0 | 0 | None |
| 2038 fiscal receipt | 0 | +1.790823221450457975 | 1.790823221450457975 | tx-000002 |
| 2039 fiscal receipt | 1.790823221450457975 | +0.869829778549542025 | 2.660653 | tx-000003 |
| 2039 appropriation | 2.660653 | −2.660653 | **0** | tx-000004 |

The appropriation amount is derived exactly from the selected freight quote:
`2.660653 = 1.790823221450457975 + 0.869829778549542025`.
The sponsor then pays the Earth shipper at departure, from those
appropriated funds. The original project funds remain **0.080** and
pay the original capital disbursement and subsequent **0.060** CAPEX.

**Money reconciliation** (not a claim that the Earth fiscal envelope was
pre-existing spendable treasury cash):

`opening modeled accounts 0.080 + separately modelled fiscal ingress 2.660653
 = ending modeled account balances 2.740653`.

The treasury itself opens **0** and closes **0**, and every fiscal receipt,
appropriation and payment has actual frozen-ledger transaction lineage.

### Annual consequence and negative controls

| Year close | Unpaid commitment | In transit | Delivered | Factory capacity |
|---|---:|---:|---:|---:|
| 2038 | 2.660653 | 0 | 0 | 0 |
| 2039 | 0 | 2.660653 | 0 | **0** |
| 2040 | 0 | 0 | 2.660653 | **5** |

The actual **Mars** row (ready at 2037 A1 review year end) discovers a
cheapest eligible quote **1.164017 MODEL_CURRENCY** with candidate
departure 2039-09-19, but has `treasury:TEST` opening/closing **0**,
no authored fiscal receipt and no appropriation. Therefore it is
`BLOCKED_TREASURY_UNFUNDED`: real departure/arrival dates **null**,
no payment, no delivery and zero capacity. The separate Ceres
empty-treasury test overrides the fiscal receipt schedule to empty,
and also blocks without cash mutation or factory capacity.

`NO_FEASIBLE_DEPARTURE` and `WAIT_LIMIT_EXHAUSTED` remain distinct,
focused-tested no-geometry conditions, not invented descriptions of the
affordable or unaffordable cases.

The local finance-only re-settlement reuses the **completed full-search
geometry choices unchanged** and replays both rows twice, producing
byte-identical JSON and the corrected completed-scenario fingerprint:

`46e390772ed0ef4cca3d07e79e39a4dfa1a26db5c774162a77dff7887b0b0563`

The complete generated record is outside Git:
`/tmp/loom-transport-money-20261015-treasury-correction.json`.
The old scenario fingerprint is superseded, not a claim of the same
state. Legacy Ceres stays pinned at **8,798 transactions**, **249**
campaign receipts; the existing Build 7 tests remain untouched.

**No merge without kT approval.**
