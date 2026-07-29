# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: day-ranges, full DMY, and month+year (hr), fresh
years not covered by test_nl_ranges_sweep (2017-2021) / test_nl_dmy_sweep
(2017/2019/2020/2021).

"od D. do D. <month-genitive> <year>" day ranges, "D. <month-genitive>
<year>" full dates, and bare "<month-nominative> <year>" month spans.  Gold
is fixed calendar arithmetic, never the parser.  Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start_end

_GEN = {1: 'siječnja', 2: 'veljače', 3: 'ožujka', 4: 'travnja',
        5: 'svibnja', 6: 'lipnja', 7: 'srpnja', 8: 'kolovoza',
        9: 'rujna', 10: 'listopada', 11: 'studenog', 12: 'prosinca'}
_NOM = {1: 'siječanj', 2: 'veljača', 3: 'ožujak', 4: 'travanj',
        5: 'svibanj', 6: 'lipanj', 7: 'srpanj', 8: 'kolovoz',
        9: 'rujan', 10: 'listopad', 11: 'studeni', 12: 'prosinac'}

_YEARS = (2022, 2023, 2024, 2025)

# --- day ranges, explicit year ----------------------------------------------
_RANGE_CASES = [(y, m, sd, ed)
                 for y in _YEARS
                 for m in (1, 3, 5, 7, 9, 11)
                 for (sd, ed) in ((5, 12), (1, 10))]


@pytest.mark.parametrize(
    "y,m,sd,ed", _RANGE_CASES,
    ids=[f"od {sd}. do {ed}. {_GEN[m]} {y}" for (y, m, sd, ed) in _RANGE_CASES])
def test_range_with_year_resweep(y, m, sd, ed):
    st, en = start_end(f"od {sd}. do {ed}. {_GEN[m]} {y}")
    assert st == AstroDate(y, m, sd)
    e = date(y, m, ed) + timedelta(days=1)
    assert en == AstroDate(e.year, e.month, e.day)


# --- full DMY, explicit year -------------------------------------------------
_DMY_CASES = [(f"{d}. {_GEN[m]} {y}", y, m, d)
              for y in _YEARS
              for m in (2, 4, 6, 8, 10, 12)
              for d in (3, 11, 19, 27)]


@pytest.mark.parametrize("phrase,y,m,d", _DMY_CASES,
                          ids=[c[0] for c in _DMY_CASES])
def test_full_dmy_resweep(phrase, y, m, d):
    s = span(phrase)
    assert s.start == AstroDate(y, m, d), phrase
    assert s.width == timedelta(days=1), phrase


# --- bare month + year, explicit year ---------------------------------------
_MY_CASES = [(f"{_NOM[m]} {y}", y, m) for y in _YEARS for m in range(1, 13)]


def _month_span(y, m):
    st = date(y, m, 1)
    en = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    return st, en


@pytest.mark.parametrize("phrase,y,m", _MY_CASES, ids=[c[0] for c in _MY_CASES])
def test_month_year_resweep(phrase, y, m):
    st, en = start_end(phrase)
    gst, gen = _month_span(y, m)
    assert st == AstroDate(gst.year, gst.month, gst.day), phrase
    assert en == AstroDate(gen.year, gen.month, gen.day), phrase
