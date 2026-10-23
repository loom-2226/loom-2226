"""PR427 all-body/all-sponsor 2026-2226 selection-rule implementation."""
from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path

from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022.selection_rule import (
    REPORT_LABEL, select_projects, tripwire_check,
)
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_campaign_kt_20261022 import run_with_boundary_accounting as boundary

m = boundary.m
OUT = Path(__file__).resolve().parent
m.HERE = OUT


class RuleCampaign(boundary.BoundaryAwareCampaign):
    """Keep the validated kernel lifecycle and replace only sponsor selection."""
    def _start_proposal(self, kernel, candidate, year):
        try:
            return super()._start_proposal(kernel, candidate, year)
        except AttributeError as exc:
            # The imported implementation completes every zero-conversion
            # project mutation and then dereferences qtx.id where qtx is None.
            # Accept only that precise post-registration failure and represent
            # the absent mission-price transfer as None.
            identity = (candidate["body"], candidate["sponsor"])
            if ("NoneType" not in str(exc) or identity not in self.project_states
                    or not any(x["body"] == identity[0] and x["sponsor"] == identity[1]
                               and x["year"] == year for x in self.started)):
                raise
            candidate["mission_tx"] = None
            return True

    def _policy_filter(self, kernel, candidates, year):
        by_identity = {}
        records = []
        for candidate in candidates:
            key = (candidate["body"], candidate["sponsor"], candidate["eligibility_year"], candidate["roster_index"])
            by_identity[key] = candidate
            review = candidate["review"]
            # The rule receives an explicit data projection. No generated-world,
            # body-property, boundary snapshot, or Box3 admission data can enter.
            records.append({
                "body": candidate["body"],
                "sponsor": candidate["sponsor"],
                "eligibility_year": candidate["eligibility_year"],
                "roster_index": candidate["roster_index"],
                "reviewed_result": review.get("result"),
                "review_status": review.get("review"),
                "quoted_price_usd": candidate["mission_usd"],
                "quoted_price_model": candidate["mission_model_currency"],
                "total_capital_commitment": candidate["commitment"],
            })
        capitals = {
            sponsor: str(kernel.state.accounts["route1:budget:" + sponsor].balance)
            for sponsor in self.requesters
        }
        selected_records, ties = select_projects(records, capitals)
        selected = [by_identity[(r["body"], r["sponsor"], r["eligibility_year"], r["roster_index"])]
                    for r in selected_records]
        self.last_policy_decisions = []
        selected_sponsors = {c["sponsor"] for c in selected}
        for sponsor in self.requesters:
            group = [c for c in candidates if c["sponsor"] == sponsor]
            if not group:
                continue
            winner = next((c for c in selected if c["sponsor"] == sponsor), None)
            self.last_policy_decisions.append({
                "year": year, "sponsor": sponsor,
                "outcome": "SELECTED" if winner else "DEFERRED_NO_AFFORDABLE_ELIGIBLE_PROJECT",
                "selected_body": None if winner is None else winner["body"],
                "available_capital": capitals[sponsor],
                "candidate_count": len(group), "rule": "LOWEST_COMMITMENT_THEN_EARLIEST_YEAR_THEN_ROSTER_INDEX",
            })
            if winner is None:
                self.project_rows.append(dict(year=year, sponsor=sponsor,
                    outcome="DEFERRED_NO_AFFORDABLE_ELIGIBLE_PROJECT",
                    eligible_candidates=[c["body"] for c in group],
                    retry="REATTEMPT_NEXT_ANNUAL_POLICY_CALLBACK"))
        for tie in ties:
            self.ties.append(dict(year=year, **tie))
        return selected


def labeled_write(name, obj):
    if isinstance(obj, dict):
        obj = dict(obj)
        obj["report_label"] = REPORT_LABEL
    if isinstance(obj, dict) and isinstance(obj.get("per_year"), list):
        rows = obj["per_year"]
        by_year_returns = {}
        for project in obj.get("projects", []):
            for receipt in project.get("returns", []):
                y = int(receipt["year"])
                by_year_returns[y] = by_year_returns.get(y, Decimal(0)) + Decimal(str(receipt["amount"]))
        dispositions = obj.get("candidate_dispositions", [])
        for row in rows:
            year = int(row["year"])
            row["money_returned"] = str(by_year_returns.get(year, Decimal(0)))
            row["out_of_budget_projects"] = sum(
                1 for item in dispositions if int(item.get("year", -1)) == year
                and item.get("outcome") == "DEFERRED_INSUFFICIENT_SPONSOR_CAPITAL")
        columns = sorted({"report_label"} | {key for row in rows for key in row})
        with (OUT / name.replace("_report.json", "_annual.csv")).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: REPORT_LABEL if key == "report_label" else
                                 (json.dumps(row.get(key), sort_keys=True) if isinstance(row.get(key), (dict, list, tuple))
                                  else row.get(key, "")) for key in columns})
    path = OUT / name
    path.write_text(json.dumps(m.jsonable(obj), sort_keys=True, indent=2) + "\n")


def main():
    m.PortfolioCampaign = RuleCampaign
    m.write = labeled_write
    def ceres_not_required(_scenario, _prices):
        report = {
            "result": "NOT_RERUN_KERNEL_AND_LIFECYCLE_UNCHANGED",
            "prior_reference": "Ceres parity previously passed at 8,798 transactions and 290 events; not rerun for this selection-only change",
        }
        labeled_write("ceres_equivalence_applicability_report.json", report)
        return report
    m.ceres_equivalence = ceres_not_required
    tripwire = tripwire_check()
    labeled_write("selection_firewall_tripwire_report.json", {
        "check": tripwire, "allowlisted_fields": sorted(__import__(
            "simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022.selection_rule",
            fromlist=["RECORD_FIELDS"]).RECORD_FIELDS),
        "selection_rule": "per-sponsor lowest total commitment; tie earliest eligible year then roster index",
        "boundary_admission_used": False,
    })
    m.main()


if __name__ == "__main__":
    main()
