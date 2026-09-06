import pytest

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


def test_campaign_clock_requires_timezone_and_nonnegative_revision():
    clock = CampaignClockState("campaign-1", 9, "2226-08-22T00:00:00Z")
    assert clock.revision == 9
    with pytest.raises(ContractError):
        CampaignClockState("campaign-1", -1, "2226-08-22T00:00:00Z")
    with pytest.raises(ContractError):
        CampaignClockState("campaign-1", 1, "2226-08-22T00:00:00")


def test_spatial_state_is_explicit_xyz_and_frame():
    state = spatial()
    assert state.position_km == (1.0, 2.0, 3.0)
    assert state.velocity_km_s == (0.1, 0.2, 0.3)
    with pytest.raises(ContractError):
        SpatialState("SHIP", "2226-08-22T00:00:00Z", "FRAME", (1, 2), (0, 0, 0))


def test_trajectory_solution_is_campaign_stamped():
    start = spatial(epoch="2226-08-22T00:00:00Z")
    end = spatial(epoch="2226-08-22T01:00:00Z")
    seg = TrajectorySegment("seg-1", "TORCH", start.epoch_utc, end.epoch_utc, "CRUISE", start, end, (start, end))
    solution = TrajectorySolution(
        "traj-1", 9, start.epoch_utc, "MARS", "CERES", start.reference_frame,
        start.epoch_utc, end.epoch_utc, (seg,)
    )
    assert solution.campaign_revision == 9
    assert solution.segments[0].samples[-1].epoch_utc == end.epoch_utc


def test_loom_solution_is_not_metric_path_and_bounds_confidence():
    route = LoomRouteSolution(
        "loom-1", 9, "2226-08-22T00:00:00Z", "SOL", "TAU_CETI",
        ({"edge_id": "SOL>TAU", "kind": "RELATIONAL"},), 0.82, "A_TO_B"
    )
    assert route.relational_edges[0]["kind"] == "RELATIONAL"
    with pytest.raises(ContractError):
        LoomRouteSolution("bad", 9, "2226-08-22T00:00:00Z", "SOL", "TAU", solution_confidence=1.2)


def test_playback_cursor_is_non_authoritative_state_contract():
    playback = FlightPlaybackState(
        "flight-1", "traj-1", "2226-08-22T00:00:00Z", "2226-08-22T01:00:00Z",
        "2226-08-22T00:30:00Z", playback_rate=100.0, camera_mode="follow_ship"
    )
    assert playback.camera_mode == "FOLLOW_SHIP"
    assert playback.playback_rate == 100.0
