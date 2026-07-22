"""Ordinal counting from the anchor (feature 2), French.

"3 vendredis à partir de maintenant" = the 3rd vendredi strictly after now;
"le week-end après le prochain" = skip the next weekend, take the following.
Anchor 2017-06-27 (mardi, weekday index 1).  The past-order idiom ("il y a
N ...") is a different word order, out of scope for this pass.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start, nomatch

_MID = ANCHOR.replace(hour=0, minute=0)
_WD = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
       "vendredi": 4, "samedi": 5, "dimanche": 6}


def _nth(weekday, n):
    ahead = (_WD[weekday] - ANCHOR.weekday()) % 7 or 7
    d = _MID + timedelta(days=ahead + 7 * (n - 1))
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,wd,n", [
    ("1 vendredi à partir de maintenant", "vendredi", 1),
    ("2 vendredis à partir de maintenant", "vendredi", 2),
    ("3 vendredis à partir de maintenant", "vendredi", 3),
    ("2 lundis à partir de maintenant", "lundi", 2),
    ("4 lundis à partir de maintenant", "lundi", 4),
    ("3 mardis à partir de maintenant", "mardi", 3),
    ("2 mercredis à partir de maintenant", "mercredi", 2),
    ("3 jeudis à partir de maintenant", "jeudi", 3),
    ("2 samedis à partir de maintenant", "samedi", 2),
    ("5 dimanches à partir de maintenant", "dimanche", 5),
])
def test_weekdays_from_now(text, wd, n):
    assert start(text) == _nth(wd, n)


def test_weekend_after_next():
    s = span("le week-end après le prochain")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)


def test_count_is_day_wide():
    assert span("3 vendredis à partir de maintenant").width == timedelta(days=1)


@pytest.mark.parametrize("text", [
    "3 vendredis",                          # no from-now marker
    "vendredis à partir de maintenant",     # no count
])
def test_no_count_no_match(text):
    nomatch(text)
