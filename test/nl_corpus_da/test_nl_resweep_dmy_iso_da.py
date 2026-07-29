# -*- coding: utf-8 -*-
"""da (second-pass resweep): full DMY dates, bare month+year, calendar
quarters, and ISO weeks, over fresh years/months/weeks not exercised by
``test_da_calendar.py`` (spot dates only), ``test_nl_quarter.py`` (2018,
2020, 2026) or ``test_nl_iso_week.py`` (1999, 2017, 2020, 2024, 2026, 2030).

All gold values are independent stdlib ``date`` arithmetic, never read back
from the parser.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, span, start_end, AstroDate

_MONTHS = {1: "januar", 2: "februar", 3: "marts", 4: "april", 5: "maj",
           6: "juni", 7: "juli", 8: "august", 9: "september",
           10: "oktober", 11: "november", 12: "december"}
_YEARS = (2028, 2029, 2030, 2033)
_DAYS = (1, 9, 17, 28)


def _clamp(y, m, d):
    while True:
        try:
            return date(y, m, d)
        except ValueError:
            d -= 1


_DMY_CASES = []
for _y in _YEARS:
    for _m, _mname in _MONTHS.items():
        for _d in _DAYS:
            _dt = _clamp(_y, _m, _d)
            _DMY_CASES.append((f"{_dt.day}. {_mname} {_y}", _dt))


@pytest.mark.parametrize("text,exp", _DMY_CASES)
def test_full_dmy_fresh(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


_MY_CASES = []
for _y in (2028, 2031, 2035, 2040):
    for _m, _mname in _MONTHS.items():
        _MY_CASES.append((f"{_mname} {_y}", _y, _m))


@pytest.mark.parametrize("text,y,m", _MY_CASES)
def test_month_year_fresh(text, y, m):
    s = span(text)
    assert s.start == AstroDate(y, m, 1)
    assert (s.end.year, s.end.month) == ((y + 1, 1) if m == 12 else (y, m + 1))


_Q_CASES = []
for _y in (2028, 2029, 2031, 2033, 2036):
    for _q in (1, 2, 3, 4):
        _sm = 3 * _q - 2
        _em = _sm + 3
        _sy, _ey = _y, _y
        if _em == 13:
            _em, _ey = 1, _y + 1
        _Q_CASES.append((f"Q{_q} {_y}", _y, _sm, _ey, _em))


@pytest.mark.parametrize("text,sy,sm,ey,em", _Q_CASES)
def test_quarter_fresh(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


_ISO_CASES = []
for _iy in (2028, 2029, 2032, 2033, 2037):
    for _iw in (1, 12, 26, 40, 52):
        _ISO_CASES.append((f"uge {_iw} af {_iy}", _iy, _iw))
# 2032 and 2037 are 53-ISO-week years -- exercise the boundary week too
_ISO_CASES.append(("uge 53 af 2032", 2032, 53))
_ISO_CASES.append(("uge 53 af 2037", 2037, 53))


@pytest.mark.parametrize("text,iy,iw", _ISO_CASES)
def test_iso_week_fresh(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)
