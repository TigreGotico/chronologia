# -*- coding: utf-8 -*-
"""German meteorological seasons with an explicit year, across many years.

Northern-hemisphere meteorological boundaries: Frühling = Mar-May, Sommer =
Jun-Aug, Herbst = Sep-Nov, Winter = Dec-Feb (of the following year). The oracle
is fixed arithmetic on those month boundaries. The optional article ("der
Frühling 2019") must not change the span. Years here are chosen to avoid the
four cases already pinned in ``test_de_scoped_seasons_fuzzy.py``
(sommer 2020, frühling 2021, winter 2020, herbst 2019).

Anchor 2017-06-27.
"""
import pytest

from ._corpus import AstroDate, start_end

# season -> (start_month, end_month_exclusive, end_rolls_to_next_year)
_SEASON = {
    "frühling": (3, 6, False),
    "sommer": (6, 9, False),
    "herbst": (9, 12, False),
    "winter": (12, 3, True),
}

_YEARS = [2016, 2017, 2018, 2022, 2023, 2024, 2025]

_CASES = []
for _s, (_m0, _m1, _roll) in _SEASON.items():
    for _y in _YEARS:
        _start = AstroDate(_y, _m0, 1)
        _end = AstroDate(_y + 1 if _roll else _y, _m1, 1)
        _CASES.append((f"{_s} {_y}", _start, _end))
        _CASES.append((f"der {_s} {_y}", _start, _end))  # article is inert


@pytest.mark.parametrize("text,s,e", _CASES)
def test_season_of_year(text, s, e):
    assert start_end(text) == (s, e), f"{text!r}"
