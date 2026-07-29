# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: quarters, ISO weeks, month-thirds (hr), fresh years.

test_nl_quarter only exercises 2017-2020/2026; test_nl_iso_week only
2017/2020/2024/2026/2030; test_nl_month_thirds_sweep only 2017.  This
resweep widens all three to fresh explicit years.  Gold is fixed calendar
arithmetic (``date.fromisocalendar`` for ISO weeks, equal-thirds division for
month-thirds), never the parser.  Anchor 2017-06-27.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

# --- quarters, fresh years ---------------------------------------------------
_Q_YEARS = (2022, 2023, 2025, 2028)
_Q_CASES = [(f"{q}. kvartal {y}.", y, mm, (y + 1 if mm == 10 else y),
             (1 if mm == 10 else mm + 3))
            for y in _Q_YEARS
            for q, mm in ((1, 1), (2, 4), (3, 7), (4, 10))]


@pytest.mark.parametrize("text,sy,sm,ey,em", _Q_CASES,
                          ids=[c[0] for c in _Q_CASES])
def test_quarter_resweep(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


# --- ISO weeks, fresh years ---------------------------------------------------
_ISO_CASES = [
    (2022, 1), (2022, 27), (2022, 52),
    (2023, 5), (2023, 33),
    (2025, 12), (2025, 44),
    (2029, 9), (2029, 41),
]


@pytest.mark.parametrize("iy,iw", _ISO_CASES,
                          ids=[f"tjedan {w} {y}" for y, w in _ISO_CASES])
def test_iso_week_resweep(iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(f"tjedan {iw} {iy}")
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


# --- month-thirds, fresh years -------------------------------------------------
_GEN = {1: 'siječnja', 2: 'veljače', 3: 'ožujka', 4: 'travnja',
        5: 'svibnja', 6: 'lipnja', 7: 'srpnja', 8: 'kolovoza',
        9: 'rujna', 10: 'listopada', 11: 'studenog', 12: 'prosinca'}
_PARTS = ['početak', 'sredina', 'kraj']


def _thirds(y, m):
    start = datetime(y, m, 1)
    end = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    tot = end - start
    b1 = start + tot / 3
    b2 = start + 2 * tot / 3
    return [(start, b1), (b1, b2), (b2, end)]


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                      dt.second, dt.microsecond)


_THIRD_CASES = []
for _y in (2022, 2023):
    for _m, _gen in _GEN.items():
        _ths = _thirds(_y, _m)
        for _i, _part in enumerate(_PARTS):
            _THIRD_CASES.append(
                (f"{_part} {_gen} {_y}", _ths[_i][0], _ths[_i][1]))


@pytest.mark.parametrize("phrase,s,e", _THIRD_CASES,
                          ids=[c[0] for c in _THIRD_CASES])
def test_month_third_resweep(phrase, s, e):
    assert start_end(phrase) == (_ad(s), _ad(e)), phrase
