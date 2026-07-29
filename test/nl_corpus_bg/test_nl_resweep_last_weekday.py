# -*- coding: utf-8 -*-
"""Second-pass oracle sweep: "last <weekday> of <month> <year>" (bg), a FRESH
(month, year) grid disjoint from test_nl_last_weekday_sweep.py and
test_nl_last_weekday_of_month.py so no phrase is duplicated.

Both the short determiner "последен" and the definite form "последният"
select the final matching weekday in the named month. Gold is an independent
calendar walk (:func:`_last_weekday`), never the parser.

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

# disjoint from the GRIDs in test_nl_last_weekday_sweep.py (and the two
# pairs pinned in test_nl_last_weekday_of_month.py)
GRID = [(1, 2020), (1, 2021), (1, 2022),
        (4, 2019), (4, 2021), (4, 2022),
        (7, 2019), (7, 2020), (7, 2022),
        (10, 2019), (10, 2020), (10, 2021),
        (2, 2019), (2, 2020), (2, 2021),
        (3, 2019), (3, 2020), (3, 2021),
        (11, 2019), (11, 2020),
        (12, 2018), (12, 2019), (12, 2021), (12, 2022),
        (5, 2018), (5, 2019), (5, 2020), (5, 2021), (6, 2018), (6, 2019)]


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
def test_last_weekday_of_month_resweep(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
