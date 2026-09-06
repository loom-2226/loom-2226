"""Authoritative spatial runtime primitives for LOOM 2226."""
from .frames import (
    SpatialFrame,
    SpatialTransformError,
    transform_state,
    relative_state,
)
from .gravity import (
    CANONICAL_GRAVITY_FRAME,
    GravityContribution,
    GravityEvaluation,
    GravityModelError,
    GravitySource,
    acceleration_from_source,
    evaluate_gravity,
)
from .runtime import SpatialRuntime, SpatialRuntimeError

__all__ = [
    "SpatialFrame",
    "SpatialTransformError",
    "transform_state",
    "relative_state",
    "CANONICAL_GRAVITY_FRAME",
    "GravityContribution",
    "GravityEvaluation",
    "GravityModelError",
    "GravitySource",
    "acceleration_from_source",
    "evaluate_gravity",
    "SpatialRuntime",
    "SpatialRuntimeError",
]
