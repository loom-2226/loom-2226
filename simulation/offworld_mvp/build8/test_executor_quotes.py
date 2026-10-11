"""Unit and functional checks for Build 8 PI01 authored executor quotes."""

from dataclasses import replace
from decimal import Decimal as D
import unittest

from .executor_quotes import EXECUTORS, REQUESTS, evaluate_quotes


class ExecutorQuoteTests(unittest.TestCase):
    def test_authored_offers_have_expected_price_and_terms(self):
        rows = evaluate_quotes()
        self.assertEqual([row.status for row in rows], ["OFFER", "OFFER"])
        by_category = {row.category: row for row in rows}

        build = by_category["BUILD"]
        self.assertEqual(build.executor, "Northrop Grumman")
        self.assertEqual(build.authored_cost, D("2.00"))
        self.assertEqual(build.markup_rate, D("0.25"))
        self.assertEqual(build.quoted_price, D("2.5000"))
        self.assertEqual(build.duration_years, 2)

        land = by_category["LAND"]
        self.assertEqual(land.executor, "Firefly Aerospace")
        self.assertEqual(land.quoted_price, D("3.6000"))
        self.assertEqual(land.duration_years, 2)
        self.assertIn("launch-plus-LAND bundle", land.basis)
        self.assertIn("Blue Ghost Mission 1", land.basis)

    def test_zero_capacity_produces_explicit_refusal_without_price(self):
        constrained = tuple(
            replace(executor, available_capacity=0)
            if executor.category == "LAND"
            else executor
            for executor in EXECUTORS
        )
        rows = evaluate_quotes(executors=constrained)
        by_category = {row.category: row for row in rows}
        self.assertEqual(by_category["BUILD"].status, "OFFER")
        self.assertEqual(by_category["LAND"].status, "REFUSAL")
        self.assertEqual(
            by_category["LAND"].reason, "INSUFFICIENT_AUTHORED_CAPACITY"
        )
        self.assertIsNone(by_category["LAND"].quoted_price)
        self.assertEqual(by_category["LAND"].available_capacity, 0)

    def test_request_and_executor_input_order_do_not_change_output(self):
        expected = evaluate_quotes()
        self.assertEqual(
            evaluate_quotes(tuple(reversed(REQUESTS)), tuple(reversed(EXECUTORS))),
            expected,
        )
        self.assertEqual(evaluate_quotes(), expected)

    def test_requires_one_request_for_each_category(self):
        with self.assertRaisesRegex(ValueError, "exactly one BUILD and one LAND"):
            evaluate_quotes(REQUESTS[:1])


if __name__ == "__main__":
    unittest.main()
