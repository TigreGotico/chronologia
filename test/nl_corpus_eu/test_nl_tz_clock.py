"""Timezone-qualified clocks (eu): trailing UTC/GMT (+ offset) makes the clock
aware. Named-city zones out of scope."""
from datetime import datetime, timedelta, timezone
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span

A = datetime(2017, 6, 27, 13, 4)

def _aw(y, mo, d, h, mi, off):
    return AstroDate(y, mo, d, h, mi, tzinfo=timezone(timedelta(minutes=off)))

_CASES = [(t, _aw(y, mo, d, h, mi, off)) for (t, y, mo, d, h, mi, off) in [
    ("15:00 UTC", 2017, 6, 27, 15, 0, 0), ("15:00 GMT", 2017, 6, 27, 15, 0, 0),
    ("09:00 UTC", 2017, 6, 28, 9, 0, 0), ("23:00 GMT", 2017, 6, 27, 23, 0, 0),
    ("06:00 UTC", 2017, 6, 28, 6, 0, 0), ("15:00 UTC+2", 2017, 6, 27, 15, 0, 120),
    ("15:00 UTC-5", 2017, 6, 27, 15, 0, -300), ("15:00 UTC+5:30", 2017, 6, 27, 15, 0, 330)]]

@pytest.mark.parametrize("text,want", _CASES)
def test_tz_clock(text, want):
    s = span(text, A).start
    assert s.tzinfo is not None
    assert s.utcoffset() == want.utcoffset()
    assert (s.year, s.month, s.day, s.hour, s.minute) == (want.year, want.month, want.day, want.hour, want.minute)

def test_bare_clock_is_naive():
    assert span("15:00", A).start.tzinfo is None
