# -*- coding: utf-8 -*-
"""Ordinal-weekday-of-month sweep (nl): "de <ord> <weekday> van <maand> <jaar>".

The gold date is produced by an independent calendar walk (:func:`nth_weekday`)
that never consults the parser: it lands on the first day of the named month
carrying the target weekday, then steps forward whole weeks.  Combinations
whose n-th occurrence would spill into the following month simply do not exist
and are dropped from the sweep -- the parser returns ``None`` for those (see
:func:`test_nonexistent_fifth_is_no_match`), so asserting a date would be
dishonest.

Ordinals eerste..vijfde bind, and so does "laatste" (last) -- the last-of-month
reading is exercised below.

Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, span, start

# Dutch ordinal word -> n
_ORD = {"eerste": 1, "tweede": 2, "derde": 3, "vierde": 4, "vijfde": 5}
# Dutch weekday word -> python weekday() index (Mon=0 .. Sun=6)
_WD = {
    "maandag": 0, "dinsdag": 1, "woensdag": 2, "donderdag": 3,
    "vrijdag": 4, "zaterdag": 5, "zondag": 6,
}
_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
_YEARS = [2018, 2019, 2020, 2021, 2022, 2023]


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
def test_ordinal_weekday_of_month(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = datetime(gold.year, gold.month, gold.day) + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert parse(phrase)[1] == "", phrase


@pytest.mark.parametrize("phrase", [
    "de vijfde maandag van februari 2021",   # Feb 2021: only 4 Mondays
    "de vijfde zondag van juni 2021",        # Jun 2021: only 4 Sundays
    "de vijfde zaterdag van april 2020",     # Apr 2020: only 4 Saturdays
])
def test_nonexistent_fifth_is_no_match(phrase):
    # The 5th occurrence does not exist in these months; the parser must not
    # invent a date. Confirmed independently: the calendar walk returns None.
    word = phrase.split()[2]
    mname = phrase.split()[4]
    year = int(phrase.split()[5])
    mi = _MONTHS.index(mname) + 1
    assert nth_weekday(year, mi, _WD[word], 5) is None
    assert parse(phrase) is None


def test_laatste_weekday_of_month_binds():
    # "de laatste zaterdag van augustus" binds the last-of-month reading.
    # Gold (independent): last Saturday of August 2019 = 2019-08-31.
    assert start("de laatste zaterdag van augustus 2019") == AstroDate(2019, 8, 31)
