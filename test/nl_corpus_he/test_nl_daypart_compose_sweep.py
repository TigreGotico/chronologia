# -*- coding: utf-8 -*-
"""Named relative day composed with a time-of-day band (CLDR he day-periods).

Named days: היום/מחר/אתמול/מחרתיים/שלשום.  Bands (locale he):
בבוקר 06-12, בצהריים 12:00-12:01 (noon point), בערב 18-22, בלילה 22-06 (crosses
midnight into the next day).  Gold is the named day's date carrying the band's
clock, by independent arithmetic against the mission anchor (Tuesday 13:04).
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, span

A = datetime(2017, 6, 27, 13, 4)

# named day -> day offset from the anchor date
_DAYS = {"היום": 0, "מחר": 1, "אתמול": -1, "מחרתיים": 2, "שלשום": -2}


def _band(d, kind):
    """Return (start_dt, end_dt) for date ``d`` and band ``kind``."""
    base = datetime(d.year, d.month, d.day)
    if kind == "בבוקר":
        return base.replace(hour=6), base.replace(hour=12)
    if kind == "בצהריים":
        return base.replace(hour=12), base.replace(hour=12, minute=1)
    if kind == "בערב":
        return base.replace(hour=18), base.replace(hour=22)
    if kind == "בלילה":
        return base.replace(hour=22), base.replace(hour=6) + timedelta(days=1)
    raise AssertionError(kind)


_BANDS = ("בבוקר", "בצהריים", "בערב", "בלילה")


def _cases():
    out = []
    for day, off in _DAYS.items():
        d = (A + timedelta(days=off)).date()
        for band in _BANDS:
            s, e = _band(d, band)
            out.append((f"{day} {band}", s, e))
    return out


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


@pytest.mark.parametrize("text,s,e", _cases())
def test_daypart_compose(text, s, e):
    sp = span(text, A)
    assert (sp.start, sp.end) == (_ad(s), _ad(e)), f"{text!r} -> {sp}"
