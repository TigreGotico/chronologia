"""Hindi calendar dates, weekdays and years, in both digit systems.

The written date runs day-month-year with the month name uninflected, and the
locative postposition को may trail the whole date ("15 मार्च 2024 को").  A bare
weekday names its next occurrence and may likewise be closed by को
("सोमवार को" -- on Monday), the reading en.wiktionary gives under को's "in, at
the time of" sense with the worked example "बुधवार को".

Expected values are plain calendar facts about the corpus anchor, never the
parser's own output.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, nomatch, remainder, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ("15 मार्च 2024", 2024, 3, 15),
    ("1 जनवरी 2000", 2000, 1, 1),
    ("31 दिसंबर 1999", 1999, 12, 31),
    ("26 जनवरी 1950", 1950, 1, 26),
    ("15 अगस्त 1947", 1947, 8, 15),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", ["15 मार्च 2024", "15 मार्च 2024 को"])
def test_a_full_date_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,y,m,d", [
    ("5 जुलाई", 2017, 7, 5),
    ("24 दिसंबर", 2017, 12, 24),
    ("1 मार्च", 2018, 3, 1),
])
def test_month_day_without_a_year_resolves_forward(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("month_word,m", [
    ("जनवरी", 1), ("फ़रवरी", 2), ("फरवरी", 2), ("मार्च", 3), ("अप्रैल", 4),
    ("मई", 5), ("जून", 6), ("जुलाई", 7), ("अगस्त", 8), ("सितंबर", 9),
    ("अक्टूबर", 10), ("नवंबर", 11), ("दिसंबर", 12),
])
def test_every_month_name(month_word, m):
    s = span(month_word)
    assert s.start.month == m and s.start.day == 1
    assert (s.end - s.start).days >= 28


def test_the_nukta_and_nukta_less_february_are_the_same_month():
    """फ़रवरी is फ + U+093C; the nukta-less फरवरी is as commonly typed."""
    assert span("फ़रवरी").start == span("फरवरी").start


@pytest.mark.parametrize("weekday,index", [
    ("सोमवार", 0), ("मंगलवार", 1), ("बुधवार", 2), ("गुरुवार", 3),
    ("शुक्रवार", 4), ("शनिवार", 5), ("रविवार", 6),
])
def test_every_weekday_resolves_to_its_next_occurrence(weekday, index):
    from datetime import timedelta
    ahead = (index - ANCHOR.weekday()) % 7 or 7
    expected = (ANCHOR + timedelta(days=ahead)).date()
    s = start(weekday)
    assert (s.year, s.month, s.day) == (expected.year, expected.month,
                                        expected.day)


def test_the_colloquial_sunday_is_the_same_day():
    assert span("इतवार").start == span("रविवार").start


@pytest.mark.parametrize("text", [
    "सोमवार को", "शुक्रवार को", "पिछले शुक्रवार को", "अगले सोमवार को",
])
def test_the_locative_postposition_is_consumed(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,expected", [
    # the anchor is Tuesday 2017-06-27; the Fridays either side of it are the
    # 23rd and the 30th of June
    ("पिछले शुक्रवार को", AstroDate(2017, 6, 23)),
    ("अगले शुक्रवार को", AstroDate(2017, 6, 30)),
    ("पिछले सोमवार को", AstroDate(2017, 6, 26)),
    ("अगले सोमवार को", AstroDate(2017, 7, 3)),
])
def test_last_and_next_weekday_point_opposite_ways(text, expected):
    assert start(text) == expected


@pytest.mark.parametrize("text,y", [
    ("2019", 2019), ("1918", 2018 - 100), ("1947", 1947),
])
def test_bare_year(text, y):
    s = span(text)
    assert s.start == AstroDate(y, 1, 1) and s.end == AstroDate(y + 1, 1, 1)


@pytest.mark.parametrize("text,century", [
    ("इक्कीसवीं सदी", 21), ("बीसवीं सदी", 20), ("उन्नीसवीं शताब्दी", 19),
])
def test_ordinal_century(text, century):
    """The ordinal is feminine because सदी and शताब्दी are -- the -वीं column
    of the ā̃-stem paradigm.  "इक्कीसवीं सदी" is en.wiktionary's own usage
    example under सदी."""
    s = span(text)
    assert s.start.year == (century - 1) * 100
    assert s.end.year == century * 100


@pytest.mark.parametrize("text", [
    "पाँचवाँ", "इक्कीसवीं", "asdf qwerty", "", "   ", "नमस्ते कैसे हो",
])
def test_no_date_without_something_to_date(text):
    nomatch(text)
