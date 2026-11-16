"""In Estonian, Finnish, Hungarian and Basque the "during" word follows its
noun, so it belongs to the phrase before a season or holiday, not to the
season or holiday after it.  Wiktionary: fi "aikana" and et "jooksul" are
postpositions "during", hu "alatt" is a postposition "in the course of",
eu "zehar" is "across, through".

Meteorological summer is June, July and August (NOAA NCEI, "Meteorological
Versus Astronomical Seasons"); Christmas is 25 December.  Anchor 16
November 2026.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 16, 12, 0)
SUMMER_2026 = (datetime(2026, 6, 1), datetime(2026, 9, 1))
CHRISTMAS_2026 = (datetime(2026, 12, 25), datetime(2026, 12, 26))


@pytest.mark.parametrize("lang, text, bounds, remainder", [
    ("fi", "luen paljon loman aikana kesällä", SUMMER_2026,
     "luen paljon loman aikana"),
    ("fi", "remontin aikana kesällä", SUMMER_2026, "remontin aikana"),
    ("et", "loen palju puhkuse jooksul suvel", SUMMER_2026,
     "loen palju puhkuse jooksul"),
    ("hu", "sokat olvasok a szünet alatt nyáron", SUMMER_2026,
     "sokat olvasok a szünet alatt"),
    ("fi", "luen paljon loman aikana joulu", CHRISTMAS_2026,
     "luen paljon loman aikana"),
    ("et", "loen palju puhkuse jooksul jõulud", CHRISTMAS_2026,
     "loen palju puhkuse jooksul"),
    ("hu", "a szünet alatt karácsony", CHRISTMAS_2026, "a szünet alatt"),
    ("eu", "oporretan zehar Gabonak lasaiak dira", CHRISTMAS_2026,
     "oporretan zehar lasaiak dira"),
])
def test_a_postposition_stays_with_the_phrase_before_the_reference(
        lang, text, bounds, remainder):
    span, rest = extract_timespan(text, lang, anchor=ANCHOR)
    assert (span.start, span.end) == bounds
    assert rest == remainder


@pytest.mark.parametrize("lang, text, bounds", [
    ("hu", "karácsony alatt", CHRISTMAS_2026),
    ("hu", "a nyár alatt", SUMMER_2026),
    ("eu", "Gabonak zehar", CHRISTMAS_2026),
    ("eu", "udan zehar", SUMMER_2026),
])
def test_a_trailing_postposition_reads_with_its_reference(lang, text, bounds):
    span, rest = extract_timespan(text, lang, anchor=ANCHOR)
    assert (span.start, span.end) == bounds
    assert rest == ""
