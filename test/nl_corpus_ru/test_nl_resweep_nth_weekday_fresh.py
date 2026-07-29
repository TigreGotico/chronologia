# -*- coding: utf-8 -*-
"""Second-pass sweep: Nth-weekday-of-month (ru), fresh years.

Round 1 (``test_ru_ordinal_weekday_sweep``) swept ordinals 1..4 across all
weekdays and months for years 2018..2023.  This file re-sweeps the identical
grammar with FRESH years (2024, 2025, 2026) that round 1 never touched, so no
case duplicates an existing parametrize id.

"<ordinal> <weekday> <month-genitive> <year>" selects the N-th occurrence of
the named weekday inside the named month/year.  The ordinal agrees in gender
with the weekday noun:
  masculine  (-ый/-ой forms): понедельник, вторник, четверг
  feminine   (-ая forms):     среда, пятница, суббота
  neuter     (-ое form):      воскресенье

Gold is an independent forward calendar walk (``_nth_weekday``), never the
parser.  Anchor 2017-06-27 (unused for the explicit-year reading, but the
module contract).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

_WEEKDAYS = {
    "понедельник": (0, "m"),
    "вторник": (1, "m"),
    "среда": (2, "f"),
    "четверг": (3, "m"),
    "пятница": (4, "f"),
    "суббота": (5, "f"),
    "воскресенье": (6, "n"),
}

_ORD = {
    1: {"m": "первый", "f": "первая", "n": "первое"},
    2: {"m": "второй", "f": "вторая", "n": "второе"},
    3: {"m": "третий", "f": "третья", "n": "третье"},
    4: {"m": "четвёртый", "f": "четвёртая", "n": "четвёртое"},
}

# fresh years -- disjoint from round-1's (2018, 2019, 2020, 2021, 2022, 2023)
_YEARS = (2024, 2025, 2026)


def _nth_weekday(year, month, weekday, n):
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    day = 1 + offset + (n - 1) * 7
    return date(year, month, day)


def _cases():
    out = []
    for wd_word, (wd_idx, gender) in _WEEKDAYS.items():
        for n in (1, 2, 3, 4):
            ord_word = _ORD[n][gender]
            for month in range(1, 13):
                for year in _YEARS:
                    d = _nth_weekday(year, month, wd_idx, n)
                    text = f"{ord_word} {wd_word} {_MONTHS_GEN[month]} {year}"
                    out.append((text, d.year, d.month, d.day))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m,dd", _CASES, ids=[c[0] for c in _CASES])
def test_ordinal_weekday_of_month_fresh(text, y, m, dd):
    st, en = start_end(text)
    assert st == AstroDate(y, m, dd), text
    nxt = date(y, m, dd) + timedelta(days=1)
    assert en == AstroDate(nxt.year, nxt.month, nxt.day)
