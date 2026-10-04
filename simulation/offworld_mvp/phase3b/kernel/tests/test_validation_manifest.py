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
            out_of_sample_status=OutOfSampleStatus.IN_SAMPLE_ONLY,
            out_of_sample_disclosure='in-sample only; no held-out claim',
            overlap_disclosure='same target reused; not independent validation').validate()


    def test_empirical_validation_requires_explicit_oos_standing(self):
        with self.assertRaisesRegex(InvariantError,'held-out/out-of-sample status'):
            ValidationManifest(
                'finance',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL2_COMPONENT_EMPIRICAL,
                empirical_evidence_refs=('DATASET:X',)).validate()

    def test_held_out_status_requires_refs_and_disclosure(self):
        with self.assertRaisesRegex(InvariantError,'held-out/out-of-sample disclosure'):
            ValidationManifest(
                'finance',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL2_COMPONENT_EMPIRICAL,
                empirical_evidence_refs=('DATASET:X',),
                out_of_sample_status=OutOfSampleStatus.HELD_OUT,
                held_out_set_refs=('DATASET:HELDOUT',)).validate()
        with self.assertRaisesRegex(InvariantError,'held-out set references'):
            ValidationManifest(
                'finance',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL2_COMPONENT_EMPIRICAL,
                empirical_evidence_refs=('DATASET:X',),
                out_of_sample_status=OutOfSampleStatus.HELD_OUT,
                out_of_sample_disclosure='held-out period').validate()

    def test_val6_requires_out_of_sample_or_mixed(self):
        with self.assertRaisesRegex(InvariantError,'VAL6_OUT_OF_SAMPLE'):
            ValidationManifest(
                'finance',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL6_OUT_OF_SAMPLE,
                empirical_evidence_refs=('DATASET:X',),
                held_out_set_refs=('DATASET:H',),
                out_of_sample_status=OutOfSampleStatus.HELD_OUT,
                out_of_sample_disclosure='held-out but not external OOS').validate()
        ValidationManifest(
            'finance',(VerificationLevel.V1_SCHEMA,),ValidationLevel.VAL6_OUT_OF_SAMPLE,
            empirical_evidence_refs=('DATASET:X',),
            calibration_set_refs=('DATASET:CAL',),
            validation_set_refs=('DATASET:VAL',),
            held_out_set_refs=('DATASET:OOS',),
            out_of_sample_status=OutOfSampleStatus.OUT_OF_SAMPLE,
            out_of_sample_disclosure='external later-period test not used for calibration').validate()

if __name__=='__main__': unittest.main()
