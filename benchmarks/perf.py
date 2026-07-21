"""A timeit-based micro-benchmark suite for chronologia's hot paths.

Run directly to print a table::

    python -m benchmarks.perf

The numbers are wall-clock means on the current machine; the companion test
(``test/test_perf.py``) asserts only a generous order-of-magnitude bound on
``extract_timespan`` so a real regression is caught without the suite being
flaky about absolute timings.
"""
from __future__ import annotations

import timeit
from typing import Callable, List, Tuple

import chronologia as c

# Ten representative natural-language phrases for the extraction benchmark.
EXTRACT_PHRASES: Tuple[str, ...] = (
    "last summer",
    "next friday",
    "in 2024",
    "june 1984",
    "three days ago",
    "the 15th of march",
    "5 BC",
    "the 1990s",
    "christmas 2020",
    "the second week of july",
)


def _time(fn: Callable[[], object], number: int) -> float:
    """Mean seconds per call over ``number`` iterations."""
    return timeit.timeit(fn, number=number) / number


def _bench_jdn_roundtrips() -> List[Tuple[str, float]]:
    rows = []
    for key in sorted(c.CALENDARS):
        cal = c.CALENDARS[key]
        starts = getattr(cal, "starts", None)
        if starts:                              # tabulated: stay inside coverage
            jdn = (starts[0] + starts[-1]) // 2
        else:
            jdn = cal.epoch_jdn + 100_000

        def _rt(cal=cal, jdn=jdn):
            y, m, d = cal.from_jdn(jdn)
            cal.to_jdn(y, m, d)

        rows.append((f"jdn round-trip [{key}]", _time(_rt, 20_000)))
    return rows


def _bench_extract() -> Tuple[List[Tuple[str, float]], float]:
    rows = []
    total = 0.0
    for phrase in EXTRACT_PHRASES:
        t = _time(lambda phrase=phrase: c.extract_timespan(phrase), 200)
        total += t
        rows.append((f"extract_timespan({phrase!r})", t))
    mean = total / len(EXTRACT_PHRASES)
    rows.append(("extract_timespan MEAN / phrase", mean))
    return rows, mean


def _bench_misc() -> List[Tuple[str, float]]:
    return [
        ("parse_edtf('1984-06-11~')",
         _time(lambda: c.parse_edtf("1984-06-11~"), 20_000)),
        ("easter(2024)", _time(lambda: c.easter(2024), 20_000)),
        ("equinox(2024, 'march')",
         _time(lambda: c.equinox(2024, "march"), 5_000)),
        ("holidays_for('US', 2024)",
         _time(lambda: c.holidays_for("US", 2024), 2_000)),
    ]


def collect() -> Tuple[List[Tuple[str, float]], float]:
    """Return ``(rows, extract_mean_seconds)`` for the whole suite."""
    rows: List[Tuple[str, float]] = []
    rows += _bench_jdn_roundtrips()
    extract_rows, mean = _bench_extract()
    rows += extract_rows
    rows += _bench_misc()
    return rows, mean


def _print_table(rows: List[Tuple[str, float]]) -> None:
    width = max(len(label) for label, _ in rows)
    print(f"{'benchmark':<{width}}  {'mean':>12}")
    print("-" * (width + 14))
    for label, seconds in rows:
        us = seconds * 1_000_000
        if us >= 1000:
            shown = f"{us / 1000:.3f} ms"
        else:
            shown = f"{us:.2f} us"
        print(f"{label:<{width}}  {shown:>12}")


def main() -> None:
    rows, _ = collect()
    _print_table(rows)


if __name__ == "__main__":
    main()
