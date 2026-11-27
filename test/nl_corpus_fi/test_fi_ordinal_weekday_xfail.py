"""REGRESSION: Finnish "Nth <weekday> of <month>" binds correctly.

"maaliskuun kolmas maanantai" means *the third Monday of March*.  This used
to mis-parse -- the parser read "kolmas" as the ordinal day-of-month (the
3rd) and dropped the weekday, returning March 3rd.  It now binds the ordinal
to the named weekday.  With no year the month takes the year the month alone takes
(ruling 1, changed 26 November 2026): March and May have ended at the anchor
(2017-06-27), so they are 2018; November is 2017.  Gold below is the true Nth-weekday computed independently.

Reproduction (anchor 2017-06-27):
    extract_timespan("maaliskuun kolmas maanantai", "fi", anchor)
    -> 2018-03-19  (the third Monday of March 2018; it was 2017-03-20 before ruling 1)
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

# ruling 1: a bare month takes the year the month alone takes; the anchor is
# 2017-06-27, so March and May (ended) are 2018 and November is 2017
_YEAR = 2017


def _nth_weekday(y, mo, wd, n):
    d = date(y, mo, 1)
    d += timedelta(days=(wd - d.weekday()) % 7)
    d += timedelta(weeks=n - 1)
    return d


_CASES = [
    (f"{mon} {ordw} {wdw}", _nth_weekday(_YEAR + (mo < 6), mo, wd, n))
    for mon, mo in _MON.items()
    for ordw, n in _ORD.items()
    for wdw, wd in _WD.items()
]


@pytest.mark.parametrize("text,d", _CASES)
def test_nth_weekday_of_month(text, d):
    assert start(text) == ad(datetime(d.year, d.month, d.day))
