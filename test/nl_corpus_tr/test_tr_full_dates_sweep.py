# -*- coding: utf-8 -*-
"""Full Gregorian dates in Turkish (gün ay yıl) -- parametrized oracle sweep.

Turkish writes dates day-month-year in words: "5 mart 2019".  The gold is
pure construction: the phrase names calendar day ``AstroDate(y, m, d)`` and
spans exactly one day.  Nothing here reads a value back from the parser; the
year/month/day come straight from the loop that builds each phrase, so a
regression that mis-reads any field fails loudly.

Anchor: Tuesday 2017-06-27 13:04 (explicit years, so the anchor is inert).
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import span, start

A = datetime(2017, 6, 27, 13, 4)

# Turkish month names, indexed 1..12.
_MONTHS = {
    1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
    7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım",
    12: "aralık",
}

# Day of month picked so every month is valid (<= 28); years span a wide
# historical range to exercise the year field.
_DAYS = [1, 7, 14, 21, 28]
_YEARS = [1923, 1945, 1969, 2001, 2019, 2024, 2030]


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 13):
            for d in _DAYS:
                out.append((f"{d} {_MONTHS[m]} {y}", y, m, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_full_date(text, y, m, d):
    assert start(text, A) == AstroDate(y, m, d)
    assert span(text, A).width == timedelta(days=1)
