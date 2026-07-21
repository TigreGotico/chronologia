"""A single order-of-magnitude perf guard over ``extract_timespan``.

The bound (50 ms mean per phrase) is deliberately generous — real means on
dev hardware are hundreds of microseconds. The point is to catch an
order-of-magnitude regression (an accidental O(n^2) or a per-call reload),
not to police absolute timings, so the test is not flaky on a slow CI box.
"""
from benchmarks.perf import EXTRACT_PHRASES, collect


def test_extract_timespan_mean_under_50ms():
    _, mean_seconds = collect()
    assert mean_seconds < 0.050, (
        f"extract_timespan mean {mean_seconds * 1000:.2f} ms/phrase exceeds "
        "the 50 ms order-of-magnitude regression bound")


def test_benchmark_phrases_are_representative():
    # The suite times ten distinct phrases; keep it honest if edited.
    assert len(EXTRACT_PHRASES) == 10
    assert len(set(EXTRACT_PHRASES)) == 10
