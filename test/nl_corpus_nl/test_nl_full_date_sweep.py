# -*- coding: utf-8 -*-
"""Full calendar-date sweep (nl): "<dag> <maand> <jaar>" -> a one-day span.

Days are chosen per month from a representative set plus that month's true
last day (via ``calendar.monthrange``), so February 28/29 and the 30/31-day
month ends are all exercised. Every gold date is a literal; the span is the
single named day [D, D+1). Anchor 2017-06-27.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, span

_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
_YEARS = [2019, 2020, 2021]
_SAMPLE_DAYS = [1, 7, 13, 15, 22, 28]


def _build():
    cases = []
    for y in _YEARS:
        for mi, mname in enumerate(_MONTHS, start=1):
            last = calendar.monthrange(y, mi)[1]
            days = sorted(set(_SAMPLE_DAYS + [last]))
            for d in days:
                if d > last:
                    continue
                cases.append((f"{d} {mname} {y}", date(y, mi, d)))
    return cases


_CASES = _build()


@pytest.mark.parametrize("phrase,gold", _CASES, ids=[c[0] for c in _CASES])
def test_full_date(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert parse(phrase)[1] == "", phrase
