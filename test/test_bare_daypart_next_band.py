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

from chronologia import AstroDate, extract_candidates, extract_timespan

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
    # "i" before a bare Nordic part-of-day noun, and the Kabyle -a suffix,
    # name today's band
    ("sv", "i förmiddag", LATE),
    ("da", "i formiddag", LATE),
    ("nb", "i ettermiddag", LATE),
    ("nn", "i føremiddag", LATE),
    ("kab", "ṣṣbeḥ-a", LATE),
])
def test_a_band_still_running_or_with_its_own_day_stays_today(
        lang, text, anchor):
    start, _ = _band(text, lang, anchor)
    assert (start.year, start.month, start.day) == (
        anchor.year, anchor.month, anchor.day)



NOON = datetime(2023, 1, 15, 12, 0)
BEFORE_NOON = datetime(2023, 1, 15, 11, 59)


def test_the_band_has_ended_at_its_last_instant():
    # the en morning is [06:00, 12:00): over at 12:00, running at 11:59
    assert _band("in the morning", "en", NOON) == (
        AstroDate(2023, 1, 16, 6), AstroDate(2023, 1, 16, 12))
    assert _band("in the morning", "en", BEFORE_NOON) == (
        AstroDate(2023, 1, 15, 6), AstroDate(2023, 1, 15, 12))


SATURDAY_ONE_PM = datetime(2026, 10, 17, 13, 0)


@pytest.mark.parametrize("lang, text, start", [
    # a range that holds the anchor is the current one (ruling 1, class 3):
    # the morning has ended at 13:00, but the range runs on into the evening
    ("en", "between morning and afternoon", AstroDate(2026, 10, 17, 6)),
    ("en", "from morning to evening", AstroDate(2026, 10, 17, 6)),
    ("pt", "de manhã à noite", AstroDate(2026, 10, 17, 6)),
    ("es", "de la mañana a la noche", AstroDate(2026, 10, 17, 6)),
])
def test_a_range_of_parts_of_the_day_keeps_the_anchor_day(lang, text, start):
    assert _band(text, lang, SATURDAY_ONE_PM)[0] == start


def test_a_fused_today_word_keeps_the_anchor_day():
    # nl "vannacht" is van + nacht, "this night", like "vanavond"
    assert _band("vannacht", "nl", datetime(2026, 10, 17, 10, 0)) == (
        AstroDate(2026, 10, 17, 0), AstroDate(2026, 10, 17, 6))


def test_the_candidates_agree_with_the_single_reading():
    top = extract_candidates("à tarde", "pt", LATE)[0]
    assert (top.span.start, top.span.end) == (
        AstroDate(2023, 1, 16, 12), AstroDate(2023, 1, 16, 19))
