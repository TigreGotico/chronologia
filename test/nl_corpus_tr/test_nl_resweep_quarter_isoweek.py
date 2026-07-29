# -*- coding: utf-8 -*-
"""RESWEEP: Turkish calendar quarters and ISO-8601 weeks, fresh year/index
grid disjoint from ``test_nl_quarter.py`` and ``test_nl_iso_week.py``.

Quarter N spans months [3N-2 .. 3N], both digit ("3. çeyrek") and spelled
ordinal ("üçüncü çeyrek") forms fold to the same number. ISO weeks are
Monday-based per the standard; "hafta N YYYY" pins both the week and the
ISO year. Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

_ORDINAL = {1: "birinci", 2: "ikinci", 3: "üçüncü", 4: "dördüncü"}

# Fresh years, disjoint from test_nl_quarter.py's {2026, 2020, 2018}.
_Q_YEARS = [1930, 1955, 1972, 1988, 2003, 2013, 2032, 2044]


def _quarter_cases():
    out = []
    for y in _Q_YEARS:
        for n in (1, 2, 3, 4):
            out.append((f"{n}. çeyrek {y}", y, n))
            out.append((f"{_ORDINAL[n]} çeyrek {y}", y, n))
    return out


@pytest.mark.parametrize("text,y,n", _quarter_cases())
def test_quarter_resweep(text, y, n):
    s, e = start_end(text, A)
    sm = 3 * n - 2
    assert s == AstroDate(y, sm, 1)
    em_y, em_m = (y + 1, 1) if sm + 3 > 12 else (y, sm + 3)
    assert e == AstroDate(em_y, em_m, 1)


# Fresh (iso-year, week) pairs, disjoint from test_nl_iso_week.py's
# [(2017,32),(2017,1),(2017,26),(2017,52),(2026,32),(2026,1),(2020,53),
#  (1999,10),(2024,40),(2030,7)].
_ISO_CASES = [
    (1985, 5), (1985, 44), (1996, 20), (2001, 12), (2001, 51),
    (2008, 18), (2011, 30), (2011, 48), (2015, 3), (2033, 22),
    (2033, 45), (2038, 9),
]


@pytest.mark.parametrize("iy,iw", _ISO_CASES)
def test_iso_week_resweep(iy, iw):
    text = f"hafta {iw} {iy}"
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text, A)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)
