# -*- coding: utf-8 -*-
"""Last-weekday-of-month sweep with explicit year (ru), all weekdays x months.

"последний <weekday> <month> <year>" selects the FINAL occurrence of the named
weekday inside the named month/year.  Round 1 pinned only two spot cases; this
file sweeps every weekday across every month and several years.

The "last" determiner agrees with the weekday-noun's grammatical gender:
  masculine  (последний):  понедельник, вторник, четверг
  feminine   (последняя):  среда, пятница, суббота
  neuter     (последнее):  воскресенье

Gold is an independent backward calendar walk from the last day of the month,
never the parser.  Anchor 2017-06-27.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

# weekday noun -> (weekday index Mon=0, gender-agreeing "last" word)
_WEEKDAYS = {
    "понедельник": (0, "последний"),
    "вторник": (1, "последний"),
    "среда": (2, "последняя"),
    "четверг": (3, "последний"),
    "пятница": (4, "последняя"),
    "суббота": (5, "последняя"),
    "воскресенье": (6, "последнее"),
}

_YEARS = (2018, 2019, 2020, 2021, 2022, 2023)


def _last_weekday(y, m, wd):
    last = calendar.monthrange(y, m)[1]
    for d in range(last, 0, -1):
        if date(y, m, d).weekday() == wd:
            return date(y, m, d)
    raise AssertionError((y, m, wd))


def _cases():
    out = []
    for noun, (wd, last_word) in _WEEKDAYS.items():
        for m in range(1, 13):
            for y in _YEARS:
                text = f"{last_word} {noun} {_MONTHS_GEN[m]} {y}"
                out.append((text, y, m, wd))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m,wd", _CASES, ids=[c[0] for c in _CASES])
def test_last_weekday_of_month_year(text, y, m, wd):
    gold = _last_weekday(y, m, wd)
    st, en = start_end(text)
    assert st == AstroDate(gold.year, gold.month, gold.day), text
    nxt = gold + timedelta(days=1)
    assert en == AstroDate(nxt.year, nxt.month, nxt.day), text
