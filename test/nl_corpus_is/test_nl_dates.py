"""Icelandic calendar dates, in both the digit and the spelled-day forms.

The written date runs day-month-year with the day closed by a period and the
month name uninflected: "25. desember 2020".  The spoken day is a weak
masculine ordinal agreeing with an elided "dagur", so the same date reads
"tuttugasti og fimmti desember"; a compound inflects only its last element.

Expected values are plain calendar facts about the corpus anchor, never the
parser's own output.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import nomatch, remainder, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ("1. mars 1990", 1990, 3, 1),
    ("25. desember 2020", 2020, 12, 25),
    ("16. febrúar 1918", 1918, 2, 16),
    ("1. maí 2004", 2004, 5, 1),
    ("17. júní 1944", 1944, 6, 17),
])
def test_full_written_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", ["1. mars 1990", "25. desember 2020"])
def test_full_written_date_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,y,m,d", [
    ("5. júlí", 2017, 7, 5),
    ("24. desember", 2017, 12, 24),
    ("1. mars", 2018, 3, 1),
    ("5. júní", 2018, 6, 5),
])
def test_day_month_without_year(text, y, m, d):
    """With no year stated the date resolves forward from the anchor."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("fimmti júlí", 2017, 7, 5),
    ("fyrsti janúar", 2018, 1, 1),
    ("tíundi nóvember", 2017, 11, 10),
    ("tuttugasti desember", 2017, 12, 20),
    ("sextándi febrúar", 2018, 2, 16),
    ("sautjándi júní", 2018, 6, 17),
])
def test_spelled_ordinal_day(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", ["fimmti júlí", "fyrsti janúar"])
def test_spelled_ordinal_day_is_one_day_wide(text):
    s = span(text)
    assert (s.end - s.start).days == 1


@pytest.mark.parametrize("text,y,m,d", [
    ("tuttugasti og fimmti desember", 2017, 12, 25),
    ("þrítugasti og fyrsti desember", 2017, 12, 31),
    ("tuttugasti og þriðji júlí", 2017, 7, 23),
    ("þrítugasti og fyrsti mars", 2018, 3, 31),
])
def test_compound_day_keeps_its_tens(text, y, m, d):
    """The tens element must survive: answering the fifth when the speaker
    said the twenty-fifth is the silent-wrong this table exists to prevent."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("fimmta júlí", 2017, 7, 5),
    ("tuttugasta og fimmta desember", 2017, 12, 25),
])
def test_oblique_ordinal_day_binds_too(text, y, m, d):
    """The weak ordinal's oblique form ("fimmta") names the same day as its
    nominative -- both agree with the elided masculine "dagur"."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,m", [
    ("desember", 12), ("maí", 5), ("janúar", 1), ("ágúst", 8),
    ("september", 9),
])
def test_bare_month_is_the_whole_month(text, m):
    s = span(text)
    assert s.start.month == m and s.start.day == 1
    assert (s.end - s.start).days >= 28


@pytest.mark.parametrize("text,m", [
    ("des.", 12), ("jan.", 1), ("okt.", 10), ("feb.", 2),
])
def test_abbreviated_month(text, m):
    assert span(text).start.month == m


@pytest.mark.parametrize("text", [
    "fimmti", "tuttugasti og fimmti", "asdf qwerty", "",
])
def test_no_date_without_a_month(text):
    """An ordinal with nothing to attach to, and outright garbage, must fail
    honestly rather than inventing a day."""
    nomatch(text)


@pytest.mark.parametrize("text,y", [("árið 1990", 1990), ("2019", 2019)])
def test_year_reference(text, y):
    s = span(text)
    assert s.start == AstroDate(y, 1, 1) and s.end == AstroDate(y + 1, 1, 1)


def test_year_word_is_consumed():
    assert remainder("árið 1990") == ""


def test_iso_literal_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
