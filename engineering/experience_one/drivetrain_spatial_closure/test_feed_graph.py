"""PR D logical connectivity regression suite; no physical feed qualification."""
from dataclasses import replace
import unittest
from unittest.mock import patch

from engineering.experience_one.drivetrain_spatial_closure.feed_graph import (
    EXTERNAL, RESERVE, TANKS, TORCH, FeedState, edges, reachable, verify_feed_state,
)


class FeedGraphTests(unittest.TestCase):
    def test_four_normal_tanks_route_independently(self):
        result = verify_feed_state(FeedState())
        self.assertEqual(result['normal_reachable'], (True,) * 4)
        self.assertEqual(result['external_reachable'], (False, False))
        self.assertFalse(result['reserve_reachable'])

    def test_each_tank_isolates_without_disabling_others(self):
        for index in range(4):
            with self.subTest(tank=index + 1):
                valves = tuple(i != index for i in range(4))
                self.assertEqual(verify_feed_state(FeedState(normal_open=valves))['normal_reachable'], valves)

    def test_header_isolation_and_shutdown(self):
        for state in (FeedState(header_open=False), FeedState(torch_enabled=False),
                      FeedState(torch_enabled=False, high_metric_enabled=True)):
            with self.subTest(state=state):
                result = verify_feed_state(state)
                self.assertEqual(result['normal_reachable'], (False,) * 4)
                self.assertEqual(result['external_reachable'], (False, False))

    def test_external_attachment_is_not_automatic_feed_permission(self):
        state = FeedState(external_attached=(True, True))
        self.assertEqual(verify_feed_state(state)['external_reachable'], (False, False))
        self.assertEqual(verify_feed_state(replace(state, external_open=(True, False)))['external_reachable'], (True, False))
        self.assertEqual(verify_feed_state(replace(state, external_open=(True, True)))['external_reachable'], (True, True))

    def test_detached_open_feed_rejected(self):
        with self.assertRaises(ValueError):
            FeedState(external_open=(True, False))

    def test_torch_metric_exclusion(self):
        with self.assertRaises(ValueError):
            FeedState(torch_enabled=True, high_metric_enabled=True)

    def test_state_shapes_and_types_rejected(self):
        with self.assertRaises(ValueError):
            FeedState(normal_open=(True, True, True))
        with self.assertRaises(ValueError):
            FeedState(header_open=1)

    def test_protected_reserve_has_no_route(self):
        links = edges(FeedState(external_attached=(True, True), external_open=(True, True)))
        self.assertFalse(reachable(links, RESERVE, TORCH))
        self.assertFalse(any(RESERVE in edge for edge in links))

    def test_injected_reserve_bypass_rejected(self):
        real_edges = edges
        def compromised(state):
            return real_edges(state) | {(RESERVE, TORCH)}
        with patch('engineering.experience_one.drivetrain_spatial_closure.feed_graph.edges', compromised):
            with self.assertRaisesRegex(ValueError, 'protected reserve'):
                verify_feed_state(FeedState())

    def test_injected_closed_tank_bypass_rejected(self):
        state = FeedState(normal_open=(False, True, True, True))
        real_edges = edges
        def compromised(value):
            return real_edges(value) | {(TANKS[0], TORCH)}
        with patch('engineering.experience_one.drivetrain_spatial_closure.feed_graph.edges', compromised):
            with self.assertRaisesRegex(ValueError, 'isolation bypass'):
                verify_feed_state(state)

    def test_injected_detached_external_bypass_rejected(self):
        real_edges = edges
        def compromised(value):
            return real_edges(value) | {(EXTERNAL[0], TORCH)}
        with patch('engineering.experience_one.drivetrain_spatial_closure.feed_graph.edges', compromised):
            with self.assertRaisesRegex(ValueError, 'isolation bypass'):
                verify_feed_state(FeedState())


if __name__ == '__main__':
    unittest.main()
