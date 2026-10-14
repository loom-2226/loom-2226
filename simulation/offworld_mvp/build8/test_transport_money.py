"""Focused Build 8 generic dated seed-shipment money tests (no runtime consumers)."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal as D
from unittest import TestCase
import copy

from .transport_money_rows import AUTHORED_TRANSPORT_ROWS
from .transport_to_money import (ready_from_review,quote_and_choose,
                                  settle_money_chain,stable_bytes,_iso)
from .transport_money_trial import run_transport_money_trial
from .travel_pilot.on_demand import OnDemandTravel
from .travel_pilot.pilot import _day,price_table


STUDIES = (
    dict(body="CERES",stage="A2",review="ADVANCE",result="SUPPORTS_ADVANCE",year=2038),
    dict(body="MARS",stage="A1",review="ADVANCE",result="SUPPORTS_ADVANCE",year=2037),
)


class FakeDailyGeometry:
    """Same daily lookup contract; single witnessed departure and arrival."""
    def __init__(self, opportunity_offset=10, ready=None):
        self.ready = _day(ready) if ready else None
        self.opportunity_offset = opportunity_offset
        self.solve_count = 0
        self._geometry = {}
        self.seen = []

    def lookup(self, origin, destination, departure, *, wait_limit_days,
               departure_limit,arrival_limit,flight_range_days,strategy):
        self.seen.append((origin,destination,_iso(_day(departure)),
                          tuple(flight_range_days),departure_limit,arrival_limit))
        self.solve_count+=1
        chosen = (self.ready is not None and
            _day(departure) == self.ready + timedelta(days=self.opportunity_offset))
        option = dict(flight_days=400.,
                      departure_vinf_km_s=3.,
                      arrival_vinf_km_s=3.)
        return dict(opportunities=([dict(departure=_iso(_day(departure)),
                                          options=[option])] if chosen else []))


class GenericDatedMoneyTests(TestCase):
    def test_review_year_end_not_january_and_mars_no_false_a2(self):
        for row in AUTHORED_TRANSPORT_ROWS:
            ready=ready_from_review(row,STUDIES)
            self.assertIsNotNone(ready)
            self.assertEqual((ready.month,ready.day,ready.hour,ready.minute),
                             (12,31,23,59))
        a2=copy.deepcopy(AUTHORED_TRANSPORT_ROWS[1])
        a2["prerequisite"]["stage"]="A2"
        self.assertIsNone(ready_from_review(a2,STUDIES))

    def test_both_rows_use_identical_mechanics_funded_and_blocked(self):
        reports=[]
        for row in AUTHORED_TRANSPORT_ROWS:
            ready=ready_from_review(row,STUDIES)
            fake=FakeDailyGeometry(ready=ready)
            search=quote_and_choose(row,ready,geometry=fake)
            self.assertEqual(search["status"],"AVAILABLE")
            self.assertEqual(search["solves"],730)
            self.assertEqual(len(fake.seen),730)
            self.assertTrue(all(x[3]==(45.,3000.) and x[4]==10 and x[5]==10
                                for x in fake.seen))
            result=settle_money_chain(row,ready,search)
            self.assertEqual(result["money_initial"],result["money_final"])
            self.assertTrue(all(D(y["new_capital_draw"]) +
                                D(y["recycled_returned_cash_spent"]) ==
                                D(y["offworld_draw"]) for y in result["annual"]))
            reports.append(result)
        funded, blocked=reports
        ship=funded["shipment"]
        self.assertEqual(ship["status"],"BUILT_AFTER_DELIVERY")
        self.assertEqual(ship["payment_status"],"PAID_AT_DEPARTURE")
        self.assertEqual(ship["delivery_status"],"DELIVERED_SCRIPTED")
        self.assertEqual(D(ship["seed_funding"]),
                         D(ship["cost_model_currency"]))
        self.assertEqual(D(ship["total_initial_funding"]),
                         D(ship["original_project_funds"])+
                         D(ship["cost_model_currency"]))
        self.assertEqual([e["type"] for e in funded["events"]],
                         ["READY","ORDER_COMMITMENT","PAYMENT","DEPARTURE",
                          "ARRIVAL","DELIVERY","BUILD"])
        departure=_day(ship["departure"]);arrival=_day(ship["arrival"])
        self.assertLess(departure.year,arrival.year)
        self.assertGreater(arrival,_day(ship["ready_date"]))
        for y in funded["annual"]:
            self.assertEqual(y["capacity"],"0" if y["year"]<arrival.year else "5")
        self.assertTrue(any(D(y["in_transit"])>0 for y in funded["annual"]))
        self.assertTrue(any(D(y["committed_unpaid"])>0 for y in funded["annual"]))
        self.assertEqual(blocked["shipment"]["status"],"BLOCKED_UNAFFORDABLE")
        self.assertEqual(blocked["shipment"]["departure"],None)
        self.assertEqual(blocked["shipment"]["arrival"],None)
        self.assertEqual(blocked["shipment"]["delivery_status"],"NOT_DELIVERED")
        self.assertEqual(blocked["productive_capacity"],"0")
        self.assertFalse(any(e["type"] in ("BUILD","PAYMENT","DELIVERY")
                              for e in blocked["events"]))

    def test_no_feasible_exhausted_and_no_payment(self):
        row=AUTHORED_TRANSPORT_ROWS[0]
        ready=ready_from_review(row,STUDIES)
        fake=FakeDailyGeometry()
        search=quote_and_choose(row,ready,geometry=fake)
        self.assertEqual(search["status"],"NO_FEASIBLE_DEPARTURE")
        self.assertEqual(search["solves"],730)
        trial=settle_money_chain(row,ready,search)
        self.assertEqual(trial["shipment"]["status"],"WAIT_LIMIT_EXHAUSTED")
        self.assertEqual(trial["shipment"]["search_status"],"NO_FEASIBLE_DEPARTURE")
        self.assertEqual(trial["shipment"]["cost_model_currency"],None)
        self.assertEqual(trial["shipment"]["departure"],None)
        self.assertEqual(trial["shipment"]["arrival"],None)
        self.assertEqual(trial["shipment"]["transport_payment_tx"],None)
        self.assertEqual(trial["productive_capacity"],"0")
        self.assertEqual(trial["money_initial"],trial["money_final"])

    def test_complete_replay_byte_identity(self):
        maker=lambda:run_transport_money_trial(
            studies=STUDIES,
            geometry_factory=lambda:FakeDailyGeometry(
                ready=ready_from_review(AUTHORED_TRANSPORT_ROWS[0],STUDIES)),
            legacy_check=False)
        # Each simulation run is deterministic, and its full serialised bytes
        # must match; no elapsed/wall-clock timing fields can leak into state.
        one=maker()
        two=maker()
        self.assertEqual(stable_bytes(one),stable_bytes(two))
        self.assertEqual(one["fingerprint"],two["fingerprint"])

    def test_cache_range_and_vehicle_price_independence(self):
        engine=OnDemandTravel()
        narrow=engine.geometry("EARTH","MARS","2039-08-01",
                               flight_range_days=(45.,1400.))
        wide=engine.geometry("EARTH","MARS","2039-08-01",
                             flight_range_days=(45.,3000.))
        self.assertEqual(narrow["sampled_solutions"],5421)
        self.assertEqual(wide["sampled_solutions"],11821)
        self.assertNotEqual(narrow["key"]["flight_time_grid_sha256"],
                            wide["key"]["flight_time_grid_sha256"])
        self.assertNotEqual(narrow["key"]["flight_duration_brackets_days"],
                            wide["key"]["flight_duration_brackets_days"])
        self.assertFalse(any("limit" in k or "price" in k or "vehicle" in k
                            for k in wide["key"]))
        self.assertEqual(engine.geometry("EARTH","MARS","2039-08-01",
                         flight_range_days=(45.,3000.)),wide)
        self.assertTrue(engine.admissible(wide,departure_limit=10,arrival_limit=10))
        self.assertTrue(engine.admissible(wide,departure_limit=20,arrival_limit=20))
