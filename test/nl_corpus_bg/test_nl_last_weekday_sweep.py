# -*- coding: utf-8 -*-
"""Oracle sweep: "last <weekday> of <month> <year>" binds the final
occurrence of the named weekday inside the named month (bg).

Both the short determiner "последен" and its definite form "последният"
select the last matching weekday.  Gold is an independent calendar walk
(:func:`_last_weekday`) over every (surface, weekday, month, year)
combination -- never the parser.  The (month, year) grid deliberately avoids
the two phrases already pinned in test_nl_last_weekday_of_month.py.

Anchor 2017-06-27 (Tuesday, 13:04).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

MONTHS = ["", "януари", "февруари", "март", "април", "май", "юни", "юли",
          "август", "септември", "октомври", "ноември", "декември"]
WEEKDAYS = {"понеделник": 0, "вторник": 1, "сряда": 2, "четвъртък": 3,
            "петък": 4, "събота": 5, "неделя": 6}
SURFACES = ["последен", "последният"]
GRID = [(1, 2019), (4, 2020), (7, 2021), (10, 2022), (2, 2023),
        (3, 2024), (8, 2025), (11, 2026), (9, 2018)]


def _last_weekday(y, m, wd):
    days = [d for d in range(1, calendar.monthrange(y, m)[1] + 1)
            if date(y, m, d).weekday() == wd]
    return date(y, m, days[-1])


def _cases():
    out = []
    for surface in SURFACES:
        for wd_word, wd in WEEKDAYS.items():
            for m, y in GRID:
                gold = _last_weekday(y, m, wd)
                phrase = f"{surface} {wd_word} на {MONTHS[m]} {y}"
                out.append((phrase, gold))
    return out


CASES = _cases()


@pytest.mark.parametrize("phrase,gold", CASES, ids=[c[0] for c in CASES])
def test_last_weekday_of_month(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
