"""The public extractors raise ONLY TypeError / NotImplementedError.

`extract_timespan` and friends are documented never-raises: anything they cannot
read returns None / an empty list. A resolver handler that omits a reachable
unit must not escape as ResolverInvariant (the OCE-001 regression: "3 decades
ago" once crashed because the offset handler lacked decade/century/millennium/
second). This locks the contract, and specifically the offset-unit coverage.
"""
from datetime import datetime

import pytest

from chronologia import (extract_candidates, extract_duration,
                         extract_recurrence, extract_timespan, extract_timespans)

_ANCHOR = datetime(2017, 6, 27, 13, 4)
_ALLOWED = (TypeError, NotImplementedError)

# Every relative-offset phrasing over every temporal unit English ships a
# surface for -- exactly the matrix that would have caught OCE-001.
_UNITS = ["second", "minute", "hour", "day", "week", "fortnight",
          "month", "year", "decade", "century", "millennium"]
_PHRASES = (
    [f"3 {u}s ago" for u in _UNITS]
    + [f"in 2 {u}s" for u in _UNITS]
    + [f"last {u}" for u in _UNITS]
    + [f"next {u}" for u in _UNITS]
    + ["not tomorrow but friday", "no later than friday", "3rd tuesday of march",
       "the 15th of ramadan 1446", "from june 5 to june 12", "", "   ", "asdfgh"]
)


@pytest.mark.parametrize("text", _PHRASES)
def test_public_extractors_never_raise_unexpectedly(text):
    for fn in (extract_timespan, extract_candidates, extract_timespans,
               extract_recurrence, extract_duration):
        try:
            fn(text, "en", _ANCHOR)
        except _ALLOWED:
            pass
        except Exception as exc:  # noqa: BLE001 - the point is to catch leaks
            pytest.fail(f"{fn.__name__}({text!r}) leaked {type(exc).__name__}: {exc}")


@pytest.mark.parametrize("text,expected", [
    ("3 decades ago", "1987-06-27"),
    ("a century ago", "1917-06-27"),
    ("5 centuries ago", "1517-06-27"),
    ("in 3 decades", "2047-06-27"),
])
def test_large_unit_offsets_resolve(text, expected):
    r = extract_timespan(text, "en", _ANCHOR)
    assert r is not None
    assert r[0].start_datetime.date().isoformat() == expected
