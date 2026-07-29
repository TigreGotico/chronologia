# -*- coding: utf-8 -*-
"""Second-pass resweep: Solar-Hijri closed ranges that CROSS a month or year
boundary (``از <d1> <mon1> [<y1>] تا <d2> <mon2> <y2>``).

The original range sweep (``test_nl_sweep_ranges_dayparts.py``) only exercises
same-month, same-year ranges.  Cross-month and cross-Esfand/Nowruz-boundary
ranges are new coverage.  Every endpoint is the independent Borkowski oracle
from ``_jalali``; the range resolves to [start-of-first-day,
end-of-last-day) with the last day inclusive, so the end is the day after the
closing date.  Year 1404 and any endpoint that lands in it are avoided, same
as the rest of the fa Solar-Hijri corpus.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end
from ._jalali import JMON, j2g

_CASES = [
    # (text, y1, m1, d1, y2, m2, d2)
    ("از 25 خرداد تا 5 تیر 1403", 1403, 3, 25, 1403, 4, 5),
    ("از 20 اسفند 1402 تا 5 فروردین 1403", 1402, 12, 20, 1403, 1, 5),
    ("از 20 مرداد 1401 تا 10 شهریور 1401", 1401, 5, 20, 1401, 6, 10),
    ("از 15 آذر 1400 تا 10 دی 1400", 1400, 9, 15, 1400, 10, 10),
    ("از 25 اردیبهشت 1399 تا 5 خرداد 1399", 1399, 2, 25, 1399, 3, 5),
    ("از 20 بهمن 1398 تا 15 اسفند 1398", 1398, 11, 20, 1398, 12, 15),
    ("از 10 تیر 1402 تا 20 مرداد 1402", 1402, 4, 10, 1402, 5, 20),
    ("از 1 مهر 1401 تا 10 آبان 1401", 1401, 7, 1, 1401, 8, 10),
]


@pytest.mark.parametrize("text,y1,m1,d1,y2,m2,d2", _CASES)
def test_solar_hijri_cross_range(text, y1, m1, d1, y2, m2, d2):
    s = j2g(y1, m1, d1)
    e = j2g(y2, m2, d2) + timedelta(days=1)
    assert start_end(text) == (ad(datetime(s.year, s.month, s.day)),
                               ad(datetime(e.year, e.month, e.day)))
