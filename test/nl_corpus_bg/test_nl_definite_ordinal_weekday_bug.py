# -*- coding: utf-8 -*-
"""BUG guard: definite-article ordinal + weekday-of-month does NOT bind (bg).

The short ordinal forms bind correctly ("трети понеделник на март 2019" -> the
3rd Monday), but the definite masculine long forms ("първият", "вторият",
"третият") silently DROP the weekday and the whole month/year tail: the
weekday token is stranded in the residue and a bogus anchor-relative day is
returned instead.  Reproductions (anchor 2017-06-27):

    "първият понеделник на март 2019"  -> 2017-07-03, residue "първият на март 2019"
    "третият вторник на юни 2017"      -> 2017-07-04, residue "третият на юни 2017"

These are pinned as strict xfails so the corpus never ships a wrong gold; when
the definite-article path is wired to bind like the short forms, these flip to
XPASS and must be promoted to real assertions.
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


@pytest.mark.xfail(reason="definite-article ordinal drops the weekday; "
                          "ordinal-weekday-of-month does not bind (BUG)",
                   strict=True)
@pytest.mark.parametrize("phrase,gold", CASES, ids=[c[0] for c in CASES])
def test_definite_ordinal_weekday_binds(phrase, gold):
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
