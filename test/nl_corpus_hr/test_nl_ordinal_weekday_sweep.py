# -*- coding: utf-8 -*-
"""Broad oracle sweep: "Nth <weekday> of <month> <year>" (hr, genitive order).

Croatian binds the ordinal-weekday-of-month idiom with a *genitive* month name
directly after the weekday, no connector: "treći ponedjeljak ožujka 2020"
(third Monday of March 2020).  Masculine weekdays take masculine ordinals
(prvi/drugi/treći/četvrti), feminine weekdays (srijeda/subota/nedjelja) take
feminine ordinals (prva/druga/treća).

Gold is an INDEPENDENT calendar walk (``_nth_weekday``) that never touches the
parser.  Anchor 2017-06-27 (Tuesday, 13:04).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_MONTHS = {1: 'siječnja', 2: 'veljače', 3: 'ožujka', 4: 'travnja',
           5: 'svibnja', 6: 'lipnja', 7: 'srpnja', 8: 'kolovoza',
           9: 'rujna', 10: 'listopada', 11: 'studenog', 12: 'prosinca'}

_MASC_WD = {'ponedjeljak': 0, 'utorak': 1, 'četvrtak': 3, 'petak': 4}
_MASC_ORD = {1: 'prvi', 2: 'drugi', 3: 'treći', 4: 'četvrti'}
_FEM_WD = {'srijeda': 2, 'subota': 5, 'nedjelja': 6}
_FEM_ORD = {1: 'prva', 2: 'druga', 3: 'treća'}


def _nth_weekday(y, m, wd, n):
    d = date(y, m, 1)
    c = 0
    while d.month == m:
        if d.weekday() == wd:
            c += 1
            if c == n:
                return d
        d += timedelta(days=1)
    return None


def _build(years, wds, ords):
    out = []
    for y in years:
        for m in range(1, 13):
            for wn, wd in wds.items():
                for on, oname in ords.items():
                    g = _nth_weekday(y, m, wd, on)
                    if g is None:
                        continue
                    out.append((f"{oname} {wn} {_MONTHS[m]} {y}", y, m, wd, on))
    return out


_CASES = (_build([2019, 2020, 2021], _MASC_WD, _MASC_ORD)
          + _build([2020, 2021], _FEM_WD, _FEM_ORD))


@pytest.mark.parametrize("phrase,y,m,wd,n", _CASES, ids=[c[0] for c in _CASES])
def test_ordinal_weekday_of_month(phrase, y, m, wd, n):
    gold = _nth_weekday(y, m, wd, n)
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
