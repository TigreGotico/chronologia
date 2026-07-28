# -*- coding: utf-8 -*-
"""da: "<season> <year>" across many years.

Danish meteorological seasons, each a three-month block; vinter wraps into the
following March.  Boundaries are calendar constants, computed here, never read
from the parser.  test_da_scoped_seasons covers a couple of these plus the
relative forms; this file is the wide year sweep.
"""
import pytest

from ._corpus import start_end, AstroDate

# (start month, end month, end-year offset)
_SEASON = {
    "forår": (3, 6, 0),
    "sommer": (6, 9, 0),
    "efterår": (9, 12, 0),
    "vinter": (12, 3, 1),
}
_YEARS = tuple(range(2015, 2027))

_CASES = []
for _name, (_a, _b, _yoff) in _SEASON.items():
    for _y in _YEARS:
        _CASES.append((f"{_name} {_y}",
                       AstroDate(_y, _a, 1),
                       AstroDate(_y + _yoff, _b, 1)))


@pytest.mark.parametrize("text,s,e", _CASES)
def test_season_of_year(text, s, e):
    assert start_end(text) == (s, e)
