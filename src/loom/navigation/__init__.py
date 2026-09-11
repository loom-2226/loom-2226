"""Authoritative navigation domain boundary for LOOM 2226."""

from .contracts import (
    ArrivalState,
    EphemerisSnapshot,
    FlightExecutionResult,
    FlightPlan,
    NavigationContext,
    NavigationRequest,
    RouteCandidate,
    TrajectorySegment,
)
from .gravity_shadow import (
    GravityShadowError,
    GravityShadowReport,
    GravityShadowSample,
    OrdinaryTrajectorySample,
    compare_gravity_shadow,
    ordinary_samples_from_route_trajectory,
)
from .route_layer import (
    GEOMETRY_MODE,
    LegacyRouteLayerAdapter,
    LoomRouteLayerV1,
    RouteLayerBodyV1,
    RouteLayerError,
    RouteLayerSegmentV1,
    ROUTE_LAYER_VERSION,
)
from .trajectory_solution_adapter import (
    TRAJECTORY_PACKET_ADAPTER_VERSION,
    TrajectoryPacketAdapterError,
    trajectory_solution_from_flight_plan,
    trajectory_solution_from_route_layer,
)
from .trajectory_time_state import (
    TRAJECTORY_TIME_STATE_VERSION,
    TrajectoryTimeStateError,
    TrajectoryTimeStateV1,
    evaluate_trajectory_at_epoch,
)
from .trajectory_visual_sampling import (
    TRAJECTORY_VISUAL_SAMPLING_VERSION,
    TrajectoryVisualSampleSetV1,
    TrajectoryVisualSamplingConfig,
    TrajectoryVisualSamplingError,
    sample_trajectory_for_visualization,
)
from .service import LegacyNavigationService, NavigationServiceError
from .targeting import NavigationTargetAdapter, NavigationTargetError

__all__ = [
    "ArrivalState",
    "EphemerisSnapshot",
    "FlightExecutionResult",
    "FlightPlan",
    "NavigationContext",
    "NavigationRequest",
    "RouteCandidate",
    "TrajectorySegment",
    "GravityShadowError",
    "GravityShadowReport",
    "GravityShadowSample",
    "OrdinaryTrajectorySample",
    "compare_gravity_shadow",
    "ordinary_samples_from_route_trajectory",
    "GEOMETRY_MODE",
    "LegacyRouteLayerAdapter",
    "LoomRouteLayerV1",
    "RouteLayerBodyV1",
    "RouteLayerError",
    "RouteLayerSegmentV1",
    "ROUTE_LAYER_VERSION",
    "TRAJECTORY_PACKET_ADAPTER_VERSION",
    "TrajectoryPacketAdapterError",
    "trajectory_solution_from_flight_plan",
    "trajectory_solution_from_route_layer",
    "TRAJECTORY_TIME_STATE_VERSION",
    "TrajectoryTimeStateError",
    "TrajectoryTimeStateV1",
    "evaluate_trajectory_at_epoch",
    "TRAJECTORY_VISUAL_SAMPLING_VERSION",
    "TrajectoryVisualSampleSetV1",
    "TrajectoryVisualSamplingConfig",
    "TrajectoryVisualSamplingError",
    "sample_trajectory_for_visualization",
    "LegacyNavigationService",
    "NavigationServiceError",
    "NavigationTargetAdapter",
    "NavigationTargetError",
]
