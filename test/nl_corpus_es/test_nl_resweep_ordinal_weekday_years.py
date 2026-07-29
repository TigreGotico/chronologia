# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: nth-weekday-of-month with an EXPLICIT YEAR, across a
matrix of years/months/weekdays/ordinals in Spanish: "el tercer lunes de
marzo 2019".

``test_nl_ordinal_weekday_es.py`` already proves the bare-month grid (anchor
year 2017 only) and pins six spot explicit-year cases; this file exercises
the *year* axis exhaustively so the "de <month> <year>" tail is proven for
every weekday x ordinal x month, not just six hand-picked combinations.

Gold is the same independent calendar oracle (walk from day 1 of the target
month/year to the requested weekday offset, then step by weeks), duplicated
here rather than imported so this file can be read standalone.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_MONTHS = [
    ("enero", 1), ("febrero", 2), ("marzo", 3), ("abril", 4),
    ("mayo", 5), ("junio", 6), ("julio", 7), ("agosto", 8),
    ("septiembre", 9), ("octubre", 10), ("noviembre", 11), ("diciembre", 12),
]
_WD = [
    ("lunes", 0), ("martes", 1), ("miércoles", 2), ("jueves", 3),
    ("viernes", 4), ("sábado", 5), ("domingo", 6),
]
_ORD = [("primer", 1), ("segundo", 2), ("tercer", 3)]
_YEARS = [2016, 2019, 2020, 2023]

# exact strings already pinned by test_nl_ordinal_weekday_es.py -- never
# re-emit them here.
_ALREADY_COVERED = {
    "el primer lunes de marzo 2019",
    "el segundo martes de noviembre 2019",
    "el tercer domingo de junio 2020",
    "el último viernes de agosto 2021",
    "el primer jueves de enero 2018",
    "el segundo sábado de mayo 2022",
}


def _nth_weekday(year, month, wd, n):
    first = date(year, month, 1)
    offset = (wd - first.weekday()) % 7
    day = 1 + offset + 7 * (n - 1)
    return date(year, month, day)


def _last_weekday(year, month, wd):
    last = calendar.monthrange(year, month)[1]
    d = date(year, month, last)
    offset = (d.weekday() - wd) % 7
    return date(year, month, last - offset)


def _ordinal_cases():
    out = []
    for y in _YEARS:
        for ow, n in _ORD:
            for wn, wd in _WD:
                for mn, m in _MONTHS:
                    text = f"el {ow} {wn} de {mn} {y}"
                    if text in _ALREADY_COVERED:
                        continue
                    g = _nth_weekday(y, m, wd, n)
                    out.append((text, g))
    return out


def _last_cases():
    out = []
    for y in _YEARS:
        for wn, wd in _WD:
            for mn, m in _MONTHS:
                text = f"el último {wn} de {mn} {y}"
                if text in _ALREADY_COVERED:
                    continue
                out.append((text, _last_weekday(y, m, wd)))
    return out


@pytest.mark.parametrize("text,g", _ordinal_cases())
def test_ordinal_weekday_of_month_with_year(text, g):
    s = span(text)
    assert s.start == AstroDate(g.year, g.month, g.day), f"{text!r} -> {s.start}"
    assert s.width == timedelta(days=1)


@pytest.mark.parametrize("text,g", _last_cases())
def test_last_weekday_of_month_with_year(text, g):
    s = span(text)
    assert s.start == AstroDate(g.year, g.month, g.day), f"{text!r} -> {s.start}"
    assert s.width == timedelta(days=1)
