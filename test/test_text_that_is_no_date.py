# -*- coding: utf-8 -*-
"""Text that is no date reads as no date: arithmetic, amounts, impossible
days, a verb that spells like a marker, a lone numeral, a stray word.

Each expected value is None, or hand arithmetic from the anchor.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1035"
LISBON = ZoneInfo("Europe/Lisbon")
OCT17 = datetime(2026, 10, 17, 12, 0, tzinfo=LISBON)

NO_DATE = [
    ("nl", "3 mensen 4 uur", OCT17),
    ("en", "2400", datetime(2117, 9, 3, 13, 30)),
    ("nl", "2400", datetime(1998, 1, 1)),
    ("nl", "2400", datetime(2017, 6, 27, 13, 4)),
    ("en", "2400", datetime(2017, 6, 27, 13, 4)),
    ("eu", "ordu barru", datetime(2117, 9, 3, 13, 30)),
    ("it", "quanto fa 5 meno 2", OCT17),
    ("it", "quanto fa cinque meno due", OCT17),
    ("it", "dieci meno due", OCT17),
    ("it", "il 12 15 marzo", OCT17),
    ("it", "ho speso 20 e 30 euro", OCT17),
    ("de", "am 0. januar", datetime(2017, 6, 27)),
    ("de", "am 0. januar", datetime(2117, 9, 3, 13, 30)),
    ("fr", "elle a 2h de route", datetime(2117, 9, 3, 13, 30)),
    ("fr", "il a 3 heures de retard", datetime(2017, 6, 27, 13, 4)),
    ("fr", "il a 3 heures de retard", datetime(2117, 9, 3, 13, 30)),
    ("ro", "mai vorbim", datetime(2017, 6, 27, 13, 4)),
    ("ro", "vreau mai mult", datetime(2017, 6, 27, 13, 4)),
    ("fa", "یک ساعت و پنجاه و هفت و نیم دقیقه طول می", datetime(2026, 3, 11, 10)),
    ("fa", "یک ساعت و پنجاه و هفت و نیم دقیقه طول می کشد",
     datetime(2026, 3, 11, 10)),
    ("hu", "április 31 8 órakor", datetime(2017, 6, 27, 13, 4)),
    ("hu", "április 31 8 órakor", datetime(2017, 6, 27)),
    ("nl", "0 februari", datetime(1998, 1, 1)),
    ("fy", "february 30 2020", datetime(2020, 1, 1)),
    ("nl", "het gaat om 8 of 9 mensen", OCT17),
    ("nl", "om 8 en 9 kinderen", OCT17),
    ("nl", "om acht of negen mensen", OCT17),
    ("nl", "om 8 en negen", OCT17),
] + [("en", "%s third of the month" % w, OCT17) for w in (
    "a full", "a solid", "a fair", "a clear", "a complete", "a large",
    "a total", "another", "some", "any", "the first", "the last",
    "the final")] + [("en", "%s fifth of the month" % w, OCT17) for w in (
        "a whole", "an entire", "a mere", "an extra")]


FIXED_NO_DATE = {"mai vorbim", "vreau mai mult"}


@pytest.mark.parametrize("lang,text,anchor", [
    row if row[1] in FIXED_NO_DATE else pytest.param(
        *row, marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE))
    for row in NO_DATE])
def test_it_is_no_date(lang, text, anchor):
    assert extract_timespan(text, lang, anchor) is None


# lang, text, anchor, expected start (hand arithmetic from the anchor)
START = [
    # the named day keeps the spoken hour (ruling 17)
    ("it", "il 3 alle 5", OCT17, datetime(2026, 11, 3, 5, 0)),
    ("it", "il 20 alle 8", OCT17, datetime(2026, 10, 20, 8, 0)),
    # 8 has passed at 15:00, so the evening reading is 20:00
    ("nl", "ik ben vanochtend gaan lopen, zet een wekker om 8",
     datetime(2026, 10, 17, 15, 0, tzinfo=LISBON),
     datetime(2026, 10, 17, 20, 0)),
    # a holiday name is a modifier of the noun, not the date
    ("en", "buy christmas presents at 5pm", datetime(2026, 9, 25, 12),
     datetime(2026, 9, 25, 17, 0)),
    ("en", "play christmas music at 9pm", datetime(2026, 9, 25, 12),
     datetime(2026, 9, 25, 21, 0)),
    ("en", "christmas island at 9am", datetime(2026, 9, 25, 12),
     datetime(2026, 9, 26, 9, 0)),
    ("fr", "musique de noël à 21 heures", datetime(2026, 9, 25, 12),
     datetime(2026, 9, 25, 21, 0)),
    ("de", "geschenke für weihnachten um 17 uhr kaufen",
     datetime(2026, 9, 25, 12), datetime(2026, 9, 25, 17, 0)),
    ("en", "play christmas music on friday", datetime(2026, 9, 25, 12),
     datetime(2026, 9, 25, 0, 0)),
    # "friday at 9am" said on Friday at 12:00 is the next Friday (ruling 16)
    ("en", "play christmas music on friday at 9am", datetime(2026, 9, 25, 12),
     datetime(2026, 10, 2, 9, 0)),
    ("en", "remind me on friday at 9am about christmas",
     datetime(2026, 9, 25, 12), datetime(2026, 10, 2, 9, 0)),
    ("en", "remind me at 9am on friday about christmas",
     datetime(2026, 9, 25, 12), datetime(2026, 10, 2, 9, 0)),
    # "demain" from Monday 2026-01-05 is the 6th; the count is no hour
    ("fr", "de 5 à 8 personnes demain", datetime(2026, 1, 5, 6, 0),
     datetime(2026, 1, 6, 0, 0)),
    # "Version 1.15.20" is no date, so "morgen" is 24 September 2026
    ("de", "Installiere Version 1.15.20 morgen", datetime(2026, 9, 23, 12),
     datetime(2026, 9, 24, 0, 0)),
    # two counts joined by "of" leave the day, not a clock
    ("nl", "morgen om 8 of 9 mensen", OCT17, datetime(2026, 10, 18, 0, 0)),
]


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,anchor,expected", START)
def test_the_date_comes_from_the_words_that_name_one(
        lang, text, anchor, expected):
    start = extract_timespan(text, lang, anchor).span.start.datetime()
    assert start == expected


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
@pytest.mark.parametrize("text,remainder", [
    ("café ☕ tomorrow", "café ☕"),
    ("☕ tomorrow", "☕"),
])
def test_a_symbol_beside_a_date_stays_in_the_remainder(text, remainder):
    found = extract_timespan(text, "en", datetime(2026, 3, 11, 10))
    assert found.remainder == remainder


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_a_version_number_stays_in_the_remainder():
    found = extract_timespan(
        "Installiere Version 1.15.20 morgen", "de", datetime(2026, 9, 23, 12))
    assert "1.15.20" in found.remainder


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_a_holiday_name_after_a_clock_stays_in_the_remainder():
    found = extract_timespan(
        "remind me at 5pm to buy christmas cards", "en",
        datetime(2026, 9, 25, 12))
    assert found.span.start.datetime() == datetime(2026, 9, 25, 17, 0)
    assert found.span.end.datetime() == datetime(2026, 9, 25, 17, 1)
    assert "christmas" in found.remainder
