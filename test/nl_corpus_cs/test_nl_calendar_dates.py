"""Czech calendar dates: day-month-year order, ordinal-dot day, genitive
month name ("15. srpna 2020").  A bare day+month with no year rolls to the
next occurrence (prefer_future) against the 2017-06-27 anchor.
"""
import pytest

from ._corpus import AstroDate, span, start, start_end, parse


# -- full DMY dates with a year (day-wide) -------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15. srpna 2020", 2020, 8, 15),
    ("1. ledna 2000", 2000, 1, 1),
    ("10. dubna 2019", 2019, 4, 10),
    ("29. února 2020", 2020, 2, 29),
    ("31. prosince 1999", 1999, 12, 31),
    ("3. ledna 2020", 2020, 1, 3),
    ("5. června 2027", 2027, 6, 5),
    ("24. prosince 2021", 2021, 12, 24),
    ("28. října 1918", 1918, 10, 28),
    ("17. listopadu 1989", 1989, 11, 17),
])
def test_full_date(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e == AstroDate(y, m, d + 1) if d < 28 else e > s


def test_full_date_is_day_wide():
    from datetime import timedelta
    assert span("15. srpna 2020").width == timedelta(days=1)


# -- day + month, no year -> next occurrence (prefer_future) -------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15. srpna", 2017, 8, 15),     # still ahead in 2017
    ("10. dubna", 2018, 4, 10),     # April already past -> 2018
    ("1. ledna", 2018, 1, 1),
    ("5. července", 2017, 7, 5),
])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


# -- bare month + year is month-wide -------------------------------------

def test_month_year_is_month_wide():
    from datetime import timedelta
    s, e = start_end("srpen 2020")
    assert s == AstroDate(2020, 8, 1)
    assert (e.year, e.month) == (2020, 9)


# -- ISO literal ---------------------------------------------------------

def test_iso_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


# -- bare year -----------------------------------------------------------

@pytest.mark.parametrize("text,y", [("2019", 2019), ("1989", 1989),
                                    ("v roce 2000", 2000)])
def test_year(text, y):
    assert start(text) == AstroDate(y, 1, 1)


# adversarial: a 3-digit run is not a bare year (guard)
def test_three_digit_not_a_year():
    r = parse("999")
    assert r is None or r[0].start.year != 999
