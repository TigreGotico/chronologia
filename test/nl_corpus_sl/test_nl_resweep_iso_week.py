# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: ISO calendar week (sl), ``teden N LETO``.

``teden 22 2022`` names ISO week 22 of 2022: the Monday-Sunday span
``[iso_monday 00:00, iso_monday+7 00:00)``.  Gold is computed with
``date.fromisocalendar`` (Python's own ISO-8601 week arithmetic), independent
of the parser under test.  Weeks 2-51 are used throughout to sidestep the
year-transition ambiguity of week 1 / week 52-53 (out of scope for this
sweep).  Verified live against four fresh years.  Anchor: Tuesday
2017-06-27 13:04.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import start_end, ad

_YEARS = [2022, 2023, 2024, 2025]
_WEEKS = list(range(2, 52))


def _iso_week_bounds(y, wk):
    mon = date.fromisocalendar(y, wk, 1)
    d0 = datetime(mon.year, mon.month, mon.day)
    return d0, d0 + timedelta(days=7)


_CASES = [
    (f"teden {wk} {y}", y, wk) for y in _YEARS for wk in _WEEKS
]


@pytest.mark.parametrize("text,y,wk", _CASES)
def test_iso_week(text, y, wk):
    lo, hi = _iso_week_bounds(y, wk)
    s, e = start_end(text)
    assert s == ad(lo)
    assert e == ad(hi)
