# -*- coding: utf-8 -*-
"""Kabyle "MONTH DAY [YEAR]" calendar order (lang.json calendar_date order
"MONTH DAY? YEAR?"). Complements test_nl_calendar.py's "DAY MONTH" order.

Without an explicit year the date is future-shifted into the anchor year or the
next (prefer_future=true); with a year it is that exact date. Gold from
independent arithmetic against anchor Tue 2017-06-27. Month surfaces are the
Tamazight month names in months.voc.
"""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start

MONTHS = {
    1: "yennayer", 2: "fuṛar", 3: "meɣres", 4: "yebrir", 5: "mayyu",
    6: "yunyu", 7: "yulyu", 8: "ɣuct", 9: "ctembeṛ", 10: "tubeṛ",
    11: "wambeṛ", 12: "dujembeṛ",
}

_AD = ANCHOR.date()


def _future_year(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


# MONTH DAY (no year) -> future-shifted
_NO_YEAR = [(3, 1), (20, 6), (25, 12), (4, 7), (6, 8), (11, 9), (1, 1)]


@pytest.mark.parametrize("d,m", _NO_YEAR)
def test_month_day_no_year(d, m):
    text = "%s %d" % (MONTHS[m], d)
    y = _future_year(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


# MONTH DAY YEAR -> exact
_WITH_YEAR = [
    (20, 7, 1969), (6, 8, 1945), (11, 9, 2001), (14, 7, 1789),
    (25, 12, 2025), (1, 1, 2000), (12, 10, 1492), (29, 2, 2028),
]


@pytest.mark.parametrize("d,m,y", _WITH_YEAR)
def test_month_day_year(d, m, y):
    text = "%s %d %d" % (MONTHS[m], d, y)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)
