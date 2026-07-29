# -*- coding: utf-8 -*-
"""RESWEEP: full Gregorian dates in Turkish (gün ay yıl), fresh day/year grid.

Same construction as ``test_tr_full_dates_sweep.py`` (day-month-year, e.g.
"5 mart 2019") but over a disjoint day set and a disjoint year set so no
surface here was already exercised there. The gold is pure construction: the
phrase names calendar day ``AstroDate(y, m, d)`` and spans exactly one day.

Anchor: Tuesday 2017-06-27 13:04 (explicit years, so the anchor is inert).
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import span, start

A = datetime(2017, 6, 27, 13, 4)

_MONTHS = {
    1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
    7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım",
    12: "aralık",
}

# Disjoint from test_tr_full_dates_sweep.py's [1, 7, 14, 21, 28].
_DAYS = [2, 9, 16, 23]

# Disjoint from test_tr_full_dates_sweep.py's
# [1923, 1945, 1969, 2001, 2019, 2024, 2030].
_YEARS = [1900, 1910, 1933, 1950, 1960, 1977, 1988, 1995, 2005, 2012,
          2016, 2022, 2027, 2035, 2050]


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 13):
            for d in _DAYS:
                out.append((f"{d} {_MONTHS[m]} {y}", y, m, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_full_date_resweep(text, y, m, d):
    assert start(text, A) == AstroDate(y, m, d)
    assert span(text, A).width == timedelta(days=1)
