# -*- coding: utf-8 -*-
"""Italian month-thirds: "inizio / metà / fine <mese>".

The month is split into three equal-*duration* thirds. A month of ``L`` days
runs ``L*24`` hours; since 24 is divisible by 3 every boundary lands on a whole
hour ``L*8`` hours apart, so no fractional-minute rounding is ever needed:

    inizio  [first,              first + L*8h)
    metà    [first + L*8h,       first + L*16h)
    fine    [first + L*16h,      first + L*24h == next month)

The oracle below is pure calendar arithmetic (``calendar.monthrange``); it never
consults the parser. Anchor Tue 2017-06-27, so a bare month name binds its 2017
occurrence.
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


# every 2017-occurrence month, all three thirds -> 36 cases
_CASES = []
for _name, _m in _MONTHS.items():
    _thd = _thirds(2017, _m)
    for _which in ("inizio", "metà", "fine"):
        _CASES.append((f"{_which} {_name}", *_thd[_which]))


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
    assert (s, e) == (AstroDate(2017, 2, 1), AstroDate(2017, 2, 10, 8, 0))
