"""Estonian whole-month references (``MONTH YEAR``).

A bare month plus a year names the whole month: the span runs from the first
of that month to the first of the next.  Both the nominative citation form
(``märts 2019``) and the genitive (``märtsi 2019``) resolve identically.
Gold is independent ``datetime`` arithmetic.
"""
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ad, start_end
from .test_et_full_date_sweep import MONTHS

YEARS = [1988, 2011, 2024]


def _cases():
    for y in YEARS:
        for mo in range(1, 13):
            nom, gen = MONTHS[mo]
            yield (f"{nom} {y}", y, mo)
            if gen != nom:
                yield (f"{gen} {y}", y, mo)


CASES = list(_cases())


@pytest.mark.parametrize("text,y,mo", CASES)
def test_month_year(text, y, mo):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, 1))
    assert e == ad(datetime(y, mo, 1) + relativedelta(months=1))
