"""Estonian full-date sweep (DMY, ordinal dot on the day).

Estonian writes calendar dates as ``D. MONTH YEAR`` where MONTH may be the
nominative citation form (``märts``) or, more idiomatically, the genitive
(``märtsi``) governed by the ordinal day.  Both are asserted across every
month, a spread of days, and several years.  A full date is a one-day span;
every expected value is derived by independent ``datetime`` arithmetic that
never touches the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end

# month index -> (nominative, genitive) citation surfaces
MONTHS = {
    1: ("jaanuar", "jaanuari"),
    2: ("veebruar", "veebruari"),
    3: ("märts", "märtsi"),
    4: ("aprill", "aprilli"),
    5: ("mai", "mai"),
    6: ("juuni", "juuni"),
    7: ("juuli", "juuli"),
    8: ("august", "augusti"),
    9: ("september", "septembri"),
    10: ("oktoober", "oktoobri"),
    11: ("november", "novembri"),
    12: ("detsember", "detsembri"),
}

DAYS = [1, 4, 7, 11, 15, 19, 23, 28]
YEARS = [1999, 2015, 2023]


def _cases():
    for y in YEARS:
        for mo in range(1, 13):
            nom, gen = MONTHS[mo]
            for d in DAYS:
                yield (f"{d}. {nom} {y}", y, mo, d)
                if gen != nom:
                    yield (f"{d}. {gen} {y}", y, mo, d)


CASES = list(_cases())


@pytest.mark.parametrize("text,y,mo,d", CASES)
def test_full_date(text, y, mo, d):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d))
    assert e == ad(datetime(y, mo, d) + timedelta(days=1))
