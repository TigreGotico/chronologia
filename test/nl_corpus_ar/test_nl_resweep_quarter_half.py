# -*- coding: utf-8 -*-
"""Second-pass oracle re-sweep: quarters (ar) and calendar halves (ar) over a
fresh set of years disjoint from ``test_nl_quarter`` (2017, 2026, 2020) and
``test_nl_half_period`` (2020).  Quarter N spans months [3N-2 .. 3N] of the
given year (``الربع N YEAR``); halves split at July 1
(``النصف الأول/الثاني من YEAR``).  Gold by independent arithmetic."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end

YEARS = (1965, 1979, 1988, 1996, 2005, 2013, 2027, 2038)


def _quarter_cases():
    out = []
    for y in YEARS:
        for q in (1, 2, 3, 4):
            sm = 3 * q - 2
            ey, em = (y + 1, 1) if q == 4 else (y, sm + 3)
            out.append((f"الربع {q} {y}", y, sm, ey, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _quarter_cases())
def test_quarter_resweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


def _half_cases():
    out = []
    for y in YEARS:
        out.append((f"النصف الأول من {y}", y, 1, y, 7))
        out.append((f"النصف الثاني من {y}", y, 7, y + 1, 1))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _half_cases())
def test_half_period_resweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)
