"""Wide sweep of Finnish DMY calendar dates.

Two families, both with hand-independent oracles that never consult the
parser:

* explicit-year dates ``"D. <month-partitive> YYYY"`` -> exactly that day;
* bare day+month ``"D. <month-partitive>"`` -> the next occurrence on or
  after the anchor (2017-06-27), rolling into 2018 for months already past.

The partitive month names (tammikuuta ... joulukuuta) are the ordinary way
a Finnish speaker writes a date, e.g. "15. maaliskuuta 1999".
"""
from datetime import date, datetime

import pytest

from ._corpus import ad, start, start_end

# nominative index -> partitive genitive-of-time month name
_PART = [
    None, "tammikuuta", "helmikuuta", "maaliskuuta", "huhtikuuta",
    "toukokuuta", "kesäkuuta", "heinäkuuta", "elokuuta", "syyskuuta",
    "lokakuuta", "marraskuuta", "joulukuuta",
]

_DAYS = [1, 4, 7, 11, 15, 19, 23, 28]
_YEARS = [1985, 1999, 2012, 2024]

_FULL = [
    (f"{d}. {_PART[mo]} {y}", y, mo, d)
    for y in _YEARS
    for mo in range(1, 13)
    for d in _DAYS
]


@pytest.mark.parametrize("text,y,mo,d", _FULL)
def test_full_date_sweep(text, y, mo, d):
    from datetime import timedelta
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d))
    # every full date is a one-day span; day+1 is always valid here since the
    # largest swept day is the 28th.
    assert e == ad(datetime(y, mo, d) + timedelta(days=1))


def _roll(mo, d):
    """Next occurrence of (mo, d) on or after 2017-06-27, else next year."""
    y = 2017 if (mo, d) >= (6, 27) else 2018
    return date(y, mo, d)


_BARE = [
    (f"{d}. {_PART[mo]}", *(_roll(mo, d).timetuple()[:3]))
    for mo in range(1, 13)
    for d in [3, 15, 22]
]


@pytest.mark.parametrize("text,y,mo,d", _BARE)
def test_bare_day_month_rolls(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))
