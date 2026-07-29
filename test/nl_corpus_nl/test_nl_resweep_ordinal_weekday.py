# -*- coding: utf-8 -*-
"""Second-pass resweep: ordinal-weekday-of-month (nl), fresh years.

Same shape as :mod:`test_nl_ordinal_weekday_sweep` ("de <ord> <weekday> van
<maand> <jaar>") but over years 2029-2033, which that file does not cover
(it sweeps 2018-2023). The gold date is produced by an independent calendar
walk (:func:`nth_weekday`) that never consults the parser: it lands on the
first day of the named month carrying the target weekday, then steps forward
whole weeks. Combinations whose n-th occurrence would spill into the
following month do not exist and are dropped from the sweep.

Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, span

_ORD = {"eerste": 1, "tweede": 2, "derde": 3, "vierde": 4, "vijfde": 5}
_WD = {
    "maandag": 0, "dinsdag": 1, "woensdag": 2, "donderdag": 3,
    "vrijdag": 4, "zaterdag": 5, "zondag": 6,
}
_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
_YEARS = [2029, 2030, 2031, 2032, 2033]


def nth_weekday(year, month, weekday, n):
    """First day of (year, month) with weekday, plus (n-1) whole weeks.

    Returns None when the n-th occurrence overflows the month."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    day = 1 + offset + (n - 1) * 7
    if day > calendar.monthrange(year, month)[1]:
        return None
    return date(year, month, day)


def _build_cases():
    cases = []
    for year in _YEARS:
        for mi, mname in enumerate(_MONTHS, start=1):
            for wword, wd in _WD.items():
                for oword, n in _ORD.items():
                    gold = nth_weekday(year, mi, wd, n)
                    if gold is None:
                        continue
                    phrase = f"de {oword} {wword} van {mname} {year}"
                    cases.append((phrase, gold))
    return cases


_CASES = _build_cases()


@pytest.mark.parametrize("phrase,gold", _CASES, ids=[c[0] for c in _CASES])
def test_ordinal_weekday_of_month_resweep(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = datetime(gold.year, gold.month, gold.day) + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert parse(phrase)[1] == "", phrase
