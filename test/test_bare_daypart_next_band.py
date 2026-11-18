"""A bare part of the day is today's band until it ends, then tomorrow's.

Ruling 28 of the chronologia disagreement rulings: a part-of-day word said
with no day names that band on the anchor's day while the band has not
ended, and the next day's band once it has, as class 3 reads the next
occurrence.  "this <part of the day>" and a today word ("tonight") keep the
anchor's day.  The band edges are the ones chronologia gives for each word
on the anchor's day; only the day moves.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate, extract_timespan

LATE = datetime(2023, 1, 15, 21, 0)
EARLY = datetime(2023, 1, 15, 10, 0)
LUNCH = datetime(2017, 6, 27, 13, 4)
DAY = timedelta(days=1)


def _band(text, lang, anchor):
    span, _ = extract_timespan(text, lang, anchor)
    return span.start, span.end


@pytest.mark.parametrize("lang, text, anchor, hours", [
    # the pt afternoon is 12:00 to 19:00, over at 21:00 (the #997 row)
    ("pt", "à tarde", LATE, (12, 19)),
    ("pt", "de manhã", LATE, (6, 12)),
    ("es", "por la mañana", LATE, (6, 12)),
    ("es", "por la tarde", LATE, (12, 20)),
    ("en", "when does it start getting light in the morning", LUNCH, (6, 12)),
    ("pt", "Que horas começa a clarear de manhã?", LUNCH, (6, 12)),
    ("es", "¿A qué horas empieza a aclarar por la mañana?", LUNCH, (6, 12)),
    ("es", "necesito que suene una alarma por la mañana", LUNCH, (6, 12)),
    ("pt", "acorda-me com música de manhã", LUNCH, (6, 12)),
])
def test_a_band_that_has_ended_is_tomorrows(lang, text, anchor, hours):
    tomorrow = anchor.replace(hour=0, minute=0) + DAY
    assert _band(text, lang, anchor) == tuple(
        AstroDate.from_datetime(tomorrow.replace(hour=h)) for h in hours)


@pytest.mark.parametrize("lang, text, anchor", [
    ("pt", "à tarde", EARLY),
    ("pt", "à noite", LATE),
    ("en", "this morning", LUNCH),
    ("en", "tonight", LATE),
    ("pt", "hoje de manhã", LATE),
])
def test_a_band_still_running_or_with_its_own_day_stays_today(
        lang, text, anchor):
    start, _ = _band(text, lang, anchor)
    assert (start.year, start.month, start.day) == (
        anchor.year, anchor.month, anchor.day)

