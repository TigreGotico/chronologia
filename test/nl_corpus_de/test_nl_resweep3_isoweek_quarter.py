# -*- coding: utf-8 -*-
"""Third-pass sweep of two numeric-international idioms on fresh years:
the ISO-8601 week designator ``YYYY-Www`` (language-neutral, so it reads
identically in German) and the German calendar-quarter idiom
("Qn <year>" / "<ordinal> quartal <year>").

``test_de_iso_week_literal.py`` touches 1914/1918/1919/2020/2024/2026;
``test_nl_quarter.py`` touches 2019/2020/2026. This file uses 5 fresh years
(2031, 2035, 2040, 2045, 2049) that overlap neither.

Gold for the ISO weeks comes from :func:`date.fromisocalendar` (stdlib,
never the parser). Gold for quarters is plain arithmetic: quarter N starts
on month 3N-2 and spans 3 months.

Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_YEARS = (2031, 2035, 2040, 2045, 2049)
_WEEKS = (1, 10, 26, 52)
_ORD_Q = {1: "erstes", 2: "zweites", 3: "drittes", 4: "viertes"}

_ISO_CASES = []
for _y in _YEARS:
    for _w in _WEEKS:
        _mon = date.fromisocalendar(_y, _w, 1)
        _ISO_CASES.append((f"{_y}-W{_w}", _mon))

_Q_CASES = []
for _y in _YEARS:
    for _q in (1, 2, 3, 4):
        _sm = 3 * _q - 2
        _sy, _ey, _em = _y, _y, _sm + 3
        if _em > 12:
            _em -= 12
            _ey += 1
        _Q_CASES.append((f"Q{_q} {_y}", _sy, _sm, _ey, _em))
        _Q_CASES.append(
            (f"{_ORD_Q[_q]} quartal {_y}", _sy, _sm, _ey, _em))


@pytest.mark.parametrize("text,monday", _ISO_CASES)
def test_iso_week_literal_de_resweep3(text, monday):
    nxt = monday + timedelta(days=7)
    s, e = start_end(text)
    assert s == AstroDate(monday.year, monday.month, monday.day)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text,sy,sm,ey,em", _Q_CASES)
def test_quarter_de_resweep3(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


def test_years_disjoint_from_prior_passes():
    _prior_iso = {1914, 1918, 1919, 1999, 2020, 2024, 2026, 2030}
    _prior_q = {2017, 2018, 2019, 2020, 2026}
    assert not (set(_YEARS) & _prior_iso)
    assert not (set(_YEARS) & _prior_q)


def test_grid_size_sanity():
    assert len(_ISO_CASES) == len(_YEARS) * len(_WEEKS)
    assert len(_Q_CASES) == len(_YEARS) * 4 * 2
