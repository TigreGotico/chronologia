# -*- coding: utf-8 -*-
"""RESWEEP: Turkish intra-month numeric day ranges "D1-D2 MONTH", fresh pairs.

Disjoint day-pair set from ``test_tr_numeric_range_sweep.py``'s
[(3, 9), (10, 20), (1, 15), (22, 28)]. Same oracle: the engine returns the
half-open span [D1, D2+1) in the next on-or-after year for the range's last
day. Anchor: 2017-06-27.
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
        for d1, d2 in [(2, 6), (11, 19), (21, 27), (5, 13), (7, 12),
                       (16, 24)]:
            out.append((f"{d1}-{d2} {_MONTHS[m]}", m, d1, d2))
    return out


@pytest.mark.parametrize("text,m,d1,d2", _cases())
def test_numeric_day_range_resweep(text, m, d1, d2):
    y = _next_year(m, d2)
    end_d = date(y, m, d2) + timedelta(days=1)
    s, e = start_end(text, A)
    assert s == AstroDate(y, m, d1)
    assert e == AstroDate(end_d.year, end_d.month, end_d.day)
