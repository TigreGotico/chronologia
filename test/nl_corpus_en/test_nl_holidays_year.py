"""Named holidays pinned to an explicit year: "christmas 2019",
"good friday 2021", "ash wednesday 2023".

Once a year is stated the anchor's next-occurrence roll no longer applies --
the holiday resolves inside that named year, one civil day wide.

Fixed-date feasts carry a hardcoded month/day.  Movable (Easter-relative)
feasts are derived here by an INDEPENDENT Gregorian computus plus the known
day-offset from Easter Sunday -- the parser never defines the gold.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end


def _easter(year):
    """Anonymous Gregorian computus -- independent Easter Sunday oracle."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    month = (h + ll - 7 * m + 114) // 31
    day = ((h + ll - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)


_YEARS = (2018, 2019, 2020, 2021, 2022, 2023)

# fixed-date holidays: name -> (month, day)
_FIXED = {
    "new years day": (1, 1),
    "new years eve": (12, 31),
    "christmas": (12, 25),
    "christmas day": (12, 25),
    "christmas eve": (12, 24),
    "boxing day": (12, 26),
    "valentines day": (2, 14),
    "st patricks day": (3, 17),
    "halloween": (10, 31),
    "all saints day": (11, 1),
    "epiphany": (1, 6),
}

# movable feasts: name -> day-offset from Easter Sunday
_MOVABLE = {
    "easter": 0,
    "good friday": -2,
    "easter monday": 1,
    "ash wednesday": -46,
    "mardi gras": -47,
    "palm sunday": -7,
    "pentecost": 49,
    "ascension day": 39,
}


def _fixed_cases():
    return [(f"{n} {y}", n, y) for y in _YEARS for n in _FIXED]


def _movable_cases():
    return [(f"{n} {y}", n, y) for y in _YEARS for n in _MOVABLE]


@pytest.mark.parametrize("text,name,year", _fixed_cases())
def test_fixed_holiday_year(text, name, year):
    mo, da = _FIXED[name]
    start = datetime(year, mo, da)
    end = start + timedelta(days=1)
    assert start_end(text) == (AstroDate(start.year, start.month, start.day),
                               AstroDate(end.year, end.month, end.day))


@pytest.mark.parametrize("text,name,year", _movable_cases())
def test_movable_feast_year(text, name, year):
    start = _easter(year) + timedelta(days=_MOVABLE[name])
    end = start + timedelta(days=1)
    assert start_end(text) == (AstroDate(start.year, start.month, start.day),
                               AstroDate(end.year, end.month, end.day))
