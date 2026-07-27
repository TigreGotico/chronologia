"""Buddhist Era vocab + era-anchored year narrowed by a calendar month.

Two verified silent-wrongs:

1. the Buddhist Era ("Buddhist Era 2560", "2560 BE") was defined in the era
   registry (BE == CE + 543) but no English surface routed to it, so the BE
   number was read literally as a Gregorian year and the era name stranded;

2. an era-anchored year that already resolved correctly (a Japanese nengo
   like "Reiwa 2" -> 2020, or a Buddhist-Era year) could not be narrowed by
   an adjacent calendar month ("Reiwa 2 May"): the month stranded and the
   span stayed the whole year.

Reference values are independent of the parser -- BE years come from
:func:`chronologia.resolve_era`, month spans from hand arithmetic.
"""
import pytest

from chronologia import resolve_era

from ._corpus import ANCHOR, AstroDate, parse, span, start_end


# -- Buddhist Era: BE == CE + 543, epoch-correct + name consumed ----------
@pytest.mark.parametrize("text, value", [
    ("Buddhist Era 2560", 2560),
    ("2560 BE", 2560),
    ("in the Buddhist Era 2560", 2560),
    ("2483 BE", 2483),          # 1940
    ("Buddhist Era 2500", 2500),
])
def test_buddhist_era_resolves_through_epoch(text, value):
    s = span(text)
    expected = resolve_era("buddhist", value)
    assert s.start.year == expected.year
    assert s.start == AstroDate(expected.year, 1, 1)
    assert parse(text)[1] == ""          # era name fully consumed


def test_buddhist_2560_is_2017():
    s, e = start_end("Buddhist Era 2560")
    assert s == AstroDate(2017, 1, 1)
    assert e == AstroDate(2018, 1, 1)


# -- era-anchored year narrowed by an adjacent named month ----------------
@pytest.mark.parametrize("text, year, month", [
    ("Reiwa 2 May", 2020, 5),
    ("Showa 63 May", 1988, 5),
    ("Buddhist Era 2560 May", 2017, 5),
    ("2560 BE May", 2017, 5),
    ("Reiwa 2 March", 2020, 3),
])
def test_era_year_narrowed_by_month(text, year, month):
    s, e = start_end(text)
    assert s == AstroDate(year, month, 1)
    nyear, nmonth = (year + 1, 1) if month == 12 else (year, month + 1)
    assert e == AstroDate(nyear, nmonth, 1)
    assert parse(text)[1] == ""          # month fully consumed


# -- regression: bare era-years keep their whole-year span ----------------
@pytest.mark.parametrize("text, year", [
    ("Reiwa 2", 2020),
    ("Showa 63", 1988),
])
def test_bare_era_year_stays_whole_year(text, year):
    s, e = start_end(text)
    assert s == AstroDate(year, 1, 1)
    assert e == AstroDate(year + 1, 1, 1)


@pytest.mark.parametrize("text, year", [
    ("100 AD", 100), ("500 CE", 500),
])
def test_plain_ad_era_years_unchanged(text, year):
    assert start_end(text)[0] == AstroDate(year, 1, 1)


def test_bce_year_unchanged():
    # BC years correctly have start_datetime=None but a valid .start AstroDate
    assert start_end("500 BCE")[0] == AstroDate(1 - 500, 1, 1)
