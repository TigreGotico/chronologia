"""A clock said with a counted offset from a holiday has ranked readings.

Ruling 31 of the chronologia disagreement rulings: the first reading is the
stated clock on the day the offset lands on, in the twelve-hour reading
nearer to the offset instant.  The offset instant comes next, then the
clock's other twelve-hour reading.  A clock with an am or pm word or an hour
over 12 has no other reading, and a clock that agrees with the offset gives
one reading.  The offset instant is ruling 30: the count runs from 00:00 of
the holiday.  The golds are clock arithmetic: Christmas 2026 is 25 December,
New Year 2027 is 1 January, Easter 2027 is 28 March, so Easter Monday is 29
March.  Anchor 25 September 2026, 12:00.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate, extract_candidates, extract_timespan

ANCHOR = datetime(2026, 9, 25, 12, 0)

#: 1 hour before Christmas
CHRISTMAS_EVE_23 = datetime(2026, 12, 24, 23, 0)


@pytest.mark.parametrize("lang, text, readings", [
    # instant 24 Dec 23:00: 21:00 is 2 hours from it, 09:00 is 14 hours
    ("pt", "às 9 uma hora antes do natal",
     [datetime(2026, 12, 24, 21), CHRISTMAS_EVE_23, datetime(2026, 12, 24, 9)]),
    ("en", "at 9 one hour before christmas",
     [datetime(2026, 12, 24, 21), CHRISTMAS_EVE_23, datetime(2026, 12, 24, 9)]),
    ("es", "a las 9 una hora antes de navidad",
     [datetime(2026, 12, 24, 21), CHRISTMAS_EVE_23, datetime(2026, 12, 24, 9)]),
    ("fr", "à 9 heures une heure avant noël",
     [datetime(2026, 12, 24, 21), CHRISTMAS_EVE_23, datetime(2026, 12, 24, 9)]),
    ("de", "um 9 eine Stunde vor Weihnachten",
     [datetime(2026, 12, 24, 21), CHRISTMAS_EVE_23, datetime(2026, 12, 24, 9)]),
    ("en", "at 9:30 one hour before christmas",
     [datetime(2026, 12, 24, 21, 30), CHRISTMAS_EVE_23,
      datetime(2026, 12, 24, 9, 30)]),
    # instant 25 Dec 02:00: 09:00 is 7 hours from it, 21:00 is 19 hours
    ("en", "at 9 two hours after christmas",
     [datetime(2026, 12, 25, 9), datetime(2026, 12, 25, 2),
      datetime(2026, 12, 25, 21)]),
    # instant 31 Dec 22:00: 12:00 is 10 hours from it, 00:00 is 22 hours
    ("en", "at 12 two hours before new year",
     [datetime(2026, 12, 31, 12), datetime(2026, 12, 31, 22),
      datetime(2026, 12, 31, 0)]),
    # 36 hours before 29 Mar 00:00 is 27 Mar 12:00: 09:00 is 3 hours from it
    ("en", "at 9 36 hours before easter monday",
     [datetime(2027, 3, 27, 9), datetime(2027, 3, 27, 12),
      datetime(2027, 3, 27, 21)]),
    # 12 hours before 29 Mar 00:00 is 28 Mar 12:00; "6am" has one reading
    ("en", "at 6am 12 hours before easter monday",
     [datetime(2027, 3, 28, 6), datetime(2027, 3, 28, 12)]),
    ("en", "at 9pm one hour before christmas",
     [datetime(2026, 12, 24, 21), CHRISTMAS_EVE_23]),
    # a day and a half before 29 Mar 00:00 is 27 Mar 12:00
    ("en", "a day and a half before easter monday at 9am",
     [datetime(2027, 3, 27, 9), datetime(2027, 3, 27, 12)]),
    # the clock agrees with the offset
    ("en", "at 11 one hour before christmas", [CHRISTMAS_EVE_23]),
    ("en", "at 23 one hour before christmas", [CHRISTMAS_EVE_23]),
])
def test_the_readings_rank_the_clock_then_the_offset_instant(
        lang, text, readings):
    expected = [AstroDate.from_datetime(t) for t in readings]
    span, remainder = extract_timespan(text, lang, ANCHOR)
    assert (span.start, remainder) == (expected[0], "")
    got = [c.span.start for c in extract_candidates(text, lang, ANCHOR)]
    assert got[:len(readings)] == expected
    if len(readings) < 3:
        # no other twelve-hour reading is offered for the first one
        half = timedelta(hours=12 if expected[0].hour < 12 else -12)
        assert expected[0] + half not in got


@pytest.mark.parametrize("text, clock", [
    # a whole number of days lands on no instant: the clock reads as written
    ("at 9 two days before christmas", datetime(2026, 12, 23, 9)),
    # a clock after the holiday is the holiday's own time ("christmas at 9")
    ("one hour before christmas at 9", datetime(2026, 12, 25, 8)),
])
def test_an_offset_with_no_instant_keeps_the_written_clock(text, clock):
    span, remainder = extract_timespan(text, "en", ANCHOR)
    assert (span.start, remainder) == (AstroDate.from_datetime(clock), "")
