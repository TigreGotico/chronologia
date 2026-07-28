# -*- coding: utf-8 -*-
"""Holiday sweep with explicit year (nl): "<feestdag> <jaar>".

Every gold date is computed by parser-independent arithmetic:

* Fixed civil dates are literals (Nieuwjaar 1-jan, Driekoningen 6-jan,
  Valentijnsdag 14-feb, Allerheiligen 1-nov, Halloween 31-okt, Kerstavond
  24-dec, Eerste/Tweede Kerstdag 25/26-dec, Oudejaarsavond 31-dec).
* Movable feasts hang off Western Easter via the Anonymous Gregorian
  (Meeus/Butcher) computus in :func:`easter`, offset in whole days.
* Moederdag (2nd Sunday of May) and Vaderdag (3rd Sunday of June) walk the
  calendar independently.

Holidays whose explicit-year surface does NOT bind in this locale
(Koningsdag, Bevrijdingsdag, Sinterklaas, Aswoensdag, Witte Donderdag,
Dodenherdenking) are deliberately excluded -- see the vocabulary-gap note in
the campaign report; asserting a date the parser cannot reach would be
dishonest. "carnaval" binds but its intended civil definition is ambiguous
(Shrove Sunday vs Tuesday) and is left out on gold-honesty grounds.

Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, span

_YEARS = list(range(2018, 2028))


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


def _build():
    cases = []
    for y in _YEARS:
        for table in (_fixed(y), _movable(y), _weekday_based(y)):
            for name, gold in table.items():
                cases.append((f"{name} {y}", gold))
    return cases


_CASES = _build()


@pytest.mark.parametrize("phrase,gold", _CASES, ids=[c[0] for c in _CASES])
def test_holiday_year(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert parse(phrase)[1] == "", phrase


@pytest.mark.parametrize("phrase", [
    # koningsdag / bevrijdingsdag / sinterklaas now bind (round-2 civil
    # holidays) -- see test_nl_national_holidays_2.py. aswoensdag /
    # dodenherdenking remain unregistered coverage gaps.
    "aswoensdag 2020", "dodenherdenking 2020",
])
def test_unregistered_holiday_leaves_year(phrase):
    """These holiday words are not in the nl vocabulary: the year still binds
    (whole calendar year) and the holiday word is returned as remainder. This
    documents the coverage gap without asserting an unreachable date."""
    r = parse(phrase)
    assert r is not None
    year = int(phrase.split()[-1])
    assert (r[0].start, r[0].end) == (AstroDate(year, 1, 1), AstroDate(year + 1, 1, 1))
    assert phrase.split()[0] in r[1]
