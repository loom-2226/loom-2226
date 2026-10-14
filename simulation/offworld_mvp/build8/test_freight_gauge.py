"""One additive, Earth-side freight *report line*, no canonical state mutation."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal as D
from unittest import TestCase

from offworld_kernel.kernel import Kernel
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .freight_gauge import LINE, eligible_transport_payments, with_earth_side_freight_line
from .transport_money_rows import AUTHORED_TRANSPORT_ROWS
from .transport_to_money import ready_from_review, settle_money_chain, stable_bytes, _iso

# Exact real-trajectory candidate from PR #410's fully scanned 730-day window.
# No flight algorithm, price, wait, vehicle or delivery setting changes.
STUDIES = (
    dict(body="CERES", stage="A2", review="ADVANCE",
         result="SUPPORTS_ADVANCE", year=2038),
    dict(body="MARS", stage="A1", review="ADVANCE",
         result="SUPPORTS_ADVANCE", year=2037),
)
CANDIDATES = (
    dict(departure="2039-07-01T23:59:59Z",
         arrival="2040-07-15T23:59:59Z", wait_days=182.,
         flight_days=380., cost_model_currency="2.660653"),
    dict(departure="2039-09-19T23:59:59Z",
         arrival="2040-08-25T05:59:59Z", wait_days=627.,
         flight_days=341.25, cost_model_currency="1.164017"),
)


def completed_search(row, index):
    ready = ready_from_review(row, STUDIES)
    return ready, dict(status="AVAILABLE", policy="CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED",
                       ready_date=_iso(ready), chosen=CANDIDATES[index])


class FreightGaugeTests(TestCase):
    def test_ceres_2039_real_quote_once_and_no_pin_changed(self):
        row = AUTHORED_TRANSPORT_ROWS[0]
        ready, search = completed_search(row, 0)
        before = settle_money_chain(row, ready, search)
        after, annual = settle_money_chain(
            row, ready, search, report_freight_gauge=True)
        self.assertEqual(stable_bytes(before), stable_bytes(after))
        self.assertEqual(before["fingerprint"], after["fingerprint"])
        self.assertEqual(
            [{k: v for k, v in line.items() if k != LINE} for line in annual],
            before["annual"])
        amounts = {entry["year"]: D(entry[LINE]) for entry in annual}
        self.assertEqual(amounts[2039], D("2.660653"))
        self.assertEqual(amounts[2038], D(0))
        self.assertEqual(amounts[2040], D(0))
        self.assertEqual(sum(amounts.values(), D(0)), D("2.660653"))
        self.assertEqual(len(annual), 201)
        self.assertEqual(before["shipment"]["transport_payment_tx"],
                         next(e["tx"] for e in before["events"] if e["type"]=="PAYMENT"))
        self.assertEqual(sum(e["type"]=="PAYMENT" for e in before["events"]), 1)
        self.assertTrue(all(
            D(x["new_capital_draw"]) + D(x["recycled_returned_cash_spent"])
                == D(x["offworld_draw"])
            for x in annual))
        self.assertEqual(D(next(x for x in annual if x["year"]==2038)
                            ["offworld_draw"]), D("0.080"))
        self.assertEqual(D(next(x for x in annual if x["year"]==2039)
                            ["offworld_draw"]), D(0))
        self.assertEqual(D(next(x for x in annual if x["year"]==2039)
                            ["in_transit"]), D("2.660653"))

    def test_mars_unfunded_is_visible_zero_not_missing(self):
        row = AUTHORED_TRANSPORT_ROWS[1]
        ready, search = completed_search(row, 1)
        baseline = settle_money_chain(row, ready, search)
        original, gauge = settle_money_chain(
            row, ready, search, report_freight_gauge=True)
        self.assertEqual(stable_bytes(baseline), stable_bytes(original))
        self.assertEqual(original["shipment"]["status"],
                         "BLOCKED_TREASURY_UNFUNDED")
        self.assertTrue(all(x[LINE] == "0" for x in gauge))
        self.assertTrue(all(LINE in x for x in gauge))
        self.assertTrue(all(
            D(x["new_capital_draw"]) + D(x["recycled_returned_cash_spent"])
                == D(x["offworld_draw"]) for x in gauge))

    def test_empty_ceres_treasury_and_no_feasible_both_zero(self):
        row = deepcopy(AUTHORED_TRANSPORT_ROWS[0])
        row["fiscal_available_by_year"] = ()
        ready, search = completed_search(row, 0)
        result, gauge = settle_money_chain(
            row, ready, search, report_freight_gauge=True)
        self.assertEqual(result["shipment"]["status"],
                         "BLOCKED_TREASURY_UNFUNDED")
        self.assertTrue(all(x[LINE] == "0" for x in gauge))
        no_flight = dict(search, status="NO_FEASIBLE_DEPARTURE", chosen=None)
        result, gauge = settle_money_chain(
            row, ready, no_flight, report_freight_gauge=True)
        self.assertEqual(result["shipment"]["status"], "WAIT_LIMIT_EXHAUSTED")
        self.assertTrue(all(x[LINE] == "0" for x in gauge))

    def test_each_qualifying_payment_counted_once_no_false_inclusion(self):
        k = Kernel()
        k.add_node("EARTH:A", NodeKind.EARTH)
        k.add_node("EARTH:B", NodeKind.EARTH)
        k.add_node("OFF:TARGET", NodeKind.OFFWORLD)
        k.add_account("payer", "sponsor", "EARTH:A", AccountKind.FUNDS, D(100))
        k.add_account("shipper", "carrier", "EARTH:B", AccountKind.SUPPLIER)
        k.add_account("offworld", "project", "OFF:TARGET",
                      AccountKind.PROJECT_CASH, D(10))
        k.add_project("PROJECT", "OFF:TARGET", "offworld")
        first = k.transfer(2039, "payer", "shipper", D("2.5"),
                           TxPurpose.TRANSPORT_PAYMENT,
                           parent_ids=("PROJECT:transport_order",))
        second = k.transfer(2039, "payer", "shipper", D("2.5"),
                            TxPurpose.TRANSPORT_PAYMENT,
                            parent_ids=("PROJECT",))
        k.transfer(2039, "payer", "shipper", D(6),
                   TxPurpose.TRANSPORT_PAYMENT,
                   parent_ids=("UNLINKED_PROJECT:transport_order",))
        k.transfer(2039, "payer", "shipper", D(7),
                   TxPurpose.PUBLIC_SUBSIDY,
                   parent_ids=("PROJECT:transport_order",))
        k.transfer(2039, "payer", "offworld", D(8),
                   TxPurpose.TRANSPORT_PAYMENT,
                   parent_ids=("PROJECT:transport_order",))
        k.transfer(2039, "offworld", "shipper", D(4),
                   TxPurpose.TRANSPORT_PAYMENT,
                   parent_ids=("PROJECT:transport_order",))
        qualifying = eligible_transport_payments(k.state)
        self.assertEqual([tx.id for tx in qualifying], [first.id, second.id])
        gauge = with_earth_side_freight_line(
            k.state, [dict(year=y, offworld_draw="0") for y in (2038,2039,2040)])
        self.assertEqual([x[LINE] for x in gauge], ["0","5.0","0"])
        self.assertTrue(all(x["offworld_draw"]=="0" for x in gauge))
