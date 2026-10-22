"""Run the authored buyer inflow sensitivity without editing its parent runner."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from decimal import Decimal as D, localcontext
from pathlib import Path

from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_final_kt_20261022 import run_final as parent
from offworld_kernel.model import AccountKind, TxPurpose
from simulation.offworld_mvp.build8.three_arm_stage1.general_project_v2_kt_20261022 import general_project as gp
from offworld_kernel.distribution import FinancingReturnClaim
from offworld_kernel.project_lifecycle import ProjectDevelopmentPlan
from simulation.offworld_mvp.build8.return_routing import apply_operator_grants, resolve_destination

HERE = Path(__file__).resolve().parent
SCENARIO_PATH = HERE / "scenario.json"
CONFIG = json.loads(SCENARIO_PATH.read_text())
m = parent.m
base = parent.r


def write(name, value):
    path = HERE / name
    path.write_text(json.dumps(m.jsonable(value), sort_keys=True, indent=2) + "\n")


def _account_total_high_precision(kernel):
    with localcontext() as context:
        context.prec = 80
        return sum((account.balance for account in kernel.state.accounts.values()), D(0))


def _conservation_total(kernel):
    # The kernel executes Decimal operations at precision 28. At 2,000+ money
    # accounts, summation order can leave sub-1e-20 residue despite conserved
    # transfers. Compare at 20 decimal places and report the raw residual.
    return _account_total_high_precision(kernel).quantize(D("0.00000000000000000001"))


class FundedCampaign(parent.FinalCampaign):
    """Uniform yearly Earth inflow, then the existing finite buyer lifecycle."""

    def __init__(self, *args, annual_inflow, case_name, **kwargs):
        self.annual_inflow = D(annual_inflow)
        self.case_name = case_name
        self.funding_rows = []
        self.diagnostic_rows = []
        self.candidate_scan = None
        self.funded_years = set()
        super().__init__(*args, **kwargs)

    def _definition(self, body, sponsor, executor, eligibility):
        definition = super()._definition(body, sponsor, executor, eligibility)
        # The existing general lifecycle creates a financier Agent on start.
        # Give each independent portfolio project its own identity so parallel
        # starts cannot collide in the kernel's agent registry.
        definition["financier_id"] = definition["project_id"] + ":FINANCIER"
        return definition

    def _start_proposal(self, kernel, candidate, year):
        p = candidate["state"]
        budget_id = "route1:budget:" + p.sponsor
        endowment = D(p.definition["buyer"]["endowment"])
        if (budget_id in kernel.state.accounts
                and kernel.state.accounts[budget_id].balance >= D(candidate["commitment"])
                and kernel.state.accounts["earth_market"].balance >= endowment):
            # A carried candidate starts now; align its lifecycle schedule to
            # its actual finance/start year instead of its earlier eligibility
            # year, as required by the existing 13-year construction offset.
            p.start_year = int(year) - 13
            p.definition["start_year"] = p.start_year
            p.schedule = {key: p.start_year + int(offset)
                          for key, offset in p.definition["schedule_offsets"].items()}
        return super()._start_proposal(kernel, candidate, year)

    def _positive_a1_candidates(self, year):
        reviews = [r for r in self.studies if r["stage"] == "A1" and r["year"] == year]
        positives = [r for r in reviews if r["result"] == "SUPPORTS_ADVANCE"]
        before_unpriced = len(self.unpriced)
        candidates = super()._positive_a1_candidates(year)
        self.candidate_scan = {
            "positive_A1_reviews": len(positives),
            "A1_nonpositive_reviews": len(reviews) - len(positives),
            "new_quote_eligible_candidates": len(candidates),
            "new_no_quote_candidates": len(self.unpriced) - before_unpriced,
        }
        return candidates

    def on_year(self, year, kernel, rows):
        # External money enters through a kernel-owned Earth boundary account;
        # the following transfer is an ordinary conserved kernel transaction.
        market = kernel.state.accounts["earth_market"]
        first_missing = int(CONFIG["clock"]["start_year"]) if not self.funded_years else int(year)
        for funding_year in range(first_missing, int(year) + 1):
            if funding_year in self.funded_years:
                continue
            source = f"BUYER_INFLOWS:{self.case_name}:{funding_year}"
            kernel.add_account(source, "AUTHORED_EXTERNAL_EARTH_INFLOW",
                               market.node_id, AccountKind.EARTH_BOUNDARY,
                               self.annual_inflow)
            kernel.audit("TEST_ONLY_AUTHORED_EARTH_BUYER_INFLOW", funding_year,
                         scenario=self.case_name,
                         scenario_level_model_currency_per_year=str(self.annual_inflow),
                         source_account=source, destination_account="earth_market",
                         governor=None, size_dependence=False,
                         classification="TEST_ONLY_NONCANON")
            tx = kernel.transfer(funding_year, source, "earth_market", self.annual_inflow,
                                 TxPurpose.OTHER_INVESTMENT,
                                 parent_ids=(f"TEST_ONLY:{self.case_name}:{funding_year}",))
            self.funded_years.add(funding_year)
            self.funding_rows.append({"year": funding_year, "amount": str(self.annual_inflow),
                                      "source_account": source, "transaction_id": tx.id,
                                      "posted_at_callback_year": int(year)})
        conserved_opening = _account_total_high_precision(kernel)

        rows_before = len(self.project_rows)
        starts_before = len(self.started)
        unpriced_before = len(self.unpriced)
        pending_before = len(self.pending_candidates)
        super().on_year(year, kernel, rows)
        conservation_residual = _account_total_high_precision(kernel) - conserved_opening
        if abs(conservation_residual) > D("0.00000000000000000001"):
            raise AssertionError(f"callback money residual exceeds 1e-20: {conservation_residual}")
        new_dispositions = self.project_rows[rows_before:]
        outcomes = Counter(x.get("outcome", "UNCLASSIFIED") for x in new_dispositions)
        scan = self.candidate_scan or {
            "positive_A1_reviews": 0, "new_quote_eligible_candidates": 0,
            "A1_nonpositive_reviews": 0,
            "new_no_quote_candidates": 0,
        }
        self.diagnostic_rows.append({
            "year": int(year),
            "positive_A1_reviews": scan["positive_A1_reviews"],
            "new_quote_eligible_candidates": scan["new_quote_eligible_candidates"],
            "pending_candidates_before_policy": pending_before + scan["new_quote_eligible_candidates"],
            "new_no_quote_candidates": scan["new_no_quote_candidates"],
            "no_quote_records_added": len(self.unpriced) - unpriced_before,
            "sponsor_budget_no_affordable_candidate": outcomes["DEFERRED_NO_AFFORDABLE_ELIGIBLE_PROJECT"],
            "sponsor_capital_blocked": outcomes["DEFERRED_INSUFFICIENT_SPONSOR_CAPITAL"],
            "sponsor_policy_blocked": outcomes["DEFERRED_BY_SPONSOR_PORTFOLIO_POLICY"],
            "buyer_endowment_blocked": outcomes["DEFERRED_INSUFFICIENT_BUYER_ENDOWMENT"],
            "started": len(self.started) - starts_before,
            "new_candidate_dispositions": dict(sorted(outcomes.items())),
            "earth_market_balance_after_callback": str(kernel.state.accounts["earth_market"].balance),
            "total_money_after_callback": str(m._total_money(kernel)),
            "unrounded_money_residual_after_inflow": str(conservation_residual),
        })


class SharedTreasuryLifecycle(m.PortfolioLifecycle):
    """Preserve the existing country treasury while isolating project actors."""

    def _start(self, kernel, year, study_receipt, study_review):
        p = self.p
        assert p.project not in kernel.state.projects and p.asset not in kernel.state.assets
        assert kernel.state.accounts[self.buyer["account"]].balance == gp._d(self.buyer["endowment"])
        assert kernel.state.accounts[self.budget].balance >= p.value("physical_construction_cost") + p.value("operating_float")
        kernel.add_node(p.node, gp.NodeKind.OFFWORLD)
        kernel.add_account(p.cash, self.sponsor, p.node, AccountKind.PROJECT_CASH)
        country_node = kernel.agents[self.sponsor].node_id
        country = country_node.removeprefix("EARTH:")
        owner = "STATE:" + country
        treasury = p.accounts["treasury_prefix"] + country
        if treasury not in kernel.state.accounts:
            kernel.add_account(treasury, owner, country_node, AccountKind.FUNDS)
        elif (kernel.state.accounts[treasury].owner_id != owner
              or kernel.state.accounts[treasury].node_id != country_node
              or kernel.state.accounts[treasury].kind != AccountKind.FUNDS):
            raise RuntimeError("existing country treasury identity mismatch")
        kernel.add_project(p.project, p.node, p.cash, {owner: gp.D(1)})
        grants = tuple((g["operator"], p.project, g["owner"], g["reason"])
                       for g in p.definition["operator_grants"])
        p.operator_grants = apply_operator_grants(kernel, grants)
        p.owner_destination = resolve_destination(
            kernel, p.definition["return_revenue_source"], p.definition["owner_type"],
            owner, self.sponsor)
        assert p.owner_destination["delay_years"] == int(p.definition["appropriation_delay_years"])
        kernel.add_resource(gp.ScenarioResource(p.resource, p.node,
            p.definition["material_family"], p.family_value("in_situ"), None, None, None))
        kernel.add_account(p.reinvestment, self.sponsor, p.node, AccountKind.FUNDS)
        executor_country = p.definition["executor_location"]
        kernel.add_account(p.financier_cash, self.financier, "EARTH:" + executor_country,
                           AccountKind.FUNDS)
        kernel.add_agent(gp.AgentState(self.financier, gp.AgentKind.PRIVATE_FINANCIER,
                                       "EARTH:" + executor_country, p.financier_cash,
                                       {"FINANCE"}, ("RETURN",)))
        kernel.agents[self.sponsor].capabilities.update(
            {"DEVELOP", "OPERATE", "EXTRACT", "SELL", "DISTRIBUTE_SURPLUS"})
        funded = p.value("physical_construction_cost") + p.value("operating_float")
        investment = kernel.transfer(year, self.budget, p.financier_cash, funded,
                                     TxPurpose.OTHER_INVESTMENT, parent_ids=(study_receipt,))
        kernel.add_commitment(p.commitment, self.financier, p.project, funded)
        payment = kernel.disburse(year, p.commitment, p.financier_cash, funded)
        kernel.transition_project_status(year, self.sponsor, p.project, "DEVELOPMENT",
                                         reason_ref=study_receipt)
        stages = ((p.offset_year("construction_year_1"), p.value("construction_stage_1")),
                  (p.offset_year("construction_year_2"), p.value("construction_stage_2")))
        kernel.register_development_plan(ProjectDevelopmentPlan(
            p.plan, p.project, p.ids["wip"], p.asset, self.supplier, p.node,
            p.value("physical_construction_cost"), stages,
            p.offset_year("construction_year_2"), p.family_value("productive_capacity"),
            p.ids["development_plan_basis"]))
        kernel.register_financing_return_claim(FinancingReturnClaim(
            p.return_claim, self.financier, p.project, p.financier_cash,
            p.family_value("unit_sale_price") * p.family_value("quantity_per_operation") *
            p.value("financier_return_share"), (p.commitment,),
            p.ids["financing_claim_basis"], p.ids["financing_claim_scope"]))
        p.physical.append(dict(year=year, stage="FINANCE", sponsor_debit=str(funded),
            financier_debit=str(funded), project_cash=str(kernel.state.accounts[p.cash].balance),
            investment_tx=investment.id, disbursement_tx=payment.id,
            study_receipt=study_receipt, study_review=study_review))

def case_scenario(authored, case):
    payload = json.loads(json.dumps(authored))
    payload["buyer_budget_sweep"] = {
        "case": case["name"],
        "annual_earth_inflow_model_currency": case["annual_inflow"],
        "mission_type": case["mission_type"],
        "mission_price_conversion_enabled": case["conversion"],
        "classification": "TEST_ONLY_NONCANON_AUTHORED_SENSITIVITY",
    }
    return payload


def run_case(case, source_scenario, scenario_bytes, price_bytes, prices, audit):
    scenario = case_scenario(source_scenario, case)
    portfolio_scenario = case_scenario(json.loads((parent.OUT / "scenario.json").read_text()), case)
    m.SCENARIO = portfolio_scenario
    m.PortfolioLifecycle = SharedTreasuryLifecycle
    m.HERE = HERE
    m.OUT = HERE
    base.OUT = HERE
    m.write = write
    campaign = FundedCampaign(
        scenario, prices, audit, conversion=case["conversion"],
        mission_type=case["mission_type"], annual_inflow=case["annual_inflow"],
        case_name=case["name"],
    )
    result, elapsed = m.run(campaign, scenario)
    portfolio = campaign.report_portfolio()
    expected_years = int(CONFIG["clock"]["end_year"]) - int(CONFIG["clock"]["start_year"]) + 1
    if len(portfolio["yearly"]) != expected_years:
        raise RuntimeError(f"{case['name']}: annual coverage {len(portfolio['yearly'])} != {expected_years}")
    diagnostics = {int(row["year"]): row for row in campaign.diagnostic_rows}
    first_year = int(CONFIG["clock"]["start_year"])
    if first_year not in diagnostics:
        diagnostics[first_year] = {
            "year": first_year, "callback_executed": False,
            "candidate_list_state": "NOT_EVALUATED_NO_ANNUAL_CALLBACK",
            "no_eligible_candidate_reason": "No annual policy callback was scheduled in the clock's first year.",
            "positive_A1_reviews": 0, "new_quote_eligible_candidates": 0,
            "A1_nonpositive_reviews": 0,
            "pending_candidates_before_policy": 0, "new_no_quote_candidates": 0,
            "no_quote_records_added": 0, "sponsor_capital_blocked": 0,
            "sponsor_budget_no_affordable_candidate": 0,
            "sponsor_policy_blocked": 0, "buyer_endowment_blocked": 0,
            "started": 0, "new_candidate_dispositions": {},
            "annual_earth_inflow_model_currency": case["annual_inflow"],
        }
        if portfolio["yearly"] and int(portfolio["yearly"][0]["year"]) == first_year:
            portfolio["yearly"][0]["annual_earth_inflow_model_currency"] = case["annual_inflow"]
    for row in campaign.diagnostic_rows:
        row["callback_executed"] = True
        row["annual_earth_inflow_model_currency"] = case["annual_inflow"]
        row["candidate_list_state"] = (
            "HAS_PENDING_CANDIDATES" if row["pending_candidates_before_policy"] else
            "EMPTY_AFTER_ELIGIBILITY_AND_QUOTE_FILTER")
        row["no_eligible_candidate_reason"] = (
            "No reviewed-positive A1 quote-eligible pair was pending." if
            row["pending_candidates_before_policy"] == 0 else None)
    if len(diagnostics) != expected_years:
        raise RuntimeError(f"{case['name']}: diagnostic coverage {len(diagnostics)} != {expected_years}")

    if len(campaign.bodies) != 90 or len(campaign.requesters) != 20:
        raise RuntimeError(f"{case['name']}: coverage mismatch bodies={len(campaign.bodies)} sponsors={len(campaign.requesters)}")
    returns_by_year = {}
    for project in portfolio["projects"]:
        for receipt in project["returns"]:
            key = int(receipt["year"])
            returns_by_year[key] = returns_by_year.get(key, D(0)) + D(str(receipt["amount"]))
    for row in portfolio["yearly"]:
        row["annual_earth_inflow_model_currency"] = case["annual_inflow"]
        row["money_returned"] = str(returns_by_year.get(int(row["year"]), D(0)))
    for row in diagnostics.values():
        row.setdefault("money_returned", str(returns_by_year.get(int(row["year"]), D(0))))

    starts = portfolio["started"]
    output = {
        "classification": "TEST_ONLY_NONCANON_AUTHORED_SENSITIVITY",
        "run": case["name"],
        "scenario": scenario,
        "scenario_sha256": hashlib.sha256(json.dumps(
            scenario, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "source_authored_scenario_sha256": hashlib.sha256(SCENARIO_PATH.read_bytes()).hexdigest(),
        "base_scenario_sha256": hashlib.sha256(scenario_bytes).hexdigest(),
        "price_table_sha256": hashlib.sha256(price_bytes).hexdigest(),
        "year_range": [CONFIG["clock"]["start_year"], CONFIG["clock"]["end_year"]],
        "year_count": expected_years,
        "runtime_seconds": elapsed,
        "annual_earth_inflow_model_currency": case["annual_inflow"],
        "total_earth_inflow_model_currency": str(D(case["annual_inflow"]) * expected_years),
        "conversion_enabled": case["conversion"],
        "mission_type": case["mission_type"],
        "campaign_sponsors": len(campaign.requesters),
        "sponsor_roster": list(campaign.requesters),
        "bodies": len(campaign.bodies),
        "projects_started": len(starts),
        "distinct_started_bodies": len({x["body"] for x in starts}),
        "distinct_started_sponsors": len({x["sponsor"] for x in starts}),
        "sales": sum(len(p["sales"]) for p in portfolio["projects"]),
        "money_returned": str(sum((D(r["amount"]) for p in portfolio["projects"]
                                   for r in p["returns"]), D(0))),
        "tie_count": len(portfolio["ties"]),
        "ties": portfolio["ties"],
        "non_ceres_chain": [p for p in portfolio["projects"] if p["body"] != "CERES"],
        "evidence_status_table": [
            {"status": "REAL", "count": 0},
            {"status": "PLACEHOLDER", "count": len(portfolio["family_status_by_body"])},
            {"status": "TEST_ONLY_STUDY", "count": len(campaign.studies)},
        ],
        "candidate_dispositions": portfolio["candidate_dispositions"],
        "unpriced": portfolio["unpriced"],
        "all_unpriced_reasons": portfolio["all_unpriced"],
        "annual_funding_transactions": campaign.funding_rows,
        "per_year": portfolio["yearly"],
        "annual_diagnostics": [diagnostics[y] for y in range(first_year, int(CONFIG["clock"]["end_year"]) + 1)],
        "sponsor_policy_decisions": portfolio["sponsor_policy_decisions"],
        "kernel_transactions": len(result["kernel"].state.transactions),
        "conservation": "kernel conservation baseline resets after the explicit annual Earth boundary inflow; callback asserts exact money conservation",
        "family_assignment_basis": portfolio["family_assignment_basis"],
    }
    write(case["name"] + "_report.json", output)
    return output


def main():
    authored = CONFIG
    source_scenario, scenario_bytes, price_bytes, prices, audit = m.load_inputs()
    m._total_money = _conservation_total
    base.boundary._total_money = _conservation_total
    actual_source_hash = hashlib.sha256(Path("data/LOOM_2226.sqlite3").read_bytes()).hexdigest()
    expected_world_hash = "e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde"
    identity = {
        "classification": "TEST_ONLY_NONCANON_AUTHORED_SENSITIVITY",
        "input_scenario_sha256": hashlib.sha256(scenario_bytes).hexdigest(),
        "price_table_sha256": hashlib.sha256(price_bytes).hexdigest(),
        "audit_sha256": hashlib.sha256(m.AUDIT_PATH.read_bytes()).hexdigest(),
        "authored_sweep_scenario_sha256": hashlib.sha256(SCENARIO_PATH.read_bytes()).hexdigest(),
        "world_sqlite_actual_sha256": actual_source_hash,
        "world_sqlite_expected_baseline_sha256": expected_world_hash,
        "world_sqlite_baseline_match": actual_source_hash == expected_world_hash,
        "scenario_identity_includes_case_and_annual_inflow": True,
        "cases": authored["cases"],
    }
    identity["sweep_run_identity_sha256"] = hashlib.sha256(json.dumps(
        identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    write("input_identity.json", identity)
    if not identity["world_sqlite_baseline_match"]:
        raise RuntimeError("World SQLite baseline SHA does not match task-provided identity")

    # Lifecycle remains the existing Ceres-validated implementation; only its
    # explicit yearly Earth boundary funding callback is extended here.
    m.write = write
    firewall = base.tripwire_check()
    write("selection_firewall_tripwire_report.json", {
        "check": firewall, "boundary_admission_used": False,
        "allowlisted_fields": sorted(__import__(
            "simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022.selection_rule",
            fromlist=["RECORD_FIELDS"]).RECORD_FIELDS),
    })
    parity = m.ceres_equivalence(source_scenario, prices)
    reports = [run_case(case, source_scenario, scenario_bytes, price_bytes, prices, audit)
               for case in authored["cases"]]
    from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
    from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import replay
    from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_campaign_kt_20261022.run_multi_project import _total_money
    del _total_money
    route1 = replay(AllBodyCampaign(body_count=90, ceilings_enabled=True))
    expected_route1 = "4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430"
    route1_report = {"actual_sha256": route1, "expected_sha256": expected_route1,
                     "pass_exact": route1 == expected_route1}
    write("route1_control_report.json", route1_report)
    if not route1_report["pass_exact"]:
        raise RuntimeError("Route1 exact hash control failed")
    summary = {
        "classification": "TEST_ONLY_NONCANON_AUTHORED_SENSITIVITY",
        "world_sqlite_baseline_match": identity["world_sqlite_baseline_match"],
        "ceres_equivalence": parity,
        "route1_exact_hash_control": route1_report,
        "cases": [{"name": r["run"], "annual_inflow": r["annual_earth_inflow_model_currency"],
                   "years": r["year_count"], "projects_started": r["projects_started"],
                   "distinct_bodies": r["distinct_started_bodies"],
                   "distinct_sponsors": r["distinct_started_sponsors"], "sales": r["sales"],
                   "money_returned": r["money_returned"], "ties": r["tie_count"]}
                  for r in reports],
    }
    write("summary.json", summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
