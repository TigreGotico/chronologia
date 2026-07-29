# -*- coding: utf-8 -*-
"""Second-pass sweep: Slovak month-thirds "začiatok / polovica / koniec
<month(gen)> <year>", fresh years.

test_sk_month_thirds_sweep.py covers years 2019, 2020, 2022, 2025 (a subset
of months for the year-qualified form). This sweep runs every month of five
fresh years (2016, 2017, 2023, 2024, 2028) that do not overlap. Bounds are a
month's exact ``timedelta`` divided by three, computed independently of the
parser -- never read from its own output."""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_GEN = [None, "januára", "februára", "marca", "apríla", "mája", "júna",
        "júla", "augusta", "septembra", "októbra", "novembra", "decembra"]

_WORD = {"začiatok": 0, "polovica": 1, "koniec": 2}
_YEARS = (2016, 2017, 2023, 2024, 2028)


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


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("word", list(_WORD))
@pytest.mark.parametrize("m", range(1, 13))
def test_third_with_year_fresh(word, m, year):
    text = f"{word} {_GEN[m]} {year}"
    assert start_end(text) == _expected(word, year, m), text
