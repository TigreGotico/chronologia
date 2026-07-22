# -*- coding: utf-8 -*-
"""Relative offsets (both directions), named days, weekday reference.

Direction markers: قبل/منذ (before/since -> past), بعد/خلال (after/within ->
future).  Counted plurals (3-10 take the plural noun) are used; the dual
(يومين) is a known gap and is asserted in the adversarial module.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, nomatch


def _day_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = timedelta(days=n)
        out.append((f"قبل {n} أيام", ANCHOR - d))
        out.append((f"منذ {n} أيام", ANCHOR - d))
        out.append((f"بعد {n} أيام", ANCHOR + d))
        out.append((f"خلال {n} أيام", ANCHOR + d))
    return out


def _week_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = timedelta(weeks=n)
        out.append((f"قبل {n} أسابيع", ANCHOR - d))
        out.append((f"بعد {n} أسابيع", ANCHOR + d))
    return out


def _month_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = relativedelta(months=n)
        out.append((f"قبل {n} أشهر", ANCHOR - d))
        out.append((f"بعد {n} أشهر", ANCHOR + d))
    return out


def _year_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = relativedelta(years=n)
        out.append((f"قبل {n} سنوات", ANCHOR - d))
        out.append((f"بعد {n} سنوات", ANCHOR + d))
    return out


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_offsets(text, expected):
    assert start(text) == ad(expected)


_SPELLED = [("قبل ثلاثة أيام", 3), ("قبل خمسة أيام", 5),
            ("قبل عشرة أيام", 10), ("بعد سبعة أيام", -7)]


@pytest.mark.parametrize("text,n", _SPELLED)
def test_spelled_offsets(text, n):
    assert start(text) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("text,off", [
    ("اليوم", 0), ("أمس", -1), ("البارحة", -1), ("غدا", 1), ("الغد", 1),
    ("بعد غد", 2), ("أول أمس", -2),
])
def test_named_days(text, off):
    exp = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0, second=0,
                                                 microsecond=0)
    assert start(text) == ad(exp)


def test_weekday_next():
    # الجمعة القادمة: next Friday (py idx 4) strictly after the Tuesday anchor
    ahead = ((4 - ANCHOR.weekday()) % 7) or 7
    exp = (ANCHOR + timedelta(days=ahead)).replace(hour=0, minute=0,
                                                   second=0, microsecond=0)
    assert start("الجمعة القادمة") == ad(exp)


def test_weekday_last():
    back = ((ANCHOR.weekday() - 4) % 7) or 7
    exp = (ANCHOR - timedelta(days=back)).replace(hour=0, minute=0,
                                                  second=0, microsecond=0)
    assert start("الجمعة الماضية") == ad(exp)


def test_weekday_sunday_next():
    # الأحد (Sunday, py idx 6) -- the ordinal-neutral Arabic weekday
    ahead = ((6 - ANCHOR.weekday()) % 7) or 7
    exp = (ANCHOR + timedelta(days=ahead)).replace(hour=0, minute=0,
                                                   second=0, microsecond=0)
    assert start("الأحد القادم") == ad(exp)
