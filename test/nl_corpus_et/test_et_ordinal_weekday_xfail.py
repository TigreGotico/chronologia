"""REGRESSION: Estonian "MONTH Nth WEEKDAY" binds the ordinal to the weekday.

``märtsi kolmas esmaspäev`` means "the third Monday of March", not "the third
of March".  This used to strand the weekday token and treat the ordinal
(``kolmas``) as the day-of-month, resolving to the 3rd of the month instead of
the 3rd Monday.  It now binds correctly.  With no year the month takes the year the month alone
takes (ruling 1, changed 26 November 2026): a month that has ended at the anchor
(2017-06-27) is next year's, so March and April are 2018, July to October 2017.  The gold below is the true Nth weekday,
computed independently.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

# Mon=0 .. Sun=6
WD = {
    "esmaspäev": 0, "teisipäev": 1, "kolmapäev": 2, "neljapäev": 3,
    "reede": 4, "laupäev": 5, "pühapäev": 6,
}


def _nth_weekday(y, m, wd, n):
    days = [date(y, m, d) for d in range(1, 32)
            if _in_month(y, m, d) and date(y, m, d).weekday() == wd]
    return days[n - 1]


def _in_month(y, m, d):
    try:
        date(y, m, d)
        return True
    except ValueError:
        return False


# (phrase, gold year, gold month, weekday, ordinal-n) -- true Nth weekday.
# ruling 1: March and April have ended at the anchor, so they are 2018.
CASES = [
    ("märtsi kolmas esmaspäev", 2018, 3, "esmaspäev", 3),
    ("aprilli teine reede", 2018, 4, "reede", 2),
    ("juuli esimene esmaspäev", 2017, 7, "esmaspäev", 1),
    ("septembri neljas kolmapäev", 2017, 9, "kolmapäev", 4),
    ("oktoobri teine teisipäev", 2017, 10, "teisipäev", 2),
]


@pytest.mark.parametrize("text,y,mo,wd,n", CASES)
def test_ordinal_weekday(text, y, mo, wd, n):
    gold = _nth_weekday(y, mo, WD[wd], n)
    s, e = start_end(text)
    assert s == AstroDate(gold.year, gold.month, gold.day)
    assert e == AstroDate(gold.year, gold.month, gold.day) + timedelta(days=1)
