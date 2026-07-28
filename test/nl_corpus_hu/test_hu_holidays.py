"""Hungarian calendar holidays, year-qualified ("2019. húsvét"), swept across
many years.  Fixed-date feasts land on their civil date; the movable feasts
are anchored to Gregorian Easter, whose date is computed here by the Anonymous
Gregorian algorithm -- an independent oracle that never consults the parser.

Easter-relative offsets (Western reckoning):
  nagypéntek (Good Friday)      Easter - 2
  húsvét / húsvétvasárnap        Easter
  húsvéthétfő (Easter Monday)    Easter + 1
  pünkösd (Pentecost/Whitsun)    Easter + 49
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end


def _easter(year):
    """Anonymous Gregorian computus -> date of Western Easter Sunday."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)


def _day_span(dt):
    return ad(dt), ad(dt + timedelta(days=1))


_YEARS = list(range(2000, 2031))

# -- fixed-date feasts ----------------------------------------------------
_FIXED = {
    "újév": (1, 1),
    "mindenszentek": (11, 1),
    "szenteste": (12, 24),
    "karácsony": (12, 25),
}

_FIXED_CASES = [
    (y, name, mo, d) for y in _YEARS for name, (mo, d) in _FIXED.items()
]


@pytest.mark.parametrize("y,name,mo,d", _FIXED_CASES)
def test_fixed_holiday(y, name, mo, d):
    assert start_end(f"{y}. {name}") == _day_span(datetime(y, mo, d))


# -- Easter-anchored movable feasts --------------------------------------
_MOVABLE = {
    "nagypéntek": -2,
    "húsvét": 0,
    "húsvétvasárnap": 0,
    "húsvéthétfő": 1,
    "pünkösd": 49,
}

_MOVABLE_CASES = [
    (y, name, off) for y in _YEARS for name, off in _MOVABLE.items()
]


@pytest.mark.parametrize("y,name,off", _MOVABLE_CASES)
def test_movable_holiday(y, name, off):
    target = _easter(y) + timedelta(days=off)
    assert start_end(f"{y}. {name}") == _day_span(target)
