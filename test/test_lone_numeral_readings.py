"""A numeral alone lists its hour and day-of-month readings.

Ruling 34 of the chronologia disagreement rulings: a numeral with no clock
marker, no unit and no year cue is not a date in ``extract_timespan``.
``extract_candidates`` lists its readings ranked low: an hour for 0 to 24 and
a day of the month for 1 to 31.

The anchor is Wednesday 2026-11-18 14:00.  An hour 1 to 12 takes the next of
its two clock readings (ruling 17); an hour 13 to 24 is the next time the
clock shows it.  A day is the next day with that number, this month or the
next month that has it.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate, extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 18, 14, 0)


def _readings(lang, text):
    found = {}
    for c in extract_candidates(text, lang, ANCHOR):
        found.setdefault(c.construction, (c.span.start, c.span.end))
    return found


def _span(start, length):
    return (AstroDate.from_datetime(start),
            AstroDate.from_datetime(start + length))


@pytest.mark.parametrize("lang, text, hour, day", [
    # 20:00 is still ahead today; the 20th is two days ahead
    ("da", "20", (2026, 11, 18, 20, 0), (2026, 11, 20)),
    # 02:00 has passed, 14:00 is the anchor itself; the 2nd has passed
    ("nl", "2", (2026, 11, 18, 14, 0), (2026, 12, 2)),
    ("en", "5", (2026, 11, 18, 17, 0), (2026, 12, 5)),
    ("en", "five", (2026, 11, 18, 17, 0), (2026, 12, 5)),
    ("de", "3", (2026, 11, 18, 15, 0), (2026, 12, 3)),
    # 24:00 is the midnight that ends the anchor's day
    ("en", "24", (2026, 11, 19, 0, 0), (2026, 11, 24)),
    ("en", "17", (2026, 11, 18, 17, 0), (2026, 12, 17)),
])
def test_hour_and_day_readings(lang, text, hour, day):
    assert extract_timespan(text, lang, ANCHOR) is None
    found = _readings(lang, text)
    assert found["clock_time"] == _span(datetime(*hour), timedelta(minutes=1))
    assert found["month_day_ref"] == _span(datetime(*day), timedelta(days=1))


def test_a_day_past_24_has_no_hour():
    # November has 30 days, so the next 31st is in December
    found = _readings("en", "31")
    assert "clock_time" not in found
    assert found["month_day_ref"] == _span(datetime(2026, 12, 31),
                                           timedelta(days=1))


@pytest.mark.parametrize("text", ["45", "5 people came"])
def test_no_reading_outside_the_ranges(text):
    assert extract_candidates(text, "en", ANCHOR) == []
