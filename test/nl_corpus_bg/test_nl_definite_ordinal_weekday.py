# -*- coding: utf-8 -*-
"""Definite-article ordinal + weekday-of-month (bg).

The short ordinal forms bind ("трети понеделник на март 2019" -> the 3rd
Monday), and so now do the definite masculine long forms ("първият",
"вторият", "третият") and their short-article variants ("първия", ...): the
definite surfaces fold to the same digit as the bare ``-и`` ordinal (numfold
``fold_bg``), so ORD+WEEKDAY+MONTH bind and resolve to the true Nth weekday.

Gold is the true Nth weekday of the named month by independent calendar
arithmetic (calendar.monthrange), never the parser.  Definite-article forms:
Официален правопис на българския език (БАН 2012), членуване на редните
числителни имена, мъжки род ед. ч. -- пълен член -ият, кратък член -ия.
"""
import calendar
from datetime import date

import pytest

from ._corpus import AstroDate, span

MONTHS = ["", "януари", "февруари", "март", "април", "май", "юни", "юли",
          "август", "септември", "октомври", "ноември", "декември"]
WEEKDAYS = {"понеделник": 0, "вторник": 1, "петък": 4}
ORDINALS = {"първият": 1, "вторият": 2, "третият": 3}
GRID = [(3, 2019), (6, 2017)]


def _nth_weekday(y, m, wd, n):
    days = [d for d in range(1, calendar.monthrange(y, m)[1] + 1)
            if date(y, m, d).weekday() == wd]
    return date(y, m, days[n - 1]) if len(days) >= n else None


def _cases():
    out = []
    for ord_word, n in ORDINALS.items():
        for wd_word, wd in WEEKDAYS.items():
            for m, y in GRID:
                gold = _nth_weekday(y, m, wd, n)
                if gold is not None:
                    out.append((f"{ord_word} {wd_word} на {MONTHS[m]} {y}", gold))
    return out


CASES = _cases()


@pytest.mark.parametrize("phrase,gold", CASES, ids=[c[0] for c in CASES])
def test_definite_ordinal_weekday_binds(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
