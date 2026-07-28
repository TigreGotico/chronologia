# -*- coding: utf-8 -*-
"""da: month-thirds -- "begyndelsen/midten/slutningen af <month> <year>".

The month is split into three equal wall-clock thirds; because a month is a
whole number of days, each third is an exact number of days-and-hours (the
seconds always divide evenly by three), so the boundaries are exact.  Gold is
computed here by dividing the month span, not read from the parser.

Every phrase carries an explicit year so the resolution is deterministic;
test_da_scoped_seasons carries the year-less fuzzy-month cases.
"""
from datetime import datetime

import pytest

from ._corpus import span, ad

_MONTHS = {1: "januar", 2: "februar", 3: "marts", 4: "april", 5: "maj",
           6: "juni", 7: "juli", 8: "august", 9: "september", 10: "oktober",
           11: "november", 12: "december"}
_POS = ["begyndelsen", "midten", "slutningen"]
_YEARS = (2019, 2020)  # 2020 is a leap year -> February thirds differ


def _thirds(y, m):
    ms = datetime(y, m, 1)
    nm = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    t = (nm - ms) / 3
    return [(ms, ms + t), (ms + t, ms + 2 * t), (ms + 2 * t, nm)]


_CASES = []
for _y in _YEARS:
    for _m, _mname in _MONTHS.items():
        bounds = _thirds(_y, _m)
        for _i, _pos in enumerate(_POS):
            _s, _e = bounds[_i]
            _CASES.append((f"{_pos} af {_mname} {_y}", _s, _e))


@pytest.mark.parametrize("text,s,e", _CASES)
def test_month_third(text, s, e):
    sp = span(text)
    assert (sp.start, sp.end) == (ad(s), ad(e))
