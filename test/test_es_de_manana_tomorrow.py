"""Spanish "de mañana" after a noun names tomorrow, not the morning band.

"mañana" is both the day word (tomorrow) and the day-part word (morning).
Directly after "de" with no article it is the day: "la fiesta de mañana" is
tomorrow's party.  With an article or "esta" it stays the band.  The es band
is CLDR 47 ``[06:00, 12:00)``.  Anchor: Tuesday 2023-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_timespan

ANCHOR = datetime(2023, 6, 27, 13, 4)
TODAY = ANCHOR.replace(hour=0, minute=0)
TOMORROW = TODAY + timedelta(days=1)


def _span(text):
    s = extract_timespan(text, "es", anchor=ANCHOR).span
    return (datetime(s.start.year, s.start.month, s.start.day, s.start.hour, s.start.minute),
            datetime(s.end.year, s.end.month, s.end.day, s.end.hour, s.end.minute))


@pytest.mark.parametrize("text", [
    "Mi abuela insiste en que la tarta para la fiesta de mañana tiene que hornearse con paciencia.",
    "Mi hermana insiste en que llevemos paraguas a la excursión de mañana.",
    "Mi abuela ya está preparando la masa para las empanadas de mañana, así que la cocina huele a canela.",
])
def test_noun_de_manana_is_tomorrow(text):
    assert _span(text) == (TOMORROW, TOMORROW + timedelta(days=1))


@pytest.mark.parametrize("text, start, end", [
    ("mañana por la mañana", TOMORROW + timedelta(hours=6), TOMORROW + timedelta(hours=12)),
    ("esta mañana", TODAY + timedelta(hours=6), TODAY + timedelta(hours=12)),
    ("por la mañana", TODAY + timedelta(hours=6), TODAY + timedelta(hours=12)),
])
def test_article_or_this_keeps_the_band(text, start, end):
    assert _span(text) == (start, end)


@pytest.mark.parametrize("text, lang, start, end", [
    ("el periódico de mañana", "es", TOMORROW, TOMORROW + timedelta(days=1)),
    ("a festa de mañá", "gl", TOMORROW, TOMORROW + timedelta(days=1)),
    ("mañana de mañana", "es", TOMORROW + timedelta(hours=6), TOMORROW + timedelta(hours=12)),
])
def test_owner_before_of_decides(text, lang, start, end):
    s = extract_timespan(text, lang, anchor=ANCHOR).span
    got = (datetime(s.start.year, s.start.month, s.start.day, s.start.hour, s.start.minute),
           datetime(s.end.year, s.end.month, s.end.day, s.end.hour, s.end.minute))
    assert got == (start, end)
