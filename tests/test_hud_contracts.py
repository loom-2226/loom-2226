import unittest

from loom.hud import (
    AuthorityClass,
    Availability,
    FlightViewState,
    HudStatePacket,
    ReferenceFrame,
    SceneObject,
    SceneObjectRole,
    SpatialScenePacket,
    StateDatum,
    SyntheticVisionMode,
    Vector3,
    mock_hud_packet,
)


def unavailable(unit="m"):
    return StateDatum(
        value=None,
        unit=unit,
        epoch=None,
        frame=None,
        source="NONE",
        authority=AuthorityClass.UNAVAILABLE,
        availability=Availability.UNAVAILABLE,
    )


def mock_datum(value, unit, epoch, frame):
    return StateDatum(
        value=value,
        unit=unit,
        epoch=epoch,
        frame=frame,
        source="test.mock",
        authority=AuthorityClass.MOCK,
        quality="QUALIFICATION_ONLY",
    )


class HudContractTests(unittest.TestCase):
    def test_mock_fixture_is_explicit_and_epoch_coherent(self):
        packet = mock_hud_packet()
        self.assertIs(packet.scene.authority, AuthorityClass.MOCK)
        self.assertEqual(packet.epoch, packet.scene.epoch)
        self.assertEqual(packet.selected_frame, packet.scene.frame)
        self.assertEqual(packet.selected_target_id, "TARGET_MOCK")
        self.assertTrue(all(obj.position.authority is AuthorityClass.MOCK for obj in packet.scene.objects))

    def test_unavailable_none_is_valid(self):
        datum = unavailable()
        self.assertIsNone(datum.value)
        self.assertIs(datum.availability, Availability.UNAVAILABLE)

    def test_available_none_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "must carry a value"):
            StateDatum(value=None, unit="m", epoch="2226-01-01T00:00:00Z", frame="TEST", source="test", authority=AuthorityClass.MOCK, availability=Availability.AVAILABLE)

    def test_mock_scene_rejects_silent_authoritative_injection(self):
        epoch = "2226-01-01T00:00:00Z"; frame = "TEST"
        authoritative_position = StateDatum(value=Vector3(1.0,2.0,3.0), unit="m", epoch=epoch, frame=frame, source="test", authority=AuthorityClass.AUTHORITATIVE)
        mock_velocity = StateDatum(value=Vector3(0.0,0.0,0.0), unit="m/s", epoch=epoch, frame=frame, source="test", authority=AuthorityClass.MOCK)
        obj = SceneObject(object_id="X", role=SceneObjectRole.TARGET, label="X", position=authoritative_position, velocity=mock_velocity)
        with self.assertRaisesRegex(ValueError, "higher-authority"):
            SpatialScenePacket(schema_version="0.1", packet_id="P", epoch=epoch, frame=frame, source="test", authority=AuthorityClass.MOCK, objects=(obj,))

    def test_hud_rejects_epoch_mismatch(self):
        fixture = mock_hud_packet()
        with self.assertRaisesRegex(ValueError, "epoch"):
            HudStatePacket(schema_version=fixture.schema_version, packet_id="BAD", epoch="2226-08-22T14:24:15Z", mode=fixture.mode, selected_frame=fixture.selected_frame, scene=fixture.scene, selected_target_id=fixture.selected_target_id, range_to_target=fixture.range_to_target, closing_rate=fixture.closing_rate)

    def test_hud_rejects_target_missing_from_scene(self):
        fixture = mock_hud_packet()
        with self.assertRaisesRegex(ValueError, "selected_target_id"):
            HudStatePacket(schema_version=fixture.schema_version, packet_id="BAD-TARGET", epoch=fixture.epoch, mode=fixture.mode, selected_frame=fixture.selected_frame, scene=fixture.scene, selected_target_id="NOT_PRESENT", range_to_target=fixture.range_to_target, closing_rate=fixture.closing_rate)

    def test_flight_view_state_accepts_explicit_camera_from_inertial_contract(self):
        epoch="2226-01-01T00:00:00Z"; frame="TEST_INERTIAL"
        state=FlightViewState(
            schema_version="0.1", packet_id="FV-1", epoch=epoch, inertial_frame=frame,
            reference_frame=ReferenceFrame.INERTIAL, vision_mode=SyntheticVisionMode.HYBRID,
            ship_position_inertial=mock_datum(Vector3(0,0,0),"m",epoch,frame),
            ship_velocity_inertial=mock_datum(Vector3(0,0,0),"m/s",epoch,frame),
            camera_from_inertial_xyzw=mock_datum((0,0,0,1),None,epoch,frame),
            fov_y_deg=60.0, objects=(), source="test", authority=AuthorityClass.MOCK,
        )
        self.assertEqual(state.reference_frame, ReferenceFrame.INERTIAL)
        self.assertEqual(state.vision_mode, SyntheticVisionMode.HYBRID)

    def test_flight_view_state_rejects_epoch_drift(self):
        epoch="2226-01-01T00:00:00Z"; frame="TEST_INERTIAL"
        bad_pos=mock_datum(Vector3(0,0,0),"m","2226-01-01T00:00:01Z",frame)
        with self.assertRaisesRegex(ValueError,"epoch"):
            FlightViewState(schema_version="0.1", packet_id="FV-BAD", epoch=epoch, inertial_frame=frame, reference_frame=ReferenceFrame.INERTIAL, vision_mode=SyntheticVisionMode.HYBRID, ship_position_inertial=bad_pos, ship_velocity_inertial=mock_datum(Vector3(0,0,0),"m/s",epoch,frame), camera_from_inertial_xyzw=mock_datum((0,0,0,1),None,epoch,frame), fov_y_deg=60.0, objects=(), authority=AuthorityClass.MOCK)


if __name__ == "__main__":
    unittest.main()
