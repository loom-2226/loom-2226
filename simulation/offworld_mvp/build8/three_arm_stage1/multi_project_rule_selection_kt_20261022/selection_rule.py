"""Explicit, allowlisted multi-project selection rule for the PR427 run."""
from decimal import Decimal

REPORT_LABEL = "SELECTION: Box 3 rule re-implemented. Boundary admission NOT used. Firewall checked by tripwire test only."

# The selector sees only these values. Physical/world descriptions, geology,
# availability, generated-world metadata and boundary-admission fields are out.
RECORD_FIELDS = frozenset({
    "body", "sponsor", "eligibility_year", "roster_index",
    "reviewed_result", "review_status", "quoted_price_usd",
    "quoted_price_model", "total_capital_commitment",
})


def select_projects(records, sponsor_capital):
    """Pick each sponsor's least-commitment eligible project it can fund.

    Ranking: total commitment, earliest eligible year, then roster index.
    Capital is isolated by sponsor. Equal commitment groups are counted.
    """
    clean = []
    for record in records:
        extra = set(record) - RECORD_FIELDS
        missing = RECORD_FIELDS - set(record)
        if extra or missing:
            raise ValueError(f"selection input schema violation: extra={sorted(extra)} missing={sorted(missing)}")
        if record["reviewed_result"] != "SUPPORTS_ADVANCE" or record["review_status"] != "ADVANCE":
            continue
        clean.append(record)

    selected, tie_groups = [], []
    by_sponsor = {}
    for record in clean:
        by_sponsor.setdefault(record["sponsor"], []).append(record)
    for sponsor, group in by_sponsor.items():
        group.sort(key=lambda r: (Decimal(r["total_capital_commitment"]),
                                  int(r["eligibility_year"]), int(r["roster_index"])))
        equal = {}
        for record in group:
            equal.setdefault(record["total_capital_commitment"], []).append(record)
        for amount, tied in equal.items():
            if len(tied) > 1:
                tie_groups.append({"sponsor": sponsor, "commitment": amount,
                                   "projects": [{"body": r["body"], "eligibility_year": r["eligibility_year"],
                                                 "roster_index": r["roster_index"]} for r in tied]})
        available = Decimal(str(sponsor_capital.get(sponsor, "0")))
        affordable = [r for r in group if Decimal(r["total_capital_commitment"]) <= available]
        if affordable:
            selected.append(affordable[0])
    return selected, tie_groups


def tripwire_check():
    clean = {
        "body": "BODY_A", "sponsor": "SPONSOR_A", "eligibility_year": 2038,
        "roster_index": 0, "reviewed_result": "SUPPORTS_ADVANCE", "review_status": "ADVANCE",
        "quoted_price_usd": "100", "quoted_price_model": "0.1",
        "total_capital_commitment": "0.2",
    }
    picked, _ = select_projects([clean], {"SPONSOR_A": "1"})
    if picked != [clean]:
        raise AssertionError("clean allowlisted selection did not pass")
    leaked = dict(clean, hidden_world_field="ACCESSIBLE_RESOURCE_ESTIMATE")
    try:
        select_projects([leaked], {"SPONSOR_A": "1"})
    except ValueError as exc:
        return {"clean_input": "PASS", "deliberate_hidden_field": "REJECTED", "reason": str(exc),
                "leak_removed": True}
    raise AssertionError("hidden-world field tripwire failed to reject deliberate leak")
