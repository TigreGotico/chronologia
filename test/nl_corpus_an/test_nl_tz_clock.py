# -*- coding: utf-8 -*-
"""Timezone-qualified clocks (an): a trailing UTC/GMT (+ fixed offset) makes
the clock span aware.  Wall time obeys prefer_future on the naive time-of-day
(anchor 2018-06-05 13:04)."""
from datetime import timedelta, timezone
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span

def _aw(y, mo, d, h, mi, off):
    return AstroDate(y, mo, d, h, mi, tzinfo=timezone(timedelta(minutes=off)))

_CASES = [(t, _aw(y, mo, d, h, mi, off)) for (t, y, mo, d, h, mi, off) in [
    ('15:00 utc', 2018, 6, 5, 15, 0, 0),
    ('15:00 gmt', 2018, 6, 5, 15, 0, 0),
    ('09:00 utc', 2018, 6, 6, 9, 0, 0),
    ('23:00 gmt', 2018, 6, 5, 23, 0, 0),
    ('06:00 utc', 2018, 6, 6, 6, 0, 0),
    ('15:00 utc+2', 2018, 6, 5, 15, 0, 120),
    ('15:00 utc-5', 2018, 6, 5, 15, 0, -300),
    ('15:00 utc+5:30', 2018, 6, 5, 15, 0, 330),
]]


@pytest.mark.parametrize("text,want", _CASES)
def test_tz_clock(text, want):
    s = span(text).start
    assert s.tzinfo is not None
    assert s.utcoffset() == want.utcoffset()
    assert (s.year, s.month, s.day, s.hour, s.minute) == \
        (want.year, want.month, want.day, want.hour, want.minute)


def test_bare_clock_is_naive():
    assert span("15:00").start.tzinfo is None
