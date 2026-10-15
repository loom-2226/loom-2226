"""Box 3 PR E: preregistered seeded measurement of the merged D1 observer.

No new observer, keyed sampler, governance, hidden-world, or database.
Run: PYTHONPATH=.:simulation/offworld_mvp/phase3b/kernel python3 -B -m
     simulation.offworld_mvp.build8.box3_e_seed_run --output /tmp/box3e.json
Report sample statistics and process resources; never export synthetic source truth.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal as D
from hashlib import sha256
import json
from math import sqrt
import resource
import time

from .box3_d1_repeat_attempts import (
    Box3D1, PaidAttempt, AttemptDeclined, COST, POOL,
)

N = 10_000
PREFIX = "BUILD8_BOX3_E_SEED:"
EXPECTED_PRESENT = {"first_on_1": (8000, .8),
                    "first_on_2": (1600, .16),
                    "first_on_3": (320, .032),
                    "all_three_missed": (80, .008),
                    "cumulative_miss_1": (2000, .2),
                    "cumulative_miss_2": (400, .04),
                    "cumulative_miss_3": (80, .008)}
EXPECTED_ABSENT = {"false_positive_1": (2000, .2)}
SIGMAS = 3
TOLERANCE_P = .2


def _seed(index):
    if not 0 <= index < N:
        raise ValueError("seed index outside preregistration")
    return f"{PREFIX}{index:05d}"


def _fingerprint_item(digest, *, seed, x, rows, terminal=None):
    # Includes all paid draws, D1 receipt IDs and amounts, Bayesian outcomes
    # and kernel state; DOES NOT serialize trusted synthetic source control.
    tx = x.kernel.state.transactions
    record = {
        "seed": seed,
        "attempts": [[a.attempt_number, str(a.draw), a.signal, a.transaction_id,
                      a.observation_id, str(a.paid_amount),
                      str(a.belief_before), str(a.belief_after)]
                     for a in rows],
        "transfers": [[t.id, str(t.amount), t.purpose.value, list(t.parent_ids)]
                      for t in tx],
        "account_balances": [str(x.kernel.state.accounts[n].balance)
                             for n in ("SPN:POOL", "SUPPLIER:EARTH")],
        "agent_state_fingerprint": x.kernel.decision_epoch_state_fingerprint(),
        "terminal": terminal,
    }
    digest.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n")


def forced_arm(*, synthetic_present, sample_size=N):
    """Three REAL paid D1 observations per seed, with no early stopping.

    The fixed D1 values ensure the first three are always economically funded,
    even when all three signals are negative. Refusal is a protocol failure,
    not exclusion from the denominator. D1 itself remains unchanged.
    """
    if not 1 <= sample_size <= N:
        raise ValueError("sample size outside registered inventory")
    found = Counter()
    missed = Counter()
    conditional_draw_misses = Counter()
    fingerprint = sha256()
    paid_total = 0

    for i in range(sample_size):
        seed = _seed(i)
        x = Box3D1(synthetic_conditional_present=synthetic_present, run_name=seed)
        records = []
        for attempt in range(1, 4):
            rec = x.try_attempt(attempt_number=attempt)
            if not isinstance(rec, PaidAttempt):
                raise AssertionError(f"forced draw refused: {seed} attempt {attempt}")
            records.append(rec)
            conditional_draw_misses[attempt] += rec.signal == "NEGATIVE"
        signals = tuple(a.signal for a in records)
        first = next((n for n, s in enumerate(signals, 1) if s == "POSITIVE"), None)
        if first is None:
            found["all_three_missed"] += 1
        else:
            found[f"first_on_{first}"] += 1
        if signals[0] == "NEGATIVE":
            missed["cumulative_miss_1"] += 1
            if signals[1] == "NEGATIVE":
                missed["cumulative_miss_2"] += 1
                if signals[2] == "NEGATIVE":
                    missed["cumulative_miss_3"] += 1
        paid_total += len(records) * int(COST)
        if len(x.kernel.state.transactions) != 3:
            raise AssertionError("forced experiment did not pay exactly three attempts")
        if x.kernel.state.accounts["SPN:POOL"].balance != POOL - 3 * COST:
            raise AssertionError("forced experiment cash reconciliation")
        _fingerprint_item(fingerprint, seed=seed, x=x, rows=records)

    result = {
        "seeds": sample_size,
        "paid_attempts": 3 * sample_size,
        "total_paid_model_currency": paid_total,
        "first_detection": {name: found[name] for name in (
            "first_on_1", "first_on_2", "first_on_3", "all_three_missed")},
        "cumulative_misses": {name: missed[name] for name in (
            "cumulative_miss_1", "cumulative_miss_2", "cumulative_miss_3")},
        "misses_at_each_number": {str(k): conditional_draw_misses[k] for k in (1, 2, 3)},
        "seeded_outcome_sha256": fingerprint.hexdigest(),
    }
    if synthetic_present:
        result["conditional_miss_rates"] = {
            "miss_2_given_miss_1":
                missed["cumulative_miss_2"] / missed["cumulative_miss_1"]
                if missed["cumulative_miss_1"] else None,
            "miss_3_given_first_two_miss":
                missed["cumulative_miss_3"] / missed["cumulative_miss_2"]
                if missed["cumulative_miss_2"] else None,
        }
    else:
        result["false_positive_1"] = found["first_on_1"]
    return result


def sponsor_arm(*, sample_size=N):
    """Use D1's actual per-attempt choice until its own first decline."""
    if not 1 <= sample_size <= N:
        raise ValueError("sample size outside registered inventory")
    fingerprint = sha256()
    stopping = Counter()
    reasons = Counter()
    paid_attempts = Counter()
    sum_paid = 0
    total_decisions = 0
    for i in range(sample_size):
        seed = _seed(i)
        x = Box3D1(synthetic_conditional_present=True, run_name=seed)
        rows = []
        terminal = None
        for decision_number in range(1, 7):
            outcome = x.try_attempt()
            if isinstance(outcome, AttemptDeclined):
                terminal = [decision_number, outcome.reason, str(outcome.expected_net)]
                stopping[decision_number] += 1
                reasons[outcome.reason] += 1
                total_decisions += decision_number
                break
            if not isinstance(outcome, PaidAttempt):
                raise AssertionError("unexpected D1 result type")
            rows.append(outcome)
        if terminal is None:
            raise AssertionError("sponsor did not terminate by funded-cash decision 6")
        if len(x.kernel.state.transactions) != len(rows):
            raise AssertionError("sponsor has unmatched payment")
        spent = int(COST) * len(rows)
        sum_paid += spent
        paid_attempts[len(rows)] += 1
        if x.kernel.state.accounts["SPN:POOL"].balance != POOL - D(spent):
            raise AssertionError("sponsor cash conservation failed")
        _fingerprint_item(fingerprint, seed=seed, x=x, rows=rows, terminal=terminal)
    return {
        "seeds": sample_size,
        "stopped_on_decision": {str(k): stopping[k] for k in range(1, 7)},
        "stop_reasons": dict(sorted(reasons.items())),
        "paid_attempts_per_seed": {str(k): paid_attempts[k] for k in range(0, 6)},
        "total_decision_calls": total_decisions,
        "total_paid_model_currency": sum_paid,
        "seeded_outcome_sha256": fingerprint.hexdigest(),
    }


def _count_assessment(actual, p, n):
    # Exact decimal inputs avoid a binary-float 119.99999999999997
    # accidentally rejecting the inclusive, preregistered 120 boundary.
    prob = D(str(p))
    expected = D(n) * prob
    tolerance = D(SIGMAS) * (D(n) * prob * (D(1) - prob)).sqrt()
    return {
        "observed": actual, "expected": float(expected),
        "difference": float(D(actual) - expected),
        "three_sigma_tolerance": float(tolerance),
        "within_tolerance": abs(D(actual) - expected) <= tolerance,
    }


def assess(present, absent, sponsor):
    n = present["seeds"]
    tests = {}
    for label, (expect, p) in EXPECTED_PRESENT.items():
        source = (present["first_detection"] if label.startswith("first_on_")
                  or label == "all_three_missed" else present["cumulative_misses"])
        tests["present." + label] = _count_assessment(source[label], p, n)
    tests["absent.false_positive_1"] = _count_assessment(
        absent["false_positive_1"], TOLERANCE_P, n)
    for attempt in (2, 3):
        tests[f"present.unconditional_miss_{attempt}"] = _count_assessment(
            present["misses_at_each_number"][str(attempt)], TOLERANCE_P, n)
    for name, numerator, denominator in (
        ("miss_2_given_miss_1", present["cumulative_misses"]["cumulative_miss_2"],
         present["cumulative_misses"]["cumulative_miss_1"]),
        ("miss_3_given_first_two_miss", present["cumulative_misses"]["cumulative_miss_3"],
         present["cumulative_misses"]["cumulative_miss_2"]),
    ):
        if not denominator:
            tests["present." + name] = {"within_tolerance": False, "reason": "empty cohort"}
        else:
            tests["present." + name] = _count_assessment(numerator, TOLERANCE_P, denominator)
    tests["sponsor.no_stop_in_decisions_1_2_3"] = {
        "within_tolerance": all(sponsor["stopped_on_decision"][str(k)] == 0 for k in (1, 2, 3))}
    tests["sponsor.no_stop_on_decision_5"] = {
        "within_tolerance": sponsor["stopped_on_decision"]["5"] == 0}
    tests["sponsor.early_stop_equals_triple_miss"] = {
        "within_tolerance": sponsor["stopped_on_decision"]["4"] ==
            present["cumulative_misses"]["cumulative_miss_3"]}
    tests["sponsor.every_seed_stops"] = {
        "within_tolerance": sum(sponsor["stopped_on_decision"].values()) == n}
    tests["sponsor.total_spending_conserved"] = {
        "within_tolerance": sponsor["total_paid_model_currency"] ==
            int(COST) * sum(int(k) * v for k, v in sponsor["paid_attempts_per_seed"].items())}
    return tests


def run_experiment(sample_size=N):
    start = time.perf_counter()
    timings = {}
    sections = []
    for label, fn in (
        ("present", lambda: forced_arm(synthetic_present=True, sample_size=sample_size)),
        ("absent", lambda: forced_arm(synthetic_present=False, sample_size=sample_size)),
        ("sponsor", lambda: sponsor_arm(sample_size=sample_size)),
    ):
        t0 = time.perf_counter()
        sections.append((label, fn()))
        timings[label + "_seconds"] = round(time.perf_counter() - t0, 4)
    measured = dict(sections)
    tests = assess(measured["present"], measured["absent"], measured["sponsor"])
    summary = {
        "classification": "NONCANON_SYNTHETIC_D1_ONLY_NO_DATABASE",
        "baseline": "bbfc3a4a9e014c0ece2ae1eb7abd18908a2f9399",
        "seed_rule": f"{PREFIX}00000 .. {PREFIX}{sample_size - 1:05d}",
        "sample_size": sample_size, "sigma_multiplier": SIGMAS,
        "present": measured["present"], "absent": measured["absent"],
        "sponsor": measured["sponsor"], "assessment": tests,
        "all_assessments_passed": all(t["within_tolerance"] for t in tests.values()),
    }
    summary["aggregate_sha256"] = sha256(json.dumps(
        {k: v for k, v in summary.items() if k != "aggregate_sha256"},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    metrics = {
        "elapsed_seconds": round(time.perf_counter() - start, 4),
        **timings,
        "process_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    return {"measurement": summary, "resources": metrics}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True, help="scratch JSON output, not source-controlled")
    args = p.parse_args()
    result = run_experiment()
    with open(args.output, "w", encoding="utf8") as f:
        json.dump(result, f, sort_keys=True, indent=2)
        f.write("\n")
    print(json.dumps({
        "output": args.output,
        "all_assessments_passed": result["measurement"]["all_assessments_passed"],
        "aggregate_sha256": result["measurement"]["aggregate_sha256"],
        "resources": result["resources"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
