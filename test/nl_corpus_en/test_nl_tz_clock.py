"""Timezone-qualified clock times: "3pm UTC", "noon UTC", "3pm UTC+2".

A trailing UTC / GMT marker (optionally with a fixed signed offset) makes the
clock span **aware**: its ``tzinfo`` carries the offset, so the same wall time
in two zones is two different instants.  Named-city zones are out of scope --
only UTC / GMT and a fixed offset resolve.  The wall clock still obeys
``prefer_future`` on the naive time-of-day (anchor 2017-06-27 13:04): a time
already past today rolls to tomorrow.
"""
from datetime import timedelta, timezone

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, span, parse


# (text, expected aware AstroDate start)
def _aw(y, mo, d, h, mi, off_minutes):
    return AstroDate(y, mo, d, h, mi, tzinfo=timezone(timedelta(minutes=off_minutes)))


_CASES = [
    ("3pm UTC", _aw(2017, 6, 27, 15, 0, 0)),           # 15:00 > 13:04 -> today
    ("3pm GMT", _aw(2017, 6, 27, 15, 0, 0)),
    ("at 3pm UTC", _aw(2017, 6, 27, 15, 0, 0)),
    ("noon UTC", _aw(2017, 6, 28, 12, 0, 0)),          # 12:00 < 13:04 -> tomorrow
    ("midnight UTC", _aw(2017, 6, 28, 0, 0, 0)),
    ("15:00 UTC", _aw(2017, 6, 27, 15, 0, 0)),
    ("3pm UTC+2", _aw(2017, 6, 27, 15, 0, 120)),
    ("3pm UTC-5", _aw(2017, 6, 27, 15, 0, -300)),
    ("9am UTC+1", _aw(2017, 6, 28, 9, 0, 60)),         # 09:00 < 13:04 -> tomorrow
    ("11pm GMT", _aw(2017, 6, 27, 23, 0, 0)),
    ("5pm UTC+5:30", _aw(2017, 6, 27, 17, 0, 330)),
]


@pytest.mark.parametrize("text,want", _CASES)
def test_tz_clock(text, want):
    s = span(text).start
    assert s.tzinfo is not None, f"{text!r} produced a naive time"
    assert s.utcoffset() == want.utcoffset()
    assert (s.year, s.month, s.day, s.hour, s.minute) == \
        (want.year, want.month, want.day, want.hour, want.minute)


# a bare clock with no zone stays naive; a named-city zone is not resolved
# (the city word is left in the remainder, the time stays naive).
def test_bare_clock_is_naive():
    assert span("3pm").start.tzinfo is None


def test_named_city_zone_out_of_scope():
    r = parse("3pm Berlin")
    assert r is not None
    assert r[0].start.tzinfo is None
    assert "berlin" in r[1].lower()
