"""A counted offset from a holiday counts from the instant it begins.

Ruling 30 of the chronologia disagreement rulings: the holiday stands for its
first instant, 00:00 of its day, in both directions.  A count under one day
names an instant one minute wide; a count of a day or more names that day.
The golds are clock arithmetic: Christmas 2026 is 25 December, New Year 2027
is 1 January, Easter 2027 is 28 March.  A quarter of an hour is 15 minutes.
Anchor 25 September 2026, 12:00.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 9, 25, 12, 0)
MINUTE = datetime(2000, 1, 1, 0, 1) - datetime(2000, 1, 1)
DAY = datetime(2000, 1, 2) - datetime(2000, 1, 1)


@pytest.mark.parametrize("lang, text, instant, rest", [
    ("pt", "lembra-me uma hora antes do natal", datetime(2026, 12, 24, 23, 0), "lembra-me"),
    ("pt", "lembra-me uma hora antes do ano novo", datetime(2026, 12, 31, 23, 0), "lembra-me"),
    ("pt", "meia hora antes do ano novo", datetime(2026, 12, 31, 23, 30), ""),
    ("pt", "duas horas antes do natal", datetime(2026, 12, 24, 22, 0), ""),
    ("it", "ricordami un'ora prima di capodanno", datetime(2026, 12, 31, 23, 0), "ricordami"),
    ("es", "un cuarto de hora antes de navidad", datetime(2026, 12, 24, 23, 45), ""),
    ("es", "tres cuartos de hora antes de navidad", datetime(2026, 12, 24, 23, 15), ""),
    ("fr", "un quart d'heure avant noël", datetime(2026, 12, 24, 23, 45), ""),
    ("fr", "trois quarts d'heure avant noël", datetime(2026, 12, 24, 23, 15), ""),
    ("pt", "um quarto de hora antes do natal", datetime(2026, 12, 24, 23, 45), ""),
    ("pt", "três quartos de hora antes do natal", datetime(2026, 12, 24, 23, 15), ""),
    ("ca", "un quart d'hora abans de nadal", datetime(2026, 12, 24, 23, 45), ""),
    ("gl", "un cuarto de hora antes do nadal", datetime(2026, 12, 24, 23, 45), ""),
    ("en", "remind me an hour before new year", datetime(2026, 12, 31, 23, 0), "remind me"),
    ("en", "remind me half an hour before new year", datetime(2026, 12, 31, 23, 30), "remind me"),
    ("en", "an hour and a half before christmas", datetime(2026, 12, 24, 22, 30), ""),
    ("en", "the hour before christmas", datetime(2026, 12, 24, 23, 0), ""),
    ("en", "an hour before easter", datetime(2027, 3, 27, 23, 0), ""),
    ("sv", "en kvart före jul", datetime(2026, 12, 24, 23, 45), ""),
    ("en", "2 hours after christmas", datetime(2026, 12, 25, 2, 0), ""),
    ("en", "15 minutes after new year", datetime(2027, 1, 1, 0, 15), ""),
])
def test_a_count_under_a_day_is_an_instant_from_the_holiday_start(
        lang, text, instant, rest):
    span, remainder = extract_timespan(text, lang, ANCHOR)
    assert (span.start, span.end - span.start, remainder) == (
        AstroDate.from_datetime(instant), MINUTE, rest)


@pytest.mark.parametrize("text, day", [
    ("2 days after christmas", datetime(2026, 12, 27)),
    ("2 days before christmas", datetime(2026, 12, 23)),
])
def test_a_count_of_a_day_or_more_is_that_day(text, day):
    span, _ = extract_timespan(text, "en", ANCHOR)
    assert (span.start, span.end - span.start) == (AstroDate.from_datetime(day), DAY)
