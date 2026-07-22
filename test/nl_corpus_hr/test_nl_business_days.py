# -*- coding: utf-8 -*-
"""Business-day counting (hr), holiday-blind (no jurisdiction): a business day
is any weekday that is not a weekend day. Anchor Tue 2017-06-27, so counting
forward skips Sat/Sun only:
    Wed 06-28(1) Thu 06-29(2) Fri 06-30(3) Mon 07-03(4) Tue 07-04(5).
"the next business day" is the first such day (N=1). Every date hand-derived."""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)   # Tuesday


def start(text):
    r = extract_timespan(text, "hr", ANCHOR)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("n,expected", [
    (1, date(2017, 6, 28)),
    (2, date(2017, 6, 29)),
    (3, date(2017, 6, 30)),
    (4, date(2017, 7, 3)),
    (5, date(2017, 7, 4)),
])
def test_count(n, expected):
    assert start(f"{n} radnih dana") == _ad(expected)


def test_next_business_day():
    assert start("sljedeći radni dan") == _ad(date(2017, 6, 28))


def test_span_is_day_wide():
    r = extract_timespan("3 radnih dana", "hr", ANCHOR)
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["sastanak", "radnih"])
def test_negatives(text):
    assert extract_timespan(text, "hr", ANCHOR) is None
