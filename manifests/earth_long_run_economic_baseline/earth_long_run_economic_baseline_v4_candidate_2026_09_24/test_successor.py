"""Focused successor rules; synthetic data first, live source contract second."""
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("earth_successor", HERE / "successor.py")
successor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(successor)


class SuccessorRules(unittest.TestCase):
    def test_wpp_jan1_universe_excludes_aggregates(self):
        rows = [
            {"ISO3_code": "AAA", "LocTypeName": "Country/Area", "Time": "2026", "Variant": "Medium", "TPopulation1Jan": "2", "TPopulation1July": "3", "Location": "A"},
            {"ISO3_code": "BBB", "LocTypeName": "Country/Area", "Time": "2026", "Variant": "Medium", "TPopulation1Jan": "4", "TPopulation1July": "5", "Location": "B"},
            {"ISO3_code": "", "LocTypeName": "World", "Time": "2026", "Variant": "Medium", "TPopulation1Jan": "6", "Location": "World"},
            {"ISO3_code": "CCC", "LocTypeName": "Country/Area", "Time": "2025", "Variant": "Medium", "TPopulation1Jan": "7", "Location": "C"},
        ]
        universe, world = successor.wpp_identity(rows)
        self.assertEqual(set(universe), {"AAA", "BBB"})
        self.assertEqual(universe["AAA"]["population_2026"], 2000)
        self.assertEqual(world, 6000)

    def test_wpp_duplicate_identity_fails(self):
        row = {"ISO3_code": "AAA", "LocTypeName": "Country/Area", "Time": "2026", "Variant": "Medium", "TPopulation1Jan": "2", "Location": "A"}
        with self.assertRaises(ValueError):
            successor.wpp_identity([row, row])

    def test_tail_central_preserves_original_formula(self):
        pop = {y: {"AAA": 100 * math.exp(0.01 * (y - 2091))} for y in range(2091, 2101)}
        wap = {y: {"AAA": 0.6 + 0.001 * (y - 2091)} for y in range(2091, 2101)}
        original_pop, original_wap = copy.deepcopy(pop), copy.deepcopy(wap)
        out_pop, out_wap = successor.demographic_tail(pop, wap, 40, 30, 2102)
        self.assertEqual(pop, original_pop)
        self.assertEqual(wap, original_wap)
        self.assertAlmostEqual(out_pop[2101]["AAA"], pop[2100]["AAA"] * math.exp(0.01 * 2 ** (-1 / 40)))
        self.assertAlmostEqual(out_wap[2101]["AAA"], wap[2100]["AAA"] + 0.001 * 2 ** (-1 / 30))

    def test_anomaly_uses_signed_current_and_positive_pyp(self):
        source = {("AAA", "ENERGY"): {"current_va": -3, "current_go": 40, "pyp_va": 4, "pyp_go": 20}}
        seed = {("AAA", "ENERGY"): {"value_added": 0, "gross_output": 50, "employment": 5}}
        self.assertEqual(successor.qualifying_nodes(source, seed), [("AAA", "ENERGY")])
        self.assertEqual(source[("AAA", "ENERGY")]["current_va"], -3)
        source[("AAA", "ENERGY")]["pyp_va"] = -1
        self.assertEqual(successor.qualifying_nodes(source, seed), [])

    def test_repair_preserves_country_accounts_and_observation(self):
        source = {("AAA", "ENERGY"): {"current_va": -3, "current_go": 40, "pyp_va": 4, "pyp_go": 20}}
        sectors = {
            ("AAA", "ENERGY"): {"value_added": 0., "gross_output": 50., "capital": 0., "investment": 0., "employment": 5., "sector": "ENERGY", "iso3": "AAA"},
            ("AAA", "OTHER"): {"value_added": 100., "gross_output": 150., "capital": 300., "investment": 20., "employment": 15., "sector": "OTHER", "iso3": "AAA"},
        }
        assets = {("AAA", "OTHER", "machine"): {"capital": 300., "investment": 20., "asset_class": "machine"}}
        country = {"AAA": {"value_added": 100., "gross_output": 200., "capital": 300., "investment": 20., "employment": 20., "capital_share_alpha": 0.4, "country_tfp_multiplier": 1.0}}
        repaired, repaired_assets, trace = successor.repair_seed(source, sectors, assets, country)
        self.assertEqual(len(trace), 1)
        self.assertEqual(source[("AAA", "ENERGY")]["current_va"], -3)
        self.assertGreater(repaired[("AAA", "ENERGY")]["value_added"], 0)
        for key in ("value_added", "gross_output", "capital", "investment", "employment"):
            self.assertAlmostEqual(sum(row[key] for (iso, _), row in repaired.items() if iso == "AAA"), country["AAA"][key])
        self.assertAlmostEqual(sum(r["capital"] for r in repaired_assets.values()), 300.)
        self.assertIn("method_id", trace[0])

    def test_repair_uses_asset_backed_sector_capital(self):
        source = {("AAA", "ENERGY"): {"current_va": -3, "current_go": 40, "pyp_va": 4, "pyp_go": 20}}
        sector = {
            ("AAA", "ENERGY"): {"iso3": "AAA", "sector": "ENERGY", "value_added": 0., "gross_output": 50., "capital": 0., "investment": 0., "employment": 5.},
            ("AAA", "OTHER"): {"iso3": "AAA", "sector": "OTHER", "value_added": 60., "gross_output": 100., "capital": 50., "investment": 12., "employment": 10.},
            ("AAA", "THIRD"): {"iso3": "AAA", "sector": "THIRD", "value_added": 40., "gross_output": 50., "capital": 250., "investment": 8., "employment": 5.},
        }
        asset = {("AAA", "OTHER", "machine"): {"capital": 200.},
                 ("AAA", "THIRD", "machine"): {"capital": 100.}}
        country = {"AAA": {"value_added": 100., "gross_output": 200., "capital": 300., "investment": 20., "employment": 20., "capital_share_alpha": .4, "country_tfp_multiplier": 1.}}
        repaired, _, _ = successor.repair_seed(source, sector, asset, country)
        self.assertAlmostEqual(repaired[("AAA", "OTHER")]["capital"], 180.)
        self.assertAlmostEqual(repaired[("AAA", "THIRD")]["capital"], 90.)

    def test_epsilon_asset_placeholder_does_not_set_repaired_composition(self):
        source = {("AAA", "ENERGY"): {"current_va": -3, "current_go": 40, "pyp_va": 4, "pyp_go": 20}}
        sector = {
            ("AAA", "ENERGY"): {"iso3": "AAA", "sector": "ENERGY", "value_added": 0., "gross_output": 50., "capital": 0., "investment": 0., "employment": 5.},
            ("AAA", "OTHER"): {"iso3": "AAA", "sector": "OTHER", "value_added": 100., "gross_output": 150., "capital": 300., "investment": 20., "employment": 15.},
        }
        asset = {("AAA", "ENERGY", "machine"): {"capital": 1e-30},
                 ("AAA", "ENERGY", "structures"): {"capital": 9e-30},
                 ("AAA", "OTHER", "machine"): {"capital": 200.},
                 ("AAA", "OTHER", "structures"): {"capital": 100.}}
        country = {"AAA": {"value_added": 100., "gross_output": 200., "capital": 300., "investment": 20., "employment": 20., "capital_share_alpha": .4, "country_tfp_multiplier": 1.}}
        _, repaired_assets, _ = successor.repair_seed(source, sector, asset, country)
        self.assertAlmostEqual(repaired_assets[("AAA", "ENERGY", "machine")]["capital"], 20.)
        self.assertAlmostEqual(repaired_assets[("AAA", "ENERGY", "structures")]["capital"], 10.)
        self.assertAlmostEqual(sum(r["capital"] for (i, s, cls), r in repaired_assets.items() if cls == "machine"), 200.)

    def test_v3_manifest_immutable(self):
        pointer = HERE.parent / "EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json"
        import json
        data = json.loads(pointer.read_text())
        manifest = Path(data["active_manifest"])
        self.assertEqual(hashlib.sha256(manifest.read_bytes()).hexdigest(), data["active_manifest_sha256"])
        self.assertEqual(data["active_designation"], "EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23")

    def test_live_central_demography_matches_frozen_v3(self):
        report = json.loads((HERE / "DEMOGRAPHIC_SENSITIVITY.json").read_text())
        central = report["scenarios"]["CENTRAL"]
        v3_root = Path("/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v3_repaired_2026_09_23")
        with (v3_root / "full_2226/results/countries_2226.ndjson").open() as handle:
            frozen = [json.loads(line) for line in handle]
        self.assertEqual(set(central["country_population_2226"]) >= {r["iso3"] for r in frozen}, True)
        for row in frozen:
            iso = row["iso3"]
            self.assertEqual(central["country_population_2226"][iso], row["population"])
            self.assertEqual(central["country_working_age_share_2226"][iso], row["demographic_working_age_share"])

    def test_added_areas_do_not_receive_fabricated_economies(self):
        report = json.loads((HERE / "COUNTRY_EVIDENCE.json").read_text())
        rows = report["economies"]
        self.assertEqual(len(rows), len({r["iso3"] for r in rows}))
        added = [r for r in rows if not r["v3_economic_model"]]
        self.assertTrue(added)
        for row in added:
            for layer in ("factor_shares", "investment_capital", "sector_decomposition",
                          "asset_decomposition", "trade_network_topology"):
                self.assertEqual(row[layer]["class"], "UNAVAILABLE")
                self.assertIsNone(row[layer]["method_id"])
            macro = row["macroeconomic_envelope"]
            if macro["class"] == "DERIVED_FROM_QUALIFIED_METHOD":
                self.assertIsNotNone(macro["method_id"])

    def test_signed_oecd_source_matches_v3_hash(self):
        v3 = json.loads((HERE.parent / "earth_long_run_economic_baseline_v3_repaired_2026_09_23/RUN_MANIFEST.json").read_text())
        record = v3["sources"]["oecd_2024_current_va"]
        self.assertEqual(hashlib.sha256(Path(record["path"]).read_bytes()).hexdigest(), record["sha256"])

    def test_live_temporal_repair_is_continuous_through_2061(self):
        root = Path("/home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24")
        trace = json.loads((root / "RECONSTRUCTION_TRACE.json").read_text())["qualified_nodes"]
        self.assertEqual([(r["iso3"], r["sector"]) for r in trace], [("TWN", "ENERGY")])
        self.assertLess(trace[0]["source_current_va_2024"], 0)
        stages = (root / "stage_2026_2031/country_sectors_2026_2031.ndjson",
                  root / "stage_2031_2060/country_sectors_2031_2060.ndjson",
                  root / "smoke_2061/results/country_sectors_2060_2061.ndjson")
        years = {}
        for path in stages:
            with path.open() as handle:
                for line in handle:
                    row = json.loads(line)
                    if row["iso3"] == "TWN" and row["sector"] == "ENERGY":
                        years[row["year"]] = row
        self.assertEqual(set(years), set(range(2026, 2062)))
        self.assertTrue(all(row["value_added"] > 0 and row["capital"] > 0 for row in years.values()))
        self.assertTrue(all(years[y]["value_added"] / years[y-1]["value_added"] > 0.5 for y in range(2027, 2062)))

    def test_live_taiwan_asset_class_totals_preserved(self):
        original = Path("/home/ubuntu/LOOM_Earth2026/earth2026_sector_capital_asset_reconstruction_v0.2/country_sector_assets_2026.ndjson")
        candidate = Path("/home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24/seed_assets_2026.ndjson")
        def totals(path):
            result = {}
            with path.open() as handle:
                for line in handle:
                    row = json.loads(line)
                    if row["iso3"] == "TWN":
                        key = row["asset_class"]
                        result[key] = result.get(key, 0) + row["capital"]
            return result
        old, new = totals(original), totals(candidate)
        self.assertEqual(set(old), set(new))
        for key in old:
            self.assertTrue(math.isclose(old[key], new[key], rel_tol=1e-12), key)


if __name__ == "__main__":
    unittest.main()
