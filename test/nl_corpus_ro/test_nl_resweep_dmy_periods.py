# -*- coding: utf-8 -*-
"""Second-pass Romanian sweep: full DMY dates, month+year, quarters, ISO
weeks, and month-thirds -- all over years the first-pass files never touch.

Fresh-year ranges used here (none overlapping the originals):
  * full DMY / month+year : 2032-2035 (originals: 2018-2021, 1918-2021 spot
    pins in ``test_nl_calendar.py``)
  * quarters               : 2032-2039 (originals: 2017, 2018, 2020, 2026)
  * ISO weeks               : 2032-2039 (originals: 2017, 1999, 2020, 2024,
    2026, 2030)
  * month-thirds            : 2025-2028 (originals: 2019-2022)

All gold is independent arithmetic (stdlib ``date``/``timedelta`` and
``date.fromisocalendar``), never read back from the parser.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import start, start_end, span, AstroDate

_MONTH = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie", 5: "mai",
    6: "iunie", 7: "iulie", 8: "august", 9: "septembrie", 10: "octombrie",
    11: "noiembrie", 12: "decembrie",
}


# ---------------------------------------------------------------------------
# full DMY dates
# ---------------------------------------------------------------------------
def _dmy_cases():
    out = []
    for y in (2032, 2033, 2034):
        for m in range(1, 13):
            for d in (1, 15, 28):
                out.append((f"{d} {_MONTH[m]} {y}", y, m, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _dmy_cases())
def test_full_dmy_resweep(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d), text
    assert e - s == timedelta(days=1)


# ---------------------------------------------------------------------------
# month + year
# ---------------------------------------------------------------------------
def _month_year_cases():
    out = []
    for y in (2032, 2033, 2034, 2035):
        for m in range(1, 13):
            out.append((f"{_MONTH[m]} {y}", y, m))
    return out


@pytest.mark.parametrize("text,y,m", _month_year_cases())
def test_month_year_resweep(text, y, m):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, 1), text
    assert span(text).width >= timedelta(days=28)


# ---------------------------------------------------------------------------
# quarters: Qn <year>
# ---------------------------------------------------------------------------
def _quarter_cases():
    out = []
    for y in range(2032, 2040):
        for q in range(1, 5):
            sm = 3 * q - 2
            em = sm + 3
            ey = y
            if em > 12:
                em -= 12
                ey += 1
            out.append((f"Q{q} {y}", y, sm, ey, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _quarter_cases())
def test_quarter_resweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), text
    assert e == AstroDate(ey, em, 1), text


# ---------------------------------------------------------------------------
# ISO weeks: "săptămâna N din <year>"
# ---------------------------------------------------------------------------
def _iso_week_cases():
    out = []
    for y in range(2032, 2040):
        for w in (1, 10, 20, 30, 40, 50):
            out.append((f"săptămâna {w} din {y}", y, w))
    return out


@pytest.mark.parametrize("text,iy,iw", _iso_week_cases())
def test_iso_week_resweep(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day), text
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day), text


# ---------------------------------------------------------------------------
# month-thirds: "începutul/mijlocul/sfârșitul lui <month> <year>"
# ---------------------------------------------------------------------------
_PART = {"început": "early", "mijloc": "mid", "sfârșit": "late"}


def _third(y, m, part):
    s = datetime(y, m, 1)
    e = datetime(y + (m == 12), m % 12 + 1, 1)
    w = (e - s) / 3
    lo, hi = {"early": (s, s + w),
              "mid": (s + w, s + 2 * w),
              "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(lo), AstroDate.from_datetime(hi)


def _third_cases():
    out = []
    for y in (2025, 2026, 2027, 2028):
        for m in range(1, 13):
            for word, part in _PART.items():
                out.append((f"{word}ul lui {_MONTH[m]} {y}", y, m, part))
    return out


@pytest.mark.parametrize("text,y,m,part", _third_cases())
def test_month_third_resweep(text, y, m, part):
    want_s, want_e = _third(y, m, part)
    s, e = start_end(text)
    assert s == want_s, text
    assert e == want_e, text
