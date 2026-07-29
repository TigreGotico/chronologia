# -*- coding: utf-8 -*-
"""Third-pass sweep of the "vom N. bis zum M. <Monat> <Jahr>" day-range
idiom, on fresh years past both the original terser range file
(``test_de_decades_ranges.py``, 1920-2020 decade anchors) and the
second-pass "vom .. bis zum .." resweep (``test_de_resweep_day_ranges.py``,
2018/2020/2022/2024/2026).

Grid: 12 months x 5 fresh years (2031, 2035, 2039, 2043, 2047) x 3 day-pairs
per month (1-7, 5-12, 15-20), skipping pairs whose end day does not exist in
that month. Gold is the plain calendar day pair, inclusive end rolled to
the following day (a day-wide-per-day span, exclusive end).

Anchor 2017-06-27.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_MO = ["", "januar", "februar", "märz", "april", "mai", "juni", "juli",
       "august", "september", "oktober", "november", "dezember"]
_YEARS = (2031, 2035, 2039, 2043, 2047)
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
def test_vom_bis_zum_day_range_resweep3(text, d1, d2):
    sp = span(text)
    assert sp.start == AstroDate(d1.year, d1.month, d1.day), f"{text!r} -> {sp}"
    nxt = d2 + timedelta(days=1)
    assert sp.end == AstroDate(nxt.year, nxt.month, nxt.day)


def test_years_disjoint_from_prior_passes():
    _prior = {1920, 1930, 1940, 1950, 1960, 1970, 1980, 1981, 1990, 2000,
              2001, 2017, 2018, 2020, 2022, 2024, 2026}
    assert not (set(_YEARS) & _prior)


def test_grid_has_full_february_coverage():
    texts = [t for t, *_ in _CASES if "februar 2039" in t]
    assert len(texts) == 3
