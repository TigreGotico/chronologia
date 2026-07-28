# -*- coding: utf-8 -*-
"""Month-thirds sweep (ru) -- начало / середина / конец <month> [<year>].

The engine splits a calendar month into three equal thirds by wall-clock
duration.  A month of D days spans D*24 hours from the 1st 00:00 to the next
month's 1st 00:00; the third boundaries fall at D*8h and D*16h (always whole
hours, since D*24/3 = D*8).  начало = [start, +D*8h), середина = [+D*8h,
+D*16h), конец = [+D*16h, next-month-1st).

Gold is that arithmetic, computed independently below.  Anchor 2017-06-27; a
bare month resolves to its next occurrence, so a year is pinned explicitly to
keep the oracle deterministic."""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

_YEARS = (2018, 2019, 2020, 2021)


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


def _thirds(year, month):
    start = datetime(year, month, 1)
    d = monthrange(year, month)[1]
    b1 = start + timedelta(hours=d * 8)
    b2 = start + timedelta(hours=d * 16)
    end = start + timedelta(days=d)
    return {"начало": (start, b1), "середина": (b1, b2), "конец": (b2, end)}


def _cases():
    out = []
    for word in ("начало", "середина", "конец"):
        for month in range(1, 13):
            for year in _YEARS:
                s, e = _thirds(year, month)[word]
                text = f"{word} {_MONTHS_GEN[month]} {year}"
                out.append((text, s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_month_third(text, s, e):
    st, en = start_end(text)
    assert st == _ad(s)
    assert en == _ad(e)
