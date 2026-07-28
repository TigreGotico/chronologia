# -*- coding: utf-8 -*-
"""Ordinal-weekday-of-named-month for Polish, swept across ordinals 1st-5th,
all seven weekdays (with correct masculine/feminine ordinal agreement), all
twelve genitive month names and several years.

Shape: ``ORD WEEKDAY MONTH(gen) YEAR`` -- e.g. "trzeci poniedziałek marca 2020"
binds ORD+WEEKDAY+MONTH+YEAR into the nth-weekday-of-that-month span, a single
calendar day.  The expected date is computed here by pure calendar arithmetic
(``date`` walking from the 1st of the month) and never read back from the
parser.  Combinations where the nth weekday does not exist in that month
(e.g. a 5th Monday that spills into the next month) are excluded, because the
engine correctly returns no match for them.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, datetime

import pytest

from ._corpus import AstroDate, parse, start

#: masculine / feminine ordinal surfaces, indexed 1..5.
_ORD_M = ["pierwszy", "drugi", "trzeci", "czwarty", "piąty"]
_ORD_F = ["pierwsza", "druga", "trzecia", "czwarta", "piąta"]

#: weekday surface, grammatical gender, python weekday index (Mon=0).
_WD = [
    ("poniedziałek", "m", 0),
    ("wtorek", "m", 1),
    ("środa", "f", 2),
    ("czwartek", "m", 3),
    ("piątek", "m", 4),
    ("sobota", "f", 5),
    ("niedziela", "f", 6),
]

#: genitive month names, index 1..12.
_MON = [
    "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
    "lipca", "sierpnia", "września", "października", "listopada", "grudnia",
]

_YEARS = (2020, 2021, 2022)


def _nth_weekday(year, month, wd, n):
    """The date of the nth (1-based) weekday `wd` in month, or None if it does
    not fall within that month.  Pure arithmetic -- no parser involved."""
    first = date(year, month, 1)
    offset = (wd - first.weekday()) % 7
    day = 1 + offset + 7 * (n - 1)
    try:
        cand = date(year, month, day)
    except ValueError:
        return None
    return cand if cand.month == month else None


def _cases():
    out = []
    for year in _YEARS:
        for mi, mon in enumerate(_MON, 1):
            for wname, gender, wd in _WD:
                ords = _ORD_M if gender == "m" else _ORD_F
                for n in range(1, 6):
                    gold = _nth_weekday(year, mi, wd, n)
                    if gold is None:
                        continue
                    phrase = f"{ords[n - 1]} {wname} {mon} {year}"
                    out.append((phrase, gold))
    return out


_CASES = _cases()


@pytest.mark.parametrize("phrase,gold", _CASES, ids=[c[0] for c in _CASES])
def test_ordinal_weekday_of_month(phrase, gold):
    assert start(phrase) == AstroDate(gold.year, gold.month, gold.day)
    assert parse(phrase)[1] == ""


@pytest.mark.parametrize("phrase,gold", _CASES[::37], ids=[c[0] for c in _CASES[::37]])
def test_ordinal_weekday_is_one_day(phrase, gold):
    from datetime import timedelta
    assert parse(phrase)[0].width == timedelta(days=1)
