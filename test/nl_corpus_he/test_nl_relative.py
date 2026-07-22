# -*- coding: utf-8 -*-
"""Relative offsets (both directions), named days, weekday reference.

Direction markers: לפני (before/ago -> past), בעוד/עוד (in -> future).  The
dual noun (שבועיים) is a known gap and is asserted in the adversarial
module."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start


def _day_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = timedelta(days=n)
        out.append((f"לפני {n} ימים", ANCHOR - d))
        out.append((f"בעוד {n} ימים", ANCHOR + d))
    return out


def _week_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = timedelta(weeks=n)
        out.append((f"לפני {n} שבועות", ANCHOR - d))
        out.append((f"בעוד {n} שבועות", ANCHOR + d))
    return out


def _month_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = relativedelta(months=n)
        out.append((f"לפני {n} חודשים", ANCHOR - d))
        out.append((f"בעוד {n} חודשים", ANCHOR + d))
    return out


def _year_cases():
    out = []
    for n in (1, 3, 5, 10):
        d = relativedelta(years=n)
        out.append((f"לפני {n} שנים", ANCHOR - d))
        out.append((f"בעוד {n} שנים", ANCHOR + d))
    return out


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_offsets(text, expected):
    assert start(text) == ad(expected)


_SPELLED = [("לפני שלושה ימים", 3), ("לפני חמישה ימים", 5),
            ("לפני עשרה ימים", 10), ("בעוד שבעה ימים", -7)]


@pytest.mark.parametrize("text,n", _SPELLED)
def test_spelled_offsets(text, n):
    assert start(text) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("text,off", [
    ("היום", 0), ("אתמול", -1), ("מחר", 1), ("מחרתיים", 2), ("שלשום", -2),
])
def test_named_days(text, off):
    exp = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0, second=0,
                                                 microsecond=0)
    assert start(text) == ad(exp)


def test_weekday_friday_next():
    # יום שישי הבא: next Friday (py idx 4) strictly after the Tuesday anchor
    ahead = ((4 - ANCHOR.weekday()) % 7) or 7
    exp = (ANCHOR + timedelta(days=ahead)).replace(hour=0, minute=0,
                                                   second=0, microsecond=0)
    assert start("יום שישי הבא") == ad(exp)


def test_weekday_sunday_next():
    # יום ראשון (Sunday, py idx 6): the ordinal "first day" opens the week
    ahead = ((6 - ANCHOR.weekday()) % 7) or 7
    exp = (ANCHOR + timedelta(days=ahead)).replace(hour=0, minute=0,
                                                   second=0, microsecond=0)
    assert start("יום ראשון הבא") == ad(exp)


def test_weekday_last():
    back = ((ANCHOR.weekday() - 4) % 7) or 7
    exp = (ANCHOR - timedelta(days=back)).replace(hour=0, minute=0,
                                                  second=0, microsecond=0)
    assert start("יום שישי האחרון") == ad(exp)
