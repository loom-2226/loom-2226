"""Compatibility entry point for the Solar V0.3 executable bundle."""
import tempfile
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
HERE=Path(__file__).resolve().parent
def run_integrated(seed=42):
 from engineering.civprop.method_lab.contracts import load_bundle
 from engineering.civprop.run_civprop_v1 import build_output
 with tempfile.TemporaryDirectory(prefix='civprop_solar_v03_') as td:
  p=build_bundle_dir(Path(td)); load_bundle(p)
  return build_output(input_dir=p,infrastructure_catalog_path=HERE/'contracts/infrastructure_archetypes_v1.json',seed=seed)
