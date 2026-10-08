"""Structural standing for an authorized Build 7 REGION characterization study."""
from __future__ import annotations

from offworld_kernel.project_study import ProjectStudyResultStanding


def classify_regional_material_observation(observations):
    """Classify evidence sufficiency for the next study stage, not resources."""
    signals = tuple(str(observation.signal) for observation in observations)
    if any(signal == 'POSITIVE' for signal in signals):
        return ProjectStudyResultStanding.SUPPORTS_ADVANCE
    if signals and all(signal == 'NEGATIVE' for signal in signals):
        return ProjectStudyResultStanding.NEGATIVE
    return ProjectStudyResultStanding.INSUFFICIENT
