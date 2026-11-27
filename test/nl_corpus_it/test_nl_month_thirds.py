# -*- coding: utf-8 -*-
"""Italian month-thirds: "inizio / metà / fine <mese>".

The month is split into three equal-*duration* thirds. A month of ``L`` days
runs ``L*24`` hours; since 24 is divisible by 3 every boundary lands on a whole
hour ``L*8`` hours apart, so no fractional-minute rounding is ever needed:

    inizio  [first,              first + L*8h)
    metà    [first + L*8h,       first + L*16h)
    fine    [first + L*16h,      first + L*24h == next month)

The oracle below is pure calendar arithmetic (``calendar.monthrange``); it never
consults the parser. Anchor Tue 2017-06-27.  A bare month name takes the year
the month alone takes (ruling 1, changed on 26 November 2026; before, it bound
its 2017 occurrence): 2017 for a month that holds or follows the anchor, 2018
for one that has ended before it (gennaio to maggio).
"""
import calendar
from datetime import timedelta

import pytest

from ._corpus import start_end, AstroDate

_MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5,
    "giugno": 6, "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10,
    "novembre": 11, "dicembre": 12,
}


def _thirds(year, month):
    """(inizio, metà, fine) as (start, end) AstroDate pairs -- oracle only."""
    length = calendar.monthrange(year, month)[1]
    first = AstroDate(year, month, 1)
    step = timedelta(hours=length * 8)
    b1, b2 = first + step, first + 2 * step
    nxt = AstroDate(year + (month == 12), month % 12 + 1, 1)
    return {"inizio": (first, b1), "metà": (b1, b2), "fine": (b2, nxt)}


# every month, all three thirds -> 36 cases
_CASES = []
for _name, _m in _MONTHS.items():
    # ruling 1: a month that has ended at the anchor (June 2017) is next year's
    _thd = _thirds(2017 + (_m < 6), _m)
    for _which in ("inizio", "metà", "fine"):
        _part = _thd[_which]
        # ruling 1 (26 November 2026): a part of a month is read as a span; in
        # the anchor's own month (June 2017) inizio and metà have ended at
        # 2017-06-27, so they are June 2018; fine holds the anchor, stays 2017
        if _m == 6 and _which != "fine":
            _part = _thirds(2018, _m)[_which]
        _CASES.append((f"{_which} {_name}", *_part))


@pytest.mark.parametrize("text,s,e", _CASES)
def test_month_third(text, s, e):
    assert start_end(text) == (s, e)


def test_thirds_tile_the_whole_month():
    """The three thirds abut with no gap and cover exactly the month."""
    i, m, f = (_thirds(2017, 7)[k] for k in ("inizio", "metà", "fine"))
    assert i[1] == m[0] and m[1] == f[0]
    assert i[0] == AstroDate(2017, 7, 1) and f[1] == AstroDate(2017, 8, 1)


def test_february_short_month_thirds():
    """28-day February: boundaries at 9d8h, not the 31-day 10d8h."""
    s, e = start_end("inizio febbraio")
    # ruling 1: febbraio has ended at the anchor, so it is February 2018
    # (also 28 days)
    assert (s, e) == (AstroDate(2018, 2, 1), AstroDate(2018, 2, 10, 8, 0))
