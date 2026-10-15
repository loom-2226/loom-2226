"""Build 8 Box 3 D1: local-only opt-in tests for numbered paid observations."""
import json
import unittest
from decimal import Decimal as D
from fractions import Fraction

from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import BodyRemoteObservation
from .box3_d1_repeat_attempts import (
    BODY, BELIEF_KEY, COST, DETECTION, FALSE_POSITIVE, HURDLE, MATERIAL,
    OTHER, POOL, PROJECT, QUESTION, REGION, SPONSOR, SUCCESS_VALUE, YEAR,
    AttemptDeclined, Box3D1, PaidAttempt, full_fingerprint,
)


def admitted_control(k, signal, index, actor=SPONSOR):
    """Clearly marked controlled SIGNAL, not an observer draw or paid attempt."""
    oid = f"SYNTHETIC_BAYES_CONTROL:{actor}:{index}:{signal}"
    obs = BodyRemoteObservation(
        oid, YEAR, actor, BODY, QUESTION, "CONTROL_ONLY", signal, False)
    k.observations[oid] = obs
    k.agents[actor].information.add(oid)
    return k.update_agent_belief_from_observation(
        YEAR, actor, oid, BELIEF_KEY, DETECTION, FALSE_POSITIVE,
        "D1_ADMITTED_BAYES_CONTROL", "TEST_ONLY_NOT_DRAWN")


class Box3D1Tests(unittest.TestCase):
    def test_01_two_separately_paid_same_year_distinct_draws_and_updates(self):
        x = Box3D1(synthetic_conditional_present=True)
        a, b = x.try_attempt(), x.try_attempt()
        self.assertIsInstance(a, PaidAttempt)
        self.assertIsInstance(b, PaidAttempt)
        self.assertEqual((a.attempt_number, b.attempt_number), (1, 2))
        self.assertEqual((a.paid_amount, b.paid_amount), (COST, COST))
        self.assertEqual(a.belief_update.observation_id, a.observation_id)
        self.assertEqual(b.belief_update.observation_id, b.observation_id)
        self.assertEqual(b.belief_before, a.belief_after)
        self.assertNotEqual(a.draw, b.draw)
        self.assertNotEqual(a.transaction_id, b.transaction_id)
        self.assertNotEqual(a.observation_id, b.observation_id)
        tx = x.kernel.state.transactions
        self.assertEqual(len(tx), 2)
        self.assertEqual([t.year for t in tx], [YEAR, YEAR])
        self.assertEqual([t.amount for t in tx], [COST, COST])
        self.assertEqual([t.purpose.value for t in tx], ["EXPLORATION"] * 2)
        self.assertEqual(x.evidence()["cash"], {"sponsor": "30", "supplier": "20"})
        self.assertEqual(x.kernel.state.projects[PROJECT].status, "PROPOSED")
        self.assertEqual(x.evidence()["review_count"], 0)

    def test_02_identical_replay_fingerprint_and_no_rebilling_on_same_instance(self):
        def run():
            x = Box3D1(synthetic_conditional_present=True)
            x.try_attempt(attempt_number=1)
            x.try_attempt(attempt_number=2)
            return x
        x, y = run(), run()
        self.assertEqual(x.evidence(), y.evidence())
        self.assertEqual(full_fingerprint(x.evidence()), full_fingerprint(y.evidence()))
        self.assertEqual(x.snapshot(SPONSOR).fingerprint(), y.snapshot(SPONSOR).fingerprint())
        earlier = x.evidence()
        self.assertEqual(x.try_attempt(attempt_number=1), x.attempts[1])
        self.assertEqual(x.try_attempt(attempt_number=2), x.attempts[2])
        self.assertEqual(x.evidence(), earlier)
        self.assertEqual(len(x.kernel.state.transactions), 2)
        with self.assertRaisesRegex(ValueError, "skip numbers"):
            x.try_attempt(attempt_number=4)

    def test_03_second_sponsor_no_private_read_update_or_snapshot(self):
        x = Box3D1(synthetic_conditional_present=True)
        a = x.try_attempt()
        self.assertIn(a.observation_id, x.kernel.agents[SPONSOR].information)
        self.assertNotIn(a.observation_id, x.kernel.agents[OTHER].information)
        with self.assertRaises(PermissionError):
            x.private_observation(OTHER, a.observation_id)
        with self.assertRaises(InvariantError):
            x.kernel.update_agent_belief_from_observation(
                YEAR, OTHER, a.observation_id, BELIEF_KEY, DETECTION,
                FALSE_POSITIVE, "ATTACK", "UNAUTHORIZED")
        own, other = x.snapshot(SPONSOR), x.snapshot(OTHER)
        self.assertIn(a.observation_id, own.information_refs)
        self.assertNotIn(a.observation_id, other.information_refs)
        self.assertTrue(any(a.observation_id in f.key for f in own.admitted_facts))
        self.assertFalse(any(a.observation_id in f.key for f in other.admitted_facts))
        self.assertEqual(other.beliefs, ())
        self.assertEqual(other.priors, ((BELIEF_KEY, D("0.5")),))
        self.assertEqual(x.evidence()["other_visible_refs"], [])
        self.assertEqual(len(x.kernel.state.projects), 1)

    def test_04_three_negative_control_updates_exact_current_posterior(self):
        x = Box3D1(synthetic_conditional_present=True)
        priors = []
        posteriors = []
        for number in (1, 2, 3):
            r = admitted_control(x.kernel, "NEGATIVE", number)
            priors.append(r.prior)
            posteriors.append(r.posterior)
        # Exact Bayesian fractions, separately checked against the kernel's
        # fixed 28-digit Decimal arithmetic (which rounds its final digits).
        p = Fraction(1, 2)
        exact = [p]
        for _ in range(3):
            p = (Fraction(1, 5) * p) / (
                Fraction(1, 5) * p + Fraction(4, 5) * (1 - p))
            exact.append(p)
        self.assertEqual(exact, [Fraction(1, 2), Fraction(1, 5),
                                 Fraction(1, 17), Fraction(1, 65)])
        for observed, fraction in zip([priors[0], *posteriors], exact):
            self.assertLess(abs(observed - D(fraction.numerator) / D(fraction.denominator)), D("1e-26"))
        for observed, fraction in zip(priors, exact[:3]):
            self.assertLess(abs(observed - D(fraction.numerator) / D(fraction.denominator)), D("1e-26"))
        self.assertGreater(posteriors[2], 0)
        self.assertEqual(x.kernel.agents[SPONSOR].beliefs[BELIEF_KEY], posteriors[2])

    def test_05_positive_attempt_two_updates_current_belief(self):
        # Fixed run identity with synthetic absent control has naturally
        # NEGATIVE draw 1, POSITIVE false-positive draw 2. No seed selection.
        x = Box3D1(synthetic_conditional_present=False)
        first = x.try_attempt(attempt_number=1)
        second = x.try_attempt(attempt_number=2)
        self.assertEqual((first.signal, second.signal), ("NEGATIVE", "POSITIVE"))
        self.assertEqual((first.belief_after, second.belief_before, second.belief_after),
                         (D("0.2"), D("0.2"), D("0.5")))
        self.assertEqual(second.decision_expected_net, D("30"))
        self.assertEqual(len(x.kernel.state.transactions), 2)
        self.assertEqual(second.belief_update.observation_id, second.observation_id)

    def test_06_fixed_prc_expected_value_rational_retry_then_stop(self):
        self.assertEqual((SUCCESS_VALUE, COST, HURDLE, POOL),
                         (D("200"), D("10"), D("0"), D("50")))
        x = Box3D1(synthetic_conditional_present=False)
        self.assertEqual(x.choice(), None)  # 50% -> 90 expected net
        first = x.try_attempt()
        self.assertEqual(first.signal, "NEGATIVE")
        self.assertEqual(first.decision_expected_net, D("90"))
        self.assertIsNone(x.choice())  # 20% -> 30 expected net
        second = x.try_attempt()
        self.assertEqual(second.decision_expected_net, D("30"))
        self.assertEqual(x.kernel.state.accounts["SPN:POOL"].balance, D("30"))

        # Separate authored Bayesian control demonstrates the rational third
        # search after two negatives and a decline after three negatives.
        controlled = Box3D1(synthetic_conditional_present=True)
        admitted_control(controlled.kernel, "NEGATIVE", 1)
        self.assertIsNone(controlled.choice())
        admitted_control(controlled.kernel, "NEGATIVE", 2)
        self.assertIsNone(controlled.choice())
        self.assertEqual(controlled.kernel.agents[SPONSOR].beliefs[BELIEF_KEY], D(1) / D(17))
        admitted_control(controlled.kernel, "NEGATIVE", 3)
        expected = D(1) / D(65) * SUCCESS_VALUE - COST
        declined = controlled.try_attempt(attempt_number=1)
        self.assertIsInstance(declined, AttemptDeclined)
        self.assertEqual(declined.reason, "BELOW_HURDLE")
        self.assertLess(abs(declined.expected_net - expected), D("1e-25"))
        self.assertEqual(declined.attempt_number, None)
        self.assertEqual(controlled.next_paid_number, 1)
        self.assertEqual(controlled.kernel.state.transactions, [])
        self.assertEqual(controlled.kernel.state.accounts["SPN:POOL"].balance, POOL)
        self.assertEqual(controlled.kernel.state.projects[PROJECT].status, "PROPOSED")

    def test_07_cash_insufficient_never_charges_or_consumes_number(self):
        x = Box3D1(synthetic_conditional_present=True, opening_cash=D("10"))
        a = x.try_attempt(attempt_number=1)
        self.assertIsInstance(a, PaidAttempt)
        before = x.evidence()
        refused = x.try_attempt(attempt_number=2)
        self.assertIsInstance(refused, AttemptDeclined)
        self.assertEqual(refused.reason, "INSUFFICIENT_CAPITAL")
        self.assertEqual(refused.attempt_number, None)
        self.assertEqual(refused.amount_charged, 0)
        self.assertEqual(x.next_paid_number, 2)
        self.assertEqual(x.evidence(), before)
        self.assertEqual(len(x.kernel.state.transactions), 1)
        self.assertEqual(x.kernel.state.accounts["SPN:POOL"].balance, 0)

    def test_08_old_same_year_key_reuses_same_draw_negative_control(self):
        x = Box3D1(synthetic_conditional_present=True)
        k = x.kernel
        old_key = ("OBS", YEAR, SPONSOR, f"{BODY}:{REGION}:{MATERIAL}", "REGION")
        first_old, second_old = k.keyed_draw(*old_key), k.keyed_draw(*old_key)
        self.assertEqual(first_old, second_old)
        a, b = x.try_attempt(), x.try_attempt()
        self.assertNotEqual(a.draw, b.draw)
        self.assertNotEqual(a.draw, first_old)

    def test_09_only_synthetic_observer_private_results_no_truth_export(self):
        x = Box3D1(synthetic_conditional_present=True)
        x.try_attempt()
        r = x.evidence()
        text = json.dumps(r, sort_keys=True)
        self.assertFalse(any(token in text for token in (
            "conditional_present", "hidden_world", "regional_truth",
            "truth_present", "world_seed", "sealed_truth")))
        self.assertEqual(len(x.kernel.resources), 0)
        self.assertFalse(hasattr(x.kernel, "hidden_world"))
        self.assertEqual(r["project_status"], "PROPOSED")
        self.assertEqual(r["review_count"], 0)
        self.assertFalse(x.kernel.observations[x.attempts[1].observation_id].public)

    def test_10_bad_attempt_or_actor_never_charges(self):
        x = Box3D1(synthetic_conditional_present=True)
        with self.assertRaises(PermissionError):
            x.try_attempt(sponsor=OTHER)
        with self.assertRaises(ValueError):
            x.try_attempt(attempt_number=3)
        with self.assertRaises(ValueError):
            x.try_attempt(attempt_number=0)
        self.assertEqual(x.kernel.state.transactions, [])
        self.assertEqual(x.next_paid_number, 1)
        x.kernel.assert_invariants()

    def test_11_predeclared_present_witness_first_miss_second_find(self):
        # Fixed 00..31 named identities, no tuning/adding after observing results.
        witnesses = []
        for n in range(32):
            name = f"BUILD8_BOX3_D1_REPEAT:WITNESS:{n:02d}"
            x = Box3D1(synthetic_conditional_present=True, run_name=name)
            first, second = x.try_attempt(), x.try_attempt()
            if (first.signal, second.signal) == ("NEGATIVE", "POSITIVE"):
                witnesses.append((name, x, first, second))
        self.assertTrue(witnesses, "No first-miss / second-positive witness among fixed 32")
        for name, x, first, second in witnesses:
            self.assertEqual((first.belief_before, first.belief_after),
                             (D("0.5"), D("0.2")))
            self.assertEqual((second.belief_before, second.belief_after),
                             (D("0.2"), D("0.5")))
            self.assertEqual(second.decision_expected_net, D("30"))
            self.assertNotEqual(first.draw, second.draw)
            self.assertEqual(len(x.kernel.state.transactions), 2)
            self.assertEqual(x.evidence()["cash"], {"sponsor": "30", "supplier": "20"})
            self.assertEqual(x.kernel.state.projects[PROJECT].status, "PROPOSED")
            self.assertEqual(x.evidence()["review_count"], 0)


if __name__ == "__main__":
    unittest.main()
