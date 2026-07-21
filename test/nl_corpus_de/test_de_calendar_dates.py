"""German calendar dates -- the ORDINAL-DOT convention ("3. Oktober",
"15. März 2019") the tokenizer strips (ordinal_dot=true), day-month-year
order (dmy), bare month/year spans, and the prefer_future roll for a bare
calendar date already past the anchor.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, start, start_end, span, nomatch, AstroDate


# -- full date "D. Month YYYY" -- ordinal dot, day-first ------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15. märz 2019", 2019, 3, 15), ("1. januar 2000", 2000, 1, 1),
    ("3. oktober 2020", 2020, 10, 3), ("31. dezember 1999", 1999, 12, 31),
    ("29. februar 2020", 2020, 2, 29), ("6. juni 1944", 1944, 6, 6),
    ("9. november 1989", 1989, 11, 9), ("8. mai 1945", 1945, 5, 8),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


# -- bare day+month rolls to the future (anchor 2017-06-27) ---------------

@pytest.mark.parametrize("text,y,m,d", [
    ("24. dezember", 2017, 12, 24),   # later in 2017
    ("3. oktober", 2017, 10, 3),
    ("1. januar", 2018, 1, 1),        # already past -> next year
    ("15. märz", 2018, 3, 15),        # already past -> next year
])
def test_bare_day_month_prefers_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


# -- bare month is a month-wide span --------------------------------------

@pytest.mark.parametrize("text,y,m", [
    ("oktober 2020", 2020, 10), ("märz 1999", 1999, 3),
    ("dezember 2001", 2001, 12), ("juli 2017", 2017, 7),
])
def test_month_year(text, y, m):
    s = span(text)
    assert s.start == AstroDate(y, m, 1)
    assert (s.end.year, s.end.month) == ((y + 1, 1) if m == 12 else (y, m + 1))


# -- ISO date -------------------------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("2019-03-15", 2019, 3, 15), ("2000-01-01", 2000, 1, 1),
    ("1999-12-31", 1999, 12, 31),
])
def test_iso(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


# -- bare year ------------------------------------------------------------

@pytest.mark.parametrize("text,y", [
    ("1969", 1969), ("im jahr 1969", 1969), ("das jahr 2000", 2000),
])
def test_year(text, y):
    assert start(text) == AstroDate(y, 1, 1)


# -- adversarial: impossible calendar dates never fabricate ---------------

@pytest.mark.parametrize("text", ["30. februar 2019", "31. april 2020",
                                  "0. januar 2020"])
def test_impossible_date(text):
    from ._corpus import parse
    res = parse(text)
    if res is not None:
        s = res[0].start
        # never rolls silently into the next month
        assert not (s.month == 3 and "februar" in text)
