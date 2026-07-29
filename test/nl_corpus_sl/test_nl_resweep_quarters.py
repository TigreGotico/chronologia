# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: calendar quarters via ``kvartal`` (sl), fresh area.

``prvi/drugi/tretji/četrti kvartal <year>`` names a 3-month calendar quarter:
Q1=[Y-01-01,Y-04-01), Q2=[Y-04-01,Y-07-01), Q3=[Y-07-01,Y-10-01),
Q4=[Y-10-01,(Y+1)-01-01).  Verified live: the ``kvartal`` wording resolves
correctly for all four ordinals; the alternate ``četrtletje`` wording does
not (it strands the ordinal+noun as residue and returns the whole year --
left uncovered here per instructions to drop uncertain/broken idioms rather
than mis-gold them).  Gold is fixed month arithmetic.  Anchor: Tuesday
2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, start_end

_ORD = {'prvi': 1, 'drugi': 2, 'tretji': 3, 'četrti': 4}
_YEARS = [
    1897, 1912, 1931, 1948, 1959, 1966, 1974, 1983, 1992, 2003,
    2009, 2014, 2021, 2027, 2034, 2041, 2053, 2066, 2079, 2093,
]


def _bounds(y, q):
    sm = 1 + 3 * (q - 1)
    if q == 4:
        return AstroDate(y, sm, 1), AstroDate(y + 1, 1, 1)
    return AstroDate(y, sm, 1), AstroDate(y, sm + 3, 1)


_CASES = [
    (f"{ordw} kvartal {y}", y, q)
    for y in _YEARS for (ordw, q) in _ORD.items()
]


@pytest.mark.parametrize("text,y,q", _CASES)
def test_quarter_kvartal(text, y, q):
    lo, hi = _bounds(y, q)
    assert start_end(text) == (lo, hi)
