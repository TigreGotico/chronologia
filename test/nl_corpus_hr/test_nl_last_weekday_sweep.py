# -*- coding: utf-8 -*-
"""Broad oracle sweep: "last <weekday> of <month> <year>" (hr, genitive order).

The "posljednji"/"posljednja" determiner selects the FINAL occurrence of the
named weekday inside the month.  Masculine weekdays -> "posljednji", feminine
weekdays (srijeda/subota/nedjelja) -> "posljednja".  Genitive month name,
no connector.

Gold is an INDEPENDENT reverse calendar walk (``_last_weekday``).  Anchor
2017-06-27 (Tuesday, 13:04).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_MONTHS = {1: 'siječnja', 2: 'veljače', 3: 'ožujka', 4: 'travnja',
           5: 'svibnja', 6: 'lipnja', 7: 'srpnja', 8: 'kolovoza',
           9: 'rujna', 10: 'listopada', 11: 'studenog', 12: 'prosinca'}

_MASC_WD = {'ponedjeljak': 0, 'utorak': 1, 'četvrtak': 3, 'petak': 4}
_FEM_WD = {'srijeda': 2, 'subota': 5, 'nedjelja': 6}


def _last_weekday(y, m, wd):
    last = calendar.monthrange(y, m)[1]
    for dd in range(last, 0, -1):
        if date(y, m, dd).weekday() == wd:
            return date(y, m, dd)
    raise AssertionError((y, m, wd))


def _build(det, wds):
    return [(f"{det} {wn} {_MONTHS[m]} {y}", y, m, wd)
            for y in (2019, 2020, 2021)
            for m in range(1, 13)
            for wn, wd in wds.items()]


_CASES = _build("posljednji", _MASC_WD) + _build("posljednja", _FEM_WD)


@pytest.mark.parametrize("phrase,y,m,wd", _CASES, ids=[c[0] for c in _CASES])
def test_last_weekday_of_month(phrase, y, m, wd):
    gold = _last_weekday(y, m, wd)
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
