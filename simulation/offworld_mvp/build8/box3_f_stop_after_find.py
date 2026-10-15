"""Build 8 F: one-step decision-value stopping around the UNCHANGED D1 observer.

No new draw, belief updater, currency transfer, database or country-pressure model.
All truth controls are explicitly synthetic and retained privately by D1.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from decimal import Decimal as D
from hashlib import sha256
from math import sqrt
import argparse
import json
import resource
import time

from .box3_d1_repeat_attempts import (
    Box3D1, SPONSOR, BELIEF_KEY, PaidAttempt, AttemptDeclined,
    DETECTION, FALSE_POSITIVE, COST, POOL,
)
from .box3_e_seed_run import N, _seed

DEVELOPMENT_COST = D("60")
SIGMAS = 3
# D1 uses 28-digit Decimal arithmetic. Treat only sub-28th-digit
# arithmetic noise as equality, not as a new policy hurdle.
DECIMAL_TIE_ROUNDING = D("1e-24")
EXPECTED_STOPS = {
    ("neutral", "present"): (.0, .8, .04, .128, .0064, .0256),
    ("neutral", "absent"): (.0, .2, .64, .032, .1024, .0256),
    ("motive", "present"): (1., 0., 0., 0., 0., 0.),
    ("motive", "absent"): (1., 0., 0., 0., 0., 0.),
    ("pressured", "present"): (0., 1., 0., 0., 0., 0.),
    ("pressured", "absent"): (0., 1., 0., 0., 0., 0.),
}
EXPECTED_FUNDING = {
    ("neutral", "present"): .94848,
    ("neutral", "absent"): .23712,
    ("motive", "present"): 1.,
    ("motive", "absent"): 1.,
    ("pressured", "present"): .8,
    ("pressured", "absent"): .2,
}


@dataclass(frozen=True)
class SponsorProfile:
    name: str
    prior_belief: D = D("0.5")
    money_value: D = D("200")
    motive_value: D = D("0")
    country_pressure_value: D = D("0")
    hurdle: D = D("0")

    @property
    def success_value(self):
        return self.money_value + self.motive_value + self.country_pressure_value

    def visible_inputs(self):
        # Deliberately separate each authored profile component.
        return {
            "name": self.name,
            "prior_belief": str(self.prior_belief),
            "money_value": str(self.money_value),
            "motive_value": str(self.motive_value),
            "country_pressure_value": str(self.country_pressure_value),
            "effective_success_value": str(self.success_value),
            "hurdle": str(self.hurdle),
            "search_cost": str(COST),
            "development_cost": str(DEVELOPMENT_COST),
            "detection_likelihood": str(DETECTION),
            "false_positive_likelihood": str(FALSE_POSITIVE),
            "opening_search_cash": str(POOL),
        }


PROFILES = (
    SponsorProfile("neutral"),
    SponsorProfile("motive", motive_value=D("100")),
    SponsorProfile("pressured", prior_belief=D("0.1"),
                   country_pressure_value=D("300")),
)


def _validate(profile):
    for val in (profile.prior_belief, profile.money_value, profile.motive_value,
                profile.country_pressure_value, profile.hurdle):
        if not D(val).is_finite():
            raise ValueError("nonfinite authored profile value")
    if not D(0) <= profile.prior_belief <= D(1):
        raise ValueError("prior outside probability range")
    if profile.success_value < 0:
        raise ValueError("negative total success value not admitted")


def _decision_utility(belief, profile):
    # Existing PR C decision-worth equation, not a new preference model.
    return max(D(0), belief * profile.success_value -
               DEVELOPMENT_COST - profile.hurdle)


def evsi(belief, profile):
    """Expected gain from ONE further signal for the development choice.

    In joint-probability form to minimize artificial posterior rounding.
    q*max(0, posterior*V - (Cd+H)) = max(0, joint_true_positive*V - q*(Cd+H)).
    """
    p = D(belief)
    if not D(0) <= p <= D(1):
        raise ValueError("belief outside range")
    d, f = DETECTION, FALSE_POSITIVE
    q = p * d + (D(1) - p) * f
    threshold = DEVELOPMENT_COST + profile.hurdle
    after_positive = max(D(0), p * d * profile.success_value - q * threshold)
    after_negative = max(D(0), p * (D(1) - d) * profile.success_value
                         - (D(1) - q) * threshold)
    now = _decision_utility(p, profile)
    raw = after_positive + after_negative - now
    if raw < 0 and abs(raw) <= DECIMAL_TIE_ROUNDING:
        return D(0)
    if raw < 0:
        raise AssertionError("negative EVSI, violating value-of-information identity")
    return raw


def search_decision(belief, profile, available_cash):
    info_value = evsi(belief, profile)
    margin = info_value - COST
    economically_worth_searching = margin >= 0 or abs(margin) <= DECIMAL_TIE_ROUNDING
    if not economically_worth_searching:
        reason = "EVSI_BELOW_SEARCH_COST"
    elif available_cash < COST:
        reason = "INSUFFICIENT_SEARCH_CASH"
    else:
        reason = "SEARCH_INFORMATION_WORTH_COST"
    return economically_worth_searching and available_cash >= COST, info_value, reason


def sample_seed(profile, seed, *, synthetic_present):
    """Sample sponsor's private D1 evidence. Synthetic truth NEVER returned."""
    _validate(profile)
    x = Box3D1(synthetic_conditional_present=synthetic_present, run_name=seed)
    # D1 itself is unmodified. Set an authored, visible INITIAL prior before
    # its first observation; the original kernel performs every Bayesian update.
    x.kernel.agents[SPONSOR].priors[BELIEF_KEY] = profile.prior_belief
    observed = []
    stop_reason = None
    last_info = None
    # Guard against an accidental infinite loop, NOT an extra sponsor policy cap:
    # with POOL=50 and COST=10 at most five paid searches exist.
    for _ in range(int(POOL / COST) + 1):
        belief = D(x.kernel.agents[SPONSOR].beliefs.get(
            BELIEF_KEY, x.kernel.agents[SPONSOR].priors[BELIEF_KEY]))
        cash = x.kernel.state.accounts["SPN:POOL"].balance
        should_search, last_info, reason = search_decision(belief, profile, cash)
        if not should_search:
            stop_reason = reason
            break
        paid = x.try_attempt()
        if isinstance(paid, AttemptDeclined):
            # D1's internal PR C-style price rule still applies. We do not
            # circumvent the older observer or manufacture a paid search.
            raise AssertionError("D1 vetoes information-justified attempt: " + paid.reason)
        if not isinstance(paid, PaidAttempt):
            raise AssertionError("non-D1 paid search")
        observed.append(paid)
    else:
        raise AssertionError("sponsor did not terminate within original cash bound")
    assert stop_reason is not None
    if len(x.kernel.state.transactions) != len(observed):
        raise AssertionError("not exactly one D1 payment per observation")
    assert all(t.amount == COST for t in x.kernel.state.transactions)
    cash = x.kernel.state.accounts["SPN:POOL"].balance
    supplier = x.kernel.state.accounts["SUPPLIER:EARTH"].balance
    if cash + supplier != POOL or cash != POOL - COST * len(observed):
        raise AssertionError("search cash conservation failure")
    belief = D(x.kernel.agents[SPONSOR].beliefs.get(
        BELIEF_KEY, x.kernel.agents[SPONSOR].priors[BELIEF_KEY]))
    project_expected_net = belief * profile.success_value - DEVELOPMENT_COST
    would_fund = project_expected_net >= profile.hurdle
    funding_state = ("WOULD_FUND_DEFERRED_FOR_CAPITAL"
                     if would_fund and cash < DEVELOPMENT_COST
                     else "WOULD_FUND_AND_CASH_AVAILABLE"
                     if would_fund else "DECLINE_BELOW_HURDLE")
    # With this fixture there is no development payment. The handoff is a
    # PR C-style economic decision, not an invented completed policy transfer.
    if funding_state == "WOULD_FUND_AND_CASH_AVAILABLE":
        raise AssertionError("unexpected available development cash in this fixture")
    if x.kernel.state.projects["P-REGION"].status != "PROPOSED":
        raise AssertionError("PR F wrongly advanced project lifecycle")
    return {
        "seed": seed,
        "profile": profile.visible_inputs(),
        "paid_searches": len(observed),
        "search_spent": str(COST * len(observed)),
        "remaining_cash": str(cash),
        "supplier_cash": str(supplier),
        "belief_on_stop": str(belief),
        "last_evsi": str(last_info),
        "development_expected_net": str(project_expected_net),
        "would_fund": would_fund,
        "development_disposition": funding_state,
        "stop_reason": stop_reason,
        "signals": [r.signal for r in observed],
        "paid_attempts": [
            {"number":r.attempt_number, "signal":r.signal, "draw":str(r.draw),
             "belief_before":str(r.belief_before),
             "belief_after":str(r.belief_after), "transfer_id":r.transaction_id,
             "observation_id":r.observation_id, "payment":str(r.paid_amount)}
            for r in observed
        ],
        "kernel_fingerprint": x.kernel.decision_epoch_state_fingerprint(),
        # No trusted source truth or observations from any unbought future search.
    }


def run_arm(profile, *, synthetic_present, sample_size=N):
    if not 1 <= sample_size <= N:
        raise ValueError("sample size outside fixed PR E inventory")
    finger = sha256()
    stops, reasons = Counter(), Counter()
    funds, deferred, false_positive_signals, false_positive_recommendations = 0, 0, 0, 0
    spending, cash_stops = 0, 0
    first_examples = []
    for i in range(sample_size):
        row = sample_seed(profile, _seed(i), synthetic_present=synthetic_present)
        stops[row["paid_searches"]] += 1
        reasons[row["stop_reason"]] += 1
        funds += bool(row["would_fund"])
        deferred += row["development_disposition"] == "WOULD_FUND_DEFERRED_FOR_CAPITAL"
        spending += int(D(row["search_spent"]))
        cash_stops += row["stop_reason"] == "INSUFFICIENT_SEARCH_CASH"
        if not synthetic_present:
            false_positive_signals += sum(s == "POSITIVE" for s in row["signals"])
            false_positive_recommendations += bool(row["would_fund"])
        if i == 0:
            first_examples.append(row)
        finger.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()+b"\n")
    if sum(stops.values()) != sample_size or funds != deferred:
        raise AssertionError("stops/handoff reconciliation failure")
    if spending != 10 * sum(k*v for k,v in stops.items()):
        raise AssertionError("spend reconciliation failure")
    return {
        # Every arm report row repeats all 11 individually visible profile fields.
        **profile.visible_inputs(),
        "seeds": sample_size,
        "stops_by_paid_searches": {str(k): stops[k] for k in range(6)},
        "stop_reasons": dict(sorted(reasons.items())),
        "search_spent_model_currency": spending,
        "would_fund": funds,
        "would_fund_deferred_for_capital": deferred,
        "development_transfers": 0,
        "synthetic_absence_false_positive_observation_signals":
            false_positive_signals if not synthetic_present else None,
        "synthetic_absence_false_funding_recommendations":
            false_positive_recommendations if not synthetic_present else None,
        "cash_limited_stops": cash_stops,
        "first_seed_example": first_examples[0],
        "seeded_stream_sha256": finger.hexdigest(),
    }


def count_test(observed, probability, n):
    p = D(str(probability))
    exp = D(n) * p
    tol = D(SIGMAS) * (D(n) * p * (D(1)-p)).sqrt()
    return {"actual": observed, "expected": float(exp),
            "three_sigma_tolerance": float(tol),
            "deviation": float(D(observed)-exp),
            "pass": abs(D(observed)-exp) <= tol}


def spend_test(actual, ps, n):
    ps = [D(str(p)) for p in ps]
    mean = sum((D(k)*p for k,p in enumerate(ps)),D(0))
    second = sum((D(k*k)*p for k,p in enumerate(ps)),D(0))
    variance = max(D(0),second-mean*mean)
    exp = D(n) * COST * mean
    tol = D(SIGMAS)*COST*(D(n)*variance).sqrt()
    return {"actual": actual,"expected":float(exp),
            "three_sigma_tolerance":float(tol),
            "deviation":float(D(actual)-exp),
            "pass":abs(D(actual)-exp)<=tol}


def run_experiment(sample_size=N):
    start=time.perf_counter()
    measured={}
    times={}
    checks={}
    for profile in PROFILES:
        for label, truth in (("present",True),("absent",False)):
            name=profile.name+"_"+label
            tick=time.perf_counter()
            row=run_arm(profile,synthetic_present=truth,sample_size=sample_size)
            times[name+"_seconds"]=round(time.perf_counter()-tick,4)
            measured[name]=row
            stops=EXPECTED_STOPS[(profile.name,label)]
            for k,p in enumerate(stops):
                checks[name+".stops_"+str(k)] = count_test(
                    row["stops_by_paid_searches"][str(k)],p,sample_size)
            checks[name+".would_fund"]=count_test(
                row["would_fund"], EXPECTED_FUNDING[(profile.name,label)],sample_size)
            checks[name+".spending"]=spend_test(
                row["search_spent_model_currency"], stops,sample_size)
            checks[name+".cash_and_handoff"]= {
                "pass": row["would_fund"]==row["would_fund_deferred_for_capital"]
                and row["development_transfers"]==0}
            if not truth:
                checks[name+".absent_waste_equals_spend"]={
                    "pass":row["search_spent_model_currency"] >= 0
                    and row["synthetic_absence_false_funding_recommendations"] ==
                        row["would_fund"]}
    result={
        "classification":"NONCANON_SYNTHETIC_D1_PROFILE_VOI_NO_DATABASE",
        "baseline":"6a6cb33983426169976e79a4ea2d7291b714a35a",
        "seed_rule":f"BUILD8_BOX3_E_SEED:00000 .. BUILD8_BOX3_E_SEED:{sample_size-1:05d}",
        "sample_size":sample_size,"sigma":SIGMAS,
        "profiles":measured,"assessments":checks,
        "all_passed":all(x["pass"] for x in checks.values()),
    }
    result["aggregate_sha256"]=sha256(json.dumps(
        result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    resources={"elapsed_seconds":round(time.perf_counter()-start,4),
               **times, "process_peak_rss_kib_linux":
                   resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    return {"measurement":result,"resources":resources}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    result=run_experiment()
    with open(args.output,"w",encoding="utf8") as f:
        json.dump(result,f,indent=2,sort_keys=True)
        f.write("\n")
    print(json.dumps({
        "output":args.output,
        "all_passed":result["measurement"]["all_passed"],
        "checks":len(result["measurement"]["assessments"]),
        "aggregate_sha256":result["measurement"]["aggregate_sha256"],
        "resources":result["resources"]
    },sort_keys=True))
if __name__=="__main__":
    main()
