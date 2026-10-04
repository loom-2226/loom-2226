from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Tuple
from .kernel import InvariantError

class VerificationLevel(IntEnum):
    V1_SCHEMA=1
    V2_TRANSITIONS=2
    V3_INVARIANTS=3
    V4_REPLAY=4
    V5_COUPLING_SCHEDULER=5
    V6_PROPERTY_METAMORPHIC=6
    V7_INDEPENDENT_CALC=7

class OutOfSampleStatus(IntEnum):
    NOT_APPLICABLE=0
    IN_SAMPLE_ONLY=1
    HELD_OUT=2
    OUT_OF_SAMPLE=3
    MIXED=4

class ValidationLevel(IntEnum):
    NOT_EMPIRICALLY_VALIDATED=0
    VAL1_FACE_DOMAIN=1
    VAL2_COMPONENT_EMPIRICAL=2
    VAL3_STYLIZED_PATTERN=3
    VAL4_BACKCAST=4
    VAL5_CROSS_CASE=5
    VAL6_OUT_OF_SAMPLE=6
    VAL7_DECISION_USE=7

@dataclass(frozen=True)
class ValidationManifest:
    subsystem: str
    verification_levels: Tuple[VerificationLevel,...]
    validation_level: ValidationLevel=ValidationLevel.NOT_EMPIRICALLY_VALIDATED
    empirical_evidence_refs: Tuple[str,...]=()
    calibration_targets: Tuple[str,...]=()
    validation_targets: Tuple[str,...]=()
    calibration_set_refs: Tuple[str,...]=()
    validation_set_refs: Tuple[str,...]=()
    held_out_set_refs: Tuple[str,...]=()
    out_of_sample_status: OutOfSampleStatus=OutOfSampleStatus.NOT_APPLICABLE
    out_of_sample_disclosure: str=''
    overlap_disclosure: str=''
    uncertainty_axes: Tuple[str,...]=()
    scenario_assumptions: Tuple[str,...]=()
    limitations: Tuple[str,...]=()

    def validate(self):
        if self.validation_level>ValidationLevel.NOT_EMPIRICALLY_VALIDATED and not self.empirical_evidence_refs:
            raise InvariantError('empirical validation claim requires evidence references')
        overlap=set(self.calibration_targets)&set(self.validation_targets)
        if overlap and not self.overlap_disclosure:
            raise InvariantError('calibration/validation target overlap requires disclosure')
        if len(set(self.verification_levels))!=len(self.verification_levels):
            raise InvariantError('duplicate verification level')
        if self.validation_level==ValidationLevel.NOT_EMPIRICALLY_VALIDATED:
            if self.out_of_sample_status!=OutOfSampleStatus.NOT_APPLICABLE:
                raise InvariantError('non-empirical validation manifest must use NOT_APPLICABLE out-of-sample status')
        else:
            if self.out_of_sample_status==OutOfSampleStatus.NOT_APPLICABLE:
                raise InvariantError('empirical validation claim requires explicit held-out/out-of-sample status')
            if not self.out_of_sample_disclosure:
                raise InvariantError('empirical validation claim requires held-out/out-of-sample disclosure')
            if self.out_of_sample_status in {OutOfSampleStatus.HELD_OUT,OutOfSampleStatus.OUT_OF_SAMPLE,OutOfSampleStatus.MIXED} and not self.held_out_set_refs:
                raise InvariantError('held-out/out-of-sample status requires held-out set references')
        if self.validation_level==ValidationLevel.VAL6_OUT_OF_SAMPLE and self.out_of_sample_status not in {OutOfSampleStatus.OUT_OF_SAMPLE,OutOfSampleStatus.MIXED}:
            raise InvariantError('VAL6_OUT_OF_SAMPLE requires OUT_OF_SAMPLE or MIXED status')
        return self

    @property
    def empirically_validated(self):
        return self.validation_level>ValidationLevel.NOT_EMPIRICALLY_VALIDATED
