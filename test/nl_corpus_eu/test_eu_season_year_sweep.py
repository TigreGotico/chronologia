# -*- coding: utf-8 -*-
"""Oracle sweep: ``SEASON YEAR`` names a meteorological-quarter span.

udaberria (spring) Mar-Jun, uda (summer) Jun-Sep, udazkena (autumn) Sep-Dec,
negua (winter) Dec-Mar of the following year.  Gold is independent arithmetic.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end

# season -> (start month, end month, end-year offset)
SEASONS = {
    "udaberria": (3, 6, 0),
    "uda": (6, 9, 0),
    "udazkena": (9, 12, 0),
    "negua": (12, 3, 1),
}

YEARS = [1789, 1918, 1969, 2001, 2016, 2019, 2020, 2024]

CASES = [(f"{name} {y}", name, y) for name in SEASONS for y in YEARS]


@pytest.mark.parametrize("text,name,y", CASES)
def test_season_year_span(text, name, y):
    smo, emo, eoff = SEASONS[name]
    s, e = start_end(text)
    assert s == ad(datetime(y, smo, 1))
    assert e == ad(datetime(y + eoff, emo, 1))
