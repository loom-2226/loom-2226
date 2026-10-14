"""Focused Build 8 scaled flight search tests; no default behavior changes."""
from __future__ import annotations

from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone
import json

import numpy as np

from .on_demand import OnDemandTravel
from .scaled_flight import (
    MIN_USEFUL_FLIGHT_TIME_FRACTION,
    MIN_USEFUL_FLIGHT_TIME_FLOOR_DAYS,
    useful_flight_grid, search_scaled_flight,
)


class ScaledFlightTests(TestCase):
    def setUp(self):
        self.p = OnDemandTravel()

    def request(self, *, lo=45., initial=90., limit=160., cap=20):
        return search_scaled_flight(
            self.p, "EARTH", "MARS", datetime(2026,1,1,tzinfo=timezone.utc),
            flight_range_days=(lo,initial), max_flight_time_days=limit,
            departure_limit=cap, arrival_limit=cap)

    def test_named_resolution_and_required_visible_horizon(self):
        self.assertEqual(MIN_USEFUL_FLIGHT_TIME_FRACTION,.005)
        self.assertEqual(MIN_USEFUL_FLIGHT_TIME_FLOOR_DAYS,1.)
        grid=useful_flight_grid(45,3000)
        self.assertEqual(grid[0],45.)
        self.assertEqual(grid[-1],3000.)
        self.assertTrue(all(b>a for a,b in zip(grid,grid[1:])))
        self.assertAlmostEqual(grid[1]-grid[0],1.)
        self.assertTrue(any(b-a>10 for a,b in zip(grid,grid[1:])))
        with self.assertRaisesRegex(ValueError,"EXPLICIT_INITIAL_RANGE_AND_HORIZON_REQUIRED"):
            self.p.lookup("EARTH","MARS","2026-01-01",wait_limit_days=1,
                departure_limit=10,arrival_limit=10,strategy="scaled_flight_time")
        with self.assertRaisesRegex(ValueError,"INVALID_AUTHORED_FLIGHT_HORIZON"):
            self.request(initial=90,limit=80)

    def test_open_edge_reports_unresolved_not_cheapest(self):
        def admissible(_engine,a,b,date,times):
            return np.full(len(times),3.),np.full(len(times),4.),None
        with patch("simulation.offworld_mvp.build8.travel_pilot.scaled_flight._evaluate",
                   side_effect=admissible):
            r=self.request(limit=160.)
        self.assertEqual(r["status"],"FLIGHT_RANGE_OPEN_EDGE")
        self.assertTrue(r["edge_open"])
        self.assertEqual(r["evaluated_flight_range_days"],[45.,160.])
        self.assertTrue(r["geometry_key"]["extensions"])
        self.assertEqual(r["geometry_key"]["min_useful_flight_time_fraction"],.005)
        self.assertEqual(r["geometry_key"]["min_useful_flight_time_floor_days"],1.)
        self.assertNotIn("price",json.dumps(r["geometry_key"]).lower())
        self.assertNotIn("vinf",json.dumps(r["geometry_key"]).lower())
        self.assertNotIn("limit",json.dumps(r["geometry_key"]).lower().replace("max_flight_time_days",""))
        self.assertFalse(self.p._geometry)

    def test_extended_then_closed_is_bounded_for_scoped_range(self):
        def sample(_engine,a,b,date,times):
            vals=np.array([4. if t<110 else 30. for t in times])
            return vals,vals,None
        with patch("simulation.offworld_mvp.build8.travel_pilot.scaled_flight._evaluate",
                   side_effect=sample):
            r=self.request(limit=160.)
        self.assertEqual(r["status"],"EXTENDED_BOUNDED")
        self.assertFalse(r["edge_open"])
        self.assertEqual(len(r["geometry_key"]["extensions"]),2)
        self.assertEqual(r["geometry_key"]["extensions"][-1]["trigger"],
                         "RECALL_SEARCH_TO_EXPLICIT_HORIZON")
        self.assertEqual(r["evaluated_flight_range_days"],[45.,160.])
        self.assertTrue(r["windows"])

    def test_unavailable_extended_source_is_unknown(self):
        call=0
        def source_or_fail(_engine,a,b,date,times):
            nonlocal call
            call+=1
            if call==2:raise ValueError("BULK_SOURCE_COVERAGE_SEAM")
            return np.full(len(times),3.),np.full(len(times),3.),None
        with patch("simulation.offworld_mvp.build8.travel_pilot.scaled_flight._evaluate",
                   side_effect=source_or_fail):
            r=self.request(limit=160.)
        self.assertEqual(r["status"],"UNKNOWN_FLIGHT_RANGE")
        self.assertIn("BULK_SOURCE_COVERAGE_SEAM",r["reason"])
        self.assertEqual(r["windows"],[])
        self.assertEqual(call,2)

    def test_real_pluto_source_seam_refuses_to_propagate(self):
        # Pluto is direct on departure day, but its 2199/2200 arrival
        # window crosses into a non-navigation-grade source.
        record=self.p.lookup("NEPTUNE","PLUTO","2199-10-01",
            wait_limit_days=1,departure_limit=20,arrival_limit=20,
            strategy="scaled_flight_time",
            flight_range_days=(45.,180.),
            max_flight_time_days=720.)["summaries"][0]
        self.assertEqual(record["status"],"UNKNOWN_FLIGHT_RANGE")
        self.assertIn("BULK_SOURCE_COVERAGE_SEAM",record["reason"])
        self.assertFalse(record["windows"])
        self.assertEqual(record["sampled_solutions"],0)

    def test_opt_in_never_writes_geometry_warehouse(self):
        with TemporaryDirectory() as root:
            pilot=OnDemandTravel(cache_dir=root)
            result=pilot.lookup("EARTH","MERCURY","2026-05-14",
                wait_limit_days=1,departure_limit=20,arrival_limit=20,
                strategy="scaled_flight_time",flight_range_days=(45.,180.),
                max_flight_time_days=520.)
            self.assertEqual(len(result["summaries"]),1)
            self.assertEqual(list(Path(root).iterdir()),[])
            self.assertFalse(pilot._geometry)

    def test_actual_opt_in_search_summary_stable_without_files(self):
        args=dict(wait_limit_days=1,departure_limit=20,arrival_limit=20,
                  strategy="scaled_flight_time",flight_range_days=(45.,180.),
                  max_flight_time_days=520.)
        first=self.p.lookup("EARTH","MERCURY","2026-05-14",**args)
        second=OnDemandTravel().lookup("EARTH","MERCURY","2026-05-14",**args)
        self.assertEqual(first,second)
        self.assertEqual(first["max_flight_time_days"],520.)
        self.assertEqual(first["sampling_strategy"],"scaled_flight_time")
        self.assertEqual(len(first["summaries"]),1)
        self.assertEqual(first["summaries"][0]["geometry_key"]["source_origin_id"],"DE440")
        self.assertFalse(self.p._geometry)
        self.assertNotIn("trajectories",json.dumps(first["summaries"][0]))
