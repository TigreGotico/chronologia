# -*- coding: utf-8 -*-
"""BUG: locative "u <month>" does NOT bind the ordinal-weekday-of-month idiom.

Croatian also expresses "the Nth <weekday> in <month>" with the locative
preposition + locative month name: "treći ponedjeljak u ožujku 2020" (third
Monday in March 2020).  The genitive order ("... ožujka 2020") binds correctly
(see test_nl_ordinal_weekday_sweep), but the locative "u ožujku" form is
currently NOT recognised as a month scope -- the parser drops the month and
mis-resolves to an anchor-relative weekday.  This mirrors the sk/sl locative
gap fixed upstream in #354.

These are STRICT xfails carrying the CORRECT gold (independent calendar walk):
they will start passing the moment the locative scope is wired, at which point
the strict marker forces this file to be promoted to a plain assertion.

Anchor 2017-06-27 (Tuesday).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse

_LOC = {3: 'ožujku', 4: 'travnju', 6: 'lipnju', 9: 'rujnu', 12: 'prosincu'}
_ORD = {1: 'prvi', 2: 'drugi', 3: 'treći', 4: 'četvrti'}


def _nth_monday(y, m, n):
    d = date(y, m, 1)
    c = 0
    while d.month == m:
        if d.weekday() == 0:
            c += 1
            if c == n:
                return d
        d += timedelta(days=1)
    return None


_CASES = [(f"{_ORD[o]} ponedjeljak u {_LOC[m]} {y}", y, m, o)
          for y in (2019, 2020)
          for m in _LOC
          for o in _ORD]


@pytest.mark.parametrize("phrase,y,m,o", _CASES, ids=[c[0] for c in _CASES])  # fixed: hr locative scope
def test_locative_ordinal_weekday(phrase, y, m, o):
    gold = _nth_monday(y, m, o)
    r = parse(phrase)
    assert r is not None, phrase
    assert r[0].start == AstroDate(gold.year, gold.month, gold.day), phrase
