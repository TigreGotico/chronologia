# -*- coding: utf-8 -*-
"""Oracle sweep: "Nth <weekday> of <month> <year>" binds the Nth occurrence
of the named weekday inside the named month (bg, short-form ordinals).

Bulgarian uses the preposition "на" (of) with a short masculine ordinal:
"трети понеделник на март 2019" -- lit. "third Monday of March 2019".  Gold
is an independent calendar walk (:func:`_nth_weekday`) over every
(ordinal, weekday, month, year) combination; phrases whose Nth occurrence
does not exist in that month are dropped at parametrize time so every emitted
case is a real date.  The parser is never consulted for the expected value.

Anchor 2017-06-27 (Tuesday, 13:04); the year is always explicit so each span
is deterministic.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

MONTHS = ["", "януари", "февруари", "март", "април", "май", "юни", "юли",
          "август", "септември", "октомври", "ноември", "декември"]
WEEKDAYS = {"понеделник": 0, "вторник": 1, "сряда": 2, "четвъртък": 3,
            "петък": 4, "събота": 5, "неделя": 6}
ORDINALS = {"първи": 1, "втори": 2, "трети": 3, "четвърти": 4, "пети": 5}
GRID = [(1, 2018), (3, 2019), (5, 2020), (9, 2021), (11, 2022), (2, 2024),
        (4, 2025), (6, 2019), (7, 2020), (8, 2021), (10, 2023), (12, 2026)]


def _nth_weekday(y, m, wd, n):
    days = [d for d in range(1, calendar.monthrange(y, m)[1] + 1)
            if date(y, m, d).weekday() == wd]
    return date(y, m, days[n - 1]) if len(days) >= n else None


def _cases():
    out = []
    for wd_word, wd in WEEKDAYS.items():
        for ord_word, n in ORDINALS.items():
            for m, y in GRID:
                gold = _nth_weekday(y, m, wd, n)
                if gold is None:
                    continue
                phrase = f"{ord_word} {wd_word} на {MONTHS[m]} {y}"
                out.append((phrase, gold))
    return out


CASES = _cases()


@pytest.mark.parametrize("phrase,gold", CASES, ids=[c[0] for c in CASES])
def test_ordinal_weekday_of_month(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
