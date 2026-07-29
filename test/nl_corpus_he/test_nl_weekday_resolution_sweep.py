# -*- coding: utf-8 -*-
"""Weekday resolution across several anchors and every named weekday.

הבא / הבאה = the next strictly-future occurrence; האחרון / האחרונה = the last
strictly-past one.  Israeli week convention: Sunday is the first day, so
"יום ראשון" (first day) maps to Python weekday index 6.  Each phrase carries a
directional marker, so this stays clear of the ordinal-weekday-of-month
homograph deferred under #228.  Gold is pure modular arithmetic on the anchor.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import AstroDate, LANG

# full "יום ..." weekday name -> Python weekday index (Mon=0 .. Sun=6)
_WEEKDAYS = {
    "יום ראשון": 6,
    "יום שני": 0,
    "יום שלישי": 1,
    "יום רביעי": 2,
    "יום חמישי": 3,
    "יום שישי": 4,
}
# שבת is feminine and takes הבאה / האחרונה
_SHABBAT = ("שבת", 5)

_ANCHORS = (
    datetime(2017, 6, 27, 13, 4),   # Tuesday
    datetime(2020, 1, 1, 9, 0),     # Wednesday
    datetime(2023, 11, 15, 20, 0),  # Wednesday
    datetime(1999, 12, 31, 8, 30),  # Friday
    datetime(2024, 2, 29, 0, 0),    # Thursday (leap day)
)


def _next(anchor, idx):
    ahead = (idx - anchor.weekday()) % 7 or 7
    return (anchor + timedelta(days=ahead)).date()


def _last(anchor, idx):
    back = (anchor.weekday() - idx) % 7 or 7
    return (anchor - timedelta(days=back)).date()


def _cases():
    out = []
    for anchor in _ANCHORS:
        for name, idx in _WEEKDAYS.items():
            out.append((anchor, f"{name} הבא", _next(anchor, idx)))
            out.append((anchor, f"{name} האחרון", _last(anchor, idx)))
        sname, sidx = _SHABBAT
        out.append((anchor, f"{sname} הבאה", _next(anchor, sidx)))
        out.append((anchor, f"{sname} האחרונה", _last(anchor, sidx)))
    return out


@pytest.mark.parametrize("anchor,text,gold", _cases())
def test_weekday_resolution(anchor, text, gold):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} @ {anchor} did not parse"
    sp = r[0]
    nxt = gold + timedelta(days=1)
    assert sp.start == AstroDate(gold.year, gold.month, gold.day)
    assert sp.end == AstroDate(nxt.year, nxt.month, nxt.day)
