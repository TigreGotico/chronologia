# -*- coding: utf-8 -*-
"""Oracle sweep: ``YEARko MONTH`` names a whole calendar month.

"2020ko iraila" is the span ``[YYYY-MM-01, next-month-01)``.  December wraps
into the following January.  Gold is independent ``datetime`` arithmetic.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end
from ._sweep import MONTH_ABS

YEARS = [1789, 1918, 1969, 2001, 2016, 2020]

CASES = [(f"{y}ko {MONTH_ABS[mo]}", y, mo)
         for y in YEARS for mo in range(1, 13)]


def _month_bounds(y, mo):
    start = datetime(y, mo, 1)
    end = datetime(y + 1, 1, 1) if mo == 12 else datetime(y, mo + 1, 1)
    return start, end


@pytest.mark.parametrize("text,y,mo", CASES)
def test_year_month_whole_month(text, y, mo):
    s, e = start_end(text)
    gs, ge = _month_bounds(y, mo)
    assert (s, e) == (ad(gs), ad(ge))
