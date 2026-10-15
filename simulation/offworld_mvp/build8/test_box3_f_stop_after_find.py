"""Local-only checks of Build 8 F design. Not added to CI selection."""
import unittest
from decimal import Decimal as D

from .box3_f_stop_after_find import (
    SponsorProfile, PROFILES, evsi, search_decision, sample_seed,
    run_experiment, _decision_utility, N, EXPECTED_STOPS, count_test,
    spend_test,
)
from .box3_e_seed_run import _seed


class StopAfterFindTests(unittest.TestCase):
    def test_01_preregistration_fixed(self):
        self.assertEqual(N, 10000)
        self.assertEqual(_seed(0), "BUILD8_BOX3_E_SEED:00000")
        self.assertEqual(_seed(9999), "BUILD8_BOX3_E_SEED:09999")
        self.assertEqual(EXPECTED_STOPS[("neutral","present")],
                         (0., .8, .04, .128, .0064, .0256))
        self.assertEqual(EXPECTED_STOPS[("neutral","absent")],
                         (0., .2, .64, .032, .1024, .0256))

    def test_02_hand_values_neutral(self):
        p=PROFILES[0]
        self.assertEqual(evsi(D(".5"),p), D("10"))
        self.assertEqual(evsi(D(".2"),p),D("12.8"))
        self.assertEqual(evsi(D("0.8"),p),D("0"))
        self.assertEqual(evsi(D(1)/D(17),p),D("0"))
        self.assertEqual(_decision_utility(D(".5"),p),D("40"))
        self.assertEqual(_decision_utility(D(".8"),p),D("100"))

    def test_03_tie_and_affordability(self):
        p=PROFILES[0]
        self.assertEqual(search_decision(D(".5"),p,D("50"))[0],True)
        self.assertEqual(search_decision(D(".5"),p,D("0"))[2],
                         "INSUFFICIENT_SEARCH_CASH")
        self.assertEqual(search_decision(D(".8"),p,D("50"))[2],
                         "EVSI_BELOW_SEARCH_COST")

    def test_04_profiles_separate_value_components(self):
        a,b,c=PROFILES
        self.assertEqual([p.success_value for p in PROFILES],
                         [D(200),D(300),D(500)])
        self.assertEqual(evsi(b.prior_belief,b),D(0))
        self.assertEqual(evsi(c.prior_belief,c),D("24.4"))
        self.assertEqual(search_decision(b.prior_belief,b,D(50))[0],False)
        self.assertEqual(search_decision(c.prior_belief,c,D(50))[0],True)
        for p in PROFILES:
            v=p.visible_inputs()
            self.assertEqual(D(v["money_value"])+D(v["motive_value"])+
                             D(v["country_pressure_value"]),
                             D(v["effective_success_value"]))

    def test_05_motive_defers_without_observations(self):
        row=sample_seed(PROFILES[1],_seed(0),synthetic_present=False)
        self.assertEqual(row["paid_searches"],0)
        self.assertEqual(row["signals"],[])
        self.assertEqual(row["search_spent"],"0")
        self.assertEqual(row["development_disposition"],
                         "WOULD_FUND_DEFERRED_FOR_CAPITAL")
        self.assertEqual(row["remaining_cash"],"50")

    def test_06_same_seed_draw_across_profiles(self):
        a=sample_seed(PROFILES[0],_seed(0),synthetic_present=True)
        c=sample_seed(PROFILES[2],_seed(0),synthetic_present=True)
        self.assertGreaterEqual(a["paid_searches"],1)
        self.assertEqual(c["paid_searches"],1)
        self.assertEqual(a["paid_attempts"][0]["draw"],
                         c["paid_attempts"][0]["draw"])
        self.assertEqual(a["paid_attempts"][0]["signal"],
                         c["paid_attempts"][0]["signal"])
        for row in (a,c):
            self.assertEqual(D(row["remaining_cash"])+
                             D(row["supplier_cash"]),D(50))

    def test_07_no_hidden_data_in_sampled_row(self):
        row=sample_seed(PROFILES[0],_seed(0),synthetic_present=False)
        self.assertNotIn("synthetic_present",row)
        self.assertNotIn("true_resource",row)
        self.assertNotIn("hidden_world",str(row))

    def test_08_registered_sigma_bounds(self):
        self.assertTrue(count_test(8000,.8,10000)["pass"])
        self.assertFalse(count_test(8121,.8,10000)["pass"])
        self.assertTrue(count_test(256,.0256,10000)["pass"])
        self.assertTrue(spend_test(141760,EXPECTED_STOPS[("neutral","present")],10000)["pass"])

    def test_09_small_repeat_deterministic(self):
        a=run_experiment(8)
        b=run_experiment(8)
        self.assertEqual(a["measurement"],b["measurement"])
        for name,row in a["measurement"]["profiles"].items():
            self.assertEqual(sum(row["stops_by_paid_searches"].values()),8)
            self.assertEqual(row["would_fund"],row["would_fund_deferred_for_capital"])
            self.assertEqual(row["development_transfers"],0)
        self.assertEqual(a["measurement"]["profiles"]["motive_absent"]
                         ["would_fund"],8)
        self.assertEqual(a["measurement"]["profiles"]["motive_absent"]
                         ["synthetic_absence_false_positive_observation_signals"],0)


if __name__=="__main__":
    unittest.main()
