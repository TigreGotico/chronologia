# -*- coding: utf-8 -*-
"""Second-pass oracle sweep: "Nth <weekday> of <month> <year>" (bg), a FRESH
(month, year) grid disjoint from test_nl_ordinal_weekday_sweep.py so no
phrase is duplicated across the corpus.

"четвърти петък на май 2022" -- lit. "fourth Friday of May 2022". Gold is an
independent calendar walk (:func:`_nth_weekday`); the parser is never
consulted for the expected value. Combos whose Nth occurrence does not exist
in that month are dropped at parametrize time.

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
ORDINALS = {"първи": 1, "втори": 2, "трети": 3, "четвърти": 4, "пети": 5}

# disjoint from the GRID in test_nl_ordinal_weekday_sweep.py
GRID = [(2, 2018), (2, 2019), (2, 2020), (2, 2021),
        (5, 2018), (5, 2019), (5, 2021), (5, 2022), (5, 2024),
        (6, 2020), (6, 2021), (6, 2022), (6, 2024), (6, 2025), (6, 2026),
        (9, 2019), (9, 2020), (9, 2022), (9, 2023), (9, 2024),
        (11, 2019), (11, 2020), (11, 2021), (11, 2024),
        (12, 2019), (12, 2020), (12, 2021), (12, 2022),
        (1, 2023), (1, 2024), (3, 2022), (3, 2023)]


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
def test_nth_weekday_of_month_resweep(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
