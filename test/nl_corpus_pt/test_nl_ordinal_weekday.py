# -*- coding: utf-8 -*-
""""a primeira segunda-feira de março", "o último domingo de junho": the
nth (or last) occurrence of a named weekday within a named month.

The gold day is found by independent arithmetic -- enumerate every day of the
month whose ``weekday()`` matches, then index the nth (or the last) -- and is
never read back from the parser.  The span is the whole day.

Two ordinals are deliberately absent from the count position: "segunda" and
"quarta" are also the weekday nouns Monday and Wednesday, so "a segunda
terça-feira" cannot be licensed as "the second Tuesday" without stealing the
Monday reading the language also has.  Those homographs are covered as a known
limitation in the campaign notes, not asserted here; this file uses only the
ordinals with no weekday twin -- primeiro/-a, terceiro/-a, último/-a -- so
every case has one unambiguous reading.

[[EP vs BP]]: the ordinal + "-feira" weekday construction is shared; nothing
here is norm-specific.  Bare named month resolves within the anchor's year
2017 (anchor Tuesday 2017-06-27).
"""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, span, start_end, parse

_MONTHS = {1: "janeiro", 3: "março", 6: "junho", 9: "setembro", 11: "novembro"}
_WD = {"segunda": 0, "terça": 1, "quarta": 2, "quinta": 3,
       "sexta": 4, "sábado": 5, "domingo": 6}
#: ordinal surface -> (article, nth) ; nth = -1 means "the last"
_ORD = {"primeiro": ("o", 1), "primeira": ("a", 1),
        "terceiro": ("o", 3), "terceira": ("a", 3),
        "último": ("o", -1), "última": ("a", -1)}

_YEAR = 2017


def _nth_weekday(month, weekday, n):
    days = [d for d in range(1, monthrange(_YEAR, month)[1] + 1)
            if datetime(_YEAR, month, d).weekday() == weekday]
    return days[n - 1] if n > 0 else days[-1]


def _cases():
    out = []
    for ordinal, (art, n) in _ORD.items():
        for wname, wd in _WD.items():
            surface = f"{wname}-feira" if wname not in ("sábado", "domingo") else wname
            for m in _MONTHS:
                text = f"{art} {ordinal} {surface} de {_MONTHS[m]}"
                out.append((text, m, wd, n))
    return out


@pytest.mark.parametrize("text,month,weekday,n", _cases())
def test_nth_weekday_of_month(text, month, weekday, n):
    day = _nth_weekday(month, weekday, n)
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (_YEAR, month, day), f"{text!r} -> {s}"
    assert span(text).width == timedelta(days=1)
    assert parse(text)[1] == "", f"unconsumed rest in {text!r}"


def test_last_is_not_the_fourth_when_month_has_five():
    """"o último domingo de junho" is the 4th here, but the rule is "last",
    so a five-Sunday month must still land on the fifth."""
    # July 2017 has Sundays 2,9,16,23,30 -> last == 30
    s, _ = start_end("o último domingo de julho")
    assert (s.month, s.day) == (7, 30)
