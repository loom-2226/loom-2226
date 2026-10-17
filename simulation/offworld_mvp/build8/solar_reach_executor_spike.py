"""Noncanon, cast-driven Solar Reach. Source eligibility, no prechosen body."""
from __future__ import annotations
from decimal import Decimal as D
from hashlib import sha256
import json
from pathlib import Path
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.provenance import source_tree_hash
from offworld_kernel.mvp_state import AgentKind, AgentState
from .master_cast import actor

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
CAST = HERE / "solar_reach_cast.json"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def digest(obj):
    return sha256(canonical(obj).encode()).hexdigest()


def load(path=CAST):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if raw != (json.dumps(data, sort_keys=True, indent=2) + "\n").encode():
        raise ValueError("NONCANONICAL_CAST_FILE")
    if source_tree_hash() != data["kernel_tree_sha256"]:
        raise ValueError("KERNEL_TREE_PIN_MISMATCH")
    for key in ("catalog_source", "eligibility_source", "accessibility_source"):
        if data[key] not in data["source_pins"]:
            raise ValueError("UNPINNED_PUBLIC_SOURCE")
    for relative, pinned in data["source_pins"].items():
        source = (ROOT / relative).resolve()
        if not source.is_relative_to(ROOT) or sha256(source.read_bytes()).hexdigest() != pinned:
            raise ValueError("SOURCE_PIN_MISMATCH:" + relative)
    return data, sha256(raw).hexdigest()


def full_catalog(data):
    """All public identities including explicitly ineligible ones."""
    lines = (ROOT / data["catalog_source"]).read_text().splitlines()
    rows = []
    for line in lines:
        key, name, kind, parent, status, _, _, _, id_status = line.split("|")
        if status != "ACTIVE" or id_status != "ACTIVE":
            raise ValueError("UNQUALIFIED_CATALOG_IDENTITY:" + key)
        rows.append({"body_id": key, "name": name, "body_class": kind})
    if not rows or len({r["body_id"] for r in rows}) != len(rows):
        raise ValueError("EMPTY_OR_DUPLICATE_PUBLIC_CATALOG")
    return tuple(rows)


def eligible_public_catalog(data, catalog):
    """Reuse public Build7 eligibility and access statuses, never hidden WORLD."""
    eligible = json.loads((ROOT / data["eligibility_source"]).read_text())
    access = json.loads((ROOT / data["accessibility_source"]).read_text())
    selected = {r["semantic_key"] for r in eligible["bodies"]}
    metadata = {r["body_id"]: r["accessibility_status"] for r in access["records"]}
    catalog_ids = {r["body_id"] for r in catalog}
    if (not selected or selected != set(metadata) or not selected <= catalog_ids
            or len(metadata) != len(access["records"])):
        raise ValueError("PUBLIC_ELIGIBILITY_OR_ACCESS_MISMATCH")
    forbidden = {"STAR", "BARYCENTER", "SPACECRAFT"}
    if any(r["body_id"] in selected and r["body_class"] in forbidden for r in catalog):
        raise ValueError("PUBLIC_INELIGIBLE_ENTITY_MISCLASSIFIED")
    return metadata


def decide_bid(executor, request, reserved, year):
    """Executor sees only its own prices, beliefs, capacity and public request."""
    model = executor["services"].get(request["category"])
    if model is None:
        return {"action": "DECLINE", "reason": "NO_CAPABILITY"}
    duration = int(model["duration_years"])
    occupied = any(reserved.get((executor["id"], y), 0) >= int(model["capacity"])
                   for y in range(year, year + duration))
    alpha, beta = D(executor["beliefs"]["success"]), D(executor["beliefs"]["failure"])
    reliability = alpha / (alpha + beta)
    cost = D(model["cost"])
    price = cost * (D(1) + D(model["margin"])
                    + (D(1) - reliability) * D(model["risk_weight"]))
    if occupied:
        return {"action": "DECLINE", "reason": "CAPACITY"}
    if D(executor["cash"]) < cost:
        return {"action": "DECLINE", "reason": "WORKING_CAPITAL"}
    if reliability < D(model["min_reliability"]):
        return {"action": "DECLINE", "reason": "RELIABILITY_HURDLE"}
    if price > D(executor["beliefs"]["market_price"]):
        return {"action": "DECLINE", "reason": "PRICE_EXPECTATION"}
    return {"action": "BID", "reason": "EXPECTED_SURPLUS", "price": str(price),
            "duration": duration, "reliability": str(reliability)}


def choose_body(sponsor, year, catalog, accessible, used, cash):
    """Every eligible body evaluated each year from one sponsor rule."""
    policy = sponsor["decision"]
    evaluated = []
    for body in catalog:
        key = body["body_id"]
        if key not in accessible:
            continue
        reach = accessible[key]
        raw = sha256((policy["valuation_seed"] + "|" + sponsor["name"] + "|"
                      + key).encode()).digest()
        sample = D(int.from_bytes(raw[:8], "big")) / D(2**64)
        overrides = policy["body_overrides"].get(key, {})
        value = D(policy["base_value"]) + D(policy["value_spread"]) * sample
        value += D(overrides.get("value_delta", "0"))
        reach_cost = D(policy["reach_cost_by_accessibility"][reach])
        reach_cost += D(overrides.get("reach_delta", "0"))
        expected_cost = D(policy["expected_service_cost"])
        repeated = D(policy["repeat_disutility"]) * used.get((sponsor["name"], key), 0)
        score = D(policy["prior"]) * value - expected_cost - reach_cost - repeated
        available = key not in policy["unavailable_bodies"]
        affordable = cash >= expected_cost and cash >= D(0)
        eligible = available and affordable and score >= D(policy["hurdle"])
        evaluated.append({"body": key, "score": score, "value": value, "reach_cost": reach_cost,
                          "eligible": eligible})
    ranking = sorted((r for r in evaluated if r["eligible"]),
                     key=lambda r: (-r["score"], r["body"]))
    return (ranking[0] if ranking else None), len(evaluated)


def simulate(data, cast_name, scenario_sha):
    cast = data["casts"][cast_name]
    catalog = full_catalog(data)
    accessible = eligible_public_catalog(data, catalog)
    years = range(data["clock"]["first_year"], data["clock"]["last_year"] + 1)
    actors = [*cast["sponsors"], *cast["executors"]]
    if len({x["name"] for x in actors}) != len(actors):
        raise ValueError("DUPLICATE_CAST_MEMBER")
    sponsors = {s["name"]: s for s in cast["sponsors"]}
    for sponsor in cast["sponsors"]:
        actor(sponsor["name"], role=sponsor["role"])
        policy = sponsor["decision"]
        if (set(policy["body_overrides"]) - set(accessible)
                or set(policy["unavailable_bodies"]) - set(accessible)):
            raise ValueError("UNKNOWN_PUBLIC_BODY_OVERRIDE")
    for executor in cast["executors"]:
        actual = actor(executor["name"], role="executor")
        for category in executor["services"]:
            if not any(c["category"] == category for c in actual["capabilities"]):
                raise ValueError("UNSUPPORTED_EXECUTOR_CAPABILITY")
    initial = {x["name"]: x["beliefs"] for x in cast["executors"]}
    run_id = digest({"source_sha256": scenario_sha, "cast_name": cast_name,
                     "source_pins": data["source_pins"], "initial_beliefs": initial,
                     "effective_cast": cast, "clock": data["clock"]})
    rid = RunIdentity(run_id, "BUILD8_EXECUTOR_TEST_ONLY", scenario_sha,
                      "BUILD8_NONCANON_IN_MEMORY", tuple(sorted(
                          (name, digest(value)) for name, value in initial.items())))
    kernel = MethodologyHardenedBuild4Kernel(rid)
    states = {}
    for item in actors:
        node = "EARTH:" + actor(item["name"])["home_country"]
        if node not in kernel.state.nodes:
            kernel.add_node(node, NodeKind.EARTH)
        account = "reach:cash:" + item["name"]
        kernel.add_account(account, item["name"], node, AccountKind.FUNDS
                           if item["name"] in sponsors else AccountKind.SUPPLIER,
                           D(item["cash"]))
        if item["name"] in sponsors:
            kind = (AgentKind.PUBLIC if item["role"] == "agency_sponsor"
                    else AgentKind.PRIVATE_SPONSOR)
            kernel.add_agent(AgentState(item["name"], kind, node, account,
                             {"REQUEST_FINANCE"}, ("PROCURE",)))
        else:
            kernel.add_account("reach:expense:" + item["name"],
                               item["name"] + ":COST", node, AccountKind.SUPPLIER)
            states[item["name"]] = {"id": actor(item["name"])["id"],
                                  "services": item["services"],
                                  "beliefs": dict(item["beliefs"]),
                                  "cash": str(kernel.state.accounts[account].balance),
                                  "record": {"DELIVERED": 0, "FAILED": 0}}
    initial_money = sum((a.balance for a in kernel.state.accounts.values()), D(0))
    reserved, pending, contracts, bids, annual, body_year, choices = {}, [], [], [], [], [], []
    used = {}
    belief_yearly = []
    for year in years:
        for job in sorted((p for p in pending if p["finish"] == year), key=lambda p:p["id"]):
            outcomes = data["test_only_delivery_outcomes"][job["sponsor"]]
            if job["sequence"] >= len(outcomes):
                raise ValueError("MISSING_AUTHORED_TEST_OUTCOME")
            outcome = outcomes[job["sequence"]]
            if outcome not in ("DELIVERED", "FAILED"):
                raise ValueError("INVALID_AUTHORED_TEST_OUTCOME")
            state = states[job["executor"]]
            state["record"][outcome] += 1
            column = "success" if outcome == "DELIVERED" else "failure"
            state["beliefs"][column] = str(D(state["beliefs"][column]) + D(1))
            job["outcome"] = outcome
            kernel.audit("TEST_ONLY_EXECUTOR_DELIVERY", year, contract=job["id"],
                         executor=job["executor"], outcome=outcome)
        pending = [p for p in pending if p["finish"] > year]
        for sponsor_name in sorted(sponsors):
            sponsor = sponsors[sponsor_name]
            cash = kernel.state.accounts["reach:cash:" + sponsor_name].balance
            selected, evaluated = choose_body(sponsor, year, catalog, accessible, used, cash)
            choice = {"year": year, "sponsor": sponsor_name, "body": (
                selected["body"] if selected else None), "evaluated": evaluated,
                "score": str(selected["score"]) if selected else None}
            choices.append(choice)
            if selected is None:
                continue
            policy = sponsor["decision"]
            request = {"category": policy["service_category"], "body": selected["body"],
                       "sponsor": sponsor_name}
            ranked = []
            for name in sorted(states):
                state = states[name]
                state["cash"] = str(kernel.state.accounts["reach:cash:" + name].balance)
                decision = decide_bid(state, request, reserved, year)
                bids.append({"year": year, "body": request["body"], "sponsor": sponsor_name,
                             "executor": name, **decision})
                if decision["action"] == "BID" and D(decision["price"]) <= cash:
                    if D(decision["price"]) <= D(policy["max_contract_price"]):
                        ranked.append((D(decision["price"]), state["id"], name, decision))
            if not ranked:
                kernel.audit("TEST_ONLY_UNAWARDED_WANT", year, body=request["body"],
                             sponsor=sponsor_name)
                continue
            price, _, winner, bid = min(ranked)
            price = price.quantize(D(data["policy"]["payment_quantum"]))
            ordinal = sum(c["sponsor"] == sponsor_name for c in contracts)
            outcomes = data["test_only_delivery_outcomes"].get(sponsor_name)
            if outcomes is None or ordinal >= len(outcomes):
                raise ValueError("MISSING_AUTHORED_TEST_OUTCOME")
            job_id = digest((run_id, sponsor_name, ordinal, year, request["body"]))[:22]
            job = {"id": job_id, "body": request["body"], "sponsor": sponsor_name,
                   "executor": winner, "start": year, "finish": year + bid["duration"],
                   "sequence": ordinal, "price": str(price), "outcome": "PENDING"}
            for booked in range(year, job["finish"]):
                key = (states[winner]["id"], booked)
                reserved[key] = reserved.get(key, 0) + 1
                if reserved[key] > int(states[winner]["services"][request["category"]]["capacity"]):
                    raise AssertionError("DOUBLE_BOOKED_CAPACITY")
            payment = kernel.transfer(year, "reach:cash:" + sponsor_name,
                                      "reach:cash:" + winner, price, TxPurpose.CAPEX,
                                      parent_ids=(job_id,))
            cost = D(states[winner]["services"][request["category"]]["cost"])
            kernel.transfer(year, "reach:cash:" + winner,
                            "reach:expense:" + winner, cost, TxPurpose.OTHER_INVESTMENT,
                            parent_ids=(payment.id,))
            job["payment"] = payment.id
            contracts.append(job)
            pending.append(job)
            used[(sponsor_name, request["body"])] = used.get(
                (sponsor_name, request["body"]), 0) + 1
            if data["policy"]["delivery_disclosure"] == "AWARD_PRICE_PUBLIC":
                for state in states.values():
                    if request["category"] in state["services"]:
                        learning = D(state["beliefs"]["price_learning_rate"])
                        prev = D(state["beliefs"]["market_price"])
                        state["beliefs"]["market_price"] = str(
                            prev*(D(1)-learning) + price*learning)
        kernel.assert_invariants()
        cash_total = sum((a.balance for a in kernel.state.accounts.values()), D(0))
        if cash_total != initial_money:
            raise AssertionError("YEARLY_CURRENCY_NOT_CONSERVED")
        annual.append({"year": year, "money_total": str(cash_total),
                       "awards": sum(c["start"] == year for c in contracts)})
        belief_yearly.append((year, tuple(sorted(
            (name, tuple(sorted(state["beliefs"].items())),
             tuple(sorted(state["record"].items())))
            for name, state in states.items()))))
        for body in catalog:
            body_year.append((year, body["body_id"], body["body_id"] in accessible,
                              sum(c["body"] == body["body_id"] and c["start"] <= year
                                  for c in contracts)))
    if any(j["outcome"] == "PENDING" for j in contracts):
        raise ValueError("UNFINISHED_CONTRACT_AT_HORIZON")
    final_states = {name: {"beliefs": state["beliefs"], "record": state["record"],
                           "cash": str(kernel.state.accounts["reach:cash:" + name].balance)}
                    for name, state in sorted(states.items())}
    tx = [(t.id, t.year, t.source_account, t.destination_account, str(t.amount),
           t.purpose.value, t.parent_ids) for t in kernel.state.transactions]
    replay = digest({"run": run_id, "body_year": body_year, "annual": annual,
                     "contracts": contracts, "choices": choices, "bids": bids,
                     "transactions": tx, "beliefs": final_states,
                     "belief_yearly": belief_yearly,
                     "kernel": kernel.fingerprint(), "events": kernel.event_log})
    return {"run_id": run_id, "cast_name": cast_name, "replay_hash": replay,
            "catalog_count": len(catalog), "eligible_count": len(accessible),
            "year_count": len(years), "body_year_rows": len(body_year),
            "initial_money": str(initial_money),
            "ending_money": str(sum(a.balance for a in kernel.state.accounts.values())),
            "annual_conservation": all(D(x["money_total"]) == initial_money for x in annual),
            "awards": contracts, "choices": choices, "bids": bids,
            "final_executor_state": final_states,
            "belief_yearly_sha256": digest(belief_yearly),
            "transactions": tx, "source_sha256": scenario_sha}


def report(path=CAST):
    data, fingerprint = load(path)
    output = {"scenario_sha256": fingerprint, "complete_authored_cast": data,
              "resolved_public_catalog": [x["body_id"] for x in full_catalog(data)],
              "resolved_clock": data["clock"], "inherited_values": data["inherited_values"],
              "effective_parameters": data, "results": {}}
    for name in sorted(data["casts"]):
        runs = [simulate(data, name, fingerprint) for _ in
                range(data["replay_policy"]["total_executions_per_cast"])]
        if len({r["replay_hash"] for r in runs}) != 1:
            raise AssertionError("REPLAY_HASH_MISMATCH")
        output["results"][name] = {"run": runs[0], "verified_replays": len(runs)-1,
                                   "replay_hashes": [r["replay_hash"] for r in runs]}
    return output


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
