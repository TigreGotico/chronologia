"""An offset after a month or a season counts from its last day, in every
locale and for a leading and a trailing direction word.

Meteorological summer is June, July and August (NOAA NCEI, "Meteorological
Versus Astronomical Seasons"), so at 16 November 2026 the next summer ends
on 31 August 2027.  June 2027 ends on 30 June.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 16, 12, 0)


@pytest.mark.parametrize("lang, text, day", [
    ("pt", "lembra-me duas semanas depois do próximo verão",
     date(2027, 8, 31) + timedelta(weeks=2)),
    ("de", "erinnere mich zwei Wochen nach dem nächsten Sommer",
     date(2027, 8, 31) + timedelta(weeks=2)),
    # a trailing direction word: eu "baino ... geroago", hu "után"
    ("eu", "2027ko ekaina baino 3 egun geroago",
     date(2027, 6, 30) + timedelta(days=3)),
    ("hu", "3 nappal 2027 június után", date(2027, 6, 30) + timedelta(days=3)),
    ("eu", "2027ko ekaina baino 3 egun lehenago",
     date(2027, 6, 1) - timedelta(days=3)),
])
def test_after_a_month_or_season_counts_from_its_last_day(lang, text, day):
    span = extract_timespan(text, lang, anchor=ANCHOR).span
    assert (span.start.year, span.start.month, span.start.day) == (
        day.year, day.month, day.day)
    assert span.end - span.start == timedelta(days=1)
