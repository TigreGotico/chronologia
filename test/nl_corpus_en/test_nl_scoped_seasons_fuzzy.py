"""Wave 1 -- scoped ordinals, seasons, centuries/millennia, and the fuzzy
edges (early/mid/late, decades, halves).

Scoped ordinals select the Nth unit inside a named scope (weeks resolve to
their Monday).  Seasons are meteorological and three months wide.  Absolute
periods follow the calendar convention baked into the reckoning core (the
21st century is 2000-2100).  The genuinely-fuzzy phrasings that need new
constructions are xfail'd.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, start, start_end, span, nomatch


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


# -- Nth week of a month (Monday-aligned) ---------------------------------

@pytest.mark.parametrize("text,iso", [
    ("the first week of june", "2017-6-5"),
    ("the second week of june", "2017-6-12"),
    ("the third week of june", "2017-6-19"),
    ("the fourth week of june", "2017-6-26"),
    ("the first week of july", "2017-7-3"),
    ("the second week of december", "2017-12-11"),
    ("the first week of january", "2017-1-2"),
    ("the third week of march", "2017-3-20"),
    ("the fourth week of september", "2017-9-25"),
    ("the second week of may", "2017-5-8"),
])
def test_week_of_month(text, iso):
    assert start(text) == _d(iso)
    assert span(text).width == timedelta(days=7)


# -- last day / Nth day scoped --------------------------------------------

@pytest.mark.parametrize("text,iso", [
    ("the last day of june", "2017-6-30"),
    ("the last day of february 2024", "2024-2-29"),
    ("the last day of february 2023", "2023-2-28"),
    ("the last day of december 2020", "2020-12-31"),
    ("the first day of july", "2017-7-1"),
    ("the 100th day of the year", "2017-4-10"),
    ("the last day of the year", "2017-12-31"),
])
def test_scoped_day(text, iso):
    assert start(text) == _d(iso)


# -- month-of-year / week-of-year -----------------------------------------

@pytest.mark.parametrize("text,iso", [
    ("the second month of the year", "2017-2-1"),
    ("the first month of the year", "2017-1-1"),
    ("the last month of the year", "2017-12-1"),
    ("the second week of the year", "2017-1-9"),
    ("the last week of december 2024", "2024-12-30"),
])
def test_scoped_month_week(text, iso):
    assert start(text) == _d(iso)


# -- absolute periods: century / millennium -------------------------------

@pytest.mark.parametrize("text,s,e", [
    ("the 21st century", "2000-1-1", "2100-1-1"),
    ("the 20th century", "1900-1-1", "2000-1-1"),
    ("the 19th century", "1800-1-1", "1900-1-1"),
    ("the 18th century", "1700-1-1", "1800-1-1"),
    ("the 17th century", "1600-1-1", "1700-1-1"),
    ("the 5th century", "400-1-1", "500-1-1"),
    ("the first century", "1-1-1", "101-1-1"),
    ("the third millennium", "2000-1-1", "3000-1-1"),
    ("the second millennium", "1000-1-1", "2000-1-1"),
])
def test_absolute_period(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- nested scoped: Nth decade of the Nth century -------------------------

@pytest.mark.parametrize("text,s", [
    ("the first decade of the 21st century", "2000-1-1"),
    ("the second decade of the 21st century", "2010-1-1"),
    ("the tenth decade of the 20th century", "1990-1-1"),
])
def test_nested_scoped(text, s):
    assert start(text) == _d(s)


@pytest.mark.parametrize("text,s", [
    ("the last decade of the 20th century", "1990-1-1"),
    ("the last decade of the 19th century", "1890-1-1"),
    ("the last century of the 2nd millennium", "1900-1-1"),
])
def test_nested_scoped_last(text, s):
    assert start(text) == _d(s)


# -- seasons: of YYYY, next/last/this, bare (3 months wide) ---------------

@pytest.mark.parametrize("text,s", [
    ("summer of 1969", "1969-6-1"), ("summer 1969", "1969-6-1"),
    ("winter of 2020", "2020-12-1"), ("spring of 2000", "2000-3-1"),
    ("fall of 1929", "1929-9-1"), ("autumn of 1929", "1929-9-1"),
    ("this spring", "2017-3-1"), ("spring", "2017-3-1"),
    ("next winter", "2017-12-1"), ("last winter", "2016-12-1"),
    ("next spring", "2018-3-1"), ("last spring", "2017-3-1"),
    ("this summer", "2017-6-1"), ("next summer", "2018-6-1"),
    ("summer of 2000", "2000-6-1"), ("winter of 1999", "1999-12-1"),
    ("spring of 1945", "1945-3-1"), ("fall of 2008", "2008-9-1"),
    ("autumn of 2008", "2008-9-1"), ("summer of 1776", "1776-6-1"),
])
def test_season(text, s):
    ss = start(text)
    assert ss == _d(s)
    assert span(text).width.days >= 89        # ~3 months


# -- fuzzy edges: new constructions, deferred -----------------------------

# -- fuzzy month thirds (early/mid/late <month>) --------------------------

@pytest.mark.parametrize("text,ymd,maxdays", [
    ("early june", (2017, 6, 1), 11),
    ("mid june", (2017, 6, 11), 11),
    # 31-day months slice into fractional-day thirds; the date still lands
    ("late december", (2017, 12, 21), 11),
    ("early january", (2017, 1, 1), 11),
])
def test_early_june(text, ymd, maxdays):
    s = start(text)
    assert (s.year, s.month, s.day) == ymd
    assert span(text).width.days <= maxdays


# -- decades: spoken, digit, bare-tens (nearest-past century) -------------

@pytest.mark.parametrize("text,s,e", [
    ("the nineties", 1990, 2000), ("the 1990s", 1990, 2000),
    ("the 90s", 1990, 2000), ("the 2020s", 2020, 2030),
    ("the eighties", 1980, 1990), ("1970s", 1970, 1980),
    ("the sixties", 1960, 1970), ("the 80s", 1980, 1990),
    # nearest-past: in 2017, "the twenties" is 1920 (2020 is future)
    ("the twenties", 1920, 1930), ("the thirties", 1930, 1940),
])
def test_decade(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s, 1, 1) and ee == AstroDate(e, 1, 1)


# fuzzy thirds of a ten-year decade (10/3 yr each, via chronologia subdivide)
@pytest.mark.parametrize("text,s,e", [
    ("early 1980s", 1980, 1983), ("mid 1980s", 1983, 1986),
    ("late 2020s", 2026, 2030), ("the early nineties", 1990, 1993),
])
def test_decade_fuzzy(text, s, e):
    ss, ee = start_end(text)
    assert ss.year == s and ee.year == e


def test_late_2020s():
    assert start("late 2020s").year >= 2026


# adversarial: a decade word in idiom is still a decade span, and a lone
# small integer with an 's' that is not a decade must not become one.
def test_decade_adversarial():
    from ._corpus import parse
    assert start("the nineties called").year == 1990   # remainder 'called'
    assert parse("3s") is None                          # not a decade


# -- calendar halves of a year / decade / century / millennium ------------

@pytest.mark.parametrize("text,s,e", [
    ("the first half of 2025", AstroDate(2025, 1, 1), AstroDate(2025, 7, 1)),
    ("the second half of 2025", AstroDate(2025, 7, 1), AstroDate(2026, 1, 1)),
    ("the first half of 1999", AstroDate(1999, 1, 1), AstroDate(1999, 7, 1)),
    # scope-word targets resolve the current period from the anchor (2017)
    ("the second half of the century", AstroDate(2050, 1, 1), AstroDate(2100, 1, 1)),
    ("the first half of the decade", AstroDate(2010, 1, 1), AstroDate(2015, 1, 1)),
    ("the first half of the millennium", AstroDate(2000, 1, 1), AstroDate(2500, 1, 1)),
])
def test_half_period(text, s, e):
    ss, ee = start_end(text)
    assert ss == s and ee == e
