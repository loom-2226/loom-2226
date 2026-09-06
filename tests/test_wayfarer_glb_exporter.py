import json
import struct
import unittest

from src.wayfarer_glb_exporter import build_glb_bytes, loom_to_gltf


class WayfarerGlbExporterTests(unittest.TestCase):
    def payload(self):
        return {
            "schema": "LOOM.Wayfarer.Geometry",
            "schema_version": "0.1",
            "components": [
                {
                    "id": "pressure_hull",
                    "kind": "cylinder_x",
                    "center_m": [7.0, 0.0, 0.0],
                    "dimensions": {"length_m": 14.0, "diameter_m": 8.6},
                    "status": "DESIGN_BASELINE",
                    "source": "pressure_hull.*",
                    "group": "habitat",
                },
                {
                    "id": "planetary_launch",
                    "kind": "box",
                    "center_m": [21.0, 0.0, 5.0],
                    "dimensions": {"x_m": 10.5, "y_m": 3.9, "z_m": 3.1},
                    "status": "DESIGN_BASELINE",
                    "source": "launch.*",
                    "group": "launch",
                },
                {
                    "id": "radiator_1",
                    "kind": "radiator_placeholder",
                    "center_m": [35.5, 4.5, 0.0],
                    "dimensions": {"root_length_m": 5.0, "panel_chord_m": 5.0, "azimuth_deg": 0.0},
                    "status": "OPEN",
                    "source": "radiator physical panel geometry OPEN",
                    "group": "radiators",
                },
                {
                    "id": "magnetic_nozzle",
                    "kind": "nozzle_x",
                    "center_m": [53.5, 0.0, 0.0],
                    "dimensions": {"length_m": 7.0, "aperture_diameter_m": 6.0},
                    "status": "DESIGN_BASELINE",
                    "source": "nozzle.*",
                    "group": "propulsion",
                },
            ],
        }

    @staticmethod
    def gltf_json(glb):
        magic, version, total = struct.unpack("<4sII", glb[:12])
        assert magic == b"glTF"
        assert version == 2
        assert total == len(glb)
        json_len, json_type = struct.unpack("<II", glb[12:20])
        assert json_type == 0x4E4F534A
        return json.loads(glb[20:20 + json_len].decode("utf-8").rstrip(" "))

    def test_coordinate_mapping_is_right_handed_android_friendly(self):
        self.assertEqual(loom_to_gltf((1, 2, 3)), (1.0, 3.0, -2.0))

    def test_glb_header_and_metadata(self):
        glb = build_glb_bytes(self.payload())
        doc = self.gltf_json(glb)
        self.assertEqual(doc["asset"]["version"], "2.0")
        self.assertIn("LOOM", doc["asset"]["generator"])
        self.assertIn("SQL/geometry JSON remains authoritative", doc["asset"]["extras"]["authority"])

    def test_state_selection_changes_scene(self):
        docked = self.gltf_json(build_glb_bytes(self.payload(), "DOCKED", "STOWED"))
        absent = self.gltf_json(build_glb_bytes(self.payload(), "ABSENT", "DEPLOYED"))
        self.assertIn("planetary_launch", [node["name"] for node in docked["nodes"]])
        self.assertNotIn("planetary_launch", [node["name"] for node in absent["nodes"]])
        self.assertEqual(absent["scenes"][0]["extras"]["radiator_state"], "DEPLOYED")

    def test_provenance_survives_export(self):
        doc = self.gltf_json(build_glb_bytes(self.payload()))
        launch = next(node for node in doc["nodes"] if node["name"] == "planetary_launch")
        self.assertEqual(launch["translation"], [21.0, 5.0, -0.0])
        self.assertEqual(launch["extras"]["loom_status"], "DESIGN_BASELINE")
        self.assertEqual(launch["extras"]["loom_dimensions"]["x_m"], 10.5)

    def test_export_is_deterministic(self):
        a = build_glb_bytes(self.payload(), "DOCKED", "STOWED")
        b = build_glb_bytes(self.payload(), "DOCKED", "STOWED")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
