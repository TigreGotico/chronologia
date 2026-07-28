# -*- coding: utf-8 -*-
"""Scoped ordinal "Nth <weekday> of <month> <year>" sweep (uk).

Binds ORDINAL + WEEKDAY + MONTH(gen) + YEAR into the nth-weekday-of-the-named
month, a one-day span.  The Ukrainian ordinal agrees in gender with the weekday
noun (masc. понеділок/вівторок/четвер -> перший/другий/третій/четвертий;
fem. середа/п'ятниця/субота/неділя -> перша/друга/третя/четверта).

Gold is the nth matching weekday found by pure ``calendar`` arithmetic that
never touches the parser: locate the first day of the month carrying the target
weekday, then step ``(n-1)`` whole weeks forward.  Anchor Tue 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, start

# weekday counting-noun -> (Mon=0 .. Sun=6 index, gender 'm'/'f')
_WEEKDAYS = {
    "понеділок": (0, "m"),
    "вівторок": (1, "m"),
    "середа": (2, "f"),
    "четвер": (3, "m"),
    "п’ятниця": (4, "f"),
    "субота": (5, "f"),
    "неділя": (6, "f"),
}

_ORD = {
    1: {"m": "перший", "f": "перша"},
    2: {"m": "другий", "f": "друга"},
    3: {"m": "третій", "f": "третя"},
    4: {"m": "четвертий", "f": "четверта"},
}

_MONTHS_GEN = [
    None, "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
]

_YEARS = (2020, 2021, 2022)


def _nth_weekday(year, month, wd_index, n):
    """The date of the nth (1..4) ``wd_index`` weekday in ``year``/``month``."""
    first = date(year, month, 1)
    offset = (wd_index - first.weekday()) % 7
    d = first + timedelta(days=offset + (n - 1) * 7)
    assert d.month == month  # n<=4 always lands inside the month
    return d


_CASES = []
for _wd_name, (_idx, _gender) in _WEEKDAYS.items():
    for _n in (1, 2, 3, 4):
        for _m in range(1, 13):
            for _y in _YEARS:
                _ord = _ORD[_n][_gender]
                _phrase = f"{_ord} {_wd_name} {_MONTHS_GEN[_m]} {_y}"
                _gold = _nth_weekday(_y, _m, _idx, _n)
                _CASES.append((_phrase, _gold))


@pytest.mark.parametrize("phrase,gold", _CASES)
def test_nth_weekday_of_month(phrase, gold):
    nxt = gold + timedelta(days=1)
    r = parse(phrase)
    assert r[0].start == AstroDate(gold.year, gold.month, gold.day), phrase
    assert r[0].end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert r[1] == "", phrase
