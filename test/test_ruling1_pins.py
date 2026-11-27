"""Every test that ``ruling1_pins.txt`` lists still exists.

``ruling1_pins.txt`` records the tests whose expected value ruling 1 moved on
26 November 2026: a part of a month is read as a span, so a part that has
ended is next year's.  A renamed or deleted test would leave the record
pointing at nothing, so this test collects the listed files and checks that
every listed node id is among the collected ones.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def test_every_pinned_test_is_collected():
    pins = [line for line in (HERE / "ruling1_pins.txt")
            .read_text(encoding="utf-8").splitlines() if line]
    assert pins
    files = sorted({pin.split("::", 1)[0] for pin in pins})
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:xdist", "-p", "no:cacheprovider", *files],
        cwd=HERE.parent, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    collected = set(run.stdout.splitlines())
    missing = [pin for pin in pins if pin not in collected]
    assert not missing, f"{len(missing)} pinned ids not collected: {missing[:10]}"
