# -*- coding: utf-8 -*-
"""Broad oracle sweep: day ranges "od D. do D. <month> [year]" (hr).

"od 5. do 12. lipnja" -- from the 5th to the 12th of June, a half-open span
from the first day 00:00 to the day AFTER the last day 00:00.  Without a year
the range prefers the nearest future occurrence relative to the anchor; with a
year it is absolute.

Gold is fixed calendar arithmetic.  Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_GEN = {1: 'siječnja', 2: 'veljače', 3: 'ožujka', 4: 'travnja',
        5: 'svibnja', 6: 'lipnja', 7: 'srpnja', 8: 'kolovoza',
        9: 'rujna', 10: 'listopada', 11: 'studenog', 12: 'prosinca'}
_ANCHOR = date(2017, 6, 27)


def _future_year(m, sd):
    y = 2017
    if date(y, m, sd) < _ANCHOR:
        y = 2018
    return y


_NOYEAR = [(m, sd, ed)
           for m in (1, 3, 5, 9, 11)
           for (sd, ed) in ((5, 12), (1, 10), (3, 7), (15, 20))]
_WITHYEAR = [(y, m, sd, ed)
             for y in (2019, 2020, 2021)
             for m in (2, 4, 6, 10, 12)
             for (sd, ed) in ((5, 12), (1, 10), (3, 20))]


@pytest.mark.parametrize(
    "m,sd,ed", _NOYEAR,
    ids=[f"od {sd}. do {ed}. {_GEN[m]}" for (m, sd, ed) in _NOYEAR])
def test_range_no_year(m, sd, ed):
    y = _future_year(m, sd)
    st, en = start_end(f"od {sd}. do {ed}. {_GEN[m]}")
    assert st == AstroDate(y, m, sd)
    e = date(y, m, ed) + timedelta(days=1)
    assert en == AstroDate(e.year, e.month, e.day)


@pytest.mark.parametrize(
    "y,m,sd,ed", _WITHYEAR,
    ids=[f"od {sd}. do {ed}. {_GEN[m]} {y}" for (y, m, sd, ed) in _WITHYEAR])
def test_range_with_year(y, m, sd, ed):
    st, en = start_end(f"od {sd}. do {ed}. {_GEN[m]} {y}")
    assert st == AstroDate(y, m, sd)
    e = date(y, m, ed) + timedelta(days=1)
    assert en == AstroDate(e.year, e.month, e.day)
