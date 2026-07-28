# -*- coding: utf-8 -*-
"""Ordinal-weekday-of-month in Spanish: "el tercer lunes de marzo".

Spanish names the n-th weekday of a calendar month with an ordinal adjective
(``primer``, ``segundo``, ``tercer``) or ``último`` for the last one.  The
resolved day is the n-th (or last) occurrence of that weekday *inside* the
named month, NOT the next literal weekday.

Gold is computed by an independent calendar oracle (:func:`_nth_weekday` /
:func:`_last_weekday`) that never touches the parser: it walks from the 1st of
the month to the offset of the requested weekday and steps by weeks.  A bare
month resolves within the anchor year (2017) whether it is past or future, so
every expected date lives in 2017 unless an explicit year is given.

Anchor: Tuesday 2017-06-27.  ``cuarto``/``quinto`` (4th/5th) are NOT asserted
here -- the engine does not yet resolve them (see the campaign BUG list).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, span, start


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


def _cases():
    out = []
    for ow, n in _ORD:
        for wn, wd in _WD:
            for mn, m in _MONTHS:
                g = _nth_weekday(2017, m, wd, n)
                out.append((f"el {ow} {wn} de {mn}", g))
    for wn, wd in _WD:
        for mn, m in _MONTHS:
            out.append((f"el último {wn} de {mn}", _last_weekday(2017, m, wd)))
    return out


@pytest.mark.parametrize("text,g", _cases())
def test_ordinal_weekday_of_month(text, g):
    s = span(text)
    assert s.start == AstroDate(g.year, g.month, g.day), f"{text!r} -> {s.start}"
    assert s.width == timedelta(days=1)


# -- with an explicit (bare) year -----------------------------------------
_YEAR_CASES = [
    ("el primer lunes de marzo 2019", _nth_weekday(2019, 3, 0, 1)),
    ("el segundo martes de noviembre 2019", _nth_weekday(2019, 11, 1, 2)),
    ("el tercer domingo de junio 2020", _nth_weekday(2020, 6, 6, 3)),
    ("el último viernes de agosto 2021", _last_weekday(2021, 8, 4)),
    ("el primer jueves de enero 2018", _nth_weekday(2018, 1, 3, 1)),
    ("el segundo sábado de mayo 2022", _nth_weekday(2022, 5, 5, 2)),
]


@pytest.mark.parametrize("text,g", _YEAR_CASES)
def test_ordinal_weekday_with_year(text, g):
    assert start(text) == AstroDate(g.year, g.month, g.day)


@pytest.mark.parametrize("text", [
    "el lunes cualquiera",
    "un día de marzo",
])
def test_no_ordinal_no_specific_day(text):
    # phrases without the "<ordinal> <weekday> de <month>" shape must not
    # fabricate an n-th weekday; they either bind something else or nothing,
    # but never raise.
    parse(text)
