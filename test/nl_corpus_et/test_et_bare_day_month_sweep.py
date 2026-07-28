"""Estonian bare day+month (no year) rolls to its next occurrence.

``D. MONTH`` with no year names the next occurrence on or after the anchor
date (Tuesday 2017-06-27): a date strictly before that day rolls into the
following year, the anchor date itself and everything after it stays in the
anchor year.  Genitive and nominative month surfaces are both swept.  Gold is
independent arithmetic.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start_end
from .test_et_full_date_sweep import MONTHS

DAYS = [3, 10, 17, 24]


def _roll_year(mo, d):
    if datetime(2017, mo, d).date() < ANCHOR.date():
        return 2018
    return 2017


def _cases():
    for mo in range(1, 13):
        nom, gen = MONTHS[mo]
        for d in DAYS:
            y = _roll_year(mo, d)
            yield (f"{d}. {nom}", y, mo, d)
            if gen != nom:
                yield (f"{d}. {gen}", y, mo, d)


CASES = list(_cases())


@pytest.mark.parametrize("text,y,mo,d", CASES)
def test_bare_day_month_rolls(text, y, mo, d):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d))
    assert e == ad(datetime(y, mo, d) + timedelta(days=1))
