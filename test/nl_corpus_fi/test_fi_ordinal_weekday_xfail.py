"""BUG: Finnish "Nth <weekday> of <month>" is mis-parsed.

"maaliskuun kolmas maanantai" means *the third Monday of March*, but the
parser reads "kolmas" as the ordinal day-of-month (the 3rd) and ignores the
weekday entirely, returning March 3rd.  Gold below is the true Nth-weekday
computed independently; these are strict-xfail until the parser binds the
ordinal to the named weekday.

Reproduction (anchor 2017-06-27):
    extract_timespan("maaliskuun kolmas maanantai", "fi", anchor)
    -> 2018-03-03  (WRONG; the third Monday of March 2018 is 2018-03-19)
"""
from datetime import date, timedelta

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


def _nth_weekday(y, mo, wd, n):
    d = date(y, mo, 1)
    d += timedelta(days=(wd - d.weekday()) % 7)
    d += timedelta(weeks=n - 1)
    return d


# next occurrence of that month on/after the anchor => 2018 for these months
_YEAR = 2018

# The parser (buggily) returns day-of-month == n.  Keep only cases where the
# true Nth-weekday lands on a *different* day, so the strict-xfail is a genuine
# mismatch and never coincidentally XPASSes.
_CASES = [
    (f"{mon} {ordw} {wdw}", d)
    for mon, mo in _MON.items()
    for ordw, n in _ORD.items()
    for wdw, wd in _WD.items()
    for d in [_nth_weekday(_YEAR, mo, wd, n)]
    if d.day != n
]


@pytest.mark.xfail(reason="ordinal not bound to named weekday; reads as "
                          "day-of-month", strict=True)
@pytest.mark.parametrize("text,d", _CASES)
def test_nth_weekday_of_month(text, d):
    assert start(text) == ad_date(d)


def ad_date(d):
    from datetime import datetime
    return ad(datetime(d.year, d.month, d.day))
