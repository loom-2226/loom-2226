import copy
import unittest

from src.loom_solar_basemap_contract import canonical_bytes, resource_bytes, validate_semantics


class ContractTests(unittest.TestCase):
    def test_canonical_bytes_and_gzip_are_stable(self):
        a = {"z": -0.0, "a": [1.0, 2.0]}
        b = {"a": [1.0, 2.0], "z": 0.0}
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))
        self.assertEqual(resource_bytes(a)["gzip"], resource_bytes(b)["gzip"])

    def test_non_finite_is_rejected(self):
        with self.assertRaises(ValueError): canonical_bytes({"bad": float("nan")})

    def test_unknown_major_schema_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_semantics({"schema": "loom.solar-basemap.root/9.0"})

    def test_parent_reference_cannot_be_sun_anchored(self):
        doc = {"schema": "loom.solar-basemap.root/0.1", "build_spec_id": "0"*64,
               "epoch_et": 7131844800.0, "features": [{"body_id": str(i)} for i in range(110)],
               "nodes": [{"node_id": "solar", "parent_node_id": None}],
               "curves": [{"closed": False, "semantic": "PARENT_RELATIVE_REFERENCE_ORBIT", "anchor_id": "SUN",
                           "start_et": 0, "end_et": 1, "segments": []}], "extensions": {}}
        with self.assertRaisesRegex(ValueError, "Sun anchor"):
            validate_semantics(doc)

    def test_root_requires_110_unique_governed_ids(self):
        doc = {"schema": "loom.solar-basemap.root/0.1", "build_spec_id": "0"*64,
               "epoch_et": 7131844800.0, "features": [], "nodes": [{"node_id": "solar", "parent_node_id": None}],
               "curves": [], "extensions": {}}
        with self.assertRaisesRegex(ValueError, "110 unique"):
            validate_semantics(doc)

    def test_root_rejects_parent_cycles(self):
        doc = {"schema": "loom.solar-basemap.root/0.1", "build_spec_id": "0"*64,
               "epoch_et": 7131844800.0,
               "features": [{"body_id": str(i)} for i in range(110)],
               "nodes": [{"node_id": "solar", "parent_node_id": "system:x"},
                         {"node_id": "system:x", "parent_node_id": "solar"}],
               "curves": [], "extensions": {}}
        with self.assertRaisesRegex(ValueError, "cyclic"):
            validate_semantics(doc)

    def test_manifest_preserves_qualified_authority_counts(self):
        doc={"schema":"loom.solar-basemap.manifest/0.1","frame":"ECLIPJ2000","center":"SUN","units":"km",
             "epoch_et":7131844800.0,"counts":{"catalog":110,"resolved":102,"unresolved":8,"requested_curves":12,"available_curves":12}}
        with self.assertRaisesRegex(ValueError,"counts"):
            validate_semantics(doc)

    def test_schema_version_suffix_maps_to_definition_name(self):
        chunk={"schema":"loom.solar-basemap.chunk/0.1","build_spec_id":"0"*64,
               "node_id":"solar","level":0,"curves":[],"extensions":{}}
        self.assertTrue(validate_semantics(chunk,kind="chunk"))


if __name__ == "__main__": unittest.main()
