"""Occitan eras, deep time, ranges and the scoped century."""
import pytest

from ._corpus import span, start, start_end, AstroDate

_BP = 1950


@pytest.mark.parametrize("text,year", [
    ("44 abans jèsus-crist", -43),
    ("753 abans jèsus-crist", -752),
    ("2020 aprèp jèsus-crist", 2020),
])
def test_era_year(text, year):
    assert start(text).year == year


def test_bc_year_wide():
    s = span("44 abans jèsus-crist")
    assert s.end.year - s.start.year == 1


@pytest.mark.parametrize("text,years_ago", [
    ("fa 66 milions d'ans", 66_000_000),
    ("fa 4 miliards d'ans", 4_000_000_000),
])
def test_deep_time(text, years_ago):
    assert start(text).year == _BP - years_ago


def test_year_reference():
    assert start("l'an 2000").year == 2000


@pytest.mark.parametrize("text,s,e", [
    ("de junh a agost", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("del 5 julhet al 8 agost", AstroDate(2017, 7, 5), AstroDate(2017, 8, 9)),
    ("entre julhet e setembre", AstroDate(2017, 7, 1), AstroDate(2017, 10, 1)),
])
def test_range(text, s, e):
    assert start_end(text) == (s, e)


def test_century_span():
    assert start_end("lo 20en sègle") == (
        AstroDate(1900, 1, 1), AstroDate(2000, 1, 1))
