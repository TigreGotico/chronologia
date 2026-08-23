"""Welsh calendar dates, in the digit, suffixed-digit and spelled-day forms.

A written date runs day-month-year.  The day may be a bare digit ("5 Mehefin
2027"), a digit with its ordinal suffix written solid and the month introduced
by "o" ("y 3ydd o Orffennaf 1969"), or a spelled ordinal ("y trydydd o
Orffennaf").  "o" soft-mutates the month it introduces, so July appears as
"Orffennaf" and December as "Ragfyr" -- the surface running Welsh actually
carries.

Expected values are plain calendar facts about the corpus anchor, never the
parser's own output.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import nomatch, remainder, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ("1 Mawrth 1990", 1990, 3, 1),
    ("25 Rhagfyr 2020", 2020, 12, 25),
    ("16 Chwefror 1918", 1918, 2, 16),
    ("1 Mai 2004", 2004, 5, 1),
    ("5 Medi 2009", 2009, 9, 5),
    ("19 Awst 1911", 1911, 8, 19),
])
def test_bare_day_month_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("y 3ydd o Orffennaf 1969", 1969, 7, 3),
    ("yr 11eg o Orffennaf 1923", 1923, 7, 11),
    ("y 9fed o Ragfyr 1953", 1953, 12, 9),
    ("yr 8fed o Chwefror 1839", 1839, 2, 8),
    ("y 6ed o Chwefror 1958", 1958, 2, 6),
    ("y 22ain o Hydref 1825", 1825, 10, 22),
    ("y 1af o Fedi 1969", 1969, 9, 1),
    ("y 20fed o Ebrill 1964", 1964, 4, 20),
])
def test_suffixed_digit_day_with_the_linking_o(text, y, m, d):
    """The ordinal suffix is written solid onto the digit ("3ydd"); the
    tokenizer shears it and the fold glues it back."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text", [
    "y 3ydd o Orffennaf 1969", "25 Rhagfyr 2020", "1 Mawrth 1990",
])
def test_full_date_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,y,m,d", [
    ("y cyntaf o Fawrth 1990", 1990, 3, 1),
    ("y trydydd o Orffennaf 1969", 1969, 7, 3),
    ("y pumed o Fedi 2009", 2009, 9, 5),
    ("y degfed o Ionawr 1900", 1900, 1, 10),
    ("yr unfed ar ddeg o Orffennaf 1923", 1923, 7, 11),
    ("y pymthegfed o Awst 1950", 1950, 8, 15),
    ("y deunawfed o Fai 1970", 1970, 5, 18),
    ("yr ugeinfed o Ebrill 1964", 1964, 4, 20),
    ("y pumed ar hugain o Ragfyr 2020", 2020, 12, 25),
    ("yr unfed ar ddeg ar hugain o Ionawr 1999", 1999, 1, 31),
])
def test_spelled_ordinal_day(text, y, m, d):
    """The ordinal series compounds on the vigesimal frames exactly as the
    cardinals do: 11th is "one-on-ten", 31st "one-on-ten-on-twenty"."""
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 Gorffennaf", 2017, 7, 5),
    ("24 Rhagfyr", 2017, 12, 24),
    ("1 Mawrth", 2018, 3, 1),
    ("5 Mehefin", 2018, 6, 5),
    ("y 3ydd o Orffennaf", 2017, 7, 3),
])
def test_day_month_without_year_resolves_forward(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m", [
    ("Gorffennaf", 2017, 7), ("Ionawr", 2017, 1), ("Mehefin", 2017, 6),
    ("Rhagfyr", 2017, 12),
])
def test_bare_month_is_the_whole_month(text, y, m):
    """A month named on its own is that month of the anchor's own year --
    unlike a day-and-month, which resolves forward."""
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, m, 1)


@pytest.mark.parametrize("text,y,m", [
    ("Ionawr 2030", 2030, 1), ("Rhagfyr 1999", 1999, 12),
    ("Mehefin 2027", 2027, 6),
])
def test_month_and_year(text, y, m):
    s = span(text)
    assert (s.start.year, s.start.month) == (y, m)


@pytest.mark.parametrize("text,y", [
    ("1990", 1990), ("2027", 2027), ("1969", 1969),
])
def test_bare_year(text, y):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, 1, 1)


@pytest.mark.parametrize("text", ["999", "42", "7"])
def test_short_digit_run_is_not_a_year(text):
    """A year needs four digits here, so a small number stays a number."""
    nomatch(text)
