# -*- coding: utf-8 -*-
"""Turkish intra-month numeric day ranges: "D1-D2 MONTH".

"3-9 mart" is the closed day range 3rd..9th of March; the engine returns a
half-open span [D1, D2+1).  The year is the next on-or-after occurrence of the
month.  Both edges are built independently from the loop indices.
Anchor: 2017-06-27.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)
_AD = A.date()

_MONTHS = {
    1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
    7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım",
    12: "aralık",
}


def _next_year(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


def _cases():
    out = []
    for m in range(1, 13):
        for d1, d2 in [(3, 9), (10, 20), (1, 15), (22, 28)]:
            out.append((f"{d1}-{d2} {_MONTHS[m]}", m, d1, d2))
    return out


@pytest.mark.parametrize("text,m,d1,d2", _cases())
def test_numeric_day_range(text, m, d1, d2):
    # the engine keeps the current year when the range still reaches the
    # anchor, i.e. its LAST day is on or after today.
    y = _next_year(m, d2)
    end_d = date(y, m, d2) + timedelta(days=1)
    s, e = start_end(text, A)
    assert s == AstroDate(y, m, d1)
    assert e == AstroDate(end_d.year, end_d.month, end_d.day)
