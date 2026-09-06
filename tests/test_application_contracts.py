import unittest

from loom.application.contracts import (
    CampaignClockState,
    ContractError,
    FlightPlaybackState,
    LoomRouteSolution,
    SpatialState,
    TrajectorySegment,
    TrajectorySolution,
)


def spatial(entity="SHIP", epoch="2226-08-22T00:00:00Z"):
    return SpatialState(entity, epoch, "HELIOCENTRIC_J2000_ECLIPTIC", (1, 2, 3), (0.1, 0.2, 0.3))


class ApplicationContractTests(unittest.TestCase):
    def test_campaign_clock_requires_timezone_and_nonnegative_revision(self):
        clock = CampaignClockState("campaign-1", 9, "2226-08-22T00:00:00Z")
        self.assertEqual(clock.revision, 9)
        with self.assertRaises(ContractError):
            CampaignClockState("campaign-1", -1, "2226-08-22T00:00:00Z")
        with self.assertRaises(ContractError):
            CampaignClockState("campaign-1", 1, "2226-08-22T00:00:00")

    def test_spatial_state_is_explicit_xyz_and_frame(self):
        state = spatial()
        self.assertEqual(state.position_km, (1.0, 2.0, 3.0))
        self.assertEqual(state.velocity_km_s, (0.1, 0.2, 0.3))
        with self.assertRaises(ContractError):
            SpatialState("SHIP", "2226-08-22T00:00:00Z", "FRAME", (1, 2), (0, 0, 0))

    def test_trajectory_solution_is_campaign_stamped(self):
        start = spatial(epoch="2226-08-22T00:00:00Z")
        end = spatial(epoch="2226-08-22T01:00:00Z")
        seg = TrajectorySegment("seg-1", "TORCH", start.epoch_utc, end.epoch_utc, "CRUISE", start, end, (start, end))
        solution = TrajectorySolution(
            "traj-1", 9, start.epoch_utc, "MARS", "CERES", start.reference_frame,
            start.epoch_utc, end.epoch_utc, (seg,)
        )
        self.assertEqual(solution.campaign_revision, 9)
        self.assertEqual(solution.segments[0].samples[-1].epoch_utc, end.epoch_utc)

    def test_loom_solution_is_relational_and_bounds_confidence(self):
        route = LoomRouteSolution(
            "loom-1", 9, "2226-08-22T00:00:00Z", "SOL", "TAU_CETI",
            ({"edge_id": "SOL>TAU", "kind": "RELATIONAL"},), 0.82, "A_TO_B"
        )
        self.assertEqual(route.relational_edges[0]["kind"], "RELATIONAL")
        with self.assertRaises(ContractError):
            LoomRouteSolution("bad", 9, "2226-08-22T00:00:00Z", "SOL", "TAU", solution_confidence=1.2)

    def test_playback_cursor_is_non_authoritative_state_contract(self):
        playback = FlightPlaybackState(
            "flight-1", "traj-1", "2226-08-22T00:00:00Z", "2226-08-22T01:00:00Z",
            "2226-08-22T00:30:00Z", playback_rate=100.0, camera_mode="follow_ship"
        )
        self.assertEqual(playback.camera_mode, "FOLLOW_SHIP")
        self.assertEqual(playback.playback_rate, 100.0)


if __name__ == "__main__":
    unittest.main()
