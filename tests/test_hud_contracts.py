import pytest

from loom.hud import (
    AuthorityClass,
    Availability,
    HudStatePacket,
    SceneObject,
    SceneObjectRole,
    SpatialScenePacket,
    StateDatum,
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


def test_mock_fixture_is_explicit_and_epoch_coherent():
    packet = mock_hud_packet()
    assert packet.scene.authority is AuthorityClass.MOCK
    assert packet.epoch == packet.scene.epoch
    assert packet.selected_frame == packet.scene.frame
    assert packet.selected_target_id == "TARGET_MOCK"
    assert all(
        obj.position.authority is AuthorityClass.MOCK
        for obj in packet.scene.objects
    )


def test_unavailable_none_is_valid():
    datum = unavailable()
    assert datum.value is None
    assert datum.availability is Availability.UNAVAILABLE


def test_available_none_fails_closed():
    with pytest.raises(ValueError, match="must carry a value"):
        StateDatum(
            value=None,
            unit="m",
            epoch="2226-01-01T00:00:00Z",
            frame="TEST",
            source="test",
            authority=AuthorityClass.MOCK,
            availability=Availability.AVAILABLE,
        )


def test_mock_scene_rejects_silent_authoritative_injection():
    epoch = "2226-01-01T00:00:00Z"
    frame = "TEST"
    authoritative_position = StateDatum(
        value=Vector3(1.0, 2.0, 3.0),
        unit="m",
        epoch=epoch,
        frame=frame,
        source="test",
        authority=AuthorityClass.AUTHORITATIVE,
    )
    mock_velocity = StateDatum(
        value=Vector3(0.0, 0.0, 0.0),
        unit="m/s",
        epoch=epoch,
        frame=frame,
        source="test",
        authority=AuthorityClass.MOCK,
    )
    obj = SceneObject(
        object_id="X",
        role=SceneObjectRole.TARGET,
        label="X",
        position=authoritative_position,
        velocity=mock_velocity,
    )
    with pytest.raises(ValueError, match="higher-authority"):
        SpatialScenePacket(
            schema_version="0.1",
            packet_id="P",
            epoch=epoch,
            frame=frame,
            source="test",
            authority=AuthorityClass.MOCK,
            objects=(obj,),
        )


def test_hud_rejects_epoch_mismatch():
    fixture = mock_hud_packet()
    with pytest.raises(ValueError, match="epoch"):
        HudStatePacket(
            schema_version=fixture.schema_version,
            packet_id="BAD",
            epoch="2226-08-22T14:24:15Z",
            mode=fixture.mode,
            selected_frame=fixture.selected_frame,
            scene=fixture.scene,
            selected_target_id=fixture.selected_target_id,
            range_to_target=fixture.range_to_target,
            closing_rate=fixture.closing_rate,
        )


def test_hud_rejects_target_missing_from_scene():
    fixture = mock_hud_packet()
    with pytest.raises(ValueError, match="selected_target_id"):
        HudStatePacket(
            schema_version=fixture.schema_version,
            packet_id="BAD-TARGET",
            epoch=fixture.epoch,
            mode=fixture.mode,
            selected_frame=fixture.selected_frame,
            scene=fixture.scene,
            selected_target_id="NOT_PRESENT",
            range_to_target=fixture.range_to_target,
            closing_rate=fixture.closing_rate,
        )
