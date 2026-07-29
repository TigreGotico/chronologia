# -*- coding: utf-8 -*-
"""Second-pass Romanian day-range sweep: "de la D1 la D2 <month> <year>".

``test_nl_numeric_ranges.py`` only exercises months {2, 3, 5, 6, 9, 11} over
years {2020, 2021}. This sweep covers the complement months
{1, 4, 7, 8, 10, 12} over fresh years {2028, 2029, 2031}, with a fresh set of
day pairs, so no (text, gold) pair is duplicated.

The span is half-open ``[(y, m, D1), (y, m, D2+1))`` -- an inclusive D1..D2
range. Gold is plain ``datetime.date`` arithmetic, never read back from the
parser.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start_end, AstroDate

_MONTH = {
    1: "ianuarie", 4: "aprilie", 7: "iulie",
    8: "august", 10: "octombrie", 12: "decembrie",
}
_PAIRS = [(4, 11), (2, 16), (7, 19), (1, 8), (6, 25), (10, 20), (3, 13), (15, 28)]
_FRESH_YEARS = (2028, 2029, 2031)


def _cases():
    out = []
    for y in _FRESH_YEARS:
        for m in _MONTH:
            for d1, d2 in _PAIRS:
                out.append((f"de la {d1} la {d2} {_MONTH[m]} {y}", y, m, d1, d2))
    return out


@pytest.mark.parametrize("text,y,m,d1,d2", _cases())
def test_day_range_resweep(text, y, m, d1, d2):
    end = date(y, m, d2) + timedelta(days=1)
    s, e = start_end(text)
    assert s == AstroDate(y, m, d1), text
    assert e == AstroDate(end.year, end.month, end.day), text
