"""Read-only audit of saved PR427 mission-price artifacts.

The three inputs remain separate quote populations. This module does not
select or blend a quote across incompatible runs or calculation methods.
"""
from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE1 = HERE.parent
SOURCES = {
    "recovered_combined_59": STAGE1 / "RECOVERED_COMBINED_59_PINNED_QUOTES_TEST_ONLY.csv",
    "rendezvous_v2_90": STAGE1 / "RENDEZVOUS_V2_PRICES_TEST_ONLY.csv",
    "vehicle_flyby": STAGE1 / "VEHICLE_FLYBY_PRICES_TEST_ONLY.csv",
}


def read(path):
    raw = path.read_bytes()
    return raw, list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def source_inventory(name, path):
    raw, rows = read(path)
    years = sorted({int(r["year"]) for r in rows if r.get("year", "").isdigit()})
    bodies = sorted({r["body"] for r in rows if r.get("body")})
    statuses = {}
    for row in rows:
        status = row.get("status", "MISSING_STATUS")
        statuses[status] = statuses.get(status, 0) + 1
    identities = sorted({r.get("run_identity", "") for r in rows if r.get("run_identity")})
    return {
        "source": name,
        "path": str(path.relative_to(STAGE1)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "rows": len(rows), "body_count": len(bodies), "bodies": bodies,
        "years": years, "statuses": statuses, "run_identities": identities,
        "rows_data": rows,
    }


def main():
    inventories = {name: source_inventory(name, path) for name, path in SOURCES.items()}
    # The 90-body Rendezvous V2 roster is the saved 90-body scenario roster;
    # no project/body roster is authored here.
    roster = inventories["rendezvous_v2_90"]["bodies"]
    matrix = []
    for body in roster:
        for year in (2026, 2027, 2035, 2036, 2226):
            for mission in ("flyby", "rendezvous"):
                source_rows = []
                for name, inv in inventories.items():
                    for row in inv["rows_data"]:
                        row_mission = row.get("mission_type_id")
                        if name == "rendezvous_v2_90":
                            row_mission = "rendezvous"
                        elif name == "vehicle_flyby":
                            row_mission = "flyby"
                        if row.get("body") == body and row_mission == mission and int(row.get("year", -1)) == year:
                            source_rows.append((name, row))
                exact = [(n, r) for n, r in source_rows if r.get("status") == "PRICED_TEST_ONLY"]
                # The authorized hold is explicitly the 2026 quote after 2035.
                # From 2028 through 2035 we retain the same 2026 baseline;
                # 2027 is admitted only from its own saved priced row.
                held = []
                if not exact and year not in (2026, 2027):
                    for name, inv in inventories.items():
                        candidates = []
                        for row in inv["rows_data"]:
                            mt = row.get("mission_type_id")
                            if name == "rendezvous_v2_90": mt = "rendezvous"
                            if name == "vehicle_flyby": mt = "flyby"
                            if row.get("body") == body and mt == mission and int(row.get("year", -1)) == 2026 and row.get("status") == "PRICED_TEST_ONLY":
                                candidates.append(row)
                        if candidates:
                            held.append((name, candidates[0]))
                selected = exact or held
                matrix.append({
                    "body": body, "calendar_year": year, "mission_type": mission,
                    "status": "PRICED_TEST_ONLY" if selected else "UNPRICED",
                    "quote_sources": [n for n, _ in selected],
                    "quotes": [quote_record(n, r, year) for n, r in selected],
                    "unpriced_reason": None if selected else reason_for(inventories, body, year, mission),
                    "selection_rule": "preserve all exact-year source rows; held-year rows are reported as separate source quotes; never blend source populations",
                })
    # The general project scenario records study spend independently of mission pricing.
    scenario_path = STAGE1 / "general_project_v2_kt_20261022" / "scenario.json"
    scenario = json.loads(scenario_path.read_text())
    project = scenario["project"]
    recovered = inventories["recovered_combined_59"]["rows_data"]
    sensitivity = []
    for body in roster:
        rows = [r for r in recovered if r.get("body") == body and int(r.get("year", -1)) == 2026 and r.get("status") == "PRICED_TEST_ONLY"]
        by_mission = {r.get("mission_type_id"): r for r in rows}
        flyby, rendezvous = by_mission.get("flyby"), by_mission.get("rendezvous")
        comparable = bool(flyby and rendezvous and flyby.get("run_identity") == rendezvous.get("run_identity"))
        flyby_price = Decimal(flyby["lowest_price_usd"]) if flyby else None
        rendezvous_price = Decimal(rendezvous["lowest_price_usd"]) if rendezvous else None
        sensitivity.append({
            "body": body, "status": "PAIRED_SAME_RUN" if comparable else "NO_PAIRED_SAME_RUN_QUOTES",
            "source": "RECOVERED_COMBINED_59_PINNED_QUOTES_TEST_ONLY.csv",
            "source_run_identity": flyby.get("run_identity") if comparable else None,
            "flyby_usd": None if flyby_price is None else str(flyby_price),
            "rendezvous_usd": None if rendezvous_price is None else str(rendezvous_price),
            "rendezvous_minus_flyby_usd": str(rendezvous_price - flyby_price) if comparable else None,
            "rendezvous_to_flyby_ratio": str(rendezvous_price / flyby_price) if comparable and flyby_price else None,
            "interpretation": "Hypothetical A1 physical-mission price sensitivity only; does not price or reinterpret A1 study work.",
        })
    out = {
        "classification": "TEST_ONLY_NONCANON_PRICE_PROVENANCE_AUDIT",
        "mission_prices_are_physical_mission_quotes_only": True,
        "A1_A2_study_spend_is_separate": {
            "study_a2_receipt_value_model_currency": project["study_a2_receipt_value"],
            "study_price_link": scenario["price_inputs"].get("study_price_link"),
            "physical_mission_usd_per_model_currency": scenario["price_inputs"]["usd_per_model_currency"],
            "scope": "Study payment is an authored lifecycle expense; it is not a physical-spacecraft mission quote or price sensitivity input.",
        },
        "sources": {k: {x: v for x, v in inv.items() if x != "rows_data"} for k, inv in inventories.items()},
        "roster_source": "RENDEZVOUS_V2_PRICES_TEST_ONLY.csv body column",
        "roster_count": len(roster),
        "matrix": matrix,
        "a1_physical_mission_price_sensitivity": sensitivity,
        "a1_physical_mission_sensitivity_boundary": "Flyby versus rendezvous values are hypothetical physical-spacecraft mission prices from paired same-run saved quotes. A1 study spend remains separately reported above and is not multiplied, converted, or treated as spacecraft pricing.",
        "unpriced_by_year_mission": {
            f"{year}:{mission}": [r["body"] for r in matrix if r["calendar_year"] == year and r["mission_type"] == mission and r["status"] == "UNPRICED"]
            for year in (2026, 2027, 2035, 2036, 2226) for mission in ("flyby", "rendezvous")
        },
        "limitations": [
            "The recovered combined quote population, Rendezvous V2, and Vehicle Flyby tables are preserved as separate provenance sources.",
            "The post-2035 output is a held saved quote, not a year-specific forecast.",
            "A mission quote does not establish that any body study is physically validated or that a project is eligible.",
        ],
    }
    target = HERE / "price_provenance_audit.json"
    target.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"report": str(target), "roster_count": len(roster), "source_counts": {k: v["rows"] for k, v in out["sources"].items()}, "unpriced": {k: len(v) for k, v in out["unpriced_by_year_mission"].items()}}, sort_keys=True))


def quote_record(source, row, requested_year):
    # Preserve original values and source identity rather than normalizing
    # incompatible USD/model-unit representations into one number.
    return {
        "source": source, "source_year": int(row["year"]),
        "held": int(row["year"]) != requested_year,
        "status": row.get("status"), "run_identity": row.get("run_identity"),
        "price_fields": {k: v for k, v in row.items() if "price" in k.lower() or k in ("total_usd", "model_units", "launch_cost_usd", "operating_cost_usd")},
        "method_fields": {k: row[k] for k in ("vehicle_class_id", "mission_type_id", "parent", "calculation_path", "reason", "flyby_source") if k in row},
    }


def reason_for(inventories, body, year, mission):
    matching = []
    for name, inv in inventories.items():
        for row in inv["rows_data"]:
            mt = row.get("mission_type_id")
            if name == "rendezvous_v2_90": mt = "rendezvous"
            if name == "vehicle_flyby": mt = "flyby"
            if row.get("body") == body and mt == mission:
                matching.append(row)
    if not matching:
        return "No saved row for this body and mission type in any supplied quote source."
    same_year = [r for r in matching if int(r.get("year", -1)) == year]
    if same_year:
        return "Saved row(s) exist for this body/year/mission, but all are non-PRICED_TEST_ONLY; source status and reason are retained in source tables."
    available_years = sorted({int(r["year"]) for r in matching})
    return f"No exact-year quote row for this body and mission type; saved source years are {available_years}."


if __name__ == "__main__":
    main()
