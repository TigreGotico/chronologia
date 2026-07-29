# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: calendar quarters ("el N trimestre de <year>" and
"QN <year>") across a wider year matrix than ``test_nl_quarter.py`` pins.

Quarter N spans months [3N-2 .. 3N] of the given year; gold is pure integer
arithmetic on the year/month, never touching the parser. Years are chosen to
avoid the exact strings already covered (Q3 2026, Q1 2020, trimestre-de-2020/
2018 spot cases).
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_ORD = [("primer", 1), ("segundo", 2), ("tercer", 3), ("cuarto", 4)]
_YEARS = [1999, 2005, 2010, 2015, 2019, 2022, 2028, 2033, 2040, 2045, 2050]


def _edges(y, n):
    sm = 3 * n - 2
    if sm == 10:
        return (y, 10), (y + 1, 1)
    return (y, sm), (y, sm + 3)


def _worded_cases():
    out = []
    for ow, n in _ORD:
        for y in _YEARS:
            (sy, sm), (ey, em) = _edges(y, n)
            out.append((f"el {ow} trimestre de {y}", sy, sm, ey, em))
    return out


def _q_cases():
    out = []
    for n in (1, 2, 3, 4):
        for y in _YEARS:
            (sy, sm), (ey, em) = _edges(y, n)
            out.append((f"Q{n} {y}", sy, sm, ey, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _worded_cases())
def test_worded_quarter_with_year(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), f"{text!r} start {s}"
    assert e == AstroDate(ey, em, 1), f"{text!r} end {e}"


@pytest.mark.parametrize("text,sy,sm,ey,em", _q_cases())
def test_q_letter_with_year(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), f"{text!r} start {s}"
    assert e == AstroDate(ey, em, 1), f"{text!r} end {e}"
