"""Second-pass resweep: calendar quarters ("Q2 1995", "the fourth quarter of
2035") swept across a wide span of years (1980-2039), both the "QN <year>"
and "the Nth quarter of <year>" surfaces.

``test_nl_quarter.py`` only spot-checks a handful of years (2018-2026); this
file widens the year axis across six decades to catch any epoch-dependent
regressions (leap-year adjacency, century boundaries) while keeping the same
independently-derived gold: quarter N is calendar months [3N-2..3N], spanning
from the first day of its first month to the first day of the month after
its last.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

_ORD_NAME = {1: "first", 2: "second", 3: "third", 4: "fourth"}

_YEARS = tuple(range(1980, 2040, 3))  # 1980, 1983, ..., 2039


def _edges(year, q):
    sm = 3 * q - 2
    if sm > 12:  # unreachable but keeps the formula honest
        raise ValueError
    if sm + 3 > 12:
        ey, em = year + 1, sm + 3 - 12
    else:
        ey, em = year, sm + 3
    return year, sm, ey, em


def _cases():
    out = []
    for year in _YEARS:
        for q in (1, 2, 3, 4):
            out.append((f"Q{q} {year}", year, q, "digit"))
            out.append((f"the {_ORD_NAME[q]} quarter of {year}", year, q, "prose"))
    return out


@pytest.mark.parametrize("text,year,q,style", _cases())
def test_quarter_decade_sweep(text, year, q, style):
    sy, sm, ey, em = _edges(year, q)
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), f"{text!r} start"
    assert e == AstroDate(ey, em, 1), f"{text!r} end"
