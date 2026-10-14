"""Generic Build 8 TEST_ONLY dated freight-to-money consumer.

All project/sponsor/body choices are data. Frozen Kernel owns the real cash
transactions and capital formation. Build 8 owns exact UTC freight dates.
No new Agent behaviour, fabrication, or vehicle-physics claims.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal as D, ROUND_HALF_EVEN
from hashlib import sha256
import json

from offworld_kernel.kernel import Kernel
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .travel_pilot.on_demand import OnDemandTravel
from .travel_pilot.pilot import _day, _iso, price_table

USD_MILLION_TO_MODEL = D("0.001")
QUOTE_PRECISION = D("0.000001")
POLICY = "CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED"


def stable_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def ready_from_review(row, studies):
    """The dated ready trigger is an observed campaign review's annual close."""
    rule = row["prerequisite"]
    matching = [r for r in studies if all(r.get(key) == val for key, val in
                 rule.items())]
    if len(matching) != 1 or row["ready_rule"] != "ANNUAL_REVIEW_YEAR_END_UTC":
        return None
    year = int(matching[0]["year"])
    return datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)


def _price_rate(row, rates):
    vehicle = row["vehicle"]
    if (not row["test_only"] or row["price_rule"] !=
            "BUILD7_2026_HELD_CARGO_DELIVERY_RATE" or
            vehicle["service_type"] != "CARGO_DELIVERY" or
            row["payment_rule"] != "PAY_AT_DEPARTURE" or
            row["delivery_rule"] != "SCRIPTED_ON_ORBITAL_ARRIVAL"):
        raise ValueError("UNSUPPORTED_AUTHORED_FREIGHT_ASSUMPTION")
    rate = rates[(2026, vehicle["service_type"])]
    if rate["standing"] != "HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL":
        raise ValueError("UNQUALIFIED_PRICE_RATE")
    return D(str(rate["usd_millions_per_km_s_burden"])), rate


def _row_is_valid(row):
    if not 0 < row["wait_limit_days"] <= 3660:
        raise ValueError("INVALID_AUTHORED_WAIT_LIMIT")
    if tuple(row["flight_range_days"]) != (45.0, 3000.0):
        raise ValueError("UNSUPPORTED_AUTHORED_FLIGHT_RANGE")
    if D(row["original_project_funds"]) < D(row["construction_cost"]) > 0:
        raise ValueError("PROJECT_BASE_FUNDS_INSUFFICIENT")
    if not 0 < D(row["productive_capacity"]):
        raise ValueError("INVALID_TEST_CAPACITY")
    return row


def quote_and_choose(row, ready_date, *, geometry=None, rates=None):
    """Daily geometry first, then two endpoint limits, then 2026-held quote.

    Search the entire authored WAIT interval; cheapest wins, stable tie break.
    Geometry is from the merged lookup; no vehicle/price in its cache key.
    """
    _row_is_valid(row)
    engine = geometry if geometry is not None else OnDemandTravel()
    rate, rate_row = _price_rate(row, price_table()[0] if rates is None else rates)
    ready = _day(ready_date)
    best = None
    solves_start = engine.solve_count if hasattr(engine, "solve_count") else 0
    for day in range(row["wait_limit_days"]):
        departure = ready + timedelta(days=day)
        result = engine.lookup(
            row["origin"], row["destination"], departure,
            wait_limit_days=1,
            departure_limit=row["vehicle"]["max_departure_vinf_km_s"],
            arrival_limit=row["vehicle"]["max_arrival_vinf_km_s"],
            flight_range_days=row["flight_range_days"],
            strategy="daily")
        for opportunity in result["opportunities"]:
            epoch = _day(opportunity["departure"])
            for option in opportunity["options"]:
                burden = (D(str(option["departure_vinf_km_s"])) +
                          D(str(option["arrival_vinf_km_s"])))
                cost = (rate * burden * USD_MILLION_TO_MODEL).quantize(
                    QUOTE_PRECISION, rounding=ROUND_HALF_EVEN)
                candidate = dict(
                    departure=_iso(epoch),
                    arrival=_iso(epoch + timedelta(days=float(option["flight_days"]))),
                    flight_days=option["flight_days"],
                    wait_days=round((epoch - ready).total_seconds()/86400, 8),
                    departure_vinf_km_s=option["departure_vinf_km_s"],
                    arrival_vinf_km_s=option["arrival_vinf_km_s"],
                    cost_model_currency=str(cost),
                    cost_usd_millions=str(cost / USD_MILLION_TO_MODEL),
                    cost_basis="2026_HELD_CARGO_DELIVERY_PROPORTIONAL_PROXY",
                    price_source_sha256=rate_row["source_sha256"],
                    route=[row["origin"], row["destination"]])
                score = (cost, candidate["departure"],
                         candidate["flight_days"],
                         candidate["departure_vinf_km_s"],
                         candidate["arrival_vinf_km_s"])
                if best is None or score < best[0]:
                    best = (score, candidate)
        # The per-day in-memory cache is not retained over 730 dates. Optional
        # persistent geometry cache is managed by OnDemandTravel outside git.
        # This consumer itself has no cache infrastructure.
        if hasattr(engine, "_geometry"):
            engine._geometry.clear()
    return dict(
        status="AVAILABLE" if best is not None else "NO_FEASIBLE_DEPARTURE",
        policy=POLICY, ready_date=_iso(ready),
        deadline=_iso(ready + timedelta(days=row["wait_limit_days"])),
        wait_limit_days=row["wait_limit_days"],
        flight_range_days=list(row["flight_range_days"]),
        vehicle=row["vehicle"], chosen=best[1] if best else None,
        solves=(engine.solve_count - solves_start
                if hasattr(engine, "solve_count") else None))


def _treasury_route(row, kernel):
    """Use the existing public-agency return-routing treasury identity contract.

    Its three-year rule is for *recycled Ceres sale returns*. The funds used
    here are separately authored, dated TEST_ONLY national fiscal allocation
    receipts, not future Ceres returns. No fictional return receipt is created.
    """
    from .return_routing import DESTINATIONS, SOURCE
    route = DESTINATIONS.get((SOURCE, row["treasury_owner_type"]))
    if route is None or route[0] != "country_treasury":
        raise ValueError("PAYER_NOT_TREASURY_ROUTE")
    payer = row["payer_account"]
    country = row["financing_node"].removeprefix("EARTH:")
    if (row["financing_node"] != "EARTH:" + country or
            payer != "treasury:" + country or
            row["treasury_owner_id"] != "STATE:" + country):
        raise ValueError("TREASURY_OWNER_OR_COUNTRY_MISMATCH")
    account = kernel.state.accounts[payer]
    if (account.owner_id != row["treasury_owner_id"] or
            account.kind != AccountKind.FUNDS or
            account.node_id != row["financing_node"]):
        raise ValueError("TREASURY_ACCOUNT_INVARIANT")
    return payer


def _fiscal_allocation_plan(row, quote, departure):
    """Bound a TEST_ONLY fiscal allocation by actual authored country capacity.

    The capacities are derived from Earth long-run mobilisation, specifically
    its 75% *not* already assigned to the 25% Route 1 test. This does not
    represent prior Ceres returns and does not modify their routing policy.
    """
    if row["funding_mode"] != "TEST_ONLY_TREASURY_FISCAL_APPROPRIATION":
        return (), D(0)
    if not row["fiscal_source"].startswith("UNALLOCATED_75_PERCENT_OF_ROUTE1_"):
        raise ValueError("UNQUALIFIED_FISCAL_SOURCE")
    funding = []
    outstanding = quote
    for year, cap in sorted(row["fiscal_available_by_year"]):
        amount = min(outstanding, D(cap)) if year <= departure.year else D(0)
        if amount > 0:
            funding.append((int(year), amount))
            outstanding -= amount
        if outstanding <= 0:
            break
    return tuple(funding), outstanding


def settle_money_chain(row, ready_date, search, *, year_start=2026, year_end=2226,
                       report_freight_gauge=False):
    """Generic quote -> treasury appropriation -> Earth shipper -> delivery.

    Optional display projection returns (canonical_result, enriched_annual).
    The existing result, its bytes and its fingerprint are never modified.
    """
    _row_is_valid(row)
    ready = _day(ready_date)
    if search["ready_date"] != _iso(ready):
        raise ValueError("READY_EVIDENCE_MISMATCH")
    if not year_start <= ready.year <= year_end:
        raise ValueError("READY_DATE_OUTSIDE_CONDUCTOR")
    k = Kernel()
    project = row["project_id"]
    earth = row["financing_node"]
    off = "OFF:" + row["destination"]
    for node, kind in [(earth, NodeKind.EARTH), (off, NodeKind.OFFWORLD)]:
        k.add_node(node, kind)
    cash = project + ":cash"
    budget = project + ":sponsor_budget"
    carrier = project + ":shipper_cash"
    supplier = project + ":supplier_cash"
    payer = row["payer_account"]
    base = D(row["original_project_funds"])
    offer = search["chosen"]
    quote = D(offer["cost_model_currency"]) if offer else D(0)
    k.add_account(cash, project, off, AccountKind.PROJECT_CASH)
    k.add_account(budget, row["sponsor"], earth, AccountKind.FUNDS, base)
    # The treasury ALWAYS starts empty. It must receive real ledger
    # transactions from explicitly sourced annual fiscal capacity.
    k.add_account(payer, row["treasury_owner_id"], earth, AccountKind.FUNDS)
    k.add_account(carrier, project + ":shipper", earth, AccountKind.SUPPLIER)
    k.add_account(supplier, project + ":factory_supplier",
                  earth, AccountKind.SUPPLIER)
    k.add_project(project, off, cash)
    _treasury_route(row, k)
    opening_money = sum((a.balance for a in k.state.accounts.values()), D(0))
    assert k.state.accounts[payer].balance == 0

    fiscal_plan, unfunded = (
        _fiscal_allocation_plan(row, quote, _day(offer["departure"]))
        if offer else ((), D(0)))
    funded = (search["status"] == "AVAILABLE" and quote > 0
              and unfunded == 0 and sum((x for _, x in fiscal_plan), D(0)) == quote)
    events = []
    treasury_ledger = []
    shipment = dict(
        requirement_id=row["requirement_id"], project=project,
        sponsor=row["sponsor"], origin=row["origin"],
        destination=row["destination"], payer_account=payer,
        ready_date=_iso(ready), wait_limit_days=row["wait_limit_days"],
        vehicle=row["vehicle"], price_rule=row["price_rule"],
        payment_rule=row["payment_rule"], delivery_rule=row["delivery_rule"],
        flight_range_days=list(row["flight_range_days"]),
        departure=None, wait_days=None, arrival=None, flight_days=None,
        cost_model_currency=str(quote) if offer else None,
        payment_status="NOT_ORDERED", delivery_status="NOT_DELIVERED",
        status="READY", search_status=search["status"], policy=search["policy"],
        original_project_funds=str(base), treasury_opening="0",
        transport_payment_tx=None, appropriation_tx=None, construction_tx=None)
    if funded:
        shipment.update(departure=offer["departure"], wait_days=offer["wait_days"],
                        arrival=offer["arrival"], flight_days=offer["flight_days"],
                        offer=offer)
    event_queue = [(ready, 0, "READY", None)]
    if funded:
        for year, amount in fiscal_plan:
            moment = (ready if year == ready.year else
                      datetime(year, 1, 1, tzinfo=timezone.utc))
            event_queue.append((moment, 1, "FISCAL_RECEIPT", amount))
        event_queue.extend([
            (ready, 2, "ORDER", None),
            (_day(offer["departure"]), 3, "APPROPRIATE_PAY_DEPART", None),
            (_day(offer["arrival"]), 4, "ARRIVE_AND_DELIVER", None)])
    elif search["status"] == "AVAILABLE":
        shipment["status"] = "BLOCKED_TREASURY_UNFUNDED"
        shipment["payment_status"] = "NOT_PAID"
        shipment["blocked_quote"] = offer
    else:
        event_queue.append((ready + timedelta(days=row["wait_limit_days"]),
                            5, "WAIT_LIMIT_EXHAUSTED", None))
    event_queue.sort(key=lambda x: (x[0], x[1]))
    fiscal_inflow = D(0)
    fiscal_receipt_txs = []
    yearly = []
    i = 0
    for year in range(year_start, year_end + 1):
        while i < len(event_queue) and event_queue[i][0].year == year:
            when, _, action, payload = event_queue[i]
            i += 1
            if action == "READY":
                k.add_commitment(project + ":development_finance",
                                 row["sponsor"], project, base)
                k.disburse(year, project + ":development_finance", budget, base)
                events.append(dict(date=_iso(when), type="READY",
                                   project=project, status="FUNDED_BASE_PROJECT"))
            elif action == "FISCAL_RECEIPT":
                # Existing Route1 country-capital pattern: a YEAR-specific
                # external Earth mobilisation source, not an opening
                # TEST_ONLY_EARTH_FUNDING balance. The spend is bounded by
                # the unused national-fiscal capacity declared in the row.
                source = project + ":national_fiscal_origin:" + str(year)
                k.add_account(source, "COUNTRY:" + earth.removeprefix("EARTH:"),
                              earth, AccountKind.EARTH_BOUNDARY, payload)
                before = k.state.accounts[payer].balance
                tx = k.transfer(year, source, payer, payload,
                                TxPurpose.OTHER_INVESTMENT)
                fiscal_inflow += payload
                fiscal_receipt_txs.append(tx.id)
                assert k.state.accounts[source].balance == 0
                treasury_ledger.append(dict(year=year, action="FISCAL_RECEIPT",
                    source_account=source, treasury_before=str(before),
                    amount=str(payload), treasury_after=str(k.state.accounts[payer].balance),
                    tx=tx.id, test_only=True))
                events.append(dict(date=_iso(when), type="TEST_ONLY_FISCAL_RECEIPT",
                                   amount=str(payload), tx=tx.id))
            elif action == "ORDER":
                shipment["status"] = "COMMITTED"
                shipment["payment_status"] = "COMMITTED_UNPAID"
                events.append(dict(date=_iso(when), type="ORDER_COMMITMENT",
                                   amount=str(quote), project=project))
            elif action == "APPROPRIATE_PAY_DEPART":
                before = k.state.accounts[payer].balance
                if before < quote:
                    raise AssertionError("TREASURY_FUNDS_MISSING_AT_DEPARTURE")
                # Same PUBLIC_SUBSIDY appropriation path as return_routing's
                # Ceres downstream spending. Here the authority is a
                # separately authored, contemporary fiscal allocation.
                ap = k.transfer(year, payer, budget, quote,
                    TxPurpose.PUBLIC_SUBSIDY, parent_ids=tuple(fiscal_receipt_txs))
                shipment["appropriation_tx"] = ap.id
                treasury_ledger.append(dict(year=year, action="APPROPRIATION",
                    source_account=payer, destination_account=budget,
                    treasury_before=str(before), amount=str(quote),
                    treasury_after=str(k.state.accounts[payer].balance),
                    tx=ap.id, receipt_txs=list(fiscal_receipt_txs),
                    test_only=True))
                events.append(dict(date=_iso(when), type="TREASURY_APPROPRIATION",
                                   amount=str(quote), tx=ap.id,
                                   payer_account=payer))
                tx = k.transfer(year, budget, carrier, quote,
                                TxPurpose.TRANSPORT_PAYMENT,
                                parent_ids=(ap.id, project + ":transport_order"))
                shipment["transport_payment_tx"] = tx.id
                shipment["payment_status"] = "PAID_AT_DEPARTURE"
                shipment["delivery_status"] = "IN_TRANSIT"
                shipment["status"] = "IN_TRANSIT"
                events.extend([
                    dict(date=_iso(when), type="PAYMENT", amount=str(quote),
                         tx=tx.id, source_account=budget,
                         destination_account=carrier),
                    dict(date=_iso(when), type="DEPARTURE", status="IN_TRANSIT")])
            elif action == "ARRIVE_AND_DELIVER":
                if shipment["payment_status"] != "PAID_AT_DEPARTURE":
                    raise AssertionError("SHIPMENT_NOT_PAID")
                events.extend([
                    dict(date=_iso(when), type="ARRIVAL"),
                    dict(date=_iso(when), type="DELIVERY",
                         standing="TEST_ONLY_SCRIPTED_ON_ORBITAL_ARRIVAL")])
                shipment["delivery_status"] = "DELIVERED_SCRIPTED"
                tx = k.spend_capex(year, project, supplier,
                    D(row["construction_cost"]), project + ":factory_asset", off)
                k.capitalize(project + ":factory_asset",
                             D(row["productive_capacity"]))
                shipment["construction_tx"] = tx.id
                shipment["status"] = "BUILT_AFTER_DELIVERY"
                events.append(dict(date=_iso(when), type="BUILD",
                                   tx=tx.id, capacity=row["productive_capacity"]))
            elif action == "WAIT_LIMIT_EXHAUSTED":
                shipment["status"] = "WAIT_LIMIT_EXHAUSTED"
                events.append(dict(date=_iso(when), type="WAIT_LIMIT_EXHAUSTED",
                                   predecessor="NO_FEASIBLE_DEPARTURE"))
        total_money = sum((a.balance for a in k.state.accounts.values()), D(0))
        assert total_money == opening_money + fiscal_inflow, (
            "CASH_CONSERVATION_FAILURE", year)
        k.assert_invariants()
        close = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        committed = (quote if shipment["departure"] and
                     ready <= close < _day(shipment["departure"]) else D(0))
        transit = (quote if shipment["departure"] and
                   _day(shipment["departure"]) <= close <
                   _day(shipment["arrival"]) else D(0))
        delivered = (quote if shipment["departure"] and
                     _day(shipment["arrival"]) <= close and
                     shipment["delivery_status"] == "DELIVERED_SCRIPTED"
                     else D(0))
        draw = k.state.earth_impact.capital_diverted_to_offworld.get(
            (earth, year), D(0))
        recycled = D(0)
        yearly.append(dict(year=year,
            treasury_balance=str(k.state.accounts[payer].balance),
            committed_unpaid=str(committed), in_transit=str(transit),
            delivered_cumulative=str(delivered),
            new_capital_draw=str(draw - recycled),
            recycled_returned_cash_spent=str(recycled),
            offworld_draw=str(draw),
            capacity=(str(k.state.assets[project + ":factory_asset"].capacity)
                      if project + ":factory_asset" in k.state.assets else "0")))
        assert draw == (draw - recycled) + recycled
    shipment["funding_calculation"] = dict(
        original_funds=str(base), shipment_quote=str(quote),
        treasury_opening="0",
        TEST_ONLY_fiscal_allocation=sum((a for _, a in fiscal_plan), D(0)).__str__()
            if funded else "0",
        treasury_appropriation=str(quote) if funded else "0",
        treasury_after=str(k.state.accounts[payer].balance),
        original_plus_external_fiscal=str(opening_money + fiscal_inflow),
        construction_reserved_from_original=row["construction_cost"])
    if search["status"] == "NO_FEASIBLE_DEPARTURE":
        shipment["payment_status"] = "NO_PAYMENT"
    result = dict(classification="BUILD8_TEST_ONLY_NON_CANON_NON_RUNTIME",
        project=project, shipment=shipment, events=events, annual=yearly,
        treasury_ledger=treasury_ledger,
        kernel_fingerprint=k.fingerprint(),
        transaction_count=len(k.state.transactions),
        money_initial=str(opening_money),
        money_external_fiscal=str(fiscal_inflow),
        money_final=str(sum((a.balance for a in k.state.accounts.values()), D(0))),
        productive_capacity=(str(k.state.assets[project + ":factory_asset"].capacity)
                             if project + ":factory_asset" in k.state.assets else "0"))
    result["fingerprint"] = sha256(stable_bytes(result)).hexdigest()
    if report_freight_gauge:
        from .freight_gauge import with_earth_side_freight_line
        return result, with_earth_side_freight_line(k.state, yearly)
    return result
