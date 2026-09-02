"""Armenian calendar dates, month names and years.

A spelled month leads the day in the genitive form CLDR gives as the format
name (``հունիսի 5``); the stand-alone nominative (``հունիս``) names the whole
month.  Numeric dates run day-month-year with dots, and a year may carry the
trailing ``թ.``, the abbreviation of ``թվական``, which also lets the whole
date be written year-first the way CLDR's full pattern does.
"""
import pytest

from ._corpus import ANCHOR, parse, span, start


def _ymd(text, anchor=ANCHOR):
    s = start(text, anchor)
    return s.year, s.month, s.day


@pytest.mark.parametrize("text", ["05.06.2019", "5.6.2019"])
def test_numeric_date_is_day_month_year(text):
    assert _ymd(text) == (2019, 6, 5)


@pytest.mark.parametrize("text,expected", [
    ("հունիսի 5 2019", (2019, 6, 5)),
    ("5 հունիսի 2019", (2019, 6, 5)),
    ("2019 թ. հունիսի 5", (2019, 6, 5)),
    ("հնվ 5 2020", (2020, 1, 5)),
    ("5 հնվ 2020", (2020, 1, 5)),
])
def test_spelled_date(text, expected):
    assert _ymd(text) == expected


@pytest.mark.parametrize("nominative,genitive,number", [
    ("հունվար", "հունվարի", 1),
    ("փետրվար", "փետրվարի", 2),
    ("մարտ", "մարտի", 3),
    ("ապրիլ", "ապրիլի", 4),
    ("մայիս", "մայիսի", 5),
    ("հունիս", "հունիսի", 6),
    ("հուլիս", "հուլիսի", 7),
    ("օգոստոս", "օգոստոսի", 8),
    ("սեպտեմբեր", "սեպտեմբերի", 9),
    ("հոկտեմբեր", "հոկտեմբերի", 10),
    ("նոյեմբեր", "նոյեմբերի", 11),
    ("դեկտեմբեր", "դեկտեմբերի", 12),
])
def test_both_month_forms_name_the_same_month(nominative, genitive, number):
    """The date construction reads the genitive; the bare nominative names the
    month itself.  Both must land on the same month number."""
    assert start(f"{nominative} 12 2020").month == number
    assert start(f"{genitive} 12 2020").month == number


@pytest.mark.parametrize("text,year", [
    ("2019 թ.", 2019), ("1990 թ.", 1990), ("2019", 2019),
])
def test_year_reference(text, year):
    s, e = span(text).start, span(text).end
    assert (s.year, s.month, s.day) == (year, 1, 1)
    assert (e.year, e.month, e.day) == (year + 1, 1, 1)


def test_a_bare_two_digit_number_is_not_a_year():
    """The guard keeps a short numeral out of the year slot, so a stray count
    never silently becomes a date."""
    r = parse("19")
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text,month", [
    ("գարուն", 3), ("գարնանը", 3),
    ("ամառ", 6), ("ամառը", 6),
    ("աշուն", 9), ("աշնանը", 9),
    ("ձմեռ", 12), ("ձմեռը", 12),
])
def test_seasons_bare_and_definite(text, month):
    """The definite article is a suffix, so a season noun is met both bare and
    suffixed; the northern hemisphere convention places spring in March."""
    assert start(text).month == month


@pytest.mark.parametrize("text,expected", [
    ("2026 թվականի մարտի 15", (2026, 3, 15)),
    ("1957 թվականի մարտի 22", (1957, 3, 22)),
    ("2019 թվականի հունիսի 5", (2019, 6, 5)),
])
def test_the_year_leads_the_date_with_the_full_word(text, expected):
    """The year-first date spells թվական in the genitive before the month, the
    shape Armenian prose actually uses -- "Ընդունվել է 1957 թվականի մարտի
    22-ին։"  The whole phrase is the date, so nothing is left over."""
    assert _ymd(text) == expected
    assert parse(text)[1] == ""


def test_the_year_first_date_is_not_read_as_a_bare_year():
    r = parse("2026 թվականի մարտի 15")
    assert (r[0].end - r[0].start).days == 1
