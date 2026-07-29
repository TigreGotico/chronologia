# -*- coding: utf-8 -*-
"""Relative offset sweep in Azerbaijani: "<N> <unit> sonra/əvvəl/qabaq".

sonra = future (+), əvvəl / qabaq = past (-).  Each offset yields a span that
starts at anchor ± N units and is exactly one unit wide.  Gold is computed with
timedelta / relativedelta, never from the parser.
"""
from datetime import datetime, timedelta
import pytest
from dateutil.relativedelta import relativedelta
from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


# unit-noun -> (delta factory, one-unit width factory)
_UNITS = {
    "gün": (lambda n: timedelta(days=n), lambda: timedelta(days=1)),
    "həftə": (lambda n: timedelta(weeks=n), lambda: timedelta(weeks=1)),
    "ay": (lambda n: relativedelta(months=n), lambda: relativedelta(months=1)),
    "il": (lambda n: relativedelta(years=n), lambda: relativedelta(years=1)),
    "saat": (lambda n: timedelta(hours=n), lambda: timedelta(hours=1)),
    "dəqiqə": (lambda n: timedelta(minutes=n), lambda: timedelta(minutes=1)),
}

_FUTURE = ["sonra"]
_PAST = ["əvvəl", "qabaq"]

_NS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 25, 30, 50, 100]


def _check(unit, n, marker, sign):
    dfac, wfac = _UNITS[unit]
    s_dt = A + sign * dfac(n)
    e_dt = s_dt + wfac()
    s, e = start_end("%d %s %s" % (n, unit, marker), A)
    assert s == _ad(s_dt)
    assert e == _ad(e_dt)


@pytest.mark.parametrize("unit", list(_UNITS))
@pytest.mark.parametrize("n", _NS)
def test_future_offsets(unit, n):
    _check(unit, n, "sonra", 1)


@pytest.mark.parametrize("unit", list(_UNITS))
@pytest.mark.parametrize("n", _NS)
@pytest.mark.parametrize("marker", _PAST)
def test_past_offsets(unit, n, marker):
    _check(unit, n, marker, -1)


# A handful of spelled-number offsets to prove numeral folding on this path.
_SPELLED = [
    ("beş gün sonra", timedelta(days=5), timedelta(days=1)),
    ("on gün sonra", timedelta(days=10), timedelta(days=1)),
    ("iki həftə sonra", timedelta(weeks=2), timedelta(weeks=1)),
    ("üç ay sonra", relativedelta(months=3), relativedelta(months=1)),
    ("bir il sonra", relativedelta(years=1), relativedelta(years=1)),
    ("otuz dəqiqə sonra", timedelta(minutes=30), timedelta(minutes=1)),
]


@pytest.mark.parametrize("text,delta,width", _SPELLED)
def test_spelled_offsets(text, delta, width):
    s_dt = A + delta
    s, e = start_end(text, A)
    assert s == _ad(s_dt)
    assert e == _ad(s_dt + width)
