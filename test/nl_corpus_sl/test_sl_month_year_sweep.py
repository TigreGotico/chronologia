# -*- coding: utf-8 -*-
"""Bare month + year sweep (sl): whole calendar month.

``marca 2020`` (genitive) and ``marec 2020`` (nominative) both name the whole
month: ``[Y-M-1 00:00, Y-(M+1)-1 00:00)``.  Gold is calendar arithmetic (first
of the month to first of the following month), computed here.  Anchor:
Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, start_end

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}
NOM = {
    1: 'januar', 2: 'februar', 3: 'marec', 4: 'april', 5: 'maj', 6: 'junij',
    7: 'julij', 8: 'avgust', 9: 'september', 10: 'oktober', 11: 'november',
    12: 'december',
}


def _bounds(y, m):
    ey, em = (y + 1, 1) if m == 12 else (y, m + 1)
    return AstroDate(y, m, 1), AstroDate(ey, em, 1)


_GEN_YEARS = [1888, 1950, 2001, 2019, 2044, 2100]
_GEN_CASES = [
    (f"{GEN[m]} {y}", y, m) for y in _GEN_YEARS for m in range(1, 13)
]

_NOM_YEARS = [1975, 2020, 2088]
_NOM_CASES = [
    (f"{NOM[m]} {y}", y, m) for y in _NOM_YEARS for m in range(1, 13)
]


@pytest.mark.parametrize("text,y,m", _GEN_CASES)
def test_month_year_genitive(text, y, m):
    assert start_end(text) == _bounds(y, m)


@pytest.mark.parametrize("text,y,m", _NOM_CASES)
def test_month_year_nominative(text, y, m):
    assert start_end(text) == _bounds(y, m)
