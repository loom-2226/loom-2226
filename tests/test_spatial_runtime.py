from __future__ import annotations

import unittest

from loom.application.contracts import SpatialState
from loom.spatial import SpatialFrame, SpatialRuntime, SpatialRuntimeError, SpatialTransformError, relative_state


EPOCH = "2226-06-15T02:00:00Z"


def state(entity, frame, pos, vel=(0, 0, 0)):
    return SpatialState(
        entity_id=entity,
        epoch_utc=EPOCH,
        reference_frame=frame,
        position_km=pos,
        velocity_km_s=vel,
    )


class SpatialRuntimeTest(unittest.TestCase):
    def test_relative_state_is_true_xyz_and_velocity(self):
        sun = state("SUN", "HELIOCENTRIC_J2000_ECLIPTIC", (0, 0, 0), (0, 0, 0))
        earth = state("EARTH", "HELIOCENTRIC_J2000_ECLIPTIC", (10, 20, 30), (1, 2, 3))
        rel = relative_state(earth, sun, frame_id="SUN_LOCAL_INERTIAL")
        self.assertEqual(rel.position_km, (10.0, 20.0, 30.0))
        self.assertEqual(rel.velocity_km_s, (1.0, 2.0, 3.0))
        self.assertEqual(rel.reference_frame, "SUN_LOCAL_INERTIAL")

    def test_multihop_translation_round_trips(self):
        root_id = "HELIOCENTRIC_J2000_ECLIPTIC"
        earth_origin = state("EARTH", root_id, (100, 200, 300), (1, 2, 3))
        station_origin = state("STATION", "EARTH_LOCAL_INERTIAL", (10, 20, 30), (0.1, 0.2, 0.3))
        frames = {
            root_id: SpatialFrame(root_id),
            "EARTH_LOCAL_INERTIAL": SpatialFrame("EARTH_LOCAL_INERTIAL", root_id, earth_origin),
            "STATION_LOCAL_INERTIAL": SpatialFrame("STATION_LOCAL_INERTIAL", "EARTH_LOCAL_INERTIAL", station_origin),
        }
        runtime = SpatialRuntime(root_id, frames)
        ship = state("SHIP", "STATION_LOCAL_INERTIAL", (1, 2, 3), (0.01, 0.02, 0.03))
        root = runtime.transform(ship, root_id)
        self.assertEqual(root.position_km, (111.0, 222.0, 333.0))
        self.assertEqual(root.velocity_km_s, (1.11, 2.22, 3.33))
        round_trip = runtime.transform(root, "STATION_LOCAL_INERTIAL")
        for got, expected in zip(round_trip.position_km, ship.position_km):
            self.assertAlmostEqual(got, expected)
        for got, expected in zip(round_trip.velocity_km_s, ship.velocity_km_s):
            self.assertAlmostEqual(got, expected)

    def test_epoch_mismatch_fails_closed(self):
        root_id = "HELIOCENTRIC_J2000_ECLIPTIC"
        origin = SpatialState("EARTH", "2226-06-15T03:00:00Z", root_id, (0, 0, 0), (0, 0, 0))
        runtime = SpatialRuntime(root_id, {
            root_id: SpatialFrame(root_id),
            "EARTH_LOCAL_INERTIAL": SpatialFrame("EARTH_LOCAL_INERTIAL", root_id, origin),
        })
        with self.assertRaisesRegex(SpatialRuntimeError, "epoch"):
            runtime.transform(state("SHIP", root_id, (1, 2, 3)), "EARTH_LOCAL_INERTIAL")

    def test_rotating_frame_is_not_silently_invented(self):
        root_id = "HELIOCENTRIC_J2000_ECLIPTIC"
        origin = SpatialState("EARTH", EPOCH, root_id, (0, 0, 0), (0, 0, 0), orientation={"quat": [1, 0, 0, 0]})
        with self.assertRaisesRegex(SpatialTransformError, "not yet authorized"):
            SpatialFrame("EARTH_FIXED", root_id, origin)

    def test_scene_normalization_is_deterministic_and_single_epoch(self):
        root_id = "HELIOCENTRIC_J2000_ECLIPTIC"
        runtime = SpatialRuntime(root_id, {root_id: SpatialFrame(root_id)})
        states = [state("MARS", root_id, (4, 5, 6)), state("EARTH", root_id, (1, 2, 3))]
        a = runtime.normalize_states(states, epoch_utc=EPOCH)
        b = runtime.normalize_states(reversed(states), epoch_utc=EPOCH)
        self.assertEqual(a, b)
        self.assertEqual([s.entity_id for s in a], ["EARTH", "MARS"])


if __name__ == "__main__":
    unittest.main()
