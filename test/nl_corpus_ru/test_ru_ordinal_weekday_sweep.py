# -*- coding: utf-8 -*-
"""Ordinal-weekday-of-month sweep (ru) -- "N-й <weekday> <month> <year>".

Russian names the Nth weekday of a month with a plain genitive month after a
gender-agreeing ordinal: "третий понедельник марта 2020" (3rd Monday of March
2020).  The ordinal agrees with the weekday-noun's grammatical gender --
masculine for понедельник/вторник/четверг, feminine for среда/пятница/суббота,
neuter for воскресенье.

Gold is an independent calendar walk (``_nth_weekday`` below), never the
parser.  Only ordinals 1..4 are swept -- the "последний" (last) reading is
broken in the engine (see the xfail marker in ``test_last_weekday_broken``)
and is deferred.  Anchor 2017-06-27."""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

# genitive month names, index == month number
_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

# weekday noun -> (weekday index Mon=0, grammatical gender)
_WEEKDAYS = {
    "понедельник": (0, "m"),
    "вторник": (1, "m"),
    "среда": (2, "f"),
    "четверг": (3, "m"),
    "пятница": (4, "f"),
    "суббота": (5, "f"),
    "воскресенье": (6, "n"),
}

# ordinal number -> gender -> word
_ORD = {
    1: {"m": "первый", "f": "первая", "n": "первое"},
    2: {"m": "второй", "f": "вторая", "n": "второе"},
    3: {"m": "третий", "f": "третья", "n": "третье"},
    4: {"m": "четвёртый", "f": "четвёртая", "n": "четвёртое"},
}

_YEARS = (2018, 2019, 2020, 2021, 2022, 2023)


def _nth_weekday(year, month, weekday, n):
    """Independent oracle: date of the n-th <weekday> of month, or None."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    day = 1 + offset + (n - 1) * 7
    # every month has at least 4 of each weekday, so n<=4 is always valid
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


@pytest.mark.parametrize("text,y,m,dd", _cases())
def test_ordinal_weekday_of_month(text, y, m, dd):
    st, en = start_end(text)
    assert st == AstroDate(y, m, dd)
    nxt = date(y, m, dd) + timedelta(days=1)
    assert en == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.xfail(reason="'последний' (last weekday) mis-parses: the ordinal "
                          "is dropped and residue leaks -- deferred.",
                   strict=True)
def test_last_weekday_broken():
    # последний понедельник мая 2020 -> should be 2020-05-25; engine returns a
    # bogus anchor-relative span with 'последний мая 2020' residue.
    st, _ = start_end("последний понедельник мая 2020")
    assert st == AstroDate(2020, 5, 25)
