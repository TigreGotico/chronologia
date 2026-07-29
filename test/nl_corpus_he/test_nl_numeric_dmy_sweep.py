# -*- coding: utf-8 -*-
"""Numeric civil dates as used in Israel: day/month/year with slashes, and the
ISO YYYY-MM-DD form.  Both resolve to a one-day span; gold by arithmetic."""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_DAYS = (3, 11, 25)
_MONTHS = (2, 6, 12)
_YEARS = (1990, 2015, 2031)


def _slash_cases():
    out = []
    for y in _YEARS:
        for m in _MONTHS:
            for d in _DAYS:
                out.append((f"{d:02d}/{m:02d}/{y}", y, m, d))
    return out


def _iso_cases():
    out = []
    for y in _YEARS:
        for m in _MONTHS:
            for d in _DAYS:
                out.append((f"{y}-{m:02d}-{d:02d}", y, m, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _slash_cases() + _iso_cases())
def test_numeric_date(text, y, m, d):
    s = date(y, m, d)
    e = s + timedelta(days=1)
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
