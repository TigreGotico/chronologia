"""Third-pass resweep: calendar quarters ("Q2 2047", "the fourth quarter of
2055") and ISO calendar weeks ("week 30 of 2050"), swept across a fresh,
contiguous run of years (2041-2060) not touched by either the original
``test_nl_quarter.py``/``test_nl_iso_week.py`` spot checks or the
second-pass resweep's 1980-2039 quarter window.

Quarter gold: quarter N is calendar months [3N-2..3N], spanning from the
first day of its first month to the first day of the month after its last
-- independently derived, never the parser's own output.

ISO-week gold: ``date.fromisocalendar(year, week, 1)`` (Monday of that ISO
week) through the following Monday -- stdlib arithmetic, independent of the
parser's own ISO-week handling.
"""
import datetime as _dt
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

_ORD_NAME = {1: "first", 2: "second", 3: "third", 4: "fourth"}
_YEARS = tuple(range(2041, 2061))  # 2041 .. 2060 inclusive


def _edges(year, q):
    sm = 3 * q - 2
    if sm + 3 > 12:
        ey, em = year + 1, sm + 3 - 12
    else:
        ey, em = year, sm + 3
    return year, sm, ey, em


def _quarter_cases():
    out = []
    for year in _YEARS:
        for q in (1, 2, 3, 4):
            out.append((f"Q{q} {year}", year, q))
            out.append((f"the {_ORD_NAME[q]} quarter of {year}", year, q))
    return out


@pytest.mark.parametrize("text,year,q", _quarter_cases())
def test_quarter_2040s2050s_sweep(text, year, q):
    sy, sm, ey, em = _edges(year, q)
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), f"{text!r} start"
    assert e == AstroDate(ey, em, 1), f"{text!r} end"


_WEEKS = (1, 10, 20, 30, 40, 52)


def _isoweek_cases():
    out = []
    for year in _YEARS:
        for wk in _WEEKS:
            try:
                _dt.date.fromisocalendar(year, wk, 1)
            except ValueError:
                continue
            out.append((f"week {wk} of {year}", year, wk))
    return out


@pytest.mark.parametrize("text,year,wk", _isoweek_cases())
def test_iso_week_2040s2050s_sweep(text, year, wk):
    s = _dt.date.fromisocalendar(year, wk, 1)
    e = s + timedelta(days=7)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))
