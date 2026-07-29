# -*- coding: utf-8 -*-
"""Broad oracle sweep: month-thirds "početak/sredina/kraj <month>" (hr).

The month is sliced into three equal parts by total elapsed time: "početak"
(beginning) is the first third, "sredina" (middle) the second, "kraj" (end) the
last.  Boundaries fall on fractional times for 31-day (10d8h) and 28/29-day
months; 30-day months split cleanly on 10-day marks.

Gold divides the calendar-month interval into equal thirds INDEPENDENTLY of the
parser.  March is already covered by test_nl_month_fuzzy, so it is skipped here.
Anchor 2017-06-27; bare month resolves within the anchor year 2017.
"""
from datetime import datetime

import pytest

from ._corpus import AstroDate, start_end

_GEN = {1: 'siječnja', 2: 'veljače', 4: 'travnja', 5: 'svibnja',
        6: 'lipnja', 7: 'srpnja', 8: 'kolovoza', 9: 'rujna',
        10: 'listopada', 11: 'studenog', 12: 'prosinca'}
_PARTS = ['početak', 'sredina', 'kraj']


def _thirds(y, m):
    start = datetime(y, m, 1)
    end = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    tot = end - start
    b1 = start + tot / 3
    b2 = start + 2 * tot / 3
    return [(start, b1), (b1, b2), (b2, end)]


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


_CASES = []
for _m, _gen in _GEN.items():
    _ths = _thirds(2017, _m)
    for _i, _part in enumerate(_PARTS):
        _CASES.append((f"{_part} {_gen}", _ths[_i][0], _ths[_i][1]))


@pytest.mark.parametrize("phrase,s,e", _CASES, ids=[c[0] for c in _CASES])
def test_month_third(phrase, s, e):
    assert start_end(phrase) == (_ad(s), _ad(e)), phrase
