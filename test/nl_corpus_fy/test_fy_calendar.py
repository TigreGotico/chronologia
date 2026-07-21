"""fy: calendar dates, bare month/year, ISO, prefer-future roll."""
from datetime import timedelta

import pytest

from ._corpus import start, start_end, span, nomatch, AstroDate


@pytest.mark.parametrize("text,y,m,d", [('5 juny 2018', 2018, 6, 5), ('1 jannewaris 2000', 2000, 1, 1), ('3 oktober 2020', 2020, 10, 3), ('31 desimber 1999', 1999, 12, 31), ('29 febrewaris 2020', 2020, 2, 29), ('6 juny 1944', 1944, 6, 6), ('9 novimber 1989', 1989, 11, 9), ('8 maaie 1945', 1945, 5, 8)])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [('24 desimber', 2017, 12, 24), ('3 oktober', 2017, 10, 3), ('1 jannewaris', 2018, 1, 1), ('15 maart', 2018, 3, 15)])
def test_bare_day_month_prefers_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m", [('oktober 2020', 2020, 10), ('maart 1999', 1999, 3), ('desimber 2001', 2001, 12), ('july 2017', 2017, 7)])
def test_month_year(text, y, m):
    s = span(text)
    assert s.start == AstroDate(y, m, 1)
    assert (s.end.year, s.end.month) == ((y + 1, 1) if m == 12 else (y, m + 1))


@pytest.mark.parametrize("text,y,m,d", [
    ("2019-03-15", 2019, 3, 15), ("2000-01-01", 2000, 1, 1),
    ("1999-12-31", 1999, 12, 31),
])
def test_iso(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y", [('1969', 1969), ('it jier 1969', 1969), ('it jier 2000', 2000)])
def test_year(text, y):
    assert start(text) == AstroDate(y, 1, 1)
