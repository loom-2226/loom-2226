import unittest
from offworld_kernel.validation import *
from offworld_kernel.kernel import InvariantError

class ValidationManifestTests(unittest.TestCase):
    def test_verified_is_not_empirically_validated(self):
        m=ValidationManifest('kernel',(VerificationLevel.V1_SCHEMA,VerificationLevel.V3_INVARIANTS,VerificationLevel.V4_REPLAY)).validate()
        self.assertFalse(m.empirically_validated)
        self.assertEqual(m.validation_level,ValidationLevel.NOT_EMPIRICALLY_VALIDATED)

    def test_empirical_validation_requires_evidence(self):
        with self.assertRaises(InvariantError):
            ValidationManifest('finance',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL2_COMPONENT_EMPIRICAL).validate()

    def test_calibration_target_cannot_silently_validate_itself(self):
        with self.assertRaises(InvariantError):
            ValidationManifest('belief',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL2_COMPONENT_EMPIRICAL,
                empirical_evidence_refs=('DATASET:X',),calibration_targets=('2020-2030',),validation_targets=('2020-2030',)).validate()
        ValidationManifest('belief',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL2_COMPONENT_EMPIRICAL,
            empirical_evidence_refs=('DATASET:X',),calibration_targets=('2020-2030',),validation_targets=('2020-2030',),
            overlap_disclosure='same target reused; not independent validation').validate()

if __name__=='__main__': unittest.main()
