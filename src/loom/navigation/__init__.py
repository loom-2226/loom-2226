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
from .service import LegacyNavigationService, NavigationServiceError

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
    "LegacyNavigationService",
    "NavigationServiceError",
]
