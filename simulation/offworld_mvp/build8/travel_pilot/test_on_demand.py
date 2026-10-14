"""Focused offline, non-runtime on-demand geometry tests."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json

from .on_demand import (
    OnDemandTravel, MIN_USEFUL_LAUNCH_WINDOW_DAYS, HALF_WINDOW_FACTOR,
    DENSE_FLIGHT_STEP_DAYS, pareto_geometry,
)
from .pilot import _day, _iso


class GeometryTests(TestCase):
    def test_exact_three_dimensional_dominance_preserves_limit_choices(self):
        rows = [
            dict(flight_days=100, departure_vinf_km_s=10, arrival_vinf_km_s=13),
            dict(flight_days=101, departure_vinf_km_s=11, arrival_vinf_km_s=14),
            dict(flight_days=102, departure_vinf_km_s=9, arrival_vinf_km_s=15),
            dict(flight_days=103, departure_vinf_km_s=12, arrival_vinf_km_s=8),
            dict(flight_days=104, departure_vinf_km_s=9.5, arrival_vinf_km_s=14),
        ]
        front = pareto_geometry(rows)
        self.assertLess(len(front), len(rows))
        for removed in [r for r in rows if r not in front]:
            self.assertTrue(any(
                f["flight_days"] <= removed["flight_days"]
                and f["departure_vinf_km_s"] <= removed["departure_vinf_km_s"]
                and f["arrival_vinf_km_s"] <= removed["arrival_vinf_km_s"]
                for f in front))
        for dep in [0, 9, 9.5, 10, 11, 20]:
            for arr in [0, 8, 13, 14, 15, 20]:
                admissible = lambda rs: [r["flight_days"] for r in rs
                    if r["departure_vinf_km_s"] <= dep
                    and r["arrival_vinf_km_s"] <= arr]
                self.assertEqual(min(admissible(rows), default=None),
                                 min(admissible(front), default=None))

    def test_minimum_window_and_daily_request_never_skip_calendar_dates(self):
        self.assertEqual(MIN_USEFUL_LAUNCH_WINDOW_DAYS, 1.0)
        self.assertEqual(HALF_WINDOW_FACTOR, 0.5)
        pilot = OnDemandTravel()
        observed = []
        def fake_geometry(a, b, date, *, strategy):
            observed.append(_iso(_day(date)))
            return {"trajectories": []}
        with patch.object(pilot, "geometry", side_effect=fake_geometry):
            result = pilot.lookup("EARTH", "MARS", "2026-10-29",
                                  wait_limit_days=4, departure_limit=10,
                                  arrival_limit=10)
        self.assertEqual(observed, [
            "2026-10-29T00:00:00Z", "2026-10-30T00:00:00Z",
            "2026-10-31T00:00:00Z", "2026-11-01T00:00:00Z"])
        self.assertEqual(result["opportunities"], [])

    def test_geometry_cache_excludes_vehicle_limits_and_price_and_replays(self):
        with TemporaryDirectory() as a, TemporaryDirectory() as b:
            first = OnDemandTravel(cache_dir=a)
            geometry = first.geometry("EARTH", "MARS", "2026-10-29")
            first_file, = list(Path(a).glob("*.json"))
            content = first_file.read_bytes()
            cheaper = first.admissible(geometry, departure_limit=10,
                                      arrival_limit=10)
            broader = first.admissible(geometry, departure_limit=20,
                                      arrival_limit=20)
            self.assertGreater(len(broader), len(cheaper))
            self.assertNotIn("price", json.dumps(geometry["key"]).lower())
            self.assertNotIn("limit", json.dumps(geometry["key"]).lower())
            cached = OnDemandTravel(cache_dir=a)
            self.assertEqual(cached.geometry("EARTH", "MARS", "2026-10-29"),
                             geometry)
            self.assertEqual(cached.solve_count, 0)
            replay = OnDemandTravel(cache_dir=b)
            self.assertEqual(replay.geometry("EARTH", "MARS", "2026-10-29"),
                             geometry)
            second_file, = list(Path(b).glob("*.json"))
            self.assertEqual(content, second_file.read_bytes())
            self.assertEqual(first_file.name, second_file.name)

    def test_ten_mercury_witnesses_under_existing_diagnostic_cap(self):
        pilot = OnDemandTravel()
        dates = ("2026-04-23", "2026-04-30", "2026-05-07",
                 "2027-04-15", "2027-04-22", "2031-05-15",
                 "2031-05-22", "2031-05-29",
                 "2026-05-14", "2031-05-08")
        for day in dates:
            with self.subTest(date=day):
                geom = pilot.geometry("EARTH", "MERCURY", day)
                options = pilot.admissible(
                    geom, departure_limit=10, arrival_limit=10)
                self.assertTrue(options, "lost Mercury witness " + day)
                self.assertTrue(all(r["departure_vinf_km_s"] <= 10
                                    and r["arrival_vinf_km_s"] <= 10
                                    for r in options))

    def test_research_distance_scan_recall_on_four_slower_routes_and_mercury(self):
        # Short sampled comparisons, NOT 200-year or continuous completeness.
        examples = [
            ("EARTH", "MERCURY", "2026-05-14"),
            ("EARTH", "MARS", "2026-10-29"),
            ("MARS", "CERES", "2029-06-28"),
            ("EARTH", "CERES", "2026-06-04"),
            ("CERES", "MARS", "2029-06-28"),
        ]
        pilot = OnDemandTravel()
        positives = 0
        for origin, destination, first_day in examples:
            for offset in range(3):
                day = (_day(first_day) + timedelta(days=offset)).date().isoformat()
                with self.subTest(route=(origin,destination), day=day):
                    dense = pilot.geometry(origin, destination, day, strategy="daily")
                    research = pilot.geometry(origin, destination, day,
                                              strategy="distance_research")
                    for cap in (10., 20.):
                        dense_options = pilot.admissible(
                            dense, departure_limit=cap, arrival_limit=cap)
                        research_options = pilot.admissible(
                            research, departure_limit=cap, arrival_limit=cap)
                        if dense_options:
                            positives += 1
                            self.assertTrue(research_options,
                                            "missed dense-sampled opportunity")
                    if destination == "MERCURY":
                        self.assertLessEqual(
                            pilot.steps_at(origin,destination,day)["departure_step_days"],
                            MIN_USEFUL_LAUNCH_WINDOW_DAYS)
        self.assertGreaterEqual(positives, 18)

    def test_daily_strategy_uses_quarter_day_flight_steps(self):
        pilot = OnDemandTravel()
        a = pilot.geometry("EARTH", "MARS", "2026-10-29")
        self.assertEqual(a["key"]["flight_time_step_days"],
                         DENSE_FLIGHT_STEP_DAYS)
        self.assertEqual(a["sampled_solutions"], a["key"]["flight_sample_count"])

    def test_invalid_route_fails_closed_and_no_runtime_integration(self):
        pilot = OnDemandTravel()
        with self.assertRaisesRegex(ValueError, "ROUTE_NOT_IN_NARROW_PILOT"):
            pilot.geometry("EARTH", "JUPITER", "2026-01-01")
        with self.assertRaisesRegex(ValueError, "INVALID_WAIT_LIMIT"):
            pilot.lookup("EARTH", "MARS", "2026-10-29",
                         wait_limit_days=0, departure_limit=10,
                         arrival_limit=10)
