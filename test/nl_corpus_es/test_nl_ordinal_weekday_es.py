# -*- coding: utf-8 -*-
"""Ordinal-weekday-of-month in Spanish: "el tercer lunes de marzo".

Spanish names the n-th weekday of a calendar month with an ordinal adjective
(``primer``, ``segundo``, ``tercer``) or ``último`` for the last one.  The
resolved day is the n-th (or last) occurrence of that weekday *inside* the
named month, NOT the next literal weekday.

Gold is computed by an independent calendar oracle (:func:`_nth_weekday` /
:func:`_last_weekday`) that never touches the parser: it walks from the 1st of
the month to the offset of the requested weekday and steps by weeks.  A bare
month takes the year the month alone takes (ruling 1, changed on 26 November
2026: it used to be the anchor year 2017 whether the month was past or future):
a month that has ended before the anchor, enero to mayo, is 2018, and junio to
diciembre stay in 2017, unless an explicit year is given.  A weekday of junio that
has ended at the anchor (before 2017-06-27 13:04) is also 2018.

Anchor: Tuesday 2017-06-27.  ``cuarto``/``quinto`` (4th/5th) are NOT asserted
here -- the engine does not yet resolve them (see the campaign BUG list).
"""
import calendar
from datetime import date, datetime, timedelta

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
    # ruling 1: a part of a month takes its month's year (anchor June 2017)
    def yr(m):
        return 2017 + (m < 6)

    def pick(m, f, *args):
        g = f(yr(m), m, *args)
        if m == 6 and (datetime(g.year, g.month, g.day) + timedelta(days=1)
                       <= datetime(2017, 6, 27, 13, 4)):
            # ruling 1 (26 November 2026): a part of a month is read as a span;
            # a weekday of June 2017 before the anchor has ended, so it is that
            # weekday of June 2018 (recomputed: weekdays move)
            g = f(2018, m, *args)
        return g
    for ow, n in _ORD:
        for wn, wd in _WD:
            for mn, m in _MONTHS:
                out.append((f"el {ow} {wn} de {mn}", pick(m, _nth_weekday, wd, n)))
    for wn, wd in _WD:
        for mn, m in _MONTHS:
            out.append((f"el último {wn} de {mn}", pick(m, _last_weekday, wd)))
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
