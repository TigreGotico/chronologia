# -*- coding: utf-8 -*-
"""Fixed-date feast + explicit-year sweep (uk).

Most of these feasts sit on the same Gregorian day every year, so "<feast>
<year>" resolves to that exact day.

Christmas (Різдво) and its Eve (Святвечір) are the exception: they MOVED with
the Orthodox Church of Ukraine's calendar switch -- the Julian feast (7 / 6
January) through 2022, the Gregorian 25 / 24 December from 2023 (Law No.
3258-IX; porting reference vacanza's ukraine.py, MIT). The past is exact, so the
gold below is the date actually in force for each queried year, computed
independently of the parser. Anchor Tue 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse, span, start

# feasts on a constant Gregorian day every year
_FIXED = {
    "новий рік": (1, 1),
    "день святого валентина": (2, 14),
    "гелловін": (10, 31),
}


def _christmas(year):
    return (12, 25) if year >= 2023 else (1, 7)


def _christmas_eve(year):
    return (12, 24) if year >= 2023 else (1, 6)


_YEARS = range(2018, 2028)

_CASES = []
for _name, (_m, _d) in _FIXED.items():
    for _y in _YEARS:
        _CASES.append((f"{_name} {_y}", _y, _m, _d))
for _y in _YEARS:
    _CASES.append((f"різдво {_y}", _y, *_christmas(_y)))
    _CASES.append((f"святвечір {_y}", _y, *_christmas_eve(_y)))


@pytest.mark.parametrize("phrase,y,m,d", _CASES)
def test_fixed_feast_with_year(phrase, y, m, d):
    assert start(phrase) == AstroDate(y, m, d), phrase
    assert span(phrase).width == timedelta(days=1), phrase
