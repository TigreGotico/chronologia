"""Second-pass resweep: fixed-date and movable-feast holidays bound to an
explicit year, swept across a much wider decade span than
``test_nl_holidays_year.py`` (which only covers 2018-2023).

Fixed-date names and their (month, day) come straight from that file's own
``_FIXED`` table.  Movable feasts reuse the same independent Gregorian
computus (copied verbatim, not imported, so this file's oracle does not
depend on the other test module) plus the known day-offset from Easter
Sunday.  Years chosen deliberately straddle century/leap boundaries that the
original narrow window never touched.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

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

# deliberately outside the 2018-2023 window already covered elsewhere
_YEARS = (1996, 2000, 2004, 2010, 2016, 2024, 2028, 2032, 2036, 2040)


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


def _fixed_cases():
    return [(f"{n} {y}", n, y) for y in _YEARS for n in _FIXED]


def _movable_cases():
    return [(f"{n} {y}", n, y) for y in _YEARS for n in _MOVABLE]


@pytest.mark.parametrize("text,name,year", _fixed_cases())
def test_fixed_holiday_decade_sweep(text, name, year):
    mo, da = _FIXED[name]
    start = datetime(year, mo, da)
    end = start + timedelta(days=1)
    assert start_end(text) == (AstroDate(start.year, start.month, start.day),
                               AstroDate(end.year, end.month, end.day))


@pytest.mark.parametrize("text,name,year", _movable_cases())
def test_movable_feast_decade_sweep(text, name, year):
    start = _easter(year) + timedelta(days=_MOVABLE[name])
    end = start + timedelta(days=1)
    assert start_end(text) == (AstroDate(start.year, start.month, start.day),
                               AstroDate(end.year, end.month, end.day))
