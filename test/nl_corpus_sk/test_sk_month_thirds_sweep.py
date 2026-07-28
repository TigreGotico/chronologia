# -*- coding: utf-8 -*-
"""Slovak month-thirds: "začiatok / polovica / koniec marca".

A month splits into three equal thirds: the opening ("začiatok"), the middle
("polovica") and the close ("koniec").  Each third is one-third of the month's
exact length, so the internal boundaries carry a time-of-day (a 31-day month
divides at 10 d 8 h).  A bare month-third names the month in the anchor's own
year (no roll); an explicit year overrides it.  All bounds are computed by
dividing the month's ``timedelta`` by three -- never read from the parser.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end, ANCHOR

_GEN = [None, "januára", "februára", "marca", "apríla", "mája", "júna",
        "júla", "augusta", "septembra", "októbra", "novembra", "decembra"]

_WORD = {"začiatok": 0, "polovica": 1, "koniec": 2}


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def _third_bounds(y, m):
    start = datetime(y, m, 1)
    end = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    third = (end - start) / 3
    b = [start, start + third, start + 2 * third, end]
    return [(b[i], b[i + 1]) for i in range(3)]


def _expected(word, y, m):
    lo, hi = _third_bounds(y, m)[_WORD[word]]
    return _ad(lo), _ad(hi)


@pytest.mark.parametrize("word", list(_WORD))
@pytest.mark.parametrize("m", range(1, 13))
def test_third_bare_current_year(word, m):
    """No year: the month falls in the anchor's own year, no roll."""
    text = f"{word} {_GEN[m]}"
    assert start_end(text) == _expected(word, ANCHOR.year, m), text


@pytest.mark.parametrize("year", [2019, 2020, 2022, 2025])
@pytest.mark.parametrize("word", list(_WORD))
@pytest.mark.parametrize("m", (2, 3, 4, 6, 11))
def test_third_with_year(word, m, year):
    text = f"{word} {_GEN[m]} {year}"
    assert start_end(text) == _expected(word, year, m), text
