# -*- coding: utf-8 -*-
"""sv (second-pass resweep): "QN <year>" quarters and "vecka N av <year>"
ISO weeks over fresh years, disjoint from ``test_nl_quarter.py`` (years
2018/2020/2026 + relative forms) and ``test_nl_iso_week.py`` (a handful of
scattered weeks up to 2030).

Quarter gold is computed by INDEPENDENT month arithmetic (Q1=Jan-Mar,
Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec, half-open). ISO-week gold is read back
via ``date.isocalendar()`` on the returned start (the ISO calendar itself is
the independent oracle, not the parser's internal week logic) and cross
-checked against ``datetime.fromisocalendar`` for the expected Monday.

Anchor Tuesday 2017-06-27 13:04 (irrelevant: every phrase carries an
explicit year).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end, start, parse

_QSTART = {1: 1, 2: 4, 3: 7, 4: 10}
_Q_YEARS = list(range(2028, 2038))


def _build_quarters():
    cases = []
    for q, sm in _QSTART.items():
        for yr in _Q_YEARS:
            em = sm + 3
            ey, em2 = (yr + 1, 1) if em == 13 else (yr, em)
            cases.append((f"Q{q} {yr}", AstroDate(yr, sm, 1),
                          AstroDate(ey, em2, 1)))
    return cases


_QUARTER_CASES = _build_quarters()


@pytest.mark.parametrize("text,gs,ge", _QUARTER_CASES,
                         ids=[c[0] for c in _QUARTER_CASES])
def test_quarter_resweep(text, gs, ge):
    assert start_end(text) == (gs, ge)
    assert parse(text)[1] == ""


_WEEKS = [3, 15, 22, 35, 44, 49]
_W_YEARS = list(range(2028, 2038))


def _build_isoweeks():
    cases = []
    for w in _WEEKS:
        for yr in _W_YEARS:
            monday = date.fromisocalendar(yr, w, 1)
            cases.append((f"vecka {w} av {yr}", yr, w,
                          AstroDate(monday.year, monday.month, monday.day)))
    return cases


_ISOWEEK_CASES = _build_isoweeks()


@pytest.mark.parametrize("text,iso_y,iso_w,gs", _ISOWEEK_CASES,
                         ids=[c[0] for c in _ISOWEEK_CASES])
def test_iso_week_resweep(text, iso_y, iso_w, gs):
    s = start(text)
    assert s == gs
    py_date = date(s.year, s.month, s.day)
    assert py_date.isocalendar()[:2] == (iso_y, iso_w)
    assert parse(text)[1] == ""
