"""Every script in ``examples/`` must run to completion.

The example scripts are a guided learning path (``01_...`` through
``08_...``), each self-contained and self-checking: it prints readable output
and asserts its own results. This test runs each one in a fresh subprocess and
requires exit code 0, so an example can never silently rot against the library.
"""
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_EXAMPLES = sorted((_REPO_ROOT / "examples").glob("[0-9]*.py"))


@pytest.mark.parametrize("script", _EXAMPLES, ids=lambda p: p.name)
def test_example_runs(script):
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{script.name} exited {result.returncode}\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}")


def test_examples_present():
    """Guard against the directory being emptied or renamed out from under us."""
    assert len(_EXAMPLES) >= 8
