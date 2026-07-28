# -*- coding: utf-8 -*-
"""Season + explicit year across many years, meteorological-quarter convention:
άνοιξη = Mar-May, καλοκαίρι = Jun-Aug, φθινόπωρο = Sep-Nov, χειμώνας = Dec-Feb
(winter wraps into the following year). Edges are independent arithmetic.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

# season -> (start month, end month exclusive, wraps year)
SEASON = {
    "άνοιξη": (3, 6, False),
    "καλοκαίρι": (6, 9, False),
    "φθινόπωρο": (9, 12, False),
    "χειμώνας": (12, 3, True),
}
_YEARS = [2015, 2018, 2019, 2020, 2021, 2022, 2025]

_CASES = [
    (f"{name} {y}", y, smo, emo, wrap)
    for name, (smo, emo, wrap) in SEASON.items() for y in _YEARS
]


@pytest.mark.parametrize("text,y,smo,emo,wrap", _CASES)
def test_season_year_sweep(text, y, smo, emo, wrap):
    s, e = start_end(text, A)
    assert s == AstroDate(y, smo, 1)
    assert e == AstroDate(y + 1 if wrap else y, emo, 1)
