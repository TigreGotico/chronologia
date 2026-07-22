"""Asturian eras, deep time, ranges and the scoped century."""
import pytest

from ._corpus import span, start, start_end, AstroDate

_BP = 1950


@pytest.mark.parametrize("text,year", [
    ("44 enantes de cristu", -43),
    ("753 enantes de cristu", -752),
    ("2020 dempués de cristu", 2020),
])
def test_era_year(text, year):
    assert start(text).year == year


def test_bc_year_wide():
    s = span("44 enantes de cristu")
    assert s.end.year - s.start.year == 1


@pytest.mark.parametrize("text,years_ago", [
    ("fai 66 millones d'años", 66_000_000),
    ("fai 4 millardos d'años", 4_000_000_000),
])
def test_deep_time(text, years_ago):
    assert start(text).year == _BP - years_ago


def test_year_reference():
    assert start("nel añu 2000").year == 2000


@pytest.mark.parametrize("text,s,e", [
    ("de xunu a agostu", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("dende xunu a agostu", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("ente xunetu y setiembre", AstroDate(2017, 7, 1), AstroDate(2017, 10, 1)),
])
def test_range(text, s, e):
    assert start_end(text) == (s, e)


def test_century_span():
    assert start_end("el 20 sieglu") == (
        AstroDate(1900, 1, 1), AstroDate(2000, 1, 1))
