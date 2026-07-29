"""REGRESSION: Finnish "Nth <weekday> of <month>" binds correctly.

"maaliskuun kolmas maanantai" means *the third Monday of March*.  This used
to mis-parse -- the parser read "kolmas" as the ordinal day-of-month (the
3rd) and dropped the weekday, returning March 3rd.  It now binds the ordinal
to the named weekday.  Like the "Nth weekday of month" construction in every
other locale, it does NOT roll to the future: a bare month keeps the anchor
year (2017).  Gold below is the true Nth-weekday computed independently.

Reproduction (anchor 2017-06-27):
    extract_timespan("maaliskuun kolmas maanantai", "fi", anchor)
    -> 2017-03-20  (the third Monday of March 2017)
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ad, start

# Finnish weekday name -> Python weekday() index (Mon=0)
_WD = {
    "maanantai": 0, "tiistai": 1, "keskiviikko": 2, "torstai": 3,
    "perjantai": 4, "lauantai": 5, "sunnuntai": 6,
}
# ordinal word -> n
_ORD = {"ensimmäinen": 1, "toinen": 2, "kolmas": 3, "neljäs": 4}
# month genitive -> month number
_MON = {"maaliskuun": 3, "toukokuun": 5, "marraskuun": 11}

# the construction does not roll to the future -- a bare month stays in the
# anchor year
_YEAR = 2017


def _nth_weekday(y, mo, wd, n):
    d = date(y, mo, 1)
    d += timedelta(days=(wd - d.weekday()) % 7)
    d += timedelta(weeks=n - 1)
    return d


_CASES = [
    (f"{mon} {ordw} {wdw}", _nth_weekday(_YEAR, mo, wd, n))
    for mon, mo in _MON.items()
    for ordw, n in _ORD.items()
    for wdw, wd in _WD.items()
]


@pytest.mark.parametrize("text,d", _CASES)
def test_nth_weekday_of_month(text, d):
    assert start(text) == ad(datetime(d.year, d.month, d.day))
