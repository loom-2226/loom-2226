"""Noncanon cast-driven Executor Agent experiment, unchanged monetary kernel."""
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
    if data["catalog_source"] not in data["source_pins"]:
        raise ValueError("UNPINNED_PUBLIC_CATALOG")
    if source_tree_hash() != data["kernel_tree_sha256"]:
        raise ValueError("KERNEL_TREE_PIN_MISMATCH")
    for relative, pinned in data["source_pins"].items():
        source = (ROOT / relative).resolve()
        if not source.is_relative_to(ROOT) or sha256(source.read_bytes()).hexdigest() != pinned:
            raise ValueError("SOURCE_PIN_MISMATCH:" + relative)
    return data, sha256(raw).hexdigest()



def full_catalog(data):
    """All active identities; no fixed body population or scope filter."""
    path = (ROOT / data["catalog_source"]).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("UNCONFINED_PUBLIC_CATALOG")
    rows = []
    for line in path.read_text().splitlines():
        key, name, kind, parent, status, _, _, _, identity_status = line.split("|")
        if status != "ACTIVE" or identity_status != "ACTIVE":
            raise ValueError("UNQUALIFIED_CATALOG_IDENTITY:" + key)
        rows.append({"body_id": key, "name": name, "body_class": kind})
    if not rows or len({x["body_id"] for x in rows}) != len(rows):
        raise ValueError("EMPTY_OR_DUPLICATE_PUBLIC_CATALOG")
    return tuple(rows)

def decide_bid(executor, request, reserved, year):
    """Agent-visible snapshot only. No TEST_ONLY outcome field."""
    capability = request["category"]
    model = executor["services"].get(capability)
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


def simulate(data, cast_name, scenario_sha):
    cast = data["casts"][cast_name]
    catalog = full_catalog(data)
    years = tuple(range(data["clock"]["first_year"], data["clock"]["last_year"] + 1))
    if not years or not catalog:
        raise ValueError("EMPTY_PUBLIC_WORLD")
    available_bodies = {row["body_id"] for row in catalog}
    actors = [*cast["sponsors"], *cast["executors"]]
    if len({x["name"] for x in actors}) != len(actors):
        raise ValueError("DUPLICATE_CAST_MEMBER")
    names = {x["name"] for x in cast["sponsors"]}
    for sponsor in cast["sponsors"]:
        actor(sponsor["name"], role=sponsor["role"])
        if any(w["body"] not in available_bodies or w["year"] not in years
               for w in sponsor["wants"]):
            raise ValueError("UNKNOWN_BODY_OR_YEAR")
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
    # Executor decision state is Build8-local; only money is kernel-owned.
    states = {}
    for item in actors:
        country = actor(item["name"])["home_country"]
        node = "EARTH:" + country
        if node not in kernel.state.nodes:
            kernel.add_node(node, NodeKind.EARTH)
        account = "reach:cash:" + item["name"]
        kernel.add_account(account, item["name"], node, AccountKind.FUNDS
                           if item["name"] in names else AccountKind.SUPPLIER,
                           D(item["cash"]))
        if item["name"] in names:
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
    wants = {(s["name"], w["id"]): dict(w, sponsor=s["name"])
             for s in cast["sponsors"] for w in s["wants"]}
    if len(wants) != sum(len(s["wants"]) for s in cast["sponsors"]):
        raise ValueError("DUPLICATE_WANT")
    remaining = sorted(wants.values(), key=lambda w:(w["year"],w["sponsor"],w["id"]))
    reserved = {}
    pending = []
    contracts = []
    bids = []
    annual = []
    body_year = []
    disclosure = data["policy"]["delivery_disclosure"]
    for year in years:
        # Complete existing work before evaluating new requests.
        for job in sorted((p for p in pending if p["finish"] == year),
                          key=lambda p:p["id"]):
            outcome = data["test_only_delivery_outcomes"][job["id"]]
            if outcome not in ("DELIVERED", "FAILED"):
                raise ValueError("INVALID_TEST_OUTCOME")
            executor = states[job["executor"]]
            executor["record"][outcome] += 1
            executor["beliefs"]["success" if outcome == "DELIVERED" else "failure"] = str(
                D(executor["beliefs"]["success" if outcome == "DELIVERED" else "failure"]) + D(1))
            job["outcome"] = outcome
            kernel.audit("TEST_ONLY_EXECUTOR_DELIVERY", year, contract=job["id"],
                         executor=job["executor"], outcome=outcome)
        pending = [p for p in pending if p["finish"] > year]
        for request in (w for w in remaining if w["year"] == year):
            choices = []
            for executor_name in sorted(states):
                executor = states[executor_name]
                executor["cash"] = str(kernel.state.accounts["reach:cash:" + executor_name].balance)
                decision = decide_bid(executor, request, reserved, year)
                bids.append({"year": year, "want": request["id"],
                             "executor": executor_name, **decision})
                if decision["action"] == "BID":
                    choices.append((D(decision["price"]), executor["id"],
                                    executor_name, decision))
            eligible = [c for c in choices
                        if c[0] <= D(request["max_price"])
                        and c[0] <= kernel.state.accounts[
                            "reach:cash:" + request["sponsor"]].balance]
            if not eligible:
                kernel.audit("TEST_ONLY_UNAWARDED_WANT", year, want=request["id"])
                continue
            price, _, winner, offer = min(eligible)
            job_id = request["id"]
            job = {"id": job_id, "body": request["body"], "sponsor": request["sponsor"],
                   "executor": winner, "start": year, "finish": year + offer["duration"],
                   "price": str(price), "outcome": "PENDING"}
            for booked in range(year, job["finish"]):
                key = (states[winner]["id"], booked)
                reserved[key] = reserved.get(key, 0) + 1
                if reserved[key] > int(states[winner]["services"][request["category"]]["capacity"]):
                    raise AssertionError("DOUBLE_BOOKED_CAPACITY")
            tx = kernel.transfer(year, "reach:cash:" + request["sponsor"],
                                 "reach:cash:" + winner, price, TxPurpose.CAPEX,
                                 parent_ids=(job_id,))
            cost = D(states[winner]["services"][request["category"]]["cost"])
            kernel.transfer(year, "reach:cash:" + winner,
                            "reach:expense:" + winner, cost, TxPurpose.OTHER_INVESTMENT,
                            parent_ids=(tx.id,))
            job["payment"] = tx.id
            pending.append(job)
            contracts.append(job)
            if disclosure == "AWARD_PRICE_PUBLIC":
                for name, state in states.items():
                    if request["category"] in state["services"]:
                        learning = D(state["beliefs"]["price_learning_rate"])
                        prev = D(state["beliefs"]["market_price"])
                        state["beliefs"]["market_price"] = str(
                            prev * (D(1) - learning) + price * learning)
        kernel.assert_invariants()
        current = sum((a.balance for a in kernel.state.accounts.values()), D(0))
        if current != initial_money:
            raise AssertionError("YEARLY_CURRENCY_NOT_CONSERVED")
        annual.append({"year": year, "money_total": str(current),
                       "new_awards": sum(c["start"] == year for c in contracts),
                       "completions": sum(c["finish"] == year for c in contracts)})
        for body in catalog:
            body_year.append((year, body["body_id"],
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
                     "contracts": contracts, "bids": bids, "transactions": tx,
                     "beliefs": final_states, "kernel": kernel.fingerprint(),
                     "original_event_history": kernel.event_log})
    return {"run_id": run_id, "cast_name": cast_name, "replay_hash": replay,
            "catalog_count": len(catalog), "year_count": len(years),
            "body_year_rows": len(body_year), "initial_money": str(initial_money),
            "ending_money": str(sum(a.balance for a in kernel.state.accounts.values())),
            "annual_conservation": all(D(x["money_total"]) == initial_money for x in annual),
            "awards": contracts, "bids": bids, "final_executor_state": final_states,
            "transactions": tx, "event_count": len(kernel.event_log),
            "years_with_awards": [x["year"] for x in annual if x["new_awards"]],
            "source_sha256": scenario_sha}


def report(path=CAST):
    data, fingerprint = load(path)
    output = {"scenario_sha256": fingerprint, "complete_authored_cast": data,
              "resolved_full_catalog_ids": [x["body_id"] for x in full_catalog(data)],
              "resolved_years": list(range(data["clock"]["first_year"],
                                           data["clock"]["last_year"] + 1)),
              "effective_parameters": {"cast": data["casts"], "policy": data["policy"],
                  "clock": data["clock"], "source_pins": data["source_pins"]},
              "inherited_values": data["inherited_values"], "results": {}}
    for name in sorted(data["casts"]):
        runs = [simulate(data, name, fingerprint) for _ in range(
            data["replay_policy"]["total_executions_per_cast"])]
        if len({r["replay_hash"] for r in runs}) != 1:
            raise AssertionError("REPLAY_HASH_MISMATCH")
        output["results"][name] = {"run": runs[0], "verified_replays": len(runs) - 1,
                                   "replay_hashes": [r["replay_hash"] for r in runs]}
    return output


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True, default=str))
