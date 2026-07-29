# -*- coding: utf-8 -*-
"""Second-pass sweep: full day-month-year (ru), fresh days x fresh years.

Round 1 (``test_ru_full_dmy_sweep``) swept days (3, 10, 17, 24, 28) across all
twelve genitive months and years (2018, 2019, 2020, 2021, 2023, 2025). This
file sweeps three DIFFERENT days (6, 13, 20) across three FRESH years (2026,
2027, 2028), plus the trailing year-noun form "... года", so no (text) id
duplicates round 1.

Each is a one-day span [date, date+1).  Gold is the literal calendar date,
computed independently.  Days are kept <= 28 so every (day, month) pair is
valid in every year.  Anchor 2017-06-27 (module contract; unused for the
explicit-year reading).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

# fresh days, disjoint from round 1's (3, 10, 17, 24, 28)
_DAYS = (6, 13, 20)
# fresh years, disjoint from round 1's (2018, 2019, 2020, 2021, 2023, 2025)
_YEARS = (2026, 2027, 2028)


def _end(y, m, d):
    nxt = date(y, m, d) + timedelta(days=1)
    return AstroDate(nxt.year, nxt.month, nxt.day)


def _dmy_cases():
    out = []
    for m in range(1, 13):
        for d in _DAYS:
            for y in _YEARS:
                out.append((f"{d} {_MONTHS_GEN[m]} {y}", y, m, d))
    return out


def _dmy_goda_cases():
    out = []
    for m in range(1, 13):
        for d in _DAYS:
            for y in _YEARS:
                out.append((f"{d} {_MONTHS_GEN[m]} {y} года", y, m, d))
    return out


_DMY_CASES = _dmy_cases()
_GODA_CASES = _dmy_goda_cases()


@pytest.mark.parametrize("text,y,m,d", _DMY_CASES, ids=[c[0] for c in _DMY_CASES])
def test_full_dmy_fresh(text, y, m, d):
    st, en = start_end(text)
    assert st == AstroDate(y, m, d), text
    assert en == _end(y, m, d)


@pytest.mark.parametrize("text,y,m,d", _GODA_CASES, ids=[c[0] for c in _GODA_CASES])
def test_full_dmy_goda_fresh(text, y, m, d):
    st, en = start_end(text)
    assert st == AstroDate(y, m, d), text
    assert en == _end(y, m, d)
