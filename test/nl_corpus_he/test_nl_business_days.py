# -*- coding: utf-8 -*-
"""Business days (he): ``בעוד N ימי עסקים`` ("in N business days") and the
composed ``N ימי עסקים אחרי/לפני <date>``.

A business day is a weekday outside the Israeli weekend (Friday + Saturday,
``weekend_start=4``) and not a public holiday of the ``jurisdiction``.  Anchor
Wednesday 2026-12-23.  Skipping Fri/Sat from Wed:  Thu24(1) Sun27(2) Mon28(3)
Tue29(4) Wed30(5) Thu31(6).  Israel (``IL``) has no public holiday inside this
window, so it matches the holiday-blind count -- asserted equal.  Passover
(פסח 2018 = Saturday 2018-03-31) anchors the composition."""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 12, 23, 9, 0)   # Wednesday
_ARITH = datetime(2017, 6, 27, 13, 4)


def start(text, anchor=ANCHOR, jurisdiction=None):
    r = extract_timespan(text, "he", anchor, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("בעוד 1 ימי עסקים", date(2026, 12, 24)),
    ("בעוד 2 ימי עסקים", date(2026, 12, 27)),
    ("בעוד 3 ימי עסקים", date(2026, 12, 28)),
    ("בעוד 4 ימי עסקים", date(2026, 12, 29)),
    ("בעוד 5 ימי עסקים", date(2026, 12, 30)),
    ("בעוד 6 ימי עסקים", date(2026, 12, 31)),
])
def test_count_weekend_aware(text, expected):
    assert start(text) == _ad(expected)
    assert start(text, jurisdiction="IL") == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("3 ימי עסקים אחרי פסח", date(2018, 4, 3)),
    ("2 ימי עסקים לפני פסח", date(2018, 3, 28)),
])
def test_composition(text, expected):
    assert start(text, anchor=_ARITH) == _ad(expected)


def test_span_is_one_day_wide():
    r = extract_timespan("בעוד 3 ימי עסקים", "he", ANCHOR, jurisdiction="IL")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["כרגיל", "הכל נורמלי"])
def test_negatives(text):
    assert extract_timespan(text, "he", ANCHOR) is None
