import unittest

from src.loom_neptune_mag_pds_source_contract import NEPTUNE_MAG_PDS_SOURCE_CONTRACT


class NeptuneMagPdsSourceContractTests(unittest.TestCase):
    def test_selected_mag_collection_is_ascii_nls_12s(self):
        c = NEPTUNE_MAG_PDS_SOURCE_CONTRACT
        self.assertEqual(c.mag_collection_lidvid, "urn:nasa:pds:vg2-mag-nep:data-nls-12s-asc::1.0")
        self.assertEqual(c.mag_collection_doi, "10.17189/e467-dz93")
        self.assertEqual(c.mag_sample_cadence_s, 12.0)
        self.assertEqual(c.mag_coordinate_system, "NEPTUNE_LONGITUDE_SYSTEM")
        self.assertEqual(c.mag_representation, "ASCII")

    def test_trajectory_pairing_is_required_before_sample_exposure(self):
        c = NEPTUNE_MAG_PDS_SOURCE_CONTRACT
        self.assertTrue(c.require_matching_trajectory_epoch)
        self.assertTrue(c.require_source_position)
        self.assertEqual(c.pairing_rule, "EXACT_EPOCH_ONLY_NO_INTERPOLATION")
        self.assertEqual(c.frame_transform_authority, "ZERO")
        self.assertEqual(c.interpolation_authority, "ZERO")

    def test_authority_remains_historical_only(self):
        c = NEPTUNE_MAG_PDS_SOURCE_CONTRACT
        self.assertEqual(c.endpoint_2226_authority, "ZERO")
        self.assertEqual(c.admissibility_authority, "ZERO")
        self.assertEqual(c.loom_coherence_authority, "ZERO")
        self.assertFalse(c.parser_implemented)
        self.assertFalse(c.real_record_ingested)


if __name__ == "__main__":
    unittest.main()
