import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.loom_neptune_plasma_em_source_qualification import qualification_report

print(json.dumps(qualification_report(), indent=2, sort_keys=True))
