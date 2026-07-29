# -*- coding: utf-8 -*-
"""Second-pass sweep of the "vom N. bis zum M. <Monat> <Jahr>" day-range
idiom -- the fuller everyday phrasing with both "vom" and "zum" spelled
out, as distinct from the terser "von N. Monat bis M. Monat" surface the
original range file (``test_de_decades_ranges.py``) exercises. The engine
consumes the "vom .. bis .." span and strands the "zum" connective in the
remainder, which is fine: this corpus only asserts the parsed span, never
the leftover text.

Grid: 12 months x 5 fresh years (2018, 2020, 2022, 2024, 2026) x 3 day-pairs
per month (1-7, 5-12, 15-20), skipping pairs whose end day does not exist in
that month. Gold is the plain calendar day pair, inclusive end rolled to the
following day (a day-wide-per-day span, exclusive end).

Anchor 2017-06-27.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_MO = ["", "januar", "februar", "märz", "april", "mai", "juni", "juli",
       "august", "september", "oktober", "november", "dezember"]
_YEARS = (2018, 2020, 2022, 2024, 2026)
_PAIRS = ((1, 7), (5, 12), (15, 20))

_CASES = []
for _y in _YEARS:
    for _m in range(1, 13):
        _last = calendar.monthrange(_y, _m)[1]
        for _d1, _d2 in _PAIRS:
            if _d2 > _last:
                continue
            _CASES.append(
                (f"vom {_d1}. bis zum {_d2}. {_MO[_m]} {_y}",
                 date(_y, _m, _d1), date(_y, _m, _d2)))


@pytest.mark.parametrize("text,d1,d2", _CASES)
def test_vom_bis_zum_day_range(text, d1, d2):
    sp = span(text)
    assert sp.start == AstroDate(d1.year, d1.month, d1.day), f"{text!r} -> {sp}"
    nxt = d2 + timedelta(days=1)
    assert sp.end == AstroDate(nxt.year, nxt.month, nxt.day)


def test_grid_has_full_february_coverage():
    # February (28 days even in a non-leap year) still fits all three pairs
    texts = [t for t, *_ in _CASES if "februar 2018" in t]
    assert len(texts) == 3
