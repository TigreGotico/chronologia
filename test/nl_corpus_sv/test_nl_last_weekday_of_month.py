# -*- coding: utf-8 -*-
"""NL-TDD: "last <weekday> of <month>" binds the last-of-month span (sv).

The "sista" ordinal determiner selects the FINAL occurrence of the named
weekday inside the named month. Gold is an independent calendar walk
(``_last_weekday``), never the parser. A cardinal-ordinal case is pinned too, so
the "last" wiring can never hijack the ordinary 1st-5th reading.

Anchor 2017-06-27 (Tuesday, 13:04).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start


def _last_weekday(y, m, wd):
    last = calendar.monthrange(y, m)[1]
    for d in range(last, 0, -1):
        if date(y, m, d).weekday() == wd:
            return date(y, m, d)
    raise AssertionError((y, m, wd))


_LAST = [('sista måndagen i maj 2017', 2017, 5, 0), ('sista fredagen i december 2020', 2020, 12, 4)]


@pytest.mark.parametrize("phrase,y,m,wd", _LAST, ids=[c[0] for c in _LAST])
def test_last_weekday_of_month(phrase, y, m, wd):
    gold = _last_weekday(y, m, wd)
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day)


def test_low_ordinal_regression():
    # cardinal ordinal still binds -- the "last" wiring must not hijack it.
    assert start('första måndagen i maj 2017') == AstroDate(2017, 5, 1)

