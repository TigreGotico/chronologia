# -*- coding: utf-8 -*-
"""Fixed-date Greek feasts pinned to an explicit year. Only feasts whose civil
date is calendar-fixed (Revised-Julian == Gregorian) are swept here; the gold
is the constant (month, day) placed in the requested year. Movable Orthodox
Easter is covered separately in ``test_nl_holiday_ref``; the national holidays
written with an ordinal prefix ("25η Μαρτίου", "28η Οκτωβρίου") are NOT covered
because that ordinal form does not bind (see the native-review BUG list).
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import span, start

A = datetime(2017, 6, 27, 13, 4)

# feast name -> fixed (month, day)
FIXED = {
    "πρωτοχρονιά": (1, 1),      # New Year's Day
    "θεοφάνεια": (1, 6),        # Epiphany
    "χριστούγεννα": (12, 25),   # Christmas
}
_YEARS = [1990, 2000, 2010, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

_CASES = [
    (f"{name} {y}", y, mo, d)
    for name, (mo, d) in FIXED.items() for y in _YEARS
]


@pytest.mark.parametrize("text,y,mo,d", _CASES)
def test_fixed_holiday_year(text, y, mo, d):
    assert start(text, A) == AstroDate(y, mo, d)
    assert span(text, A).width == timedelta(days=1)
