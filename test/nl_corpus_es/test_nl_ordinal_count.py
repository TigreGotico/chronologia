"""Ordinal counting from the anchor (feature 2), Spanish.

"3 viernes a partir de ahora" = the 3rd viernes strictly after now; "el fin
de semana después del próximo" = the weekend after next.  Anchor 2017-06-27
(martes, weekday index 1).  Spanish weekday names ending in -es are
invariant in the plural, so no plural strip is needed.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start, nomatch

_MID = ANCHOR.replace(hour=0, minute=0)
_WD = {"lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
       "viernes": 4, "sábado": 5, "domingo": 6}


def _nth(weekday, n):
    ahead = (_WD[weekday] - ANCHOR.weekday()) % 7 or 7
    d = _MID + timedelta(days=ahead + 7 * (n - 1))
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,wd,n", [
    ("1 viernes a partir de ahora", "viernes", 1),
    ("2 viernes a partir de ahora", "viernes", 2),
    ("3 viernes a partir de ahora", "viernes", 3),
    ("2 lunes a partir de ahora", "lunes", 2),
    ("4 lunes a partir de ahora", "lunes", 4),
    ("3 martes a partir de ahora", "martes", 3),
    ("2 jueves a partir de ahora", "jueves", 2),
    ("5 domingos a partir de ahora", "domingo", 5),
    ("2 sábados a partir de ahora", "sábado", 2),
    ("3 miércoles a partir de ahora", "miércoles", 3),
])
def test_weekdays_from_now(text, wd, n):
    assert start(text) == _nth(wd, n)


def test_weekend_after_next():
    s = span("el fin de semana después del próximo")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)


def test_count_is_day_wide():
    assert span("3 viernes a partir de ahora").width == timedelta(days=1)


@pytest.mark.parametrize("text", [
    "3 viernes",                        # no from-now marker
    "viernes a partir de ahora",        # no count
])
def test_no_marker_falls_back_to_bare_weekday(text):
    # without the full "<N> <weekday> a partir de ahora" shape the count does
    # NOT fire; the bare weekday still resolves to its next occurrence
    # (2017-06-30), never the N-th.
    assert start(text) == AstroDate(2017, 6, 30)
