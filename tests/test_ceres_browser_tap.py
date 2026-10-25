"""CI must reject zero-work success and incomplete/contradictory browser reports."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "ceres_browser_tap", Path(__file__).resolve().parents[1] / "tools/check_ceres_browser_tap.py"
)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

PASS = "TAP version 13\n" + "".join(f"ok {i} - browser case {i}\n" for i in range(1, 8)) + """1..7
# tests 7
# suites 0
# pass 7
# fail 0
# cancelled 0
# skipped 0
# todo 0
"""


def test_accepts_exactly_seven_actual_passes():
    assert checker.require_seven_passes(PASS)["pass"] == 7


@pytest.mark.parametrize("report", [
    "", PASS.split("1..7")[0],
    PASS.replace("# pass 7", "# pass 0").replace("# skipped 0", "# skipped 7"),
    PASS.replace("# pass 7", "# pass 6").replace("# fail 0", "# fail 1"),
    PASS.replace("# cancelled 0", "# cancelled 1"),
    PASS.replace("# todo 0", "# todo 1"),
    PASS.replace("# tests 7", "# tests 8"),
    PASS.replace("1..7", "1..6"),
    PASS.replace("ok 7 - browser case 7\n", ""),
    PASS.replace("ok 7", "ok 6"),
    PASS.replace("ok 1 - browser case 1", "not ok 1 - browser case 1"),
    PASS.replace("browser case 1", "browser case 1 # SKIP unavailable"),
    PASS.replace("browser case 1", "browser case 1 # TODO later"),
    PASS + "Bail out!\n", PASS + "# pass 7\n", PASS + "1..7\n",
])
def test_rejects_nonpassing_or_incomplete_reports(report):
    with pytest.raises(ValueError):
        checker.require_seven_passes(report)
