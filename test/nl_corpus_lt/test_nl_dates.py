"""Lithuanian calendar dates, in both the digit and the spelled-day forms.

The written date runs year-month-day with the month in the genitive, the year
closed by "m." (metai) and the day by "d." (diena): "1990 m. kovo 1 d.".  The
spoken day is a FEMININE ordinal agreeing with an elided "diena", so the same
date reads "kovo pirmoji"; a compound day inflects only its last element
("gruodžio dvidešimt penktoji").

Expected values are plain calendar facts about the corpus anchor, never the
parser's own output.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import nomatch, remainder, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ("1990 m. kovo 1 d.", 1990, 3, 1),
    ("2020 m. gruodžio 25 d.", 2020, 12, 25),
    ("1918 m. vasario 16 d.", 1918, 2, 16),
    ("2004 m. gegužės 1 d.", 2004, 5, 1),
])
def test_full_written_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", [
    "1990 m. kovo 1 d.", "2020 m. gruodžio 25 d.",
])
def test_full_written_date_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,y,m,d", [
    ("liepos 5 d.", 2017, 7, 5),
    ("gruodžio 24 d.", 2017, 12, 24),
    ("kovo 1 d.", 2018, 3, 1),
    ("liepos 5", 2017, 7, 5),
])
def test_month_day_without_year(text, y, m, d):
    """With no year stated the date resolves forward from the anchor."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("liepos penktoji", 2017, 7, 5),
    ("sausio pirmoji", 2018, 1, 1),
    ("lapkričio dešimtoji", 2017, 11, 10),
    ("gruodžio dvidešimtoji", 2017, 12, 20),
    ("vasario šešioliktoji", 2018, 2, 16),
])
def test_spelled_ordinal_day(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", ["liepos penktoji", "sausio pirmoji"])
def test_spelled_ordinal_day_is_one_day_wide(text):
    s = span(text)
    assert (s.end - s.start).days == 1


@pytest.mark.parametrize("text,y,m,d", [
    ("gruodžio dvidešimt penktoji", 2017, 12, 25),
    ("gruodžio trisdešimt pirmoji", 2017, 12, 31),
    ("liepos dvidešimt trečioji", 2017, 7, 23),
])
def test_compound_day_keeps_its_tens(text, y, m, d):
    """The tens element must survive: answering the fifth when the speaker
    said the twenty-fifth is the silent-wrong this table exists to prevent."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,m", [
    ("gruodžio", 12), ("gegužės", 5), ("sausio", 1), ("rugpjūčio", 8),
])
def test_bare_month_is_the_whole_month(text, m):
    s = span(text)
    assert s.start.month == m and s.start.day == 1
    assert (s.end - s.start).days >= 28


@pytest.mark.parametrize("text,m", [
    ("gruodis", 12), ("gegužė", 5), ("sausis", 1),
])
def test_nominative_month_also_binds(text, m):
    """CLDR ships the nominative as the stand-alone month name; both forms
    name the same month."""
    assert span(text).start.month == m


@pytest.mark.parametrize("text", [
    "penktoji", "dvidešimt penktoji", "asdf qwerty", "",
])
def test_no_date_without_a_month(text):
    """An ordinal with nothing to attach to, and outright garbage, must fail
    honestly rather than inventing a day."""
    nomatch(text)


@pytest.mark.parametrize("text,y", [("1990 m.", 1990), ("2019", 2019)])
def test_year_reference(text, y):
    s = span(text)
    assert s.start == AstroDate(y, 1, 1) and s.end == AstroDate(y + 1, 1, 1)


def test_year_word_is_consumed():
    assert remainder("1990 m.") == ""
