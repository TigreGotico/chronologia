# -*- coding: utf-8 -*-
"""Business days (fa): ``در N روز کاری`` ("in N working days") and the
composed ``N روز کاری بعد از/قبل از <date>``.

A business day is a weekday outside the Iranian weekend (Thursday + Friday,
``weekend_start=3``) and not a public holiday of the ``jurisdiction``.  Anchor
Wednesday 2026-12-23.  Skipping Thu/Fri from Wed:  Sat26(1) Sun27(2) Mon28(3)
Tue29(4) Wed30(5) Sat Jan2(6).  Iran (``IR``) has no public holiday inside
this window, so it matches the holiday-blind count -- asserted equal.  Nowruz
(نوروز 2018 = Wednesday 2018-03-21) anchors the composition."""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 12, 23, 9, 0)   # Wednesday
_ARITH = datetime(2017, 6, 27, 13, 4)


def start(text, anchor=ANCHOR, jurisdiction=None):
    r = extract_timespan(text, "fa", anchor, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("در 1 روز کاری", date(2026, 12, 26)),
    ("در 2 روز کاری", date(2026, 12, 27)),
    ("در 3 روز کاری", date(2026, 12, 28)),
    ("در 4 روز کاری", date(2026, 12, 29)),
    ("در 5 روز کاری", date(2026, 12, 30)),
    ("در 6 روز کاری", date(2027, 1, 2)),
])
def test_count_weekend_aware(text, expected):
    assert start(text) == _ad(expected)
    assert start(text, jurisdiction="IR") == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("3 روز کاری بعد از نوروز", date(2018, 3, 26)),
    ("2 روز کاری قبل از نوروز", date(2018, 3, 19)),
])
def test_composition(text, expected):
    assert start(text, anchor=_ARITH) == _ad(expected)


def test_span_is_one_day_wide():
    r = extract_timespan("در 3 روز کاری", "fa", ANCHOR, jurisdiction="IR")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["مثل همیشه", "همه چیز عادی است"])
def test_negatives(text):
    assert extract_timespan(text, "fa", ANCHOR) is None
