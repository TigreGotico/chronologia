# -*- coding: utf-8 -*-
"""Anchored arithmetic (ar): ``N <unit> بعد/قبل <holiday>`` (a signed unit
offset) and ``<weekday> بعد/قبل <holiday>`` (a strict weekday roll) on a
resolved reference.  Anchor 2017-06-27 (Tuesday); عيد الفطر 2018 = Friday
2018-06-15, رأس السنة الهجرية (next) = Thursday 2017-09-21.

Arabic duals (أسبوعين "two weeks") are not folded to a number by the shared
numfold, so counts use an explicit digit or the singular ``أسبوع`` (one)."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

FITR = date(2018, 6, 15)
HIJRI = date(2017, 9, 21)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 أسابيع بعد عيد الفطر", FITR + timedelta(days=21)),
    ("أسبوع بعد عيد الفطر", FITR + timedelta(days=7)),
    ("5 أيام بعد عيد الفطر", FITR + timedelta(days=5)),
    ("3 أيام قبل رأس السنة الهجرية", HIJRI - timedelta(days=3)),
    ("اليوم بعد عيد الفطر", FITR + timedelta(days=1)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("الجمعة بعد عيد الفطر", date(2018, 6, 22)),
    ("الإثنين بعد عيد الفطر", date(2018, 6, 18)),
    ("الأحد قبل رأس السنة الهجرية", date(2017, 9, 17)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("3 أسابيع بعد عيد الفطر").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("الجمعة بعد عيد الفطر").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["قبل الاجتماع", "بعد الغداء"])
def test_no_reference_no_offset(text):
    nomatch(text)
