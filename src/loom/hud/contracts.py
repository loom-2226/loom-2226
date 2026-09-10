from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Optional, Tuple, TypeVar


T = TypeVar("T")


class AuthorityClass(str, Enum):
    AUTHORITATIVE = "AUTHORITATIVE"
    DERIVED = "DERIVED"
    INTERPOLATED_NON_NAVIGATION_GRADE = "INTERPOLATED_NON_NAVIGATION_GRADE"
    QUALIFICATION_ONLY = "QUALIFICATION_ONLY"
    MOCK = "MOCK"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class Availability(str, Enum):
    AVAILABLE = "AVAILABLE"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class HudMode(str, Enum):
    CRUISE = "CRUISE"
    NAVIGATION = "NAVIGATION"
    APPROACH = "APPROACH"
    RENDEZVOUS = "RENDEZVOUS"
    PROXIMITY = "PROXIMITY"
    DOCKING = "DOCKING"
    DEPARTURE = "DEPARTURE"
    ORBITAL = "ORBITAL"
    METRIC_TRANSIT = "METRIC_TRANSIT"
    DEGRADED = "DEGRADED"


class SyntheticVisionMode(str, Enum):
    OPTICAL = "OPTICAL"
    TACTICAL = "TACTICAL"
    HYBRID = "HYBRID"


class ReferenceFrame(str, Enum):
    INERTIAL = "INERTIAL"
    VELOCITY = "VELOCITY"
    HILL_LVLH = "HILL_LVLH"
    BODY = "BODY"
    TARGET = "TARGET"


class SceneObjectRole(str, Enum):
    OWNSHIP = "OWNSHIP"
    TARGET = "TARGET"
    NATURAL_BODY = "NATURAL_BODY"
    STATION = "STATION"
    CONTACT = "CONTACT"
    FACILITY = "FACILITY"
    HAZARD = "HAZARD"
    TRANSITION_POINT = "TRANSITION_POINT"
    TRAJECTORY_SAMPLE = "TRAJECTORY_SAMPLE"


@dataclass(frozen=True)
class Vector3:
    x: float
    y: float
    z: float

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass(frozen=True)
class StateDatum(Generic[T]):
    value: Optional[T]
    unit: Optional[str]
    epoch: Optional[str]
    frame: Optional[str]
    source: str
    authority: AuthorityClass
    derivation: Optional[str] = None
    freshness_seconds: Optional[float] = None
    availability: Availability = Availability.AVAILABLE
    quality: Optional[str] = None

    def __post_init__(self) -> None:
        if self.value is None and self.availability == Availability.AVAILABLE:
            raise ValueError("available StateDatum must carry a value")
        if self.authority == AuthorityClass.UNAVAILABLE and self.value is not None:
            raise ValueError("UNAVAILABLE authority must not carry a value")


QuaternionXYZW = Tuple[float, float, float, float]


@dataclass(frozen=True)
class SceneObject:
    object_id: str
    role: SceneObjectRole
    label: str
    position: StateDatum[Vector3]
    velocity: StateDatum[Vector3]
    attitude_quaternion_xyzw: Optional[StateDatum[QuaternionXYZW]] = None
    semantic_role: Optional[str] = None
    object_type: Optional[str] = None
    radius_m: Optional[StateDatum[float]] = None
    model_uri: Optional[str] = None
    track_priority: int = 0

    def __post_init__(self) -> None:
        if not self.object_id:
            raise ValueError("scene object_id is required")
        if not self.label:
            raise ValueError("scene label is required")
        if self.track_priority < 0:
            raise ValueError("track_priority must be non-negative")


@dataclass(frozen=True)
class SpatialScenePacket:
    schema_version: str
    packet_id: str
    epoch: str
    frame: str
    source: str
    authority: AuthorityClass
    objects: Tuple[SceneObject, ...]
    campaign_revision: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.schema_version:
            raise ValueError("schema_version is required")
        if not self.packet_id:
            raise ValueError("packet_id is required")
        if not self.epoch:
            raise ValueError("epoch is required")
        if not self.frame:
            raise ValueError("frame is required")
        if self.authority == AuthorityClass.MOCK:
            for obj in self.objects:
                datums = [obj.position, obj.velocity]
                if obj.radius_m is not None:
                    datums.append(obj.radius_m)
                if obj.attitude_quaternion_xyzw is not None:
                    datums.append(obj.attitude_quaternion_xyzw)
                for datum in datums:
                    if datum.authority not in {
                        AuthorityClass.MOCK,
                        AuthorityClass.UNAVAILABLE,
                        AuthorityClass.UNKNOWN,
                    }:
                        raise ValueError(
                            "MOCK scene may not silently contain higher-authority state"
                        )


@dataclass(frozen=True)
class FlightViewState:
    """Rendering input for forward synthetic vision.

    This contract carries already-earned world state into presentation space.
    `camera_from_inertial_xyzw` rotates inertial-frame vectors into a camera
    frame whose +X axis is forward, +Y is screen-right, and +Z is up.
    Projection code may transform these values for display but must not derive
    canonical dynamics, ephemerides, burns, or vehicle state.
    """

    schema_version: str
    packet_id: str
    epoch: str
    inertial_frame: str
    reference_frame: ReferenceFrame
    vision_mode: SyntheticVisionMode
    ship_position_inertial: StateDatum[Vector3]
    ship_velocity_inertial: StateDatum[Vector3]
    camera_from_inertial_xyzw: StateDatum[QuaternionXYZW]
    fov_y_deg: float
    objects: Tuple[SceneObject, ...]
    planned_trajectory: Tuple[StateDatum[Vector3], ...] = ()
    commanded_vector: Optional[StateDatum[Vector3]] = None
    source: str = "UNKNOWN"
    authority: AuthorityClass = AuthorityClass.UNKNOWN

    def __post_init__(self) -> None:
        if not self.schema_version or not self.packet_id:
            raise ValueError("FlightViewState schema_version and packet_id are required")
        if not self.epoch or not self.inertial_frame:
            raise ValueError("FlightViewState epoch and inertial_frame are required")
        if not (1.0 <= self.fov_y_deg < 179.0):
            raise ValueError("fov_y_deg must be in [1, 179)")
        for datum in (
            self.ship_position_inertial,
            self.ship_velocity_inertial,
            self.camera_from_inertial_xyzw,
        ):
            if datum.epoch != self.epoch:
                raise ValueError("FlightViewState datum epoch must match packet epoch")
            if datum.frame != self.inertial_frame:
                raise ValueError("FlightViewState inertial datum frame mismatch")
        if self.authority == AuthorityClass.MOCK:
            for datum in (
                self.ship_position_inertial,
                self.ship_velocity_inertial,
                self.camera_from_inertial_xyzw,
            ):
                if datum.authority not in {AuthorityClass.MOCK, AuthorityClass.UNAVAILABLE, AuthorityClass.UNKNOWN}:
                    raise ValueError("MOCK FlightViewState may not contain higher-authority state")


@dataclass(frozen=True)
class HudStatePacket:
    schema_version: str
    packet_id: str
    epoch: str
    mode: HudMode
    selected_frame: str
    scene: SpatialScenePacket
    selected_target_id: Optional[str] = None
    range_to_target: StateDatum[float] = field(
        default_factory=lambda: StateDatum(
            value=None,
            unit="m",
            epoch=None,
            frame=None,
            source="NONE",
            authority=AuthorityClass.UNAVAILABLE,
            availability=Availability.UNAVAILABLE,
        )
    )
    closing_rate: StateDatum[float] = field(
        default_factory=lambda: StateDatum(
            value=None,
            unit="m/s",
            epoch=None,
            frame=None,
            source="NONE",
            authority=AuthorityClass.UNAVAILABLE,
            availability=Availability.UNAVAILABLE,
        )
    )

    def __post_init__(self) -> None:
        if self.epoch != self.scene.epoch:
            raise ValueError("HUD epoch must match scene epoch")
        if self.selected_frame != self.scene.frame:
            raise ValueError("HUD selected frame must match scene frame in v0.1")
        if self.selected_target_id is not None:
            ids = {obj.object_id for obj in self.scene.objects}
            if self.selected_target_id not in ids:
                raise ValueError("selected_target_id is not present in scene")


def _mock_vec(value: Vector3, epoch: str, frame: str, source: str) -> StateDatum[Vector3]:
    return StateDatum(
        value=value,
        unit="m" if "position" in source.lower() else "m/s",
        epoch=epoch,
        frame=frame,
        source=source,
        authority=AuthorityClass.MOCK,
        derivation="deterministic HUD qualification fixture",
        freshness_seconds=0.0,
        availability=Availability.AVAILABLE,
        quality="QUALIFICATION_ONLY",
    )


def mock_hud_packet() -> HudStatePacket:
    """Deterministic visual-qualification fixture; never navigation authority."""
    epoch = "2226-08-22T14:24:14Z"
    frame = "HUD_MOCK_LOCAL_CARTESIAN"
    ownship = SceneObject(
        object_id="WAYFARER_MOCK", role=SceneObjectRole.OWNSHIP, label="WAYFARER / MOCK",
        position=_mock_vec(Vector3(0.0, 0.0, 0.0), epoch, frame, "mock.position"),
        velocity=_mock_vec(Vector3(0.0, 0.0, 0.0), epoch, frame, "mock.velocity"),
    )
    target = SceneObject(
        object_id="TARGET_MOCK", role=SceneObjectRole.TARGET, label="RENDEZVOUS TARGET / MOCK",
        position=_mock_vec(Vector3(1800.0, 450.0, -220.0), epoch, frame, "mock.position"),
        velocity=_mock_vec(Vector3(-2.0, -0.3, 0.1), epoch, frame, "mock.velocity"),
        semantic_role="RENDEZVOUS_GATE_MOCK", track_priority=100,
    )
    station = SceneObject(
        object_id="STATION_MOCK", role=SceneObjectRole.STATION, label="STATION / MOCK GEOMETRY",
        position=_mock_vec(Vector3(2600.0, 900.0, 340.0), epoch, frame, "mock.position"),
        velocity=_mock_vec(Vector3(0.0, 0.0, 0.0), epoch, frame, "mock.velocity"),
        track_priority=50,
    )
    scene = SpatialScenePacket(
        schema_version="0.1", packet_id="HUD-MOCK-SCENE-0001", epoch=epoch, frame=frame,
        source="loom.hud.mock_hud_packet", authority=AuthorityClass.MOCK,
        objects=(ownship, target, station), campaign_revision=None,
    )
    return HudStatePacket(
        schema_version="0.1", packet_id="HUD-MOCK-0001", epoch=epoch, mode=HudMode.RENDEZVOUS,
        selected_frame=frame, scene=scene, selected_target_id="TARGET_MOCK",
        range_to_target=StateDatum(
            value=1868.9, unit="m", epoch=epoch, frame=frame, source="mock.precomputed.range",
            authority=AuthorityClass.MOCK, derivation="fixture value; not computed by HUD renderer",
            availability=Availability.AVAILABLE, quality="QUALIFICATION_ONLY",
        ),
        closing_rate=StateDatum(
            value=2.03, unit="m/s", epoch=epoch, frame=frame, source="mock.precomputed.closing_rate",
            authority=AuthorityClass.MOCK, derivation="fixture value; not computed by HUD renderer",
            availability=Availability.AVAILABLE, quality="QUALIFICATION_ONLY",
        ),
    )
