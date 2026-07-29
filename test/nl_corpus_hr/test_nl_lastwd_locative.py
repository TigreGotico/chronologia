# -*- coding: utf-8 -*-
"""Croatian locative scoped-ordinal: Nth- and last-weekday-of-month.

Croatian expresses "the Nth <weekday> in <month>" with the locative
preposition "u" + the locative month name ("u ožujku", "u lipnju"), alongside
the genitive ("ožujka") that already binds.  The last-weekday idiom uses the
determiner "posljednji"/"zadnji" in concord ("posljednja", "posljednju");
Institut za hrvatski jezik, *Hrvatski pravopis* (o-stem masc. locative -u,
a-stem fem. locative -i; adjectival "studeni" → locative "studenom").

Gold is an independent calendar walk; anchor Tuesday 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse

# locative month surfaces
_LOC = {1: 'siječnju', 2: 'veljači', 3: 'ožujku', 4: 'travnju', 5: 'svibnju',
        6: 'lipnju', 7: 'srpnju', 8: 'kolovozu', 9: 'rujnu', 10: 'listopadu',
        11: 'studenom', 12: 'prosincu'}


def _nth_weekday(y, m, weekday, n):
    d = date(y, m, 1)
    c = 0
    while d.month == m:
        if d.weekday() == weekday:
            c += 1
            if c == n:
                return d
        d += timedelta(days=1)
    return None


def _last_weekday(y, m, weekday):
    d = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    d -= timedelta(days=1)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def _assert(phrase, gold):
    r = parse(phrase)
    assert r is not None, phrase
    assert r[0].start == AstroDate(gold.year, gold.month, gold.day), phrase


# Nth-weekday-of-month, locative (Monday=0)
_NTH = [
    ("prvi ponedjeljak u siječnju 2020", 2020, 1, 0, 1),
    ("treći ponedjeljak u ožujku 2020", 2020, 3, 0, 3),
    ("drugi utorak u lipnju 2019", 2019, 6, 1, 2),
    ("četvrti petak u studenom 2021", 2021, 11, 4, 4),
]


@pytest.mark.parametrize("phrase,y,m,wd,n", _NTH)
def test_locative_nth_weekday(phrase, y, m, wd, n):
    _assert(phrase, _nth_weekday(y, m, wd, n))


# last-weekday-of-month, locative
_LAST = [
    ("posljednji petak u lipnju", 2017, 6, 4),
    ("posljednji ponedjeljak u ožujku 2020", 2020, 3, 0),
    ("posljednja srijeda u travnju 2019", 2019, 4, 2),
    ("zadnji petak u studenom 2021", 2021, 11, 4),
]


@pytest.mark.parametrize("phrase,y,m,wd", _LAST)
def test_locative_last_weekday(phrase, y, m, wd):
    _assert(phrase, _last_weekday(y, m, wd))


def test_genitive_ordinal_still_binds():
    # regression: the existing hr genitive form must stay byte-identical in
    # behaviour after the override->extend switch.
    _assert("treći ponedjeljak ožujka 2020", _nth_weekday(2020, 3, 0, 3))
