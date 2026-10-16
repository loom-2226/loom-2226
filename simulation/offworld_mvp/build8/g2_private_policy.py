"""Private sponsor evaluation. Receives only a sanitized agent snapshot and
authored, source-pinned policy parameters. No experiment literals in code.
"""
from decimal import Decimal


def evaluate(snapshot, request, params, decision_key):
    cash = Decimal(snapshot["account_balance"])
    prior_key = params["prior_key"]
    prior = dict(snapshot["priors"])[prior_key]
    probability = Decimal(prior)
    verified_cost = next(f["value"] for f in snapshot["admitted_facts"]
                         if f["key"] == "exploration.REMOTE_COST")
    cost = Decimal(verified_cost)
    if cost != Decimal(params["cost"]):
        raise ValueError("unadmitted cost mismatch")
    value = Decimal(params["information_value"])
    hurdle = Decimal(params["hurdle"])
    allowed = (snapshot["agent_kind"] == "PRIVATE_SPONSOR"
               and "EXPLORE" in snapshot["capabilities"]
               and params["policy_allowed"])
    in_time = int(params["service_year"]) <= int(params["end_year"])
    advantage = probability * value - cost
    if not in_time:
        outcome, reason = "DEFER", "OUTSIDE_AUTHORED_HORIZON"
    elif not allowed:
        outcome, reason = "DECLINE", "PRIVATE_POLICY_OR_CAPABILITY_BLOCK"
    elif cash < cost:
        outcome, reason = "DECLINE", "INSUFFICIENT_BUDGET"
    elif advantage < hurdle:
        outcome, reason = "DECLINE", "INFORMATION_VALUE_BELOW_HURDLE"
    else:
        outcome, reason = "AUTHORIZE", "APPROVED_PRIVATE_REMOTE_EXPLORATION"
    return {"outcome": outcome, "reason_code": reason,
            "authorized_cost": str(cost) if outcome == "AUTHORIZE" else "0"}
