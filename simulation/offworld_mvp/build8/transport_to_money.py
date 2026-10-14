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


def settle_money_chain(row, ready_date, search, *, year_start=2026, year_end=2226):
    """One generic project, using real frozen-kernel transfers and assets."""
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
        k.add_node(node,kind)
    cash = project+":cash"
    budget = project+":sponsor_budget"
    seed = project+":test_only_seed_funding"
    carrier = project+":carrier_cash"
    supplier = project+":supplier_cash"
    base = D(row["original_project_funds"])
    quote = D(search["chosen"]["cost_model_currency"]) if search["chosen"] else D(0)
    fund_seed = row["funding_mode"] == "TEST_ONLY_FUNDED_FROM_SELECTED_QUOTE"
    seeded = quote if fund_seed else D(0)
    k.add_account(cash,project,off,AccountKind.PROJECT_CASH)
    k.add_account(budget,row["sponsor"],earth,AccountKind.FUNDS,base)
    k.add_account(seed,"TEST_ONLY_EARTH_FUNDING",earth,AccountKind.EARTH_BOUNDARY,seeded)
    k.add_account(carrier,project+":carrier",earth,AccountKind.SUPPLIER)
    k.add_account(supplier,project+":factory_supplier",earth,AccountKind.SUPPLIER)
    k.add_project(project,off,cash)
    total_initial = sum((a.balance for a in k.state.accounts.values()),D(0))
    events = []
    shipment = dict(
        requirement_id=row["requirement_id"],project=project,sponsor=row["sponsor"],
        origin=row["origin"],destination=row["destination"],
        ready_date=_iso(ready),wait_limit_days=row["wait_limit_days"],
        vehicle=row["vehicle"],price_rule=row["price_rule"],
        payment_rule=row["payment_rule"],delivery_rule=row["delivery_rule"],
        flight_range_days=list(row["flight_range_days"]),
        departure=None,wait_days=None,arrival=None,flight_days=None,
        cost_model_currency=str(quote) if search["chosen"] else None,
        payment_status="NOT_ORDERED",delivery_status="NOT_DELIVERED",
        status="READY",search_status=search["status"],policy=search["policy"],
        seed_funding=str(seeded),original_project_funds=str(base),
        total_initial_funding=str(total_initial),
        transport_payment_tx=None,construction_tx=None)
    offer=search["chosen"]
    if offer and fund_seed:
        shipment.update(
            departure=offer["departure"],wait_days=offer["wait_days"],
            arrival=offer["arrival"],flight_days=offer["flight_days"],
            offer=offer)
    # Even a blocked project retains its historically authored baseline funds.
    # The ONLY additional money in this opt-in simulation is the explicit
    # TEST_ONLY seeded source, equal to the selected transportation quote.
    event_queue=[(ready,0,"READY")]
    if search["status"]=="AVAILABLE" and quote>0 and base+seeded>=base+quote:
        event_queue.extend([(ready,1,"ORDER"),
            (_day(offer["departure"]),2,"PAY_AND_DEPART"),
            (_day(offer["arrival"]),3,"ARRIVE_AND_DELIVER")])
    elif search["status"]=="AVAILABLE":
        shipment["status"]="BLOCKED_UNAFFORDABLE"
        shipment["payment_status"]="NOT_PAID"
        shipment["delivery_status"]="NOT_DELIVERED"
        shipment["blocked_quote"]=offer
    else:
        event_queue.append((ready+timedelta(days=row["wait_limit_days"]),
                            4,"WAIT_LIMIT_EXHAUSTED"))
    event_queue.sort(key=lambda x:(x[0],x[1]))
    yearly=[]
    i=0
    total_payment=D(0)
    for year in range(year_start,year_end+1):
        while i<len(event_queue) and event_queue[i][0].year==year:
            when,_,action=event_queue[i];i+=1
            if action=="READY":
                k.add_commitment(project+":development_finance",row["sponsor"],project,base)
                k.disburse(year,project+":development_finance",budget,base)
                # The seed is test-only exogenous INITIAL money, not a minted
                # transaction. This is just an Earth-to-Earth funding sweep.
                if seeded:
                    k.transfer(year,seed,budget,seeded,TxPurpose.OTHER_INVESTMENT)
                events.append(dict(date=_iso(when),type="READY",
                                   status="FUNDED_BASE_PROJECT",project=project))
            elif action=="ORDER":
                shipment["status"]="COMMITTED"
                shipment["payment_status"]="COMMITTED_UNPAID"
                events.append(dict(date=_iso(when),type="ORDER_COMMITMENT",
                                   amount=str(quote),project=project))
            elif action=="PAY_AND_DEPART":
                tx=k.transfer(year,budget,carrier,quote,TxPurpose.TRANSPORT_PAYMENT,
                              parent_ids=(project+":transport_order",))
                total_payment+=quote
                shipment["transport_payment_tx"]=tx.id
                shipment["payment_status"]="PAID_AT_DEPARTURE"
                shipment["delivery_status"]="IN_TRANSIT"
                shipment["status"]="IN_TRANSIT"
                events.extend([
                    dict(date=_iso(when),type="PAYMENT",amount=str(quote),tx=tx.id),
                    dict(date=_iso(when),type="DEPARTURE",status="IN_TRANSIT")])
            elif action=="ARRIVE_AND_DELIVER":
                if shipment["payment_status"]!="PAID_AT_DEPARTURE":
                    raise AssertionError("SHIPMENT_NOT_PAID")
                events.extend([
                    dict(date=_iso(when),type="ARRIVAL"),
                    dict(date=_iso(when),type="DELIVERY",
                         standing="TEST_ONLY_SCRIPTED_ON_ORBITAL_ARRIVAL")])
                shipment["delivery_status"]="DELIVERED_SCRIPTED"
                tx=k.spend_capex(year,project,supplier,D(row["construction_cost"]),
                                 project+":factory_asset",off)
                k.capitalize(project+":factory_asset",D(row["productive_capacity"]))
                shipment["construction_tx"]=tx.id
                shipment["status"]="BUILT_AFTER_DELIVERY"
                events.append(dict(date=_iso(when),type="BUILD",
                                   tx=tx.id,capacity=row["productive_capacity"]))
            elif action=="WAIT_LIMIT_EXHAUSTED":
                shipment["status"]="WAIT_LIMIT_EXHAUSTED"
                events.append(dict(date=_iso(when),type="WAIT_LIMIT_EXHAUSTED",
                                   predecessor="NO_FEASIBLE_DEPARTURE"))
        assert sum((a.balance for a in k.state.accounts.values()),D(0))==total_initial, (
            "CASH_CONSERVATION_FAILURE",year)
        k.assert_invariants()
        year_close=datetime(year,12,31,23,59,59,tzinfo=timezone.utc)
        committed = quote if (shipment["departure"] and ready<=year_close<
                              _day(shipment["departure"])) else D(0)
        in_transit = quote if (shipment["departure"] and
                      _day(shipment["departure"])<=year_close<
                      _day(shipment["arrival"])) else D(0)
        delivered = quote if (shipment["departure"] and
                     _day(shipment["arrival"])<=year_close and
                     shipment["delivery_status"]=="DELIVERED_SCRIPTED") else D(0)
        impact=k.state.earth_impact.capital_diverted_to_offworld
        draw=impact.get((earth,year),D(0))
        recycled=D(0)
        yearly.append(dict(year=year,
           committed_unpaid=str(committed),in_transit=str(in_transit),
           delivered_cumulative=str(delivered),
           new_capital_draw=str(draw-recycled),
           recycled_returned_cash_spent=str(recycled),
           offworld_draw=str(draw),
           capacity=str(k.state.assets[project+":factory_asset"].capacity)
                if project+":factory_asset" in k.state.assets else "0"))
        assert draw==(draw-recycled)+recycled
    shipment["funding_calculation"]={
        "original_funds":str(base),"shipment_quote":str(quote),
        "additional_TEST_ONLY_seed":str(seeded),
        "total_available":str(base+seeded),
        "required_original_plus_quote":str(base+quote),
        "construction_reserved_from_original":row["construction_cost"]}
    if search["status"]=="NO_FEASIBLE_DEPARTURE":
        shipment["payment_status"]="NO_PAYMENT"
        shipment["delivery_status"]="NOT_DELIVERED"
    result=dict(classification="BUILD8_TEST_ONLY_NON_CANON_NON_RUNTIME",
       project=project,shipment=shipment,events=events,annual=yearly,
       kernel_fingerprint=k.fingerprint(),
       transaction_count=len(k.state.transactions),
       money_initial=str(total_initial),
       money_final=str(sum((a.balance for a in k.state.accounts.values()),D(0))),
       productive_capacity=str(
            k.state.assets[project+":factory_asset"].capacity
            if project+":factory_asset" in k.state.assets else D(0)))
    result["fingerprint"]=sha256(stable_bytes(result)).hexdigest()
    return result
