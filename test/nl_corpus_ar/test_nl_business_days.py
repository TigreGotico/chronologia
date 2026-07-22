# -*- coding: utf-8 -*-
"""Business days (ar): ``في N أيام عمل`` ("in N business days") and the
composed ``N أيام عمل بعد/قبل <date>`` ("N business days after/before <date>").

A business day is a weekday that is not part of the Arabic weekend (Friday +
Saturday, per this locale's ``weekend_start=4``) nor a public holiday of the
``jurisdiction``.  Anchor: Wednesday 2026-12-23.  Counting from Wed, skipping
Fri/Sat:  Thu24(1) Sun27(2) Mon28(3) Tue29(4) Wed30(5) Thu31(6).

Saudi (``SA``) has no public holiday inside this window, so it matches the
holiday-blind count here -- the two are asserted equal.  Persian New Year
(نوروز 2027 = Sunday 2027-03-21) anchors the composition cases.

Note: Arabic postposes the "next" adjective (``يوم العمل القادم``), which the
business pass -- looking left of the unit for the count/next marker -- cannot
express; that surface is out of scope (documented, not tested)."""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 12, 23, 9, 0)   # Wednesday


def start(text, jurisdiction=None):
    r = extract_timespan(text, "ar", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("في 1 أيام عمل", date(2026, 12, 24)),   # Thu
    ("في 2 أيام عمل", date(2026, 12, 27)),   # Sun (skip Fri/Sat)
    ("في 3 أيام عمل", date(2026, 12, 28)),   # Mon
    ("في 4 أيام عمل", date(2026, 12, 29)),   # Tue
    ("في 5 أيام عمل", date(2026, 12, 30)),   # Wed
    ("في 6 أيام عمل", date(2026, 12, 31)),   # Thu
])
def test_count_weekend_aware(text, expected):
    assert start(text) == _ad(expected)
    # Saudi has no public holiday in this window -> same count.
    assert start(text, "SA") == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("3 أيام عمل بعد نوروز", date(2027, 3, 24)),
    ("2 أيام عمل قبل نوروز", date(2027, 3, 17)),
])
def test_composition(text, expected):
    assert start(text) == _ad(expected)


def test_span_is_one_day_wide():
    r = extract_timespan("في 3 أيام عمل", "ar", ANCHOR, jurisdiction="SA")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["كالعادة", "كل شيء طبيعي"])
def test_negatives(text):
    assert extract_timespan(text, "ar", ANCHOR) is None
