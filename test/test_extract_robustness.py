"""Adversarial robustness of :func:`~chronologia.extract.extract_timespan`.

The extractor reads untrusted natural-language transcripts, so a hostile input
must never exhaust the stack or hang.  Two shapes are pinned here:

* a long chain of range connectors ("monday to monday to monday ...") -- range
  handling scans the token stream for the first split once, it does not recurse
  once per connector, so the stack stays flat;
* a long whitespace run ("a" followed by tens of thousands of spaces) -- the
  remainder path is length-linear, with no quadratic raw-string range regex to
  drive it to seconds of backtracking.

Both assert completion well under a generous wall-clock budget *and* that no
exception escapes.
"""
import time

import pytest

from chronologia.extract import extract_timespan


@pytest.mark.parametrize("n", [500])
def test_many_range_connectors_no_recursion(n):
    # ~500 ' to ' connectors used to recurse extract_timespan once per
    # connector and blow the stack (RecursionError); the token-native scan
    # takes the first split and drops the rest to the remainder.
    def best_of(count, runs=5):
        text = " to ".join(["monday"] * count)
        times = []
        for _ in range(runs):
            t0 = time.process_time()
            result = extract_timespan(text, "en")      # must not raise
            times.append(time.process_time() - t0)
            assert result is not None
        # CPU time ignores descheduling; load only adds, so take the minimum
        return min(times)

    # Absolute budgets measure the host, not the scan.  Four times the
    # connectors takes four times as long when the scan is linear, and sixteen
    # times when a per-connector recursion re-scans the remainder.  8 lies
    # between the two with room for a busy runner.
    small, large = best_of(n // 4), best_of(n)
    assert large / small < 8, (
        f"four times {n // 4} connectors multiplied the time by {large / small:.2f}")


def test_long_whitespace_no_redos():
    # the old 'from A to B' range regex scanned the whole raw string with
    # greedy '.+?' groups on every call -- O(n^2), seconds on a 40 KB blank
    # tail.  There is no raw-string range regex any more, so this is linear.
    text = "a" + " " * 40000
    t0 = time.perf_counter()
    result = extract_timespan(text, "en")          # must not raise
    elapsed = time.perf_counter() - t0
    assert elapsed < 2.0, f"40 KB whitespace took {elapsed:.2f}s"
    # 'a' names nothing temporal -> no span
    assert result is None
