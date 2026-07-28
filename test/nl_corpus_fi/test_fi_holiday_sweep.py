"""Finnish holidays with an explicit year, swept across many years.

Two families:

* fixed-date holidays (New Year, Epiphany, Christmas Eve/Day, St Stephen's) —
  oracle is the constant month/day;
* Easter-relative holidays — oracle is Western computus computed here
  independently (Gauss/Anonymous algorithm), never the parser.

Movable Finnish civic holidays (juhannus etc.) are deliberately excluded.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import span, start


def _computus(y):
    """Western (Gregorian) Easter Sunday for year y — independent of parser."""
    a = y % 19
    b, c = divmod(y, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    mo = (h + ll - 7 * m + 114) // 31
    da = ((h + ll - 7 * m + 114) % 31) + 1
    return date(y, mo, da)


_YEARS = list(range(2018, 2031))

# ---- fixed-date holidays -------------------------------------------------

_FIXED = {
    "uudenvuodenpäivä": (1, 1),
    "loppiainen": (1, 6),
    "jouluaatto": (12, 24),
    "joulu": (12, 25),
    "joulupäivä": (12, 25),
    "tapaninpäivä": (12, 26),
}

_FIXED_CASES = [
    (f"{name} {y}", date(y, mo, d))
    for y in _YEARS
    for name, (mo, d) in _FIXED.items()
]


@pytest.mark.parametrize("text,d", _FIXED_CASES)
def test_fixed_holiday_year(text, d):
    assert start(text) == AstroDate(d.year, d.month, d.day)
    assert span(text).width == timedelta(days=1)


# ---- Easter-relative holidays -------------------------------------------

# holiday -> offset in days from Easter Sunday
_EASTER_REL = {
    "pitkäperjantai": -2,      # Good Friday
    "pääsiäinen": 0,           # Easter Sunday
    "toinen pääsiäispäivä": 1,  # Easter Monday
    "helatorstai": 39,         # Ascension
    "helluntai": 49,           # Pentecost
}

_EASTER_CASES = [
    (f"{name} {y}", _computus(y) + timedelta(days=off))
    for y in _YEARS
    for name, off in _EASTER_REL.items()
]


@pytest.mark.parametrize("text,d", _EASTER_CASES)
def test_easter_relative_year(text, d):
    assert start(text) == AstroDate(d.year, d.month, d.day)
    assert span(text).width == timedelta(days=1)
