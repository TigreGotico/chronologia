# -*- coding: utf-8 -*-
"""Second-pass resweep: Dutch holidays with explicit year, fresh years.

Extends :mod:`test_nl_holiday_computus_sweep` (years 2018-2027) and
:mod:`test_nl_national_holidays_2` (explicit-year cases only for 2019/2020)
to years 2028-2047, which neither file covers. Gold dates are computed by
independent arithmetic:

* Fixed civil dates are literals.
* Movable feasts hang off Western Easter via the Anonymous Gregorian
  (Meeus/Butcher) computus in :func:`easter`, offset in whole days.
* Moederdag (2nd Sunday of May) and Vaderdag (3rd Sunday of June) walk the
  calendar independently.
* Round-2 civil holidays (Koningsdag, Bevrijdingsdag, Sinterklaas) are fixed
  civil dates, exercised here with an explicit year for the first time at
  scale (the existing file only pins two explicit years).

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, span

_YEARS = list(range(2028, 2048))


def easter(year):
    """Western (Gregorian) Easter Sunday -- Anonymous Gregorian algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = ((h + ell - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def nth_sunday(year, month, n):
    first = date(year, month, 1)
    offset = (6 - first.weekday()) % 7
    return first + timedelta(days=offset + (n - 1) * 7)


def _fixed(year):
    return {
        "nieuwjaar": date(year, 1, 1),
        "nieuwjaarsdag": date(year, 1, 1),
        "driekoningen": date(year, 1, 6),
        "valentijnsdag": date(year, 2, 14),
        "halloween": date(year, 10, 31),
        "allerheiligen": date(year, 11, 1),
        "kerstavond": date(year, 12, 24),
        "kerstmis": date(year, 12, 25),
        "eerste kerstdag": date(year, 12, 25),
        "tweede kerstdag": date(year, 12, 26),
        "oudejaarsavond": date(year, 12, 31),
    }


def _movable(year):
    e = easter(year)
    return {
        "goede vrijdag": e + timedelta(days=-2),
        "pasen": e,
        "paasmaandag": e + timedelta(days=1),
        "hemelvaart": e + timedelta(days=39),
        "hemelvaartsdag": e + timedelta(days=39),
        "pinksteren": e + timedelta(days=49),
        "pinkstermaandag": e + timedelta(days=50),
    }


def _weekday_based(year):
    return {
        "moederdag": nth_sunday(year, 5, 2),
        "vaderdag": nth_sunday(year, 6, 3),
    }


def _round2(year):
    return {
        "koningsdag": date(year, 4, 27),
        "bevrijdingsdag": date(year, 5, 5),
        "sinterklaas": date(year, 12, 5),
    }


def _build():
    cases = []
    for y in _YEARS:
        for table in (_fixed(y), _movable(y), _weekday_based(y), _round2(y)):
            for name, gold in table.items():
                cases.append((f"{name} {y}", gold))
    return cases


_CASES = _build()


@pytest.mark.parametrize("phrase,gold", _CASES, ids=[c[0] for c in _CASES])
def test_holiday_year_resweep(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert parse(phrase)[1] == "", phrase
