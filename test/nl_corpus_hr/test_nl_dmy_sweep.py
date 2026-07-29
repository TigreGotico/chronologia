# -*- coding: utf-8 -*-
"""Broad oracle sweep: full day-month-year dates and month+year (hr).

Croatian dates run day-month-year with an ordinal-dot day and a genitive month
name: "15. srpnja 2020".  A full DMY is a single day-wide span.  A bare
month+year ("srpanj 2020" nominative, or "srpnja 2020" genitive) spans the
whole calendar month.

Gold is fixed calendar arithmetic, never the parser.  Anchor 2017-06-27.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span

_GEN = {1: 'siječnja', 2: 'veljače', 3: 'ožujka', 4: 'travnja',
        5: 'svibnja', 6: 'lipnja', 7: 'srpnja', 8: 'kolovoza',
        9: 'rujna', 10: 'listopada', 11: 'studenog', 12: 'prosinca'}
_NOM = {1: 'siječanj', 2: 'veljača', 3: 'ožujak', 4: 'travanj',
        5: 'svibanj', 6: 'lipanj', 7: 'srpanj', 8: 'kolovoz',
        9: 'rujan', 10: 'listopad', 11: 'studeni', 12: 'prosinac'}

_DMY = [(f"{d}. {_GEN[m]} {y}", y, m, d)
        for y in (2019, 2020, 2021)
        for m in (1, 3, 6, 9, 12)
        for d in (1, 7, 15, 28)]


@pytest.mark.parametrize("phrase,y,m,d", _DMY, ids=[c[0] for c in _DMY])
def test_full_dmy(phrase, y, m, d):
    s = span(phrase)
    assert s.start == AstroDate(y, m, d), phrase
    assert s.width == timedelta(days=1), phrase


_MY = [(f"{_NOM[m]} {y}", y, m) for y in (2019, 2020, 2021) for m in range(1, 13)]


@pytest.mark.parametrize("phrase,y,m", _MY, ids=[c[0] for c in _MY])
def test_month_year(phrase, y, m):
    s = span(phrase)
    assert s.start == AstroDate(y, m, 1), phrase
    ey, em = (y + 1, 1) if m == 12 else (y, m + 1)
    assert s.end == AstroDate(ey, em, 1), phrase
