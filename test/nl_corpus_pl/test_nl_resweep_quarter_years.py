# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: calendar quarters (pl), swept across many fresh
years in both digit surface forms -- "N kwartał YEAR" and "QN YEAR" -- to
extend the small hand-picked list in ``test_nl_quarter.py`` (which only
touches 2018/2019/2020/2026). Quarter N spans months [3N-2 .. 3N]; every
expected boundary is pure calendar arithmetic, never read back from the
parser.

Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import parse, start_end

#: fresh years -- disjoint from the hand-picked 2018/2019/2020/2026 cases.
_YEARS = (2011, 2013, 2014, 2015, 2016, 2022, 2023, 2025, 2028, 2031, 2033)


def _bounds(year, q):
    sm = 3 * q - 2
    if sm > 10:  # unreachable, q in 1..4
        raise ValueError
    ey, em = (year, sm + 3) if sm + 3 <= 12 else (year + 1, sm + 3 - 12)
    return year, sm, ey, em


def _cases():
    out = []
    for y in _YEARS:
        for q in range(1, 5):
            sy, sm, ey, em = _bounds(y, q)
            out.append((f"{q} kwartał {y}", sy, sm, ey, em))
            out.append((f"Q{q} {y}", sy, sm, ey, em))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES, ids=[c[0] for c in _CASES])
def test_quarter_resweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES[::7], ids=[c[0] for c in _CASES[::7]])
def test_quarter_resweep_no_residual(text, sy, sm, ey, em):
    assert parse(text)[1] == ""
