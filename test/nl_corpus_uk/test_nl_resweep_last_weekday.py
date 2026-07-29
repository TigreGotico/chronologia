# -*- coding: utf-8 -*-
"""Second-pass sweep: "останній/остання <weekday> <month(gen)> <year>" (uk).

Extends test_nl_last_weekday_of_month.py (2 pinned cases) into a full sweep
over 7 weekdays x 12 months x 4 fresh years (2023-2026). Gold is the last
occurrence of the named weekday in the named month, found by pure calendar
walk -- never the parser. Anchor Tue 2017-06-27 13:04.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse

_WEEKDAYS = {
    "понеділок": (0, "m"),
    "вівторок": (1, "m"),
    "середа": (2, "f"),
    "четвер": (3, "m"),
    "п’ятниця": (4, "f"),
    "субота": (5, "f"),
    "неділя": (6, "f"),
}

_LAST = {"m": "останній", "f": "остання"}

_MONTHS_GEN = [
    None, "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
]

_YEARS = (2023, 2024, 2025, 2026)


def _last_weekday(y, m, wd):
    last = calendar.monthrange(y, m)[1]
    for d in range(last, 0, -1):
        if date(y, m, d).weekday() == wd:
            return date(y, m, d)
    raise AssertionError((y, m, wd))


_CASES = []
for _wd_name, (_idx, _gender) in _WEEKDAYS.items():
    for _m in range(1, 13):
        for _y in _YEARS:
            _phrase = f"{_LAST[_gender]} {_wd_name} {_MONTHS_GEN[_m]} {_y}"
            _gold = _last_weekday(_y, _m, _idx)
            _CASES.append((_phrase, _gold))


@pytest.mark.parametrize("phrase,gold", _CASES)
def test_last_weekday_of_month_fresh_years(phrase, gold):
    nxt = gold + timedelta(days=1)
    r = parse(phrase)
    assert r[0].start == AstroDate(gold.year, gold.month, gold.day), phrase
    assert r[0].end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
    assert r[1] == "", phrase
