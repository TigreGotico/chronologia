# -*- coding: utf-8 -*-
"""Relative days, bare weekdays and numeric offsets anchored on the Tuesday.

Anchor is 2017-06-27 13:04 (سه‌شنبه).  All gold is arithmetic on the anchor:
relative-day words shift the calendar day; a bare weekday rolls forward to its
next future occurrence (never the anchor day itself); ``N روز/هفته/ماه/سال
بعد|پیش`` shift by that many units keeping the 13:04 wall-clock, spanning one
unit.  ASCII and Persian-Indic digits are both exercised.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, span, start_end

_MID = datetime(2017, 6, 27)   # anchor calendar day at 00:00


@pytest.mark.parametrize("text,off", [
    ("دیروز", -1), ("امروز", 0), ("فردا", 1),
    ("پس‌فردا", 2), ("پریروز", -2),
])
def test_relative_day(text, off):
    g = _MID + timedelta(days=off)
    assert start_end(text) == (ad(g), ad(g + timedelta(days=1)))


@pytest.mark.parametrize("text,dow", [
    ("شنبه", 5), ("یکشنبه", 6), ("دوشنبه", 0), ("سه‌شنبه", 1),
    ("چهارشنبه", 2), ("پنج‌شنبه", 3), ("جمعه", 4),
])
def test_bare_weekday_next_occurrence(text, dow):
    delta = (dow - _MID.weekday()) % 7 or 7
    g = _MID + timedelta(days=delta)
    assert start_end(text) == (ad(g), ad(g + timedelta(days=1)))


_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _both(n):
    return [str(n), str(n).translate(_DIGITS)]


@pytest.mark.parametrize("n", [1, 2, 3, 5, 7, 10, 14])
def test_offset_days(n):
    for num in _both(n):
        for word, sign in (("بعد", 1), ("پیش", -1)):
            g = ANCHOR + timedelta(days=sign * n)
            s = span(f"{num} روز {word}")
            assert (s.start, s.end) == (ad(g), ad(g + timedelta(days=1)))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 6])
def test_offset_weeks(n):
    for num in _both(n):
        for word, sign in (("بعد", 1), ("پیش", -1)):
            g = ANCHOR + timedelta(weeks=sign * n)
            s = span(f"{num} هفته {word}")
            assert (s.start, s.end) == (ad(g), ad(g + timedelta(days=7)))


@pytest.mark.parametrize("n", [1, 2, 3, 6, 9])
def test_offset_months(n):
    for word, sign in (("بعد", 1), ("پیش", -1)):
        g = ANCHOR + relativedelta(months=sign * n)
        s = span(f"{n} ماه {word}")
        assert (s.start, s.end) == (ad(g), ad(g + relativedelta(months=1)))


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10])
def test_offset_years(n):
    for word, sign in (("بعد", 1), ("پیش", -1)):
        g = ANCHOR + relativedelta(years=sign * n)
        s = span(f"{n} سال {word}")
        assert (s.start, s.end) == (ad(g), ad(g + relativedelta(years=1)))
