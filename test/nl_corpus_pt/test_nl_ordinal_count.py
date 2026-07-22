"""Ordinal counting from the anchor (feature 2), Portuguese.

"3 sextas a partir de agora" = the 3rd sexta strictly after now; "o fim de
semana depois do próximo" = the weekend after next.  Anchor 2017-06-27
(terça, weekday index 1).  The short weekday form ("sexta") plus a stripped
plural "s" binds the weekday.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start, nomatch

_MID = ANCHOR.replace(hour=0, minute=0)
_WD = {"segunda": 0, "terça": 1, "quarta": 2, "quinta": 3,
       "sexta": 4, "sábado": 5, "domingo": 6}


def _nth(weekday, n):
    ahead = (_WD[weekday] - ANCHOR.weekday()) % 7 or 7
    d = _MID + timedelta(days=ahead + 7 * (n - 1))
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,wd,n", [
    ("1 sexta a partir de agora", "sexta", 1),
    ("2 sextas a partir de agora", "sexta", 2),
    ("3 sextas a partir de agora", "sexta", 3),
    ("2 segundas a partir de agora", "segunda", 2),
    ("4 segundas a partir de agora", "segunda", 4),
    ("3 terças a partir de agora", "terça", 3),
    ("2 quartas a partir de agora", "quarta", 2),
    ("3 quintas a partir de agora", "quinta", 3),
    ("5 domingos a partir de agora", "domingo", 5),
    ("2 sábados a partir de agora", "sábado", 2),
])
def test_weekdays_from_now(text, wd, n):
    assert start(text) == _nth(wd, n)


def test_weekend_after_next():
    s = span("o fim de semana depois do próximo")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)


def test_count_is_day_wide():
    assert span("3 sextas a partir de agora").width == timedelta(days=1)


@pytest.mark.parametrize("text", [
    "3 sextas",                         # no from-now marker
    "sextas a partir de agora",         # no count
])
def test_no_count_no_match(text):
    nomatch(text)
