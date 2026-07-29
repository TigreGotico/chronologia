# -*- coding: utf-8 -*-
"""Second-pass sweep: Slovak full day-month-year dates "D. <gen-month> Y",
fresh day/month/year combinations.

test_sk_dmy_sweep.py covers years [2000, 2010, 2018, 2019, 2020, 2021, 2023,
2025] against a fixed 28-day-pair grid. This sweep uses a disjoint day-pair
per month (two per month, none repeated from the earlier grid) across eight
fresh years. The span is exactly that single day, computed by plain ``date``
arithmetic -- never read from the parser."""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_GEN = [None, "januára", "februára", "marca", "apríla", "mája", "júna",
        "júla", "augusta", "septembra", "októbra", "novembra", "decembra"]

_YEARS = (2001, 2011, 2016, 2017, 2022, 2024, 2026, 2027)

# two fresh (day, month) pairs per month, disjoint from test_sk_dmy_sweep.py.
_DM = [(2, 1), (18, 1), (6, 2), (22, 2), (11, 3), (29, 3), (4, 4), (19, 4),
       (8, 5), (23, 5), (2, 6), (16, 6), (11, 7), (28, 7), (3, 8), (19, 8),
       (14, 9), (29, 9), (6, 10), (22, 10), (9, 11), (24, 11), (2, 12),
       (19, 12)]


def _day(y, m, d):
    nxt = date(y, m, d) + timedelta(days=1)
    return AstroDate(y, m, d), AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("d,m", _DM)
def test_dmy_fresh(d, m, year):
    text = f"{d}. {_GEN[m]} {year}"
    assert start_end(text) == _day(year, m, d), text
