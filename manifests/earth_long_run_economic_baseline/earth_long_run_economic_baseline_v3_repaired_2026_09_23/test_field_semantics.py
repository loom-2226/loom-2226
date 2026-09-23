"""Read-only semantic checks for the designated v3 Earth baseline."""

import hashlib
import json
import math
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
POINTER = HERE.parent / "EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json"
SEMANTICS = json.loads((HERE / "FIELD_SEMANTICS.json").read_text())
EPS = 1e-12


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path, year=None):
    with path.open() as stream:
        for line in stream:
            row = json.loads(line)
            if year is None or row["year"] == year:
                yield row


def close(test, actual, expected, label):
    test.assertTrue(math.isclose(actual, expected, rel_tol=2e-10, abs_tol=1e-8),
                    f"{label}: {actual} != {expected}")


class FieldSemanticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pointer = json.loads(POINTER.read_text())
        cls.root = Path(pointer["active_manifest"]).parent
        cls.manifest = json.loads((cls.root / "BASELINE_MANIFEST.json").read_text())
        assert pointer["active_designation"] == SEMANTICS["baseline_id"]
        assert cls.manifest["designation"] == SEMANTICS["baseline_id"]

    def test_implementation_and_output_are_pinned(self):
        self.assertEqual(sha256(self.root / "BASELINE_MANIFEST.json"),
                         json.loads(POINTER.read_text())["active_manifest_sha256"])
        for name, expected in SEMANTICS["implementation_sha256"].items():
            self.assertEqual(sha256(HERE / name), expected, name)
            self.assertEqual(sha256(self.root / name), expected, name)
        for name, ref in self.manifest["selected_outputs"].items():
            if name.endswith("2226.ndjson"):
                self.assertEqual(sha256(Path(ref["path"])), ref["sha256"], name)

    def test_catalog_covers_actual_schemas(self):
        catalog = SEMANTICS["fields"]
        required = {"field_name", "meaning", "formula", "units", "quantity_kind",
                    "temporality", "origin_class", "ratio_numerator", "ratio_denominator",
                    "comparable_across_countries", "comparable_across_years", "price_basis",
                    "provenance", "valid_interpretation", "invalid_interpretation",
                    "canonical_semantic_name"}
        for context, entries in catalog.items():
            for entry in entries:
                self.assertEqual(set(entry), required, f"{context}.{entry['field_name']}")
                for key in required - {"formula", "ratio_numerator", "ratio_denominator"}:
                    self.assertTrue(entry[key], f"{context}.{entry['field_name']}.{key}")
        for dataset, rel in list(SEMANTICS["dataset_paths"].items())[:3]:
            actual = set()
            for row in rows(self.root / rel):
                actual.update(row)
            self.assertEqual(actual, {e["field_name"] for e in catalog[dataset]}, dataset)
        repairs = json.loads((self.root / "full_2226/results/active_boundary_repairs.json").read_text())
        self.assertEqual(set().union(*(set(r) for r in repairs)),
                         {e["field_name"] for e in catalog["active_boundary_repair"]})
        summary = json.loads((self.root / "TRAJECTORY_SUMMARY.json").read_text())
        for context, obj in (("trajectory_summary", summary),
                             ("trajectory_summary.global_2226", summary["global_2226"]),
                             ("trajectory_summary.top20", summary["top20"][0])):
            self.assertEqual(set(obj), {e["field_name"] for e in catalog[context]})

    def test_endpoint_ratio_and_stock_flow_identities(self):
        country = {r["iso3"]: r for r in rows(self.root / "full_2226/results/countries_2226.ndjson")}
        sector = {(r["iso3"], r["sector"]): r for r in rows(self.root / "full_2226/results/country_sectors_2226.ndjson")}
        asset = {(r["iso3"], r["sector"], r["asset_class"]): r for r in rows(self.root / "full_2226/results/country_sector_assets_2226.ndjson")}
        prior = {(r["iso3"], r["sector"], r["asset_class"]): r for r in rows(self.root / "full_2226/results/country_sector_assets_2060_2226.ndjson", 2225)}
        for iso, r in country.items():
            close(self, r["investment_output_ratio"], r["investment"] / r["value_added"], f"{iso} I/VA")
            close(self, r["labor_exponent_effective"], 1 - r["capital_share_alpha"], f"{iso} labor exponent")
            close(self, r["effective_labor_input"], r["employment"] + r["synthetic_labor_equivalent"], f"{iso} effective labor")
            close(self, r["synthetic_to_biological_employment_ratio"], r["synthetic_labor_equivalent"] / max(EPS, r["employment"]), f"{iso} synthetic ratio")
            close(self, r["demographic_working_age_population"], r["population"] * r["demographic_working_age_share"], f"{iso} working-age population")
        for key, r in sector.items():
            c = country[key[0]]
            close(self, r["labor_exponent_effective"], 1 - r["capital_share_alpha"], f"{key} exponent")
            close(self, r["effective_labor_input"], r["employment"] + r["synthetic_labor_equivalent"], f"{key} labor")
            close(self, r["labor_share_of_country"], r["employment"] / c["employment"], f"{key} labor share")
            close(self, r["investment_share_of_country"], r["investment"] / c["investment"], f"{key} investment share")
            close(self, r["synthetic_labor_equivalent_ratio"], r["synthetic_labor_equivalent"] / max(EPS, r["employment"]), f"{key} synthetic ratio")
            modeled = r["country_tfp_multiplier"] * r["technology_productivity_multiplier"] * r["A"] * r["capital"] ** r["capital_share_alpha"] * r["effective_labor_input"] ** r["labor_exponent_effective"]
            close(self, r["value_added"], modeled, f"{key} production")
        for key, r in asset.items():
            s = sector[key[:2]]
            p = prior[key]
            close(self, r["replacement_need"], r["asset_depreciation_rate"] * r["capital"], f"{key} replacement need")
            close(self, r["replacement_funded"], r["replacement_need"] * r["replacement_coverage_ratio"], f"{key} funded")
            close(self, r["investment"], r["replacement_funded"] + r["expansion_investment"], f"{key} investment")
            close(self, r["share_of_sector_capital"], r["capital"] / s["capital"], f"{key} asset share")
            close(self, r["capital"], (1 - r["asset_depreciation_rate"]) * p["capital"] + p["investment"], f"{key} stock flow")
        checks = json.loads((self.root / "full_2226/results/checkpoints.json").read_text())
        checkpoint = checks["2226"]
        close(self, checkpoint["investment_output_ratio"], checkpoint["investment"] / checkpoint["value_added"], "global I/VA")
        close(self, checkpoint["capital_output_ratio"], checkpoint["capital"] / checkpoint["value_added"], "global K/VA")

    def test_contract_formula_text_and_source_sign(self):
        fields = SEMANTICS["fields"]
        by_name = lambda context, name: next(e for e in fields[context] if e["field_name"] == name)
        self.assertEqual(by_name("country_annual", "investment_output_ratio")["ratio_denominator"], "value_added")
        self.assertEqual(by_name("checkpoint", "capital_output_ratio")["ratio_denominator"], "value_added")
        self.assertEqual(by_name("country_annual", "labor_exponent_effective")["formula"], "1 - capital_share_alpha")
        self.assertEqual(by_name("country_sector_annual", "A")["canonical_semantic_name"], "cobb_douglas_A_effective")
        repair = json.loads((self.root / "full_2226/results/active_boundary_repairs.json").read_text())
        self.assertEqual(len(repair), 1)
        self.assertEqual((repair[0]["iso3"], repair[0]["sector"]), ("TWN", "ENERGY"))
        self.assertLess(repair[0]["source_va_2024_current_usd_million"], 0)
        self.assertGreater(repair[0]["reconstructed_va_2060"], 0)


if __name__ == "__main__":
    unittest.main()
